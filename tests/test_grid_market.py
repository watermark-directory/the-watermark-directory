"""PJM wholesale-market layer (#96): the LMP / RPM-capacity / interconnection-queue
figures are transcribed reference values (medium confidence, flagged verify), the
campus scenario links the first-class facility_draw (#87), and the committed YAML
round-trips. Hermetic - reads committed reference data only, no network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bosc.config import Settings
from bosc.facility.power import derive_power_basis
from bosc.grid.market import (
    derive_pjm_market_scenario,
    load_pjm_market,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def market_settings() -> Settings:
    """Real repo data dir (reads committed reference data); no network."""
    return Settings(data_dir=REPO_ROOT / "data", hydro_offline=True, econ_offline=True)


def test_lmp_and_capacity_are_reference_sourced(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    # The LMP and RPM clearing price are transcribed reference figures, at medium
    # confidence, each flagged for verification - not asserted as fact.
    assert sc.zonal_lmp_usd_mwh.source == "reference"
    assert sc.rpm_clearing_usd_mw_day.source == "reference"
    assert sc.zonal_lmp_usd_mwh.confidence == "medium"
    assert sc.rpm_clearing_usd_mw_day.confidence == "medium"
    assert sc.zonal_lmp_usd_mwh.citation is not None
    assert sc.rpm_clearing_usd_mw_day.citation is not None
    assert "verify" in sc.zonal_lmp_usd_mwh.citation.lower()
    assert "verify" in sc.rpm_clearing_usd_mw_day.citation.lower()
    # The large-load queue is reference, order-of-magnitude, flagged verify.
    assert sc.large_load_queue_gw.source == "reference"
    assert sc.large_load_queue_gw.citation is not None
    assert "verify" in sc.large_load_queue_gw.citation.lower()


def test_scenario_links_facility_draw(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    power = derive_power_basis(settings=market_settings)
    # The campus load IS the first-class PowerBasis.facility_draw (#87).
    assert sc.campus_load_mw.value == pytest.approx(power.facility_draw.value, abs=0.1)
    # Annual consumption follows the shared convention (draw x 8760 x 0.9).
    expected_gwh = power.facility_draw.value * 8760.0 * sc.load_factor.value / 1000.0
    assert sc.annual_consumption_gwh.value == pytest.approx(expected_gwh, rel=0.01)


def test_annual_capacity_cost_is_draw_times_price_times_365(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    draw = sc.campus_load_mw.value
    price = sc.rpm_clearing_usd_mw_day.value
    # annual_capacity_cost ($M/yr) == draw (MW) x price ($/MW-day) x 365 / 1e6.
    expected_musd = draw * price * 365.0 / 1_000_000.0
    assert sc.annual_capacity_cost_musd.value == pytest.approx(expected_musd, rel=0.01)
    assert sc.annual_capacity_cost_musd.source == "derived"
    # The striking capacity footprint is on the order of tens of $M/yr.
    assert 20.0 < sc.annual_capacity_cost_musd.value < 60.0


def test_annual_energy_cost_is_consumption_times_lmp(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    consumption_mwh = sc.annual_consumption_gwh.value * 1000.0
    expected_musd = consumption_mwh * sc.zonal_lmp_usd_mwh.value / 1_000_000.0
    assert sc.annual_energy_cost_musd.value == pytest.approx(expected_musd, rel=0.01)
    assert sc.annual_energy_cost_musd.source == "derived"


def test_campus_is_small_slice_of_queue(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    draw = sc.campus_load_mw.value
    queue_gw = sc.large_load_queue_gw.value
    expected_pct = draw / (queue_gw * 1000.0) * 100.0
    assert sc.campus_share_of_queue_pct.value == pytest.approx(expected_pct, rel=0.01)
    # One campus is a small single-digit-percent slice of a tens-of-GW pipeline.
    assert 0.0 < sc.campus_share_of_queue_pct.value < 5.0


def test_caveats_present(market_settings: Settings) -> None:
    sc = derive_pjm_market_scenario(settings=market_settings)
    assert sc.caveats, "the scenario must carry screening caveats"
    joined = " ".join(sc.caveats).lower()
    assert "screening" in joined
    assert "lmp" in joined
    assert "clearing price" in joined
    assert "order-of-magnitude" in joined
    assert sc.interpretation


def test_committed_pjm_market_loads() -> None:
    """The committed reference YAML round-trips into the model."""
    ref = load_pjm_market(REPO_ROOT / "data" / "reference")
    assert ref is not None
    assert "PJM" in ref.rto.value
    # The transcribed figures are reference-sourced, medium confidence, flagged verify.
    assert ref.zonal_lmp_usd_mwh.source == "reference"
    assert ref.rpm_clearing_usd_mw_day.source == "reference"
    assert ref.rpm_clearing_usd_mw_day.confidence == "medium"
    assert ref.zonal_lmp_usd_mwh.value > 0.0
    assert ref.rpm_clearing_usd_mw_day.value > ref.rpm_prior_year_usd_mw_day.value


def test_market_scenario_refuses_a_facility_less_site() -> None:
    """A site with no documented facility cannot have a campus PJM market scenario —
    the connector refuses (no fabrication) rather than reusing Lima's facility."""
    with pytest.raises(ValueError, match="no documented facility"):
        derive_pjm_market_scenario(settings=Settings(site="findlay"))
