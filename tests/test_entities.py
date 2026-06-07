"""Tests for cross-document entity resolution."""

from __future__ import annotations

from bosc.config import Settings
from bosc.models import (
    BusinessFiling,
    Deed,
    DeedExtraction,
    EpaExtraction,
    EpaPermitAction,
    NpdesExtraction,
    NpdesPermit,
    SosExtraction,
)
from bosc.pipeline.corpus import Corpus
from bosc.pipeline.entities import (
    _base_permit,
    _looks_like_person,
    _split_multi,
    _split_principal,
    build_entity_graph,
    classify,
    enrich_with_parcel_owners,
    normalize_name,
)


def test_normalize_merges_legal_variants() -> None:
    assert normalize_name("BISTROZZI LLC") == "BISTROZZI"
    assert normalize_name("Bistrozzi LLC, a Delaware Limited Liability Company") == "BISTROZZI"
    assert (
        normalize_name("THE PORT AUTHORITY OF ALLEN COUNTY, OHIO")
        == "PORT AUTHORITY OF ALLEN COUNTY"
    )


def test_normalize_drops_middle_initial_but_keeps_two_token_orgs() -> None:
    # "Scott J. Ziance" and "Scott Ziance" resolve to one person.
    assert normalize_name("Scott J. Ziance") == normalize_name("Scott Ziance") == "SCOTT ZIANCE"
    # A two-token org ("C T Corporation") keeps both letters — no interior to drop.
    assert normalize_name("C T Corporation") == "C T"


def test_split_multi_splits_on_semicolons_not_firm_commas() -> None:
    assert _split_multi("Heather Dardinger; Scott J. Ziance") == [
        "Heather Dardinger",
        "Scott J. Ziance",
    ]
    # A firm name with internal commas stays whole.
    assert _split_multi("EMH&T; Vorys, Sater, Seymour, and Pease") == [
        "EMH&T",
        "Vorys, Sater, Seymour, and Pease",
    ]
    assert _split_multi("EMH&T") == ["EMH&T"]


def test_base_permit_strips_action_suffix() -> None:
    assert _base_permit("2PK00002*MD") == "2PK00002"
    assert _base_permit("2PK00002*LD") == "2PK00002"
    assert _base_permit("2PH00006") == "2PH00006"


def test_classify_is_conservative() -> None:
    assert classify("THE PORT AUTHORITY OF ALLEN COUNTY, OHIO")[:2] == (
        "government",
        "government_local",
    )
    assert classify("Allen County Board of Commissioners")[0] == "government"
    kind, klass, signals = classify("Bistrozzi LLC, a Delaware Limited Liability Company")
    assert (kind, klass) == ("corporate", "corporate_out_of_state")
    assert "delaware" in signals
    assert classify("NEFF FARMS, INC.")[:2] == ("corporate", "corporate_domestic")
    assert classify("American II Wastewater Treatment Plant")[0] == "facility"
    assert classify("Kyle C. Brenneman, Co-Trustee of the Living Trust")[0] == "trust"
    assert classify("James W. Neighbors")[0] == "individual"
    # A corporate token wins over the water-name heuristic.
    assert classify("Pike Run Farms LLC")[0] == "corporate"


def test_looks_like_person() -> None:
    assert _looks_like_person("Randy Barrera")
    assert _looks_like_person("Scott J. Ziance")
    assert not _looks_like_person("Bistrozzi LLC")
    assert not _looks_like_person("NEFF FARMS")
    assert not _looks_like_person("Allen County Board of Commissioners")
    assert not _looks_like_person("Kyle C. Brenneman and Sarah N. Brenneman")


