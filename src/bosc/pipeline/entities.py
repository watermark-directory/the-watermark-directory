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

import yaml

from bosc.config import Settings, get_settings
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


def _looks_like_person(s: str) -> bool:
    """Heuristic: 2-4 capitalized name tokens, no corporate/government markers.

    "Randy Barrera", "Scott J. Ziance" -> True; "Bistrozzi LLC", "NEFF FARMS",
    "Allen County Board of Commissioners" -> False.
    """
    s = s.strip()
    if not s:
        return False
    up = s.upper()
    if any(re.search(rf"\b{re.escape(t)}\b", up) for t in _CORPORATE_TOKENS):
        return False
    if "COUNTY" in up or "TRUST" in up or " AND " in f" {up} ":
        return False
    tokens = s.split()
    if not 2 <= len(tokens) <= 4:
        return False
    # Each token is an initial ("J.") or a Capitalized word with a lowercase tail
    # ("Randy") — ALL-CAPS tokens ("NEFF", "FARMS") are rejected as org-like.
    return all(re.fullmatch(r"[A-Z]\.?|[A-Z][a-z][a-zA-Z.'-]*", t) for t in tokens)


def _split_principal(raw: str) -> tuple[str, str | None]:
    """Split a "Person, Org LLC" applicant into ``(org, person)``.

    The model sometimes records an applicant as "Randy Barrera, Tilted Gate LLC".
    Resolve the org as the primary entity and the person as its principal. Returns
    ``(raw, None)`` when the string isn't that pattern (e.g. "Bistrozzi LLC, a
    Delaware limited liability company" — the part before the comma isn't a
    person, so it is left intact).
    """
    if "," not in raw:
        return raw, None
    before, after = (p.strip() for p in raw.split(",", 1))
    after_is_org = bool(
        re.search(r"\b(?:LLC|LLP|LP|INC|CORP|CORPORATION|COMPANY|LTD|PLLC)\b", after.upper())
    )
    if (
        _looks_like_person(before)
        and after_is_org
        and not after.lower().startswith(("a ", "an ", "the "))
    ):
        return after, before
    return raw, None


def _split_multi(raw: str) -> list[str]:
    """Split a field that the model packed with multiple values into parts.

    Splits only on ``;`` and newlines — *not* commas, because a firm name carries
    internal commas ("Vorys, Sater, Seymour, and Pease"). ``"Heather Dardinger;
    Scott J. Ziance"`` -> two names.
    """
    return [p.strip() for p in re.split(r"[;\n]", raw) if p.strip()]


def normalize_name(raw: str) -> str:
    """Canonical key: uppercased, descriptive clause and legal suffixes removed.

    ``"Bistrozzi LLC, a Delaware Limited Liability Company"`` and ``"BISTROZZI
    LLC"`` both reduce to ``"BISTROZZI"``; ``"Scott J. Ziance"`` and ``"Scott
    Ziance"`` both reduce to ``"SCOTT ZIANCE"`` (interior single-letter initials
    are dropped) so name variants resolve to one entity.
    """
    head = raw.upper().split(",", 1)[0]  # drop the post-comma descriptive clause
    head = re.sub(r"[^\w\s&]", " ", head)
    tokens = head.split()
    while tokens and tokens[0] == "THE":
        tokens.pop(0)
    while tokens and tokens[-1] in _LEGAL_SUFFIXES:
        tokens.pop()
    # Drop interior single-letter initials (a middle initial is matching noise);
    # keep the first and last token so "C T" (CT Corporation) is left intact.
    if len(tokens) > 2:
        tokens = [tokens[0], *[t for t in tokens[1:-1] if len(t) > 1], tokens[-1]]
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
    # conveyed_to | operates | discharges_to | registered_agent | organized_by |
    # represented_by | affiliated_with | principal_of
    rel: str
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


