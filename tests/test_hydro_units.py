"""Unit conversions — the cheapest insurance against Tier-0 mass-balance bugs."""

from __future__ import annotations

import pytest

from bosc.hydrology import units


def test_mgd_to_cfs_matches_usgs_factor() -> None:
    # 1.2 MGD (American II design flow) -> 1.857 cfs, per the Ohio EPA fact sheet.
    assert units.mgd_to_cfs(1.0) == pytest.approx(1.547, abs=1e-3)
    assert units.mgd_to_cfs(1.2) == pytest.approx(1.8564, abs=1e-3)


def test_cfs_mgd_round_trip() -> None:
    assert units.cfs_to_mgd(units.mgd_to_cfs(2.5)) == pytest.approx(2.5, rel=1e-9)


def test_acres_sqmi() -> None:
    assert units.acres_to_sqmi(640.0) == pytest.approx(1.0)
    assert units.sqmi_to_acres(1.0) == pytest.approx(640.0)
