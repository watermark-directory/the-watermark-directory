"""ECHO DMR / effluent-chart connector — fixture-backed (hermetic, no network).

Replays a committed Fort Wayne WWTP (NPDES IN0032191) effluent chart for calendar
2023: the primary outfall's reported monthly flow vs. the 74 MGD design, the CSO
outfall count, and the (empty) exceedance list. None of these may fabricate a value
ECHO didn't send — a no-discharge period stays null, an exceedance appears only where
ECHO reports one.
"""

from __future__ import annotations

import pytest

from bosc.config import Settings
from bosc.hydrology.connectors import echo_dmr
from bosc.hydrology.connectors._cache import HydroOfflineError


def test_iso_period_parses_echo_date() -> None:
    assert echo_dmr._iso_period("31-JAN-23") == "2023-01-31"
    assert echo_dmr._iso_period("28-FEB-23") == "2023-02-28"
    assert echo_dmr._iso_period(None) is None
    assert echo_dmr._iso_period("garbage") is None


def test_fetch_fort_wayne_chart_from_fixture(hydro_settings: Settings) -> None:
    chart = echo_dmr.fetch_effluent_chart(
        "IN0032191", start_date="2023-01-01", end_date="2023-12-31", settings=hydro_settings
    )
    assert chart.npdes_id == "IN0032191"
    assert chart.name == "FORT WAYNE WWTP"
    assert chart.permit_type == "NPDES Individual Permit"
    assert chart.permit_status == "Admin Continued"
    assert chart.major_minor == "M"  # a major discharger
    assert chart.snc_status == "Effluent - Monthly Average Limit"
    # The primary outfall carries 12 monthly flow values; a CSO outfall does not.
    flow_series = chart.series(echo_dmr.FLOW_PARAM)
    assert len(flow_series) >= 1
    primary = next(p for p in flow_series if p.outfall == "001")
    assert sum(1 for r in primary.rows if r.value is not None) == 12
    # Reported values are verbatim — January 2023 monthly-average flow.
    jan = next(r for r in primary.rows if r.period_end == "2023-01-31")
    assert jan.value == pytest.approx(56.016)
    assert jan.unit == "MGD"
    assert jan.stat_base == "MO AVG"


def test_summarize_actual_vs_design(hydro_settings: Settings) -> None:
    chart = echo_dmr.fetch_effluent_chart(
        "IN0032191", start_date="2023-01-01", end_date="2023-12-31", settings=hydro_settings
    )
    summary = echo_dmr.summarize_discharge(chart, design_flow_mgd=74.0)
    assert summary.primary_outfall == "001"
    assert summary.n_flow_months == 12
    # The 12-month mean of the reported monthly averages — well under the design flow.
    assert summary.actual_flow_mean_mgd == pytest.approx(43.869, abs=0.01)
    assert summary.flow_pct_of_design == pytest.approx(59.3, abs=0.1)
    assert summary.actual_flow_min_mgd == pytest.approx(30.304)
    assert summary.actual_flow_max_mgd == pytest.approx(79.287)
    # 39 CSO/bypass outfalls beyond the continuous effluent point.
    assert summary.cso_outfalls == 39
    # No ECHO-flagged effluent exceedance in the window — an empty list, never "unknown".
    assert summary.exceedances == []


def test_no_design_flow_means_no_percentage(hydro_settings: Settings) -> None:
    chart = echo_dmr.fetch_effluent_chart(
        "IN0032191", start_date="2023-01-01", end_date="2023-12-31", settings=hydro_settings
    )
    summary = echo_dmr.summarize_discharge(chart)  # design_flow_mgd=None
    assert summary.actual_flow_mean_mgd == pytest.approx(43.869, abs=0.01)
    assert summary.flow_pct_of_design is None


def test_dmr_document_is_regenerable_and_faithful(hydro_settings: Settings) -> None:
    chart = echo_dmr.fetch_effluent_chart(
        "IN0032191", start_date="2023-01-01", end_date="2023-12-31", settings=hydro_settings
    )
    summary = echo_dmr.summarize_discharge(chart, design_flow_mgd=74.0)
    doc = echo_dmr.dmr_document(chart, summary)
    assert doc["permit"]["npdes_id"] == "IN0032191"
    assert doc["discharge_summary"]["actual_flow_mean_mgd"] == pytest.approx(43.869, abs=0.01)
    assert doc["discharge_summary"]["actual_flow_mean_cfs"] == pytest.approx(67.87, abs=0.1)
    assert doc["discharge_summary"]["design_flow_cfs"] == pytest.approx(114.48, abs=0.1)
    assert len(doc["flow_monthly"]) == 12
    assert doc["exceedances"] == []
    assert "bosc dmr IN0032191" in doc["meta"]["regenerate"]


def test_offline_cache_miss_raises(hydro_settings: Settings) -> None:
    # A permit with no committed fixture -> offline miss must be loud, not silent.
    with pytest.raises(HydroOfflineError):
        echo_dmr.fetch_effluent_chart(
            "XX9999999", start_date="2023-01-01", end_date="2023-12-31", settings=hydro_settings
        )
