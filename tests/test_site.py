"""GIS findings geojson + RSEI-layer-merge tests for the bosc.site data layer."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gis_findings_geojson_is_valid() -> None:
    import json

    path = REPO_ROOT / "data" / "site" / "gis-findings.geojson"
    fc = json.loads(path.read_text(encoding="utf-8"))
    assert fc["type"] == "FeatureCollection"
    layers = {f["properties"]["layer"] for f in fc["features"]}
    assert {"campus", "jsmc", "wwtp", "floodway", "floodplain", "rsei"} <= layers
    # The corridor view layers it in: a study-area polygon + the roadwork road centerline.
    assert {"corridor", "roadwork"} <= layers
    # Every feature has non-empty geometry (polygons for areas, points for WWTPs/RSEI,
    # a line for the corridor roadwork centerline).
    for f in fc["features"]:
        assert f["geometry"]["type"] in (
            "Polygon",
            "MultiPolygon",
            "Point",
            "LineString",
            "MultiLineString",
        )
        assert f["geometry"]["coordinates"]
    # RSEI points carry a graduated radius + score for the sized overlay markers.
    rsei = [f for f in fc["features"] if f["properties"]["layer"] == "rsei"]
    assert len(rsei) >= 40
    assert all(f["geometry"]["type"] == "Point" for f in rsei)
    assert all("radius" in f["properties"] and "score" in f["properties"] for f in rsei)


def test_merge_rsei_layer_is_idempotent() -> None:
    """Merging RSEI points twice yields the same single rsei layer (no duplication)."""
    from bosc.config import Settings
    from bosc.rsei import load_inventory
    from bosc.site.gismap import merge_rsei_layer

    inv = load_inventory(Settings(data_dir=REPO_ROOT / "data").reference_dir)
    assert inv is not None
    base: dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"layer": "wwtp", "label": "x"},
            }
        ],
    }
    once, n1 = merge_rsei_layer(base, inv)
    twice, n2 = merge_rsei_layer(once, inv)
    assert n1 == n2 > 0
    rsei_once = [f for f in once["features"] if f["properties"]["layer"] == "rsei"]
    rsei_twice = [f for f in twice["features"] if f["properties"]["layer"] == "rsei"]
    assert len(rsei_once) == len(rsei_twice) == n1
    # The pre-existing non-rsei feature is preserved.
    assert any(f["properties"]["layer"] == "wwtp" for f in twice["features"])


def test_merge_rsei_layer_rings_flagged_water_dischargers() -> None:
    """With the toxic screen, critical water dischargers get a water_flag property."""
    from bosc.config import Settings
    from bosc.hydrology import toxics
    from bosc.rsei import load_inventory
    from bosc.site.gismap import merge_rsei_layer

    ref = Settings(data_dir=REPO_ROOT / "data").reference_dir
    inv = load_inventory(ref)
    screen = toxics.build_screen(Settings(data_dir=REPO_ROOT / "data"))
    assert inv is not None
    base: dict = {"type": "FeatureCollection", "features": []}
    fc, _ = merge_rsei_layer(base, inv, screen)
    flagged = [f for f in fc["features"] if f["properties"].get("water_flag")]
    # The three Ottawa-corridor majors plus the one elevated terminal.
    assert {f["properties"]["water_flag"] for f in flagged} <= {"critical", "elevated"}
    assert sum(1 for f in flagged if f["properties"]["water_flag"] == "critical") == 3
    # A ringed feature names its receiving water in the popup label.
    crit = next(f for f in flagged if f["properties"]["water_flag"] == "critical")
    assert "toxic water discharger" in crit["properties"]["label"]
    # Without the screen, no rings.
    plain, _ = merge_rsei_layer({"type": "FeatureCollection", "features": []}, inv)
    assert not any(f["properties"].get("water_flag") for f in plain["features"])
