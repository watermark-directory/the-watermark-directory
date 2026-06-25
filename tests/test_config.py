"""Tests for settings loading and derived paths."""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings, repo_fixtures_dir


def test_defaults() -> None:
    settings = Settings()
    assert settings.model == "claude-opus-4-8"
    assert settings.max_turns == 20


def test_env_prefix_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("BOSC_MODEL", "claude-sonnet-4-6")
    monkeypatch.setenv("BOSC_MAX_TURNS", "5")
    settings = Settings()
    assert settings.model == "claude-sonnet-4-6"
    assert settings.max_turns == 5


def test_derived_paths(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    assert settings.documents_dir == tmp_path / "documents"
    assert settings.extracted_dir == tmp_path / "extracted"
    settings.ensure_dirs()
    assert settings.documents_dir.is_dir()
    assert settings.extracted_dir.is_dir()


def test_repo_fixtures_dir_anchored_to_repo_not_data_dir(tmp_path: Path) -> None:
    """#616: offline `--offline` fixture paths must resolve relative to the repo, not
    `data_dir.parent` — which breaks under a relocated BOSC_DATA_DIR (e.g. a tmp dir)."""
    relocated = Settings(data_dir=tmp_path)
    fixtures = repo_fixtures_dir("hydrology")
    # Anchored at the real repo tree (these are committed), independent of data_dir.
    assert fixtures.is_dir()
    assert tmp_path not in fixtures.parents
    # And the committed gis/poi fixtures resolve the same way.
    assert repo_fixtures_dir("gis").is_dir()
    assert repo_fixtures_dir("poi").is_dir()
    # The relocated settings didn't change where fixtures live.
    assert relocated.data_dir == tmp_path


def test_site_default_resolves_lima() -> None:
    # The per-site knobs resolve from the active (default Lima) site profile (#325).
    settings = Settings()
    assert settings.site == "lima"
    assert settings.nwis_sites == ["04187100", "04186500"]
    assert settings.nasa_power_lat == 40.74
    assert settings.rsei_fips == "39003"
    assert settings.econ_fips == "39003"
    assert settings.eia861_utility_number == 14006
    assert settings.hydro_utm_epsg == 32617


def test_env_overrides_site_profile(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # An explicit env var still wins over the profile, but unrelated knobs stay profile-sourced.
    monkeypatch.setenv("BOSC_NWIS_SITES", '["99999999"]')
    settings = Settings()
    assert settings.nwis_sites == ["99999999"]
    assert settings.rsei_fips == "39003"  # untouched -> from the Lima profile
