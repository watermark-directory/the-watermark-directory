"""Multi-level, multi-hypothesis layer over the water-balance scenarios.

The baseline/buildout scenarios answer one question — how big is the campus cooling
draw against the Ottawa's low flow. A :class:`Hypothesis` tags a scenario with the
**level** it speaks to (``macro`` = Maumee basin, ``local`` = Lima loop, ``site`` =
per-campus / per-WWTP) and an optional **routing override**, so several what-ifs can
be evaluated and compared against the shared baseline in one pass.

Honesty guard (see CLAUDE.md): ``level`` is a *framing* dimension over the same
Lima-loop numbers — a macro hypothesis reads the result against basin-scale context
(the Maumee TMDL), it does **not** run a different solver. A routing override changes
which forcemain routes are treated as *built* (re-labelling the BOSC→WWTP topology);
the dilution math depends on cooling demand + WWTP design flows, not on which plant
receives the campus load. This keeps the default ``buildout-confirmed`` hypothesis
numerically identical to :func:`watermark.pipeline.hydrology.run_scenarios`' buildout.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from watermark.config import Settings, get_settings
from watermark.hydrology import scenario as scenario_stage
from watermark.hydrology.model import Scenario, ScenarioDiff, ScenarioResult
from watermark.hydrology.routing import BoscRoute, RouteStatus, RoutingTable, load_routing
from watermark.logging import get_logger

log = get_logger(__name__)

HypothesisLevel = Literal["macro", "local", "site"]


class Hypothesis(BaseModel):
    """One what-if: a cooling scenario tagged by level, with optional routing overrides."""

    model_config = ConfigDict(extra="forbid")

    name: str
    level: HypothesisLevel
    description: str = ""
    scenario: Scenario
    # forcemain via-id -> promoted status (e.g. promote the theorized Shawnee II route).
    routing_overrides: dict[str, RouteStatus] = {}
    basis: str = ""


class HypothesisResult(BaseModel):
    """A hypothesis evaluated against the shared baseline, with its routing recorded."""

    model_config = ConfigDict(extra="forbid")

    hypothesis: Hypothesis
    result: ScenarioResult
    diff_vs_baseline: ScenarioDiff
    routing_applied: list[BoscRoute] = []  # BOSC routes treated as built under this hypothesis
    excluded_theorized: list[BoscRoute] = []  # theorized routes held out (e.g. Shawnee II FM-3)


class HypothesisComparison(BaseModel):
    """The shared baseline plus every evaluated hypothesis."""

    model_config = ConfigDict(extra="forbid")

    baseline: ScenarioResult
    hypotheses: list[HypothesisResult]


def _resolve_bosc_routing(
    routing: RoutingTable | None, overrides: dict[str, RouteStatus]
) -> tuple[list[BoscRoute], list[BoscRoute]]:
    """Split BOSC forcemain routes into (treated-as-built, held-out) under the overrides."""
    applied: list[BoscRoute] = []
    excluded: list[BoscRoute] = []
    for br in routing.bosc_routing if routing is not None else []:
        status = overrides.get(br.via, br.status)
        (applied if status == "confirmed" else excluded).append(br)
    return applied, excluded


def default_hypotheses(
    *, cooling_demand_mgd: float | None = None, consumptive_fraction: float | None = None
) -> list[Hypothesis]:
    """The committed default set: confirmed-routing buildout + the FM-3 what-if (site level).

    ``macro``/``local`` hypotheses are not pre-built (they would re-label the same
    numbers); the model supports them so callers can author basin/loop-specific
    hypotheses with different inputs.
    """
    build = scenario_stage.buildout_scenario(
        cooling_demand_mgd=cooling_demand_mgd, consumptive_fraction=consumptive_fraction
    )
    return [
        Hypothesis(
            name="buildout-confirmed",
            level="site",
            description=(
                "Campus cooling draw vs the Ottawa, BOSC routed to Lima (FM-2) + "
                "American Bath/II (FM-1) only — the confirmed routing."
            ),
            scenario=build,
            basis="confirmed BOSC routing (routing.yaml; DOSSIER §1)",
        ),
        Hypothesis(
            name="buildout-with-fm3",
            level="site",
            description=(
                "WHAT-IF: the theorized FM-3 to Shawnee II is built, adding Shawnee II "
                "to the BOSC-receiving plants. Numerically identical — a topology label."
            ),
            scenario=build,
            routing_overrides={"theorized-fm3-shawnee-ii": "confirmed"},
            basis="hypothetical promotion of the theorized Shawnee II route",
        ),
    ]


def run_hypotheses(
    hypotheses: list[Hypothesis] | None = None,
    *,
    cooling_demand_mgd: float | None = None,
    consumptive_fraction: float | None = None,
    settings: Settings | None = None,
    live: bool = True,
) -> HypothesisComparison:
    """Evaluate a list of hypotheses against the shared baseline; default set if ``None``."""
    settings = settings or get_settings()
    base = scenario_stage.evaluate(scenario_stage.baseline_scenario(), settings=settings, live=live)
    routing = load_routing(settings=settings)
    hyps = (
        hypotheses
        if hypotheses is not None
        else default_hypotheses(
            cooling_demand_mgd=cooling_demand_mgd, consumptive_fraction=consumptive_fraction
        )
    )
    results: list[HypothesisResult] = []
    for h in hyps:
        result = scenario_stage.evaluate(h.scenario, settings=settings, live=live)
        applied, excluded = _resolve_bosc_routing(routing, h.routing_overrides)
        results.append(
            HypothesisResult(
                hypothesis=h,
                result=result,
                diff_vs_baseline=scenario_stage.diff(base, result),
                routing_applied=applied,
                excluded_theorized=excluded,
            )
        )
    log.info("hydro.hypotheses", n=len(results), levels=sorted({h.level for h in hyps}))
    return HypothesisComparison(baseline=base, hypotheses=results)