def test_split_principal() -> None:
    assert _split_principal("Randy Barrera, Tilted Gate LLC") == (
        "Tilted Gate LLC",
        "Randy Barrera",
    )
    assert _split_principal("Timothy Chadwick, Tilted Gate, LLC") == (
        "Tilted Gate, LLC",
        "Timothy Chadwick",
    )
    # Not the pattern: a bare org, or an org followed by a descriptive clause.
    assert _split_principal("Bistrozzi LLC") == ("Bistrozzi LLC", None)
    assert _split_principal("Bistrozzi LLC, a Delaware limited liability company") == (
        "Bistrozzi LLC, a Delaware limited liability company",
        None,
    )
    assert _split_principal("THE PORT AUTHORITY OF ALLEN COUNTY, OHIO")[1] is None


def _deed(
    rel: str, *, no: str, grantor: str, grantee: str, parcels: list[str]
) -> tuple[str, DeedExtraction]:
    return rel, DeedExtraction(
        doc_id=no,
        source_path=f"/x/{no}.pdf",
        kind="deed",
        dpi=200,
        deed=Deed(
            instrument_no=no,
            recording_date="2025-08-13",
            grantors=[grantor],
            grantees=[grantee],
            parcel_ids=parcels,
        ),
    )


def _permit(
    rel: str, *, no: str, facility: str, applicant: str, water: str
) -> tuple[str, NpdesExtraction]:
    return rel, NpdesExtraction(
        doc_id=no,
        source_path=f"/x/{rel}",
        kind="npdes",
        dpi=150,
        permit=NpdesPermit(
            permit_no=no, facility_name=facility, applicant=applicant, receiving_water=water
        ),
    )


def test_build_graph_resolves_and_links() -> None:
    corpus = Corpus(
        deeds=[
            _deed(
                "recorder/a.deed.yaml",
                no="I1",
                grantor="NEFF FARMS, INC.",
                grantee="BISTROZZI LLC",
                parcels=["P1"],
            ),
            _deed(
                "recorder/b.deed.yaml",
                no="I2",
                grantor="Pike Run Farms LLC",
                grantee="Bistrozzi LLC, a Delaware Limited Liability Company",
                parcels=["P2"],
            ),
        ],
        permits=[
            # Same base permit, different action suffix + name spelling.
            _permit(
                "oepa/p1.npdes.yaml",
                no="2PK00002*LD",
                facility="Shawnee II WWTP",
                applicant="Allen County Board of Commissioners",
                water="Ottawa River",
            ),
            _permit(
                "oepa/p2.npdes.yaml",
                no="2PK00002*MD",
                facility="Shawnee II Wastewater Treatment Works",
                applicant="Allen County Board of Commissioners",
                water="Ottawa River at River Mile 5",
            ),
        ],
    )
    graph = build_entity_graph(corpus)

    # The two Bistrozzi spellings resolve to one grantee with both parcels.
    bistrozzi = graph.get("BISTROZZI LLC")
    assert bistrozzi is not None
    assert bistrozzi.roles["grantee"] == 2
    assert bistrozzi.parcels == {"P1", "P2"}
    assert "delaware" in bistrozzi.signals

    # The facility merges across the *LD/*MD suffix into a single entity.
    facilities = [e for e in graph.entities.values() if e.kind == "facility"]
    assert len(facilities) == 1
    assert facilities[0].roles["facility"] == 2

    rels = {(r.src, r.rel, r.dst) for r in graph.relationships}
    assert ("NEFF FARMS", "conveyed_to", "BISTROZZI") in rels
    assert ("PIKE RUN FARMS", "conveyed_to", "BISTROZZI") in rels
    # "Ottawa River" and "Ottawa River at River Mile 5" collapse to one water node.
    discharges = [r for r in graph.relationships if r.rel == "discharges_to"]
    assert len(discharges) == 1


