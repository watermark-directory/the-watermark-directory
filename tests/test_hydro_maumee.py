"""Maumee TMDL phosphorus WLAs: loader, provenance, and report weave (hermetic)."""

from __future__ import annotations

from bosc.config import Settings
from bosc.hydrology.maumee import load_maumee_tmdl
from bosc.hydrology.report import render_report


def test_tmdl_wlas_load_cited(hydro_settings: Settings) -> None:
    tmdl = load_maumee_tmdl(settings=hydro_settings)
    assert tmdl is not None
    by_npdes = {f.npdes: f for f in tmdl.facilities}
    # The same permits the low-flow assimilative screen flags.
    assert {"2PH00006", "2PH00007", "2IG00001"} <= set(by_npdes)
    am2 = by_npdes["2PH00006"]  # American No 2 WWTP
    assert am2.spring_tp.value == 0.30
    assert am2.daily_tp.value == 2.0
    assert am2.spring_tp.unit == "metric tons"
    assert am2.daily_tp.unit == "kg/day"
    # Verbatim, document-tagged with a citation to Appendix 4.
    assert am2.spring_tp.source == "document" and am2.spring_tp.citation
    assert "Appendix 4" in am2.spring_tp.citation


def test_grouped_load_total(hydro_settings: Settings) -> None:
    tmdl = load_maumee_tmdl(settings=hydro_settings)
    assert tmdl is not None
    assert tmdl.grouped_spring_tp is not None and tmdl.grouped_spring_tp.value == 64.1
    assert tmdl.grouped_daily_tp is not None and tmdl.grouped_daily_tp.value == 418.8
    assert tmdl.facility("Lima WWTP") is not None


def test_report_weaves_tmdl_section(hydro_settings: Settings) -> None:
    md = render_report(settings=hydro_settings)
    assert "## 2. The Maumee Nutrient TMDL" in md
    # Renumbering held: later sections shifted down by one.
    assert "## 3. Stormwater" in md
    assert "## 4. Scenario" in md
    assert "## 5. Tier-1 escalation" in md
    # A concrete WLA figure and the grouped-load total render.
    assert "2PH00006" in md
    assert "64.1 metric tons" in md


def test_short_reach_label() -> None:
    """#611: the inline natural-flow breakdown uses short reach labels derived from the model."""
    from bosc.hydrology.report import _short_reach

    assert _short_reach("Ottawa River upstream of Lima") == "Ottawa"
    assert _short_reach("Dug Run (headwater)") == "Dug Run"
    assert _short_reach("Pike Run (headwater)") == "Pike Run"
    assert _short_reach("Blanchard River") == "Blanchard"
