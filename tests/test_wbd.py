"""USGS WBD connector + the committed watershed boundaries (issue #61).

Hermetic: the connector replays the recorded WBD responses from
``tests/fixtures/hydrology/wbd/`` (offline), and the committed reference GeoJSON under
``data/reference/hydrology/wbd/`` is checked for shape + provenance. No network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from watermark.config import Settings
from watermark.gis.sites import get_site
from watermark.hydrology.connectors import wbd
from watermark.hydrology.connectors._cache import HydroOfflineError

REPO_ROOT = Path(__file__).resolve().parents[1]
WBD_DIR = REPO_ROOT / "data" / "reference" / "hydrology" / "wbd"


def _campus_centroid(settings: Settings) -> tuple[float, float]:
    """The data-center campus AOI centroid — the point the fixtures were recorded at."""
    site = get_site("data-center-campus", settings=settings)
    assert site is not None, "the data-center-campus tracking site must exist"
    minx, miny, maxx, maxy = site.bbox
    return (minx + maxx) / 2.0, (miny + maxy) / 2.0


def test_fetch_huc12_is_pike_run(hydro_settings: Settings) -> None:
    lon, lat = _campus_centroid(hydro_settings)
    hu = wbd.fetch_huc_at_point(lon, lat, level=12, settings=hydro_settings)
    assert hu is not None
    assert hu.huc == "041000070404"
    assert hu.name == "Pike Run"
    assert hu.level == 12
    assert hu.hu_label == "Subwatershed"
    assert hu.to_huc == "041000070406"
    assert hu.geometry["type"] in ("Polygon", "MultiPolygon")


def test_fetch_huc10_is_middle_ottawa_river(hydro_settings: Settings) -> None:
    lon, lat = _campus_centroid(hydro_settings)
    hu = wbd.fetch_huc_at_point(lon, lat, level=10, settings=hydro_settings)
    assert hu is not None
    assert hu.huc == "0410000704"
    assert hu.name == "Middle Ottawa River"
    assert hu.level == 10


def test_watershed_chain_is_finest_first(hydro_settings: Settings) -> None:
    lon, lat = _campus_centroid(hydro_settings)
    chain = wbd.watershed_chain(lon, lat, settings=hydro_settings)
    assert [hu.level for hu in chain] == [12, 10]
    assert chain[0].name == "Pike Run"


def test_unsupported_level_raises(hydro_settings: Settings) -> None:
    with pytest.raises(ValueError, match="unsupported HU level"):
        wbd.fetch_huc_at_point(-84.12, 40.79, level=6, settings=hydro_settings)


def test_offline_miss_raises_actionably(hydro_settings: Settings) -> None:
    """An unrecorded point must raise (naming the key to record), never fabricate a unit."""
    with pytest.raises(HydroOfflineError):
        wbd.fetch_huc_at_point(-83.0, 40.0, level=12, settings=hydro_settings)


def test_committed_boundaries_are_valid_and_provenanced() -> None:
    files = {p.name for p in WBD_DIR.glob("*.geojson")}
    assert files == {
        "041000070404-pike-run.geojson",
        "0410000704-middle-ottawa-river.geojson",
    }
    for path in sorted(WBD_DIR.glob("*.geojson")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["type"] == "FeatureCollection"
        assert len(doc["features"]) == 1
        meta = doc["meta"]
        assert "USGS" in meta["source"]
        assert meta["crs"].startswith("WGS84")
        feat = doc["features"][0]
        assert feat["properties"]["huc"] == meta["huc"]
        assert feat["geometry"]["type"] in ("Polygon", "MultiPolygon")