def test_parcel_enrichment_adds_jsmc_node(hydro_settings: Settings) -> None:
    # Enrichment is opt-in: the corpus-only graph is unchanged...
    base = build_entity_graph()
    assert base.get("UNITED STATES") is None
    # ...and adding parcel context surfaces the federally-held JSMC tank-plant land.
    enriched = build_entity_graph(enrich_parcels=True, settings=hydro_settings)
    jsmc = enriched.get("UNITED STATES")
    assert jsmc is not None
    assert jsmc.kind == "government" and jsmc.classification == "government_military"
    assert {"army_controlled", "defense_land"} <= jsmc.signals
    assert len(jsmc.parcels) == 5
    assert any("BUCKEYE" in a for a in jsmc.addresses)
    assert len(enriched.entities) == len(base.entities) + 1


def test_parcel_enrichment_is_idempotent(hydro_settings: Settings) -> None:
    graph = build_entity_graph(enrich_parcels=True, settings=hydro_settings)
    n = len(graph.entities)
    enrich_with_parcel_owners(graph, settings=hydro_settings)  # second pass
    assert len(graph.entities) == n


def _filing(
    rel: str, *, name: str, agent: str, agent_addr: str, organizer: str, juris: str
) -> tuple[str, SosExtraction]:
    return rel, SosExtraction(
        doc_id=name,
        source_path=f"/x/{rel}",
        kind="sos",
        dpi=200,
        filing=BusinessFiling(
            entity_name=name,
            entity_type="foreign LLC",
            jurisdiction=juris,
            filing_date="2025-10-01",
            registered_agent=agent,
            agent_address=agent_addr,
            organizer=organizer,
        ),
    )


def test_sos_filings_link_organizer_agent_and_flag_shared_agent() -> None:
    corpus = Corpus(
        filings=[
            _filing(
                "permits/m.sos.yaml",
                name="Magenta Capital LLC",
                agent="Corporation Service Company",
                agent_addr="1160 Dublin Rd",
                organizer="Michael Montfort",
                juris="Delaware",
            ),
            _filing(
                "permits/t.sos.yaml",
                name="Tilted Gate LLC",
                agent="Corporation Service Company",
                agent_addr="1160 Dublin Rd",
                organizer="Michael Montfort",
                juris="Delaware",
            ),
            _filing(
                "permits/b.sos.yaml",
                name="Bistrozzi Addition LLC",
                agent="C T Corporation",
                agent_addr="4400 East Commons Way",
                organizer="Scott J. Ziance",
                juris="Delaware",
            ),
        ]
    )
    graph = build_entity_graph(corpus)

    # The Delaware foreign filing upgrades each LLC to out-of-state.
    magenta = graph.get("Magenta Capital LLC")
    assert magenta is not None
    assert magenta.classification == "corporate_out_of_state"
    assert "delaware" in magenta.signals

    # Magenta + Tilted share an agent → both flagged; Bistrozzi Addition is not.
    assert "shared_agent" in graph.get("Magenta Capital LLC").signals
    assert "shared_agent" in graph.get("Tilted Gate LLC").signals
    assert "shared_agent" not in graph.get("Bistrozzi Addition LLC").signals

    # One organizer (Montfort) appears on two filings.
    montfort = graph.get("Michael Montfort")
    assert montfort is not None and montfort.roles["organizer"] == 2

    rels = {(r.src, r.rel, r.dst) for r in graph.relationships}
    assert ("MAGENTA CAPITAL", "organized_by", "MICHAEL MONTFORT") in rels
    assert ("TILTED GATE", "registered_agent", "CORPORATION SERVICE") in rels


