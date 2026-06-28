"""FAO-56 Penman-Monteith reference ET0 from the committed NASA POWER climatology."""

from __future__ import annotations

import pytest

from watermark.config import Settings
from watermark.hydrology import climate, et
from watermark.hydrology.connectors.nasa_power import ClimatologyParameter, NasaPowerClimatology


def test_et0_from_committed_climatology() -> None:
    clim = climate.load_climatology(settings=Settings())
    assert clim is not None
    e = et.penman_monteith_et0(clim)

    assert e.method.startswith("FAO-56")
    assert len(e.monthly_mm_day) == 12
    # Lima (temperate continental): reference ET0 lands ~900-1200 mm/yr.
    assert 900 < e.annual_mm < 1200
    # Strong seasonality — summer demand far exceeds winter.
    assert e.monthly_mm_day["JUL"] > e.monthly_mm_day["JAN"]
    assert all(v >= 0 for v in e.monthly_mm_day.values())
    # Summer is a precipitation deficit (ET0 > rainfall) — the growing-season pinch.
    precip = clim.get("PRECTOTCORR")
    assert precip is not None
    assert e.monthly_mm_day["JUL"] > precip.monthly["JUL"]


def test_et0_uses_provided_lat_elevation() -> None:
    """Latitude/elevation overrides flow through (radiation depends on latitude)."""
    clim = climate.load_climatology(settings=Settings())
    assert clim is not None
    base = et.penman_monteith_et0(clim)
    # A much lower latitude raises extraterrestrial radiation -> higher ET0.
    tropical = et.penman_monteith_et0(clim, latitude=5.0)
    assert tropical.annual_mm > base.annual_mm


def test_et0_missing_parameter_raises() -> None:
    """A climatology without the radiation term can't yield ET0."""
    thin = NasaPowerClimatology(
        latitude=40.74,
        longitude=-84.11,
        elevation_m=276.0,
        source_title="thin",
        parameters=[
            ClimatologyParameter(
                parameter="T2M",
                units="C",
                longname="t",
                monthly=dict.fromkeys(et._MONTHS, 10.0),
                annual=10.0,
            )
        ],
    )
    with pytest.raises(ValueError, match=r"ALLSKY_SFC_SW_DWN|T2M_MAX|RH2M|WS2M"):
        et.penman_monteith_et0(thin)
