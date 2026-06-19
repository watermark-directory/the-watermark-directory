"""Tests for the site-axis registry (#325).

The Lima profile is the live reference build: its values must reproduce the pre-#325
hardcoded defaults exactly. The golden snapshot below is the zero-drift contract — if a
literal was mistranscribed when it moved into ``bosc.sites``, this test fails before any
hydrology output can quietly change.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from bosc.config import Settings
from bosc.sites import (
    PER_SITE_OUTPUT_FIELDS,
    SITES,
    active_profile,
    get_profile,
    output_path_collisions,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# The exact pre-#325 Lima values, transcribed from the original module constants.
_LIMA_GOLDEN = {
    "slug": "lima",
    "basin": "maumee",
    "nwis_sites": ["04187100", "04186500"],
    "nasa_power_lat": 40.74,
    "nasa_power_lon": -84.11,
    "rsei_fips": "39003",
    "econ_fips": "39003",
    "eia861_utility_number": 14006,
    "eia_state": "OH",
    "gnis_default_state": "OH",
    "hydro_utm_epsg": 32617,
    "lsc_default_ga": "136",
    "design_lat": 40.797,
    "design_lon": -84.123,
    "dominant_hsg": "C",
    "pre_cover": "cropland",
    "post_cover": "developed_campus",
    "developed_pervious_cover": "open_space",
    "noaa_fallback_24h_depth_in": {
        1: 2.11,
        2: 2.52,
        5: 3.10,
        10: 3.58,
        25: 4.25,
        50: 4.81,
        100: 5.39,
        200: 6.01,
        500: 6.88,
        1000: 7.59,
    },
    "parcels_relpath": "reference/periplus/bosc-parcels.geojson",
    "footprint_relpath": "extracted/plans/bosc-site-footprint.yaml",
    "climatology_relpath": "reference/hydrology/nasa-power-climatology.yaml",
    "corridor_ddf_relpath": "reference/hydrology/atlas14-corridor-ddf.yaml",
    "baseline_relpath": "reference/economics/baseline.yaml",
    "rsei_relpath": "reference/rsei/inventory.yaml",
    "consumer_energy_relpath": "reference/eia/consumer-energy.yaml",
    "grid_relpath": "reference/eia/grid-profile.yaml",
    "toxic_corridor_bbox": (40.695, 40.725, -84.140, -84.105),
    "receiving_water_name": "Ottawa River",
    "abstraction_gage": "04187100",
    "auglaize_gage": "04186500",
    "ottawa_gage": "04187100",
    "passby_auglaize_cfs": 2.5,
    "passby_ottawa_cfs": 0.2,
    "lmp_usd_mwh": 35.0,
    "county_name": "Allen County, OH",
    "map_view_lat": 40.792,
    "map_view_lon": -84.122,
    "map_view_zoom": 14,
}


def test_lima_golden_snapshot() -> None:
    lima = get_profile("lima")
    for field, expected in _LIMA_GOLDEN.items():
        assert getattr(lima, field) == expected, field
    # The Lima GIS URLs carry their host as evidence; spot-check they're populated + correct.
    assert lima.allen_parcels_url.startswith("https://gis.allencountyohio.com/")
    assert "Lima_Zoning/MapServer/6" in lima.lima_zoning_url
    assert "Lima_Zoning/MapServer/4" in lima.lima_floodzone_url
    assert lima.hsg_citation.startswith("Allen County, OH dominant hydrologic soil group C")
    assert lima.plant_receiving["watch-shawnee-ii-wwtp"][0] == "Ottawa River"


def test_settings_resolves_active_profile() -> None:
    settings = Settings()
    assert active_profile(settings) is SITES["lima"]
    assert settings.nwis_sites == _LIMA_GOLDEN["nwis_sites"]
    assert settings.eia_state == "OH"


def test_second_profile_overrides_all_knobs(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # A synthetic site swaps in cleanly without touching Lima.
    fw = SITES["lima"].model_copy(
        update={
            "slug": "fw",
            "place": "Fort Wayne, IN",
            "nwis_sites": ["04183000"],
            "eia_state": "IN",
        }
    )
    monkeypatch.setitem(SITES, "fw", fw)
    settings = Settings(site="fw")
    assert settings.nwis_sites == ["04183000"]
    assert settings.eia_state == "IN"
    # And Lima is unchanged in the same process.
    assert Settings(site="lima").nwis_sites == ["04187100", "04186500"]


def test_explicit_kwarg_beats_profile() -> None:
    assert Settings(nwis_sites=["Y"]).nwis_sites == ["Y"]


def test_unknown_site_errors() -> None:
    with pytest.raises(ValidationError) as exc:
        Settings(site="atlantis")
    assert "atlantis" in str(exc.value)
    assert "lima" in str(exc.value)  # the message lists the known sites


def test_profile_is_frozen() -> None:
    with pytest.raises(ValidationError):
        SITES["lima"].slug = "nope"  # type: ignore[misc]


def test_sites_keyed_by_slug() -> None:
    # The registry key must equal the profile's slug (onboard scaffolds dirs by prof.slug).
    for key, prof in SITES.items():
        assert key == prof.slug


def test_per_site_output_relpaths_unique() -> None:
    # No two sites may share a per-site output relpath, or onboarding one clobbers the other
    # (#326 hardening). Fires the moment a colliding profile is added.
    for slug in SITES:
        assert output_path_collisions(slug) == {}, slug
    for field in PER_SITE_OUTPUT_FIELDS:
        values = [getattr(p, field) for p in SITES.values()]
        assert len(values) == len(set(values)), f"duplicate {field} across SITES"


def test_python_sites_registered_in_frontend() -> None:
    # Every Python-registered site must also exist in the frontend registry (its switcher +
    # coming-soon page); catches drift between the two tiers.
    ts = (REPO_ROOT / "frontend" / "src" / "lib" / "sites.ts").read_text(encoding="utf-8")
    frontend_slugs = set(re.findall(r'slug:\s*"([^"]+)"', ts))
    assert frontend_slugs, "could not parse slugs from frontend sites.ts"
    assert set(SITES) <= frontend_slugs, set(SITES) - frontend_slugs


def test_per_site_output_paths_resolve(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # The per-site onboard outputs (#326) resolve to Lima's legacy paths for lima and to
    # slug-scoped paths for a new site, so onboarding never clobbers Lima.
    from bosc.hydrology.climate import _reference_path as climatology_path
    from bosc.hydrology.drainage import _ddf_path

    lima = Settings(site="lima", data_dir=tmp_path)
    assert climatology_path(lima) == tmp_path / "reference/hydrology/nasa-power-climatology.yaml"
    assert _ddf_path(lima) == tmp_path / "reference/hydrology/atlas14-corridor-ddf.yaml"

    fw = SITES["lima"].model_copy(
        update={
            "slug": "fw",
            "climatology_relpath": "reference/hydrology/fw/nasa-power-climatology.yaml",
            "corridor_ddf_relpath": "reference/hydrology/fw/atlas14-corridor-ddf.yaml",
        }
    )
    monkeypatch.setitem(SITES, "fw", fw)
    fws = Settings(site="fw", data_dir=tmp_path)
    assert climatology_path(fws) == tmp_path / "reference/hydrology/fw/nasa-power-climatology.yaml"
    assert _ddf_path(fws) == tmp_path / "reference/hydrology/fw/atlas14-corridor-ddf.yaml"
