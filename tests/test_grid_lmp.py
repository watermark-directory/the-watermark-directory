"""PJM Data Miner 2 zonal LMP connector (#121): offline fixture replay, the key seam,
and the reference fallback for an unpinned zone. Hermetic — no network, no real key.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bosc.config import Settings
from bosc.connectors import OfflineError
from bosc.grid.lmp import PjmLmpError, fetch_zonal_lmp

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "economics"


def _offline_settings() -> Settings:
    """Offline econ settings with the committed PJM LMP fixtures (and an empty key)."""
    return Settings(
        data_dir=REPO_ROOT / "data",
        econ_offline=True,
        econ_fixtures_dir=FIXTURES,
        pjm_api_key="",  # force empty so the ambient .env key never leaks into a test
    )


def test_fetch_zonal_lmp_replays_committed_fixtures() -> None:
    # AEP + ATSI zones replay from the committed fixtures (the reduced day-ahead annual mean).
    aep = fetch_zonal_lmp(pnode_id=8445784, zone="AEP", settings=_offline_settings())
    assert aep.zone == "AEP" and aep.pnode_id == 8445784
    assert aep.n_hours == 8760  # a full year of day-ahead hours
    assert aep.mean_da_lmp_usd_mwh == pytest.approx(
        45.81, abs=0.05
    )  # real ~$46, not the $35 placeholder

    atsi = fetch_zonal_lmp(pnode_id=116013753, zone="ATSI", settings=_offline_settings())
    assert atsi.zone == "ATSI" and atsi.pnode_id == 116013753
    assert atsi.mean_da_lmp_usd_mwh == pytest.approx(45.84, abs=0.05)


def test_offline_miss_raises_naming_the_key() -> None:
    # A zone/period with no committed fixture raises (never a silent fetch / fabricated price).
    with pytest.raises(OfflineError):
        fetch_zonal_lmp(
            pnode_id=999999,
            zone="NOPE",
            settings=Settings(
                data_dir=REPO_ROOT / "data", econ_offline=True, econ_fixtures_dir=FIXTURES
            ),
        )


def test_live_pull_requires_a_subscription_key(tmp_path: Path) -> None:
    # Online with no key + no cache: refuse with a clear error before any network call.
    with pytest.raises(PjmLmpError, match="BOSC_PJM_API_KEY"):
        fetch_zonal_lmp(
            pnode_id=8445784,
            zone="AEP",
            settings=Settings(
                data_dir=tmp_path, econ_offline=False, econ_fixtures_dir=None, pjm_api_key=""
            ),
        )


def test_unpinned_zone_falls_back_to_reference() -> None:
    # A site whose PJM zone is not yet pinned (Defiance) uses the transcribed reference
    # placeholder, not a connector pull — the market layer never fabricates a zone.
    from bosc.grid.market import _zonal_lmp
    from bosc.sites import SITES

    defiance = SITES["defiance"]
    assert defiance.lmp_pnode_id == 0  # zone not pinned
    zone, lmp = _zonal_lmp(defiance, _offline_settings())
    assert lmp.source == "reference"
    assert lmp.value == defiance.lmp_usd_mwh
    assert "unpinned" in zone.value or zone.source == "reference"


def test_fort_wayne_and_bryan_pinned_to_aep() -> None:
    # I&M (Fort Wayne #361) has no separate PJM zone, and the City-of-Bryan load (#411, CTYBRYAN)
    # settles in AEP — both verified against the live PJM pnode table (2026-06-21). So both pin to
    # the AEP zone, reusing the committed AEP fixture (no new token-dependent pull).
    from bosc.sites import SITES

    for slug in ("fort-wayne", "bryan"):
        prof = SITES[slug]
        assert prof.lmp_pnode_id == 8445784, slug  # AEP zone pnode (same as Lima)
        assert prof.lmp_pnode_name == "AEP", slug
        assert prof.lmp_usd_mwh == pytest.approx(45.81, abs=0.05), slug
