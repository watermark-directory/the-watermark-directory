"""Geo helpers — areas via UTM reprojection, bbox, and WWTP node parsing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bosc.config import Settings
from bosc.hydrology import geo

REPO = Path(__file__).resolve().parents[1]
PARCELS = REPO / "tests" / "fixtures" / "periplus-bosc-parcels.geojson"
WATCH = REPO / "data" / "reference" / "periplus" / "watch-items.geojson"


def test_feature_area_matches_stated_acreage(hydro_settings: Settings) -> None:
    # The Bistrozzi Phase-1A parcel is recorded at 40.07 ac (allen_parcels footprint).
    feats = json.loads(PARCELS.read_text())["features"]
    geom = next(
        f["geometry"] for f in feats if f["properties"]["parcel_id"] == "36-0100-03-002.000"
    )
    acres = geo.feature_area_acres(geom, settings=hydro_settings)
    assert acres == pytest.approx(40.07, rel=0.05)


def test_parcels_total_and_bbox(hydro_settings: Settings) -> None:
    total = geo.parcels_total_acres(PARCELS, settings=hydro_settings)
    assert 300 < total < 380  # ~339 ac of polygon footprints (point parcels excluded)
    minx, miny, maxx, maxy = geo.bbox_of(PARCELS, pad_deg=0.01)
    # Lima, Allen County, OH.
    assert -84.3 < minx < maxx < -84.0
    assert 40.6 < miny < maxy < 40.9


def test_wwtp_nodes_from_watch_items() -> None:
    nodes = geo.wwtp_nodes_from_watch_items(WATCH)
    names = {n.name for n in nodes}
    assert {"Shawnee II WWTP", "American Bath WWTP", "American II WWTP"} <= names
    for n in nodes:
        assert n.role == "wwtp"
        assert n.lat is not None and n.lon is not None
