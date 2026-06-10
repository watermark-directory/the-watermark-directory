"""P5: POI place nodes in the entity graph + place pages on the site."""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings
from bosc.pipeline.entities import EntityGraph, enrich_with_places, normalize_name
from bosc.poi.store import load_poi, load_pois
from bosc.site.places import PlacePage, render_place_page, render_place_pages, render_places_index


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
    assert "data/poi/data-center-campus.md" in place.sources

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


def test_render_place_page(poi_settings: Settings) -> None:
    campus = load_poi("data-center-campus", settings=poi_settings)
    assert campus is not None
    md = render_place_page(campus)
    assert md.startswith("# Data-center campus")
    assert "*composite, depth: watched*" in md
    assert "36-0100-03-002.000" in md  # a parcel in the meta block
    assert "owner → Bistrozzi LLC" in md  # the relationship
    assert "imagery — sentinel-2-l2a" in md  # tracking row
    assert "## Sources" in md


def test_place_page_cross_links_graph(poi_settings: Settings) -> None:
    graph = enrich_with_places(EntityGraph(), settings=poi_settings)
    campus = load_poi("data-center-campus", settings=poi_settings)
    assert campus is not None
    md = render_place_page(campus, egraph=graph)
    assert "Appears in the [entity graph](../entities.md) as `data-center-campus`" in md


def test_render_place_pages_and_index(poi_settings: Settings, tmp_path: Path) -> None:
    pois = load_pois(settings=poi_settings)
    pages = render_place_pages(pois, tmp_path)
    assert any(p.slug == "data-center-campus" and p.tracked for p in pages)
    assert (tmp_path / "data-center-campus.md").is_file()

    index = render_places_index(
        [
            PlacePage("a-parcel", "A Parcel", "parcel", "located", 1, False),
            PlacePage("data-center-campus", "Data-center campus", "composite", "watched", 10, True),
        ]
    )
    assert index.startswith("# Places")
    assert "**2** places" in index and "**1** are tracked" in index
    assert "[Data-center campus](data-center-campus.md)" in index
