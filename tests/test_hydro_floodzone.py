"""FEMA floodzone connector + campus floodplain finding + dossier weave (hermetic)."""

from __future__ import annotations

from bosc.config import Settings
from bosc.hydrology.connectors import lima_gis
from bosc.hydrology.floodplain import load_campus_floodzone
from bosc.hydrology.report import render_report


def _footprint(settings: Settings):  # type: ignore[no-untyped-def]
    return settings.data_dir / "reference" / "periplus" / "bosc-parcels.geojson"


def test_floodzone_catalog(hydro_settings: Settings) -> None:
    cat = lima_gis.floodzone_catalog(settings=hydro_settings)
    assert sum(c.polygon_count for c in cat) == 368
    assert all(c.sfha for c in cat)  # only Special Flood Hazard Areas are mapped
    assert cat[0].fld_zone == "AE" and cat[0].polygon_count == 304  # largest class leads
    floodway = next(c for c in cat if c.zone_subtype == "FLOODWAY")
    assert floodway.fld_zone == "AE" and floodway.polygon_count == 31


def test_footprint_is_floodplain_adjacent_not_sited(hydro_settings: Settings) -> None:
    fp = _footprint(hydro_settings)
    # The recorded parcels intersect no SFHA polygon...
    assert lima_gis.footprint_floodzones(fp, distance_m=0, settings=hydro_settings) == []
    # ...but AE floodplain + floodway come within 50 m.
    nearby = lima_gis.footprint_floodzones(fp, distance_m=50, settings=hydro_settings)
    assert len(nearby) == 2
    assert {f.fld_zone for f in nearby} == {"AE"}
    assert any(f.zone_subtype == "FLOODWAY" for f in nearby)
    assert all(f.source_cit == "39003C_FIS5" for f in nearby)
    # The -9999 BFE sentinel is normalized to None, not surfaced as an elevation.
    assert all(f.static_bfe is None for f in nearby)


def test_campus_floodzone_finding_loads(hydro_settings: Settings) -> None:
    cf = load_campus_floodzone(settings=hydro_settings)
    assert cf is not None
    assert cf.in_parcels_zones == []
    assert cf.in_floodplain is False
    assert cf.nearby_zones == ["AE", "AE (FLOODWAY)"]
    assert cf.nearby_buffer_m == 50
    assert "39003C" in cf.firm


def test_report_weaves_floodplain_proximity(hydro_settings: Settings) -> None:
    md = render_report(settings=hydro_settings)
    assert "just outside the FEMA floodplain" in md
    assert "AE (FLOODWAY)" in md
    assert "regulatory" in md and "floodway" in md
