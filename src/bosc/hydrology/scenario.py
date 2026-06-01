"""Baseline vs data-center-buildout scenarios over the municipal water loop.

The dominant uncertainty in the loop is the campus's *consumptive* cooling demand —
evaporated water that never returns to the Ottawa/Auglaize basin. This module makes
that the knob: a :class:`Scenario` carries a cooling intake and a consumptive
fraction (both assumptions), and :func:`evaluate` computes the net basin loss and
sets it on the campus node's ``consumptive_use`` seam. :func:`diff` reports the new
draw against the **cited Ottawa 7Q10** (0.2 cfs) — the scale that makes the point:
at design low flow the river already nearly dries, so any material cooling draw is a
large multiple of what the Ottawa carries.

Results persist to ``data/scenarios/*.scenario.yaml`` — committed, reviewed, and
self-auditing (every number keeps its provenance tag).
"""

from __future__ import annotations

import yaml

from bosc.config import Settings, get_settings
from bosc.hydrology.assimilative import check_assimilative
from bosc.hydrology.balance import _OTTAWA_AT_LIMA, build_water_balance
from bosc.hydrology.connectors.nwis import DISCHARGE_CFS, fetch_streamflow
from bosc.hydrology.lowflow import low_flow_for
from bosc.hydrology.model import (
    ProvenancedValue,
    Scenario,
    ScenarioDiff,
    ScenarioResult,
)
from bosc.hydrology.units import mgd_to_cfs
from bosc.logging import get_logger

log = get_logger(__name__)


def baseline_scenario() -> Scenario:
    """The current system: no incremental cooling draw."""
    return Scenario(
        name="baseline",
        description="Current municipal loop, no data-center cooling draw.",
        cooling_demand=ProvenancedValue.assume(0.0, "MGD", why="baseline: no campus cooling load"),
        consumptive_fraction=ProvenancedValue.assume(0.0, "fraction", why="baseline"),
    )


def buildout_scenario(
    *,
    cooling_demand_mgd: float = 5.0,
    consumptive_fraction: float = 0.8,
) -> Scenario:
    """Data-center buildout with an evaporative-cooling consumptive draw (assumptions)."""
    return Scenario(
        name="buildout",
        description="Data-center campus with evaporative cooling drawing on Lima's supply.",
        cooling_demand=ProvenancedValue.assume(
            cooling_demand_mgd,
            "MGD",
            why="campus cooling intake — design basis TBD; scenario knob",
        ),
        consumptive_fraction=ProvenancedValue.assume(
            consumptive_fraction,
            "fraction",
            why="evaporative cooling consumptive fraction — typical high for wet cooling; scenario knob",
        ),
    )


def evaluate(
    scenario: Scenario,
    *,
    settings: Settings | None = None,
    live: bool = True,
) -> ScenarioResult:
    """Evaluate a scenario: net consumptive loss, modified balance, low-flow context."""
    settings = settings or get_settings()
    loss_cfs = mgd_to_cfs(scenario.cooling_demand.value * scenario.consumptive_fraction.value)
    consumptive = ProvenancedValue.derived(
        loss_cfs,
        "cfs",
        citation=(
            f"{scenario.cooling_demand.value:g} MGD x {scenario.consumptive_fraction.value:g} "
            f"consumptive (scenario {scenario.name})"
        ),
    )

    balance = build_water_balance(settings=settings, live=live)
    campus = balance.node("bosc-campus")
    if campus is not None:
        campus.consumptive_use = consumptive

    ottawa_7q10 = low_flow_for("Ottawa River", settings=settings)
    ottawa_live = _ottawa_live(settings=settings, live=live)

    return ScenarioResult(
        scenario=scenario,
        consumptive_loss=consumptive,
        ottawa_7q10=ottawa_7q10,
        ottawa_live=ottawa_live,
        balance=balance,
        assimilative=check_assimilative(balance),
    )


def _ottawa_live(*, settings: Settings, live: bool) -> ProvenancedValue | None:
    if not live:
        return None
    try:
        readings = fetch_streamflow(sites=[_OTTAWA_AT_LIMA], settings=settings)
    except Exception as exc:
        log.info("hydro.scenario.no_live", error=type(exc).__name__)
        return None
    flow = next(
        (r for r in readings if r.parameter_cd == DISCHARGE_CFS and r.value is not None), None
    )
    if flow is None or flow.value is None:
        return None
    return ProvenancedValue.from_connector(
        flow.value, "cfs", citation=f"NWIS {flow.site_no} ({flow.name})", asof=flow.datetime
    )


def diff(baseline: ScenarioResult, scenario: ScenarioResult) -> ScenarioDiff:
    """Net new consumptive draw and its scale against the Ottawa 7Q10."""
    increase = scenario.consumptive_loss.value - baseline.consumptive_loss.value
    q7 = scenario.ottawa_7q10.value if scenario.ottawa_7q10 else None
    multiple = (increase / q7) if (q7 and q7 > 0) else None
    return ScenarioDiff(
        baseline=baseline.scenario.name,
        scenario=scenario.scenario.name,
        consumptive_increase_cfs=round(increase, 3),
        ottawa_7q10_cfs=q7,
        multiple_of_7q10=round(multiple, 1) if multiple is not None else None,
    )


def write_scenario(result: ScenarioResult, *, settings: Settings | None = None) -> str:
    """Persist a scenario result as a committed, self-auditing YAML artifact."""
    settings = settings or get_settings()
    out_dir = settings.scenarios_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{result.scenario.name}.scenario.yaml"
    path.write_text(
        yaml.safe_dump(result.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    log.info("hydro.scenario.wrote", path=str(path))
    return str(path)
