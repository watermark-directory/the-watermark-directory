"""City of Lima zoning connector: ArcGIS parsing, parcel join, offline replay."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

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


def test_write_cited_zoning_records_the_null(tmp_path: Path) -> None:
    """The scan writer summarizes an out-of-city corridor as a verified null."""
    scan = [
        lima_gis.CitedParcelZoning(
            parcel_no="36-0100-03-002.000", normalized="36010003002000", in_city=False
        ),
        lima_gis.CitedParcelZoning(
            parcel_no="12345", normalized="12345", in_city=True, zoning="INDUSTRIAL PARK"
        ),
    ]
    path = lima_gis.write_cited_zoning(scan, tmp_path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["meta"]["n_cited"] == 2
    assert doc["meta"]["n_in_city"] == 1
    assert len(doc["parcels"]) == 2


def test_committed_cited_zoning_is_an_out_of_city_null() -> None:
    """The committed scan records that no cited corridor parcel is city-zoned."""
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "reference"
        / "lima-gis"
        / "parcels.zoning.yaml"
    )
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["meta"]["n_in_city"] == 0
    assert doc["meta"]["n_cited"] >= 40
    assert all(p["in_city"] is False and p["zoning"] is None for p in doc["parcels"])
    assert "NOT subject to the City of Lima zoning code" in doc["meta"]["finding"]
