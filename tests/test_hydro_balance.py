"""End-to-end water balance + low-flow assimilative screen, and the provenance invariant."""

from __future__ import annotations

import pytest

from bosc.config import Settings
from bosc.hydrology import lowflow
from bosc.hydrology.assimilative import assimilative_findings, check_assimilative
from bosc.hydrology.balance import build_water_balance
from bosc.pipeline.hydrology import run_baseline


def test_cited_low_flows_load(hydro_settings: Settings) -> None:
    flows = lowflow.load_low_flows(settings=hydro_settings)
    assert flows["dug run"].value == pytest.approx(0.78)
    assert flows["pike run"].value == pytest.approx(0.03)
    # Both are read straight from Ohio EPA fact sheets — document-sourced and cited.
    for pv in flows.values():
        assert pv.source == "document"
        assert pv.citation


def test_low_flow_lookup_normalizes_river_mile(hydro_settings: Settings) -> None:
    pv = lowflow.low_flow_for("Dug Run at River Mile 3.1", settings=hydro_settings)
    assert pv is not None and pv.value == pytest.approx(0.78)


def test_baseline_flags_tributary_violations(hydro_settings: Settings) -> None:
    balance, checks, findings = run_baseline(settings=hydro_settings, live=True)

    # Three county WWTPs with document design flows; the abstraction reach is live.
    assert len(balance.by_role("wwtp")) == 3
    abstraction = balance.node("lima-wtp")
    assert abstraction is not None and abstraction.inflow is not None
    assert abstraction.inflow.source == "connector"  # grounded by the NWIS fixture

    # American II -> Dug Run is the binding, document-cited near-undiluted case.
    dug = next(c for c in checks if c.receiving_water == "Dug Run")
    assert dug.discharge.value == pytest.approx(1.857, abs=0.01)  # 1.2 MGD
    assert dug.dilution_ratio < 1.0 and dug.flag == "violation"

    # All three plants discharge more than their stream's entire 7Q10 (incl. the
    # Ottawa mainstem, whose 7Q10 is now cited from the Lima Refining fact sheet).
    violations = [f for f in findings if not f.ok]
    assert {f.subject.split(" -> ")[1] for f in violations} == {
        "Dug Run",
        "Pike Run",
        "Ottawa River",
    }


def test_provenance_invariant(hydro_settings: Settings) -> None:
    """Every numeric input carries a source; document values carry a citation."""
    balance, _checks, _findings = run_baseline(settings=hydro_settings, live=True)
    values = balance.all_values()
    assert values  # not vacuous
    for pv in values:
        assert pv.source in ("document", "connector", "assumption", "derived")
        if pv.source == "document":
            assert pv.citation, f"document value without citation: {pv}"


def test_check_skips_uncited_receiving_water(hydro_settings: Settings) -> None:
    # A receiving water with no cited 7Q10 is skipped, not invented. (All three real
    # streams are now cited, so inject a plant whose receiving water is uncited.)
    balance = build_water_balance(settings=hydro_settings, live=False)
    flows = dict(lowflow.load_low_flows(settings=hydro_settings))
    flows.pop("ottawa river", None)  # drop the Ottawa citation for this check
    checks = check_assimilative(balance, flows)
    assert "Ottawa River" not in {c.receiving_water for c in checks}
    assert assimilative_findings(checks)  # the tributary checks still produced findings
