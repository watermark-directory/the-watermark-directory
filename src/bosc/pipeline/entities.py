"""Entity resolution — a small cross-document graph of who relates to whom.

Phase C item 5. Parties appear across deeds, NPDES permits, and SoS business
filings under inconsistent spellings ("BISTROZZI LLC" vs "Bistrozzi LLC, a
Delaware Limited Liability Company"). This module normalizes them to a canonical
key, merges the variants into one :class:`Entity`, classifies each (government /
corporate / individual / trust / facility / water), and records the relationships
between them (conveyances, utility operation, discharge, plus — from SoS filings —
who organized an LLC and its registered agent). A registered agent shared by more
than one entity is flagged with a ``shared_agent`` signal.

Classification follows the *conservative* posture of Periplus's owner-
classification rationale (see ``docs/reference/periplus/`` / the ``../gis`` fork):
prefer a plain corporate/individual label over a "shell" accusation; record
shell-adjacent signals (e.g. a Delaware registration) as evidence, not verdicts.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from bosc.logging import get_logger
from bosc.pipeline.corpus import Corpus, load_corpus

log = get_logger(__name__)

# Legal-form tokens stripped from the *key* (kept in the display name).
_LEGAL_SUFFIXES = frozenset(
    {
        "LLC",
        "LLP",
        "LP",
        "INC",
        "CORP",
        "CORPORATION",
        "CO",
        "COMPANY",
        "LTD",
        "LIMITED",
        "LIABILITY",
        "PLLC",
        "TRUST",
    }
)
_CORPORATE_TOKENS = frozenset(
    {"LLC", "LLP", "LP", "INC", "CORP", "CORPORATION", "COMPANY", "LTD", "PLLC"}
)
# Phrases that mark a government / public body (matched on the raw upper string).
_GOV_PHRASES = (
    "PORT AUTHORITY",
    "BOARD OF COMMISSIONERS",
    "COMMISSIONERS",
    "STATE OF OHIO",
    "CITY OF",
    "VILLAGE OF",
    "SANITARY ENGINEER",
    "BOARD OF EDUCATION",
    "BOARD OF TOWNSHIP",
    "COUNTY ENGINEER",
    "LAND BANK",
    "HOUSING AUTHORITY",
)
# Out-of-state incorporation hints — a shell-adjacent *signal*, never a verdict.
_FOREIGN_HINTS = ("DELAWARE", "WYOMING", "NEVADA")
_FACILITY_HINTS = ("WWTP", "TREATMENT PLANT", "TREATMENT WORKS", "WASTEWATER")
_WATER_HINTS = ("RUN", "RIVER", "CREEK", "DITCH", "DRAIN", "LAKE")


def _base_permit(permit_no: str) -> str:
    """Strip the ``*LD`` / ``*MD`` action suffix to a stable facility id."""
    return permit_no.split("*", 1)[0].strip()


def normalize_name(raw: str) -> str:
    """Canonical key: uppercased, descriptive clause and legal suffixes removed.

    ``"Bistrozzi LLC, a Delaware Limited Liability Company"`` and ``"BISTROZZI
    LLC"`` both reduce to ``"BISTROZZI"``, so they resolve to one entity.
    """
    head = raw.upper().split(",", 1)[0]  # drop the post-comma descriptive clause
    head = re.sub(r"[^\w\s&]", " ", head)
    tokens = head.split()
    while tokens and tokens[0] == "THE":
        tokens.pop(0)
    while tokens and tokens[-1] in _LEGAL_SUFFIXES:
        tokens.pop()
    return " ".join(tokens)


def classify(raw: str) -> tuple[str, str, tuple[str, ...]]:
    """Return ``(kind, classification, signals)`` for a party name.

    Conservative: a name is only ``corporate_out_of_state`` (not "shell") when an
    out-of-state hint is present, and that hint is also surfaced as a signal.
    """
    up = raw.upper()
    signals = tuple(h.lower() for h in _FOREIGN_HINTS if h in up)

    if any(h in up for h in _FACILITY_HINTS):
        return "facility", "facility", signals
    is_county_body = bool(re.search(r"\bCOUNTY\b", up)) and "FARM" not in up
    if any(p in up for p in _GOV_PHRASES) or is_county_body:
        return "government", "government_local", signals
    if "TRUST" in up or "TRUSTEE" in up:
        return "trust", "trust", signals
    if any(re.search(rf"\b{re.escape(t)}\b", up) for t in _CORPORATE_TOKENS):
        klass = "corporate_out_of_state" if signals else "corporate_domestic"
        return "corporate", klass, signals
    if any(re.search(rf"\b{h}\b", up) for h in _WATER_HINTS):
        return "water", "receiving_water", signals
    return "individual", "individual", signals


@dataclass
class Entity:
    """A resolved party, merged from one or more raw name variants."""

    key: str
    kind: str  # government | corporate | individual | trust | facility | water
    classification: str
    variants: set[str] = field(default_factory=set)
    signals: set[str] = field(default_factory=set)
    roles: Counter[str] = field(default_factory=Counter)  # grantee/grantor/applicant/...
    parcels: set[str] = field(default_factory=set)
    addresses: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)

    @property
    def display(self) -> str:
        """Shortest legible variant (the long legal recitals aren't useful here)."""
        return min(self.variants, key=len) if self.variants else self.key


@dataclass(frozen=True)
class Relationship:
    """A directed edge between two entity keys, traceable to one document."""

    src: str
    rel: str  # conveyed_to | operates | discharges_to
    dst: str
    date: str = ""
    ref: str = ""  # instrument / permit number
    source: str = ""


@dataclass
class EntityGraph:
    entities: dict[str, Entity] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)

    def get(self, name: str) -> Entity | None:
        """Look up an entity by raw name or canonical key."""
        return self.entities.get(normalize_name(name)) or self.entities.get(name)

    def _register(
        self,
        raw: str,
        *,
        role: str,
        source: str,
        parcels: tuple[str, ...] = (),
        key: str | None = None,
    ) -> str:
        # An explicit key (e.g. a permit number for a facility) merges name
        # variants that normalization alone wouldn't; otherwise key by name.
        key = key or normalize_name(raw)
        if not key:
            return key
        kind, klass, signals = classify(raw)
        ent = self.entities.get(key)
        if ent is None:
            ent = Entity(key=key, kind=kind, classification=klass)
            self.entities[key] = ent
        ent.variants.add(raw)
        ent.roles[role] += 1
        ent.sources.add(source)
        ent.parcels.update(parcels)
        # Signals accumulate across variants — a Delaware hint may appear in only
        # one spelling — so resolution is order-independent. Upgrade a corporate
        # entity to out-of-state once any variant carries a foreign hint.
        ent.signals.update(signals)
        if ent.kind == "corporate":
            ent.classification = "corporate_out_of_state" if ent.signals else "corporate_domestic"
        return key