def test_epa_action_links_to_same_applicant_entity() -> None:
    # A deed grantee and an EPA-permit applicant with the same name resolve to ONE
    # entity carrying both roles — the land thread and the regulatory thread meet.
    corpus = Corpus(
        deeds=[
            _deed(
                "recorder/a.deed.yaml",
                no="I1",
                grantor="Neff Farms",
                grantee="BISTROZZI LLC",
                parcels=["P1"],
            ),
        ],
        actions=[
            (
                "permits/pti.epa.yaml",
                EpaExtraction(
                    doc_id="e",
                    source_path="/x/pti.pdf",
                    kind="epa",
                    dpi=150,
                    action=EpaPermitAction(
                        agency="Ohio EPA",
                        program="Surface Water Permit-to-Install",
                        permit_no="DSWPTI-260294",
                        action="approved",
                        action_date="2026-04-07",
                        applicant="Bistrozzi LLC",
                        project_name="BOSC-1A",
                        contact_name="Scott Ziance",
                        contact_firm="Vorys",
                    ),
                ),
            ),
        ],
    )
    graph = build_entity_graph(corpus)
    bistrozzi = graph.get("BISTROZZI LLC")
    assert bistrozzi is not None
    assert bistrozzi.roles["grantee"] == 1
    assert bistrozzi.roles["epa_applicant"] == 1  # same node, both threads
    rels = {(r.src, r.rel, r.dst) for r in graph.relationships}
    assert ("BISTROZZI", "represented_by", "SCOTT ZIANCE") in rels
    assert ("SCOTT ZIANCE", "affiliated_with", "VORYS") in rels


def _epa(rel: str, *, applicant: str) -> tuple[str, EpaExtraction]:
    return rel, EpaExtraction(
        doc_id=rel,
        source_path=f"/x/{rel}",
        kind="epa",
        dpi=150,
        action=EpaPermitAction(
            agency="USACE",
            program="Section 404",
            applicant=applicant,
            action="application",
            action_date="2026-04-01",
        ),
    )


def test_epa_multi_value_contacts_split_into_separate_nodes() -> None:
    rel = "permits/x.epa.yaml"
    corpus = Corpus(
        actions=[
            (
                rel,
                EpaExtraction(
                    doc_id="x",
                    source_path=f"/x/{rel}",
                    kind="epa",
                    dpi=150,
                    action=EpaPermitAction(
                        agency="USACE",
                        program="Section 404",
                        applicant="Tilted Gate LLC",
                        action="application",
                        action_date="2026-04-01",
                        contact_name="Heather Dardinger; Scott J. Ziance",
                        contact_firm="EMH&T; Vorys, Sater, Seymour, and Pease",
                    ),
                ),
            ),
        ]
    )
    graph = build_entity_graph(corpus)
    # Two distinct contacts, not one conflated node.
    assert graph.get("Heather Dardinger") is not None
    assert graph.get("Scott Ziance") is not None  # middle initial dropped
    assert graph.get("Heather Dardinger; Scott J. Ziance") is None
    rels = {(r.src, r.rel, r.dst) for r in graph.relationships}
    # The firm with internal commas resolves to VORYS, not a combined junk node.
    assert ("HEATHER DARDINGER", "affiliated_with", "VORYS") in rels
    assert ("SCOTT ZIANCE", "affiliated_with", "EMH&T") in rels


def test_person_org_applicant_splits_into_principal_edge() -> None:
    # Two letters name the applicant as "<person>, Tilted Gate LLC" with different
    # people; both must resolve to ONE Tilted Gate org with two principal edges.
    corpus = Corpus(
        actions=[
            _epa("permits/a.epa.yaml", applicant="Randy Barrera, Tilted Gate LLC"),
            _epa("permits/b.epa.yaml", applicant="Timothy Chadwick, Tilted Gate, LLC"),
        ]
    )
    graph = build_entity_graph(corpus)
    tilted = graph.get("Tilted Gate LLC")
    assert tilted is not None and tilted.kind == "corporate"
    assert tilted.roles["epa_applicant"] == 2  # de-fragmented, not split across variants
    rels = {(r.src, r.rel, r.dst) for r in graph.relationships}
    assert ("RANDY BARRERA", "principal_of", "TILTED GATE") in rels
    assert ("TIMOTHY CHADWICK", "principal_of", "TILTED GATE") in rels
    # The person node is an individual, not the conflated corporate "Person, LLC".
    barrera = graph.get("Randy Barrera")
    assert barrera is not None and barrera.kind == "individual"
