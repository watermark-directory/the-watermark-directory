"""Site graph/timeline feed exporters (#620): sets→sorted lists, ``""``→None, Counter→dict."""

from __future__ import annotations

from collections import Counter

from bosc.pipeline.entities import Entity, EntityGraph, Relationship
from bosc.pipeline.timeline import TimelineEvent
from bosc.site.graph import export_entities, export_relationships, export_timeline


def test_export_timeline_carries_fields_and_a_document_citation() -> None:
    events = [
        TimelineEvent(
            date="2025-08-13",
            category="deed_recorded",
            title="Seven-parcel deed recorded",
            source="recorder/deed.yaml",
            ref="instr-8300",
            parties=("Bistrozzi LLC",),
            detail="340.2 ac",
            also_sources=("auditor/transfer.yaml",),
        )
    ]
    out = export_timeline(events)
    assert len(out) == 1
    e = out[0]
    assert e.title == "Seven-parcel deed recorded"
    assert e.ref == "instr-8300"
    assert e.parties == ["Bistrozzi LLC"]  # tuple → list
    assert e.also_sources == ["auditor/transfer.yaml"]
    assert e.citation.source == "recorder/deed.yaml"
    assert e.citation.source_kind == "document"


def test_export_entities_sorts_sets_and_keeps_role_counts() -> None:
    g = EntityGraph()
    g.entities["GOOGLE"] = Entity(
        key="GOOGLE",
        kind="corporate",
        classification="operator",
        variants={"Google LLC", "Google"},
        signals={"offtaker", "anchor"},
        roles=Counter({"applicant": 2, "grantee": 1}),
        parcels={"P2", "P1"},
        sources={"s2", "s1"},
    )
    g.entities["TRUST"] = Entity(key="TRUST", kind="trust", classification="seller")
    out = export_entities(g)
    # Sorted by (kind, key): corporate GOOGLE before trust TRUST.
    assert [n.key for n in out] == ["GOOGLE", "TRUST"]
    node = out[0]
    assert node.variants == ["Google", "Google LLC"]  # set → sorted list
    assert node.signals == ["anchor", "offtaker"]
    assert node.parcels == ["P1", "P2"]
    assert node.sources == ["s1", "s2"]
    assert node.roles == {"applicant": 2, "grantee": 1}  # Counter → dict, most_common order


def test_export_relationships_blanks_overlay_to_none() -> None:
    g = EntityGraph()
    g.relationships.append(
        Relationship(
            src="A", rel="owned_by", dst="GOOGLE", source="s1"
        )  # relation_class="" default
    )
    g.relationships.append(
        Relationship(
            src="B",
            rel="operates",
            dst="C",
            source="s2",
            relation_class="adverse",
            relation_basis="cited",
        )
    )
    out = export_relationships(g)
    assert out[0].relation_class is None and out[0].relation_basis is None  # "" → None
    assert out[1].relation_class == "adverse" and out[1].relation_basis == "cited"
