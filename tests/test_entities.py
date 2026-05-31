"""Tests for cross-document entity resolution."""

from __future__ import annotations

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
    build_entity_graph,
    classify,
    normalize_name,
)


def test_normalize_merges_legal_variants() -> None:
    assert normalize_name("BISTROZZI LLC") == "BISTROZZI"
    assert normalize_name("Bistrozzi LLC, a Delaware Limited Liability Company") == "BISTROZZI"
    assert (
        normalize_name("THE PORT AUTHORITY OF ALLEN COUNTY, OHIO")
        == "PORT AUTHORITY OF ALLEN COUNTY"
    )


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
