"""NASA POWER climate reference: load committed YAML + round-trip write."""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings
from bosc.hydrology import climate
from bosc.hydrology.connectors import nasa_power

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_committed_climatology_loads() -> None:
    """The committed reference YAML loads and exposes the precip normal."""
    clim = climate.load_climatology(settings=Settings(data_dir=REPO_ROOT / "data"))
    assert clim is not None, "data/reference/hydrology/nasa-power-climatology.yaml missing"
    assert clim.get("PRECTOTCORR") is not None
    ann = clim.annual_precip_mm()
    assert ann is not None and 800 < ann < 1200


def test_write_then_load_round_trips(tmp_path: Path, hydro_settings: Settings) -> None:
    """Writing a fetched climatology and loading it returns the same values."""
    clim = nasa_power.fetch_climatology(settings=hydro_settings)
    write_settings = Settings(data_dir=tmp_path / "data")
    path = climate.write_climatology(clim, settings=write_settings)
    assert path.is_file()

    back = climate.load_climatology(settings=write_settings)
    assert back is not None
    assert back.annual_precip_mm() == clim.annual_precip_mm()
    assert {p.parameter for p in back.parameters} == {p.parameter for p in clim.parameters}


def test_load_missing_returns_none(tmp_path: Path) -> None:
    assert climate.load_climatology(settings=Settings(data_dir=tmp_path / "data")) is None
