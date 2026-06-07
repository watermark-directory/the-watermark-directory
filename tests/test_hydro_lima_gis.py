"""City of Lima zoning connector: ArcGIS parsing, parcel join, offline replay."""

from __future__ import annotations

import pytest

from bosc.config import Settings
from bosc.hydrology.connectors import lima_gis
from bosc.hydrology.connectors._cache import HydroOfflineError


def test_zoning_for_parcel_in_city(hydro_settings: Settings) -> None:
    rec = lima_gis.zoning_for_parcel("36261103018000", settings=hydro_settings)
    assert rec is not None
    assert rec.parcel_no == "36261103018000"
    assert rec.zoning == "CLASS III RESIDENTIAL APARTMENT"


def test_zoning_for_parcel_outside_city_is_none(hydro_settings: Settings) -> None:
    # A cited corridor parcel (American Township) is not within Lima city limits.
    assert lima_gis.zoning_for_parcel("36-0100-03-001.000", settings=hydro_settings) is None


def test_zoning_districts_catalog(hydro_settings: Settings) -> None:
    cat = lima_gis.zoning_districts(settings=hydro_settings)
    assert len(cat) == 10
    # Sorted by descending polygon count; the largest district leads.
    assert cat[0].code == "CLASS I RESIDENTIAL SINGLE FAMILY"
    assert cat[0].polygon_count == 696
    assert sum(d.polygon_count for d in cat) == 2670
    assert {"INDUSTRIAL PARK", "SECOND INDUSTRIAL HEAVY"} <= {d.code for d in cat}


def test_offline_unfetched_parcel_raises(hydro_settings: Settings) -> None:
    with pytest.raises(HydroOfflineError):
        lima_gis.zoning_for_parcel("99-9999-99-999.999", settings=hydro_settings)
