"""The geo feeds assembled outside gis-findings: WBD watershed + imagery AOIs (#61).

Unit-level checks of the exporters (the full-bundle integrity is in
``tests/test_site_bundle.py``). Hermetic: reads committed reference data + the POI store.
"""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings
from bosc.site import gismap

REPO_ROOT = Path(__file__).resolve().parents[1]


def _settings() -> Settings:
    return Settings(data_dir=REPO_ROOT / "data")


def test_export_watershed_geo_is_coarse_to_fine() -> None:
    fc = gismap.export_watershed_geo(_settings())
    assert fc is not None
    assert fc.feed == "watershed"
    levels = [(f.properties.model_extra or {}).get("level") for f in fc.features]
    assert levels == sorted(levels), "features must run coarsest → finest (finer draws on top)"
    names = {(f.properties.model_extra or {}).get("name") for f in fc.features}
    assert names == {"Pike Run", "Middle Ottawa River"}
    for f in fc.features:
        assert f.properties.layer == "watershed"
        assert f.properties.role == "area"
        assert f.properties.color
        assert f.geometry["type"] in ("Polygon", "MultiPolygon")
    assert fc.meta["crs"].startswith("WGS84")
    assert fc.meta["levels"] == [10, 12]


def test_export_imagery_geo_has_aoi_and_wayback_ladder() -> None:
    fc = gismap.export_imagery_geo(_settings())
    assert fc is not None
    assert fc.feed == "imagery"
    assert fc.features, "expected at least one tracked AOI footprint"
    aoi = fc.features[0]
    assert aoi.properties.layer == "imagery"
    assert aoi.properties.role == "area"
    assert aoi.geometry["type"] == "Polygon"
    # A footprint ring is closed (first == last vertex).
    ring = aoi.geometry["coordinates"][0]
    assert ring[0] == ring[-1]

    wayback = fc.meta["wayback"]
    assert wayback["releases"], "the dated Wayback ladder must be present for the slider"
    assert all("date" in r and "release" in r for r in wayback["releases"])
    assert "{release}" in wayback["tile_url_template"]