def build_entity_graph(corpus: Corpus | None = None) -> EntityGraph:
    """Resolve entities and relationships across deeds, NPDES permits, SoS filings."""
    corpus = corpus if corpus is not None else load_corpus()
    graph = EntityGraph()

    for rel, ex in corpus.deeds:
        d = ex.deed
        parcels = tuple(d.parcel_ids)
        grantees = [
            graph._register(g, role="grantee", source=rel, parcels=parcels) for g in d.grantees
        ]
        for grantor_raw in d.grantors:
            src_key = graph._register(grantor_raw, role="grantor", source=rel, parcels=parcels)
            for dst_key in grantees:
                if src_key and dst_key:
                    graph.relationships.append(
                        Relationship(
                            src_key,
                            "conveyed_to",
                            dst_key,
                            date=d.recording_date or "",
                            ref=d.instrument_no or "",
                            source=rel,
                        )
                    )

    for rel, pex in corpus.permits:
        p = pex.permit
        facility_key = ""
        if p.facility_name:
            # Identity of a facility is its *base* permit number (the ``*LD``/``*MD``
            # action suffix varies between a permit's draft, fact sheet, and final).
            fkey = f"npdes:{_base_permit(p.permit_no)}" if p.permit_no else None
            facility_key = graph._register(p.facility_name, role="facility", source=rel, key=fkey)
        if p.applicant:
            applicant_key = graph._register(p.applicant, role="applicant", source=rel)
            if applicant_key and facility_key:
                graph.relationships.append(
                    Relationship(
                        applicant_key, "operates", facility_key, ref=p.permit_no or "", source=rel
                    )
                )
        if p.receiving_water and facility_key:
            # "Dug Run at River Mile 3.1" and "Dug Run" are the same water.
            water_raw = re.split(r"\s+(?:at|near|@)\s+", p.receiving_water, maxsplit=1, flags=re.I)[
                0
            ]
            water_key = graph._register(water_raw, role="receiving_water", source=rel)
            if water_key:
                graph.relationships.append(
                    Relationship(
                        facility_key, "discharges_to", water_key, ref=p.permit_no or "", source=rel
                    )
                )

    for rel, sex in corpus.filings:
        f = sex.filing
        if not f.entity_name:
            continue
        ent_key = graph._register(f.entity_name, role="registrant", source=rel)
        ent = graph.entities[ent_key]
        if f.principal_address:
            ent.addresses.add(f.principal_address)
        # A foreign formation jurisdiction is a recorded signal (and, for a
        # corporate entity, upgrades it to out-of-state) — straight from the
        # filing, not inferred from the name.
        if f.jurisdiction and f.jurisdiction.strip().lower() not in ("ohio", "oh", ""):
            ent.signals.add(f.jurisdiction.strip().lower())
            if ent.kind == "corporate":
                ent.classification = "corporate_out_of_state"
        if f.registered_agent:
            agent_key = graph._register(f.registered_agent, role="registered_agent", source=rel)
            if f.agent_address:
                graph.entities[agent_key].addresses.add(f.agent_address)
            graph.relationships.append(
                Relationship(
                    ent_key,
                    "registered_agent",
                    agent_key,
                    date=f.filing_date or "",
                    ref=f.filing_id or "",
                    source=rel,
                )
            )
        if f.organizer:
            org_key = graph._register(f.organizer, role="organizer", source=rel)
            graph.relationships.append(
                Relationship(
                    ent_key,
                    "organized_by",
                    org_key,
                    date=f.filing_date or "",
                    ref=f.filing_id or "",
                    source=rel,
                )
            )

    for rel, eex in corpus.actions:
        a = eex.action
        app_key = ""
        if a.applicant:
            app_key = graph._register(a.applicant, role="epa_applicant", source=rel)
            if a.applicant_address:
                graph.entities[app_key].addresses.add(a.applicant_address)
        if a.contact_name:
            contact_key = graph._register(a.contact_name, role="permit_contact", source=rel)
            # Representation/affiliation are not permit-specific — blank ref so the
            # same relationship across many letters collapses to one edge.
            if app_key and contact_key:
                graph.relationships.append(
                    Relationship(app_key, "represented_by", contact_key, source=rel)
                )
            if a.contact_firm:
                firm_key = graph._register(a.contact_firm, role="firm", source=rel)
                if firm_key:
                    graph.relationships.append(
                        Relationship(contact_key, "affiliated_with", firm_key, source=rel)
                    )

    # The same conveyance / operation is reported by multiple artifacts; collapse
    # identical edges (keep the first, dropping exact duplicates).
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[Relationship] = []
    for r in graph.relationships:
        # Collapse the permit ``*LD``/``*MD`` action suffix so the same discharge
        # reported under two permit versions is one edge; deed instruments (no
        # ``*``) are untouched, keeping genuinely distinct conveyances apart.
        edge = (r.src, r.rel, r.dst, _base_permit(r.ref))
        if edge in seen:
            continue
        seen.add(edge)
        unique.append(r)
    graph.relationships = unique

    # Shell-pattern signal: a registered agent (or an agent address) shared by
    # more than one entity. This is the strongest shell tell public SoS records
    # offer — it does not reveal beneficial ownership, only common control plumbing.
    agent_to_entities: dict[str, set[str]] = defaultdict(set)
    addr_to_entities: dict[str, set[str]] = defaultdict(set)
    for r in graph.relationships:
        if r.rel == "registered_agent":
            agent_to_entities[r.dst].add(r.src)
            for addr in graph.entities[r.dst].addresses:
                addr_to_entities[addr].add(r.src)
    for shared in (*agent_to_entities.values(), *addr_to_entities.values()):
        if len(shared) > 1:
            for ent_key in shared:
                graph.entities[ent_key].signals.add("shared_agent")

    log.info("entities.built", entities=len(graph.entities), relationships=len(graph.relationships))
    return graph