def build_entity_graph(
    corpus: Corpus | None = None,
    *,
    enrich_parcels: bool = False,
    settings: Settings | None = None,
) -> EntityGraph:
    """Resolve entities and relationships across deeds, NPDES permits, SoS filings.

    With ``enrich_parcels=True`` the corpus-derived graph is augmented with cited
    parcel-owner context from ``data/reference/allen-gis`` (see
    :func:`enrich_with_parcel_owners`) — kept opt-in so the pure corpus graph that
    the tests assert on stays unchanged.
    """
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
            # "Randy Barrera, Tilted Gate LLC" -> org is the applicant entity, the
            # person becomes its principal (de-fragments the org across letters).
            org_raw, person_raw = _split_principal(a.applicant)
            app_key = graph._register(org_raw, role="epa_applicant", source=rel)
            if a.applicant_address:
                graph.entities[app_key].addresses.add(a.applicant_address)
            if person_raw:
                principal_key = graph._register(person_raw, role="principal", source=rel)
                if principal_key and app_key:
                    graph.relationships.append(
                        Relationship(principal_key, "principal_of", app_key, source=rel)
                    )
        # A letter may pack several contacts / firms into one field; split them so
        # each resolves to its own node. Representation/affiliation aren't permit-
        # specific, so blank ref lets repeats across letters collapse to one edge.
        contact_keys = []
        for name in _split_multi(a.contact_name or ""):
            ck = graph._register(name, role="permit_contact", source=rel)
            if ck and ck != app_key:
                contact_keys.append(ck)
                if app_key:
                    graph.relationships.append(
                        Relationship(app_key, "represented_by", ck, source=rel)
                    )
        for firm in _split_multi(a.contact_firm or ""):
            fk = graph._register(firm, role="firm", source=rel)
            # Skip a "firm" that is actually the applicant itself (model slip).
            if not fk or fk == app_key:
                continue
            for ck in contact_keys:
                graph.relationships.append(Relationship(ck, "affiliated_with", fk, source=rel))

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
    if enrich_parcels:
        enrich_with_parcel_owners(graph, settings=settings)
    return graph


def enrich_with_parcel_owners(
    graph: EntityGraph, *, settings: Settings | None = None
) -> EntityGraph:
    """Augment a corpus-built graph with cited parcel-owner context (committed data).

    Two additions, both from ``data/reference/allen-gis`` (verbatim county CAMA):

    1. **The federally-held JSMC / Lima Army Tank Plant land** — it appears in no
       deed in the corpus, so it is invisible to the corpus-only graph, yet it is
       the documented Allen County defense-industry footprint. Added as a single
       ``government_military`` node (owner ``UNITED STATES``) carrying its parcels,
       situs addresses, and an ``army_controlled`` signal.
    2. **CAMA situs addresses** for parcels the corpus already tracks — attached to
       the existing grantee/grantor nodes that hold those parcel ids (Bistrozzi and
       its grantors are already corpus-derived; this just grounds their addresses).

    Mutates and returns ``graph``. Idempotent.
    """
    settings = settings or get_settings()
    ref = settings.reference_dir / "allen-gis"

    defense = ref / "parcels.defense.yaml"
    if defense.is_file():
        data = yaml.safe_load(defense.read_text(encoding="utf-8")) or {}
        army = data.get("army_controlled") or []
        if army:
            key = normalize_name("UNITED STATES")
            ent = graph.entities.get(key) or Entity(
                key=key, kind="government", classification="government_military"
            )
            graph.entities[key] = ent
            for p in army:
                for variant in (p.get("owner"), p.get("deeded_owner")):
                    if variant:
                        ent.variants.add(str(variant))
                if p.get("parcel_no"):
                    ent.parcels.add(str(p["parcel_no"]))
                if p.get("situs_address"):
                    ent.addresses.add(str(p["situs_address"]))
            ent.roles["parcel_owner"] += len(army)
            ent.signals.update({"army_controlled", "defense_land"})
            ent.sources.add("data/reference/allen-gis/parcels.defense.yaml")

    cited = ref / "parcels.cited.yaml"
    if cited.is_file():
        data = yaml.safe_load(cited.read_text(encoding="utf-8")) or {}
        by_pid = {
            re.sub(r"\D", "", str(p.get("parcel_no"))): p
            for p in (data.get("parcels") or [])
            if p.get("parcel_no")
        }
        for ent in graph.entities.values():
            for pid in ent.parcels:
                rec = by_pid.get(re.sub(r"\D", "", str(pid)))
                if rec and rec.get("situs_address"):
                    ent.addresses.add(str(rec["situs_address"]))
    return graph
