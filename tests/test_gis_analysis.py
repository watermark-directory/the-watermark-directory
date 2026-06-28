"""GIS imagery analysis: NDVI/NDWI over the campus AOI, offline (band fixtures)."""

from __future__ import annotations

from pathlib import Path

import pytest
import rasterio
import yaml

from watermark.config import Settings
from watermark.gis import imagery
from watermark.gis.analysis import compute_index
from watermark.gis.imagery import Scene


def _campus_top(settings: Settings) -> tuple[object, Scene]:
    site, scenes = imagery.search_site(
        "data-center-campus",
        collection="sentinel-2-l2a",
        datetime_range="2024-06-01/2024-09-30",
        max_cloud=20.0,
        limit=5,
        settings=settings,
    )
    return site, scenes[0]  # T17TKF — the scene we have B03/B04/B08 fixtures for


def test_compute_ndvi_offline(gis_settings: Settings, tmp_path: Path) -> None:
    site, scene = _campus_top(gis_settings)
    r = compute_index(scene, site, index="ndvi", out_dir=tmp_path, settings=gis_settings)  # type: ignore[arg-type]

    assert r.index == "ndvi"
    assert r.epsg == 32617
    assert r.valid_fraction == 1.0
    assert r.mean is not None and 0.15 < r.mean < 0.5  # vegetated Sept farmland
    assert r.water_fraction is None  # NDVI has no water stat

    tif = Path(r.path)
    assert tif.name == "2024-09-20.ndvi.tif"
    with rasterio.open(tif) as ds:
        assert ds.count == 1 and ds.dtypes[0] == "float32" and ds.crs.to_epsg() == 32617

    meta = yaml.safe_load(Path(r.sidecar).read_text())["meta"]
    assert meta["index"] == "ndvi" and meta["source"] == "derived"
    assert "B08" in meta["formula"] and "B04" in meta["formula"]
    assert meta["sha256"] == r.sha256


def test_compute_ndwi_offline_water_fraction(gis_settings: Settings, tmp_path: Path) -> None:
    site, scene = _campus_top(gis_settings)
    r = compute_index(scene, site, index="ndwi", out_dir=tmp_path, settings=gis_settings)  # type: ignore[arg-type]

    assert r.index == "ndwi"
    assert r.mean is not None and r.mean < 0  # mostly land
    assert r.water_fraction == 0.0  # no open water on the campus (the reservoir signal == 0 here)
    with rasterio.open(r.path) as ds:
        assert ds.dtypes[0] == "float32"


def test_unknown_collection_index_raises(gis_settings: Settings, tmp_path: Path) -> None:
    site, _ = _campus_top(gis_settings)
    naip = Scene(
        collection="naip",
        scene_id="x",
        acquired=None,
        platform=None,
        cloud_cover=None,
        epsg=None,
        bbox=None,
        assets={},
    )
    with pytest.raises(ValueError, match="no ndvi band mapping"):
        compute_index(naip, site, index="ndvi", out_dir=tmp_path, settings=gis_settings)  # type: ignore[arg-type]
