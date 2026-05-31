"""Tests for cross-document entity resolution."""

from __future__ import annotations

from bosc.models import Deed, DeedExtraction, NpdesExtraction, NpdesPermit
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
