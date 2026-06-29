"""P5: POI place nodes in the entity graph."""

from __future__ import annotations

from watermark.config import Settings
from watermark.pipeline.entities import EntityGraph, enrich_with_places, normalize_name


def test_enrich_with_places_adds_node_and_owner_edge(poi_settings: Settings) -> None:
    graph = EntityGraph()
    graph._register("Bistrozzi LLC", role="grantee", source="deed.yaml")  # the owner org
    enrich_with_places(graph, settings=poi_settings)

    place = graph.entities.get("data-center-campus")
    assert place is not None
    assert place.kind == "place"
    assert place.classification == "place_watched"
    assert len(place.parcels) == 10
    assert {"tracked", "composite"} <= place.signals
    assert "data/entities/poi/data-center-campus.md" in place.sources

    # The owner relationship links the place to the pre-existing corpus org node.
    owner_key = normalize_name("Bistrozzi LLC")  # -> "BISTROZZI"
    edges = [r for r in graph.relationships if r.src == "data-center-campus"]
    assert any(e.rel == "owner" and e.dst == owner_key for e in edges)


def test_enrich_with_places_skips_unknown_targets(poi_settings: Settings) -> None:
    # No corpus org exists here, so the place node is still created but the owner edge
    # is skipped (never fabricated) — the same discipline as every overlay.
    graph = enrich_with_places(EntityGraph(), settings=poi_settings)
    assert "data-center-campus" in graph.entities
    assert graph.relationships == []  # owner target absent → no fabricated edge
