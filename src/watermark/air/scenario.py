"""Air emissions scenario runner + synthetic-minor NSR cap-exceedance check (#1177).

Mirrors :mod:`watermark.hydrology.scenario`: a :class:`AirScenario` (inputs) →
:func:`evaluate` → :class:`AirScenarioResult` → :func:`write_scenario` (a committed,
self-auditing YAML). The investigable question is the epic's: when a reliability event
forces the "emergency" backup fleet into runtime, does the air burden breach the
**synthetic-minor NSR caps** the permit was engineered to stay under (NOx 235.62 / CO
96.06 tpy)?

Two scenarios: :func:`baseline_scenario` (permit maintenance/testing hours) and
:func:`reliability_dispatch_scenario` (the #1176 forced-runtime band). :func:`evaluate`
rolls runtime-hours x per-engine factors x fleet into annual tonnage per pollutant and
flags any cap crossing; :func:`diff` reports the net increase over baseline. The
standalone-shippable Tier-0 deliverable — defensible without AERMOD (Tier-1).

Three rules the cap check keeps (epic #2095):

- **The cap is cumulative** (AQ-01, #2096). Readiness testing is not an alternative to
  dispatch hours — both count against the same rolling-12-month limit, so a dispatch
  scenario is checked as ``annual_tpy = testing baseline (idle) + dispatch (load)``. The
  scenario's own ``tpy`` stays the net-new burden that :func:`diff` reports.
- **The modeled fleet is the fleet the cap covers** (AQ-15, #2110). Units the permit rates
  separately (Lima's P115 HUBGEN) are modeled at their own rate, not dropped.
- **No cap is not "within cap"** (AQ-03, #2098). A site with no wired air permit reports
  ``cap_status="unknown"`` and ``any_cap_exceeded=None`` — never an affirmative ``False``.
"""

from __future__ import annotations

from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

from watermark.air.emissions import load_emission_factors, load_nsr_caps
from watermark.air.model import (
    POLLUTANTS,
    AuxiliaryUnits,
    FactorBasis,
    GensetEmissionFactors,
    LoadRegime,
    Pollutant,
)
from watermark.config import Settings, get_settings
from watermark.hydrology.model import ProvenancedValue
from watermark.logging import get_logger
from watermark.sites import active_profile

log = get_logger(__name__)

LB_PER_TON = 2000.0

# Standard emergency-engine maintenance & readiness-testing allowance (40 CFR 60.4211(f)
# / NFPA 110). The baseline runtime — what the fleet runs absent any reliability event.
_BASELINE_TEST_HOURS = 100.0

# Where one pollutant stands against the synthetic-minor cap. ``unknown`` = the site has no
# wired air permit, so whether a cap exists (and what it is) is not established; ``uncapped`` =
# the wired permit caps other pollutants but not this one.
CapStatus = Literal["within", "exceeded", "unknown", "uncapped"]

# ``baseline`` is the testing allowance itself; a ``dispatch`` runs on top of it, in the same
# rolling-12-month window the cap counts.
ScenarioRole = Literal["baseline", "dispatch"]


class AirScenario(BaseModel):
    """Inputs for one emissions scenario: how long the fleet runs, and on which factors.

    Defaults to the ``permit`` basis: it carries both engine-load points (idle testing vs
    a dispatch carrying load) and is the source the synthetic-minor cap is actually tracked
    against, so the cap-exceedance check is most faithful on it. AP-42 (``factors_basis=
    "ap42"``) is available as the conservative cross-check, at load only.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    runtime_hours: ProvenancedValue  # per-engine hr/yr
    factors_basis: FactorBasis = "permit"
    load_regime: LoadRegime = "load"
    role: ScenarioRole = "dispatch"


class PollutantTonnage(BaseModel):
    """One pollutant's annual fleet emissions and its standing against the NSR cap.

    ``tpy`` is this scenario's own tonnage (the net-new burden :func:`diff` reports).
    ``annual_tpy`` is what the cap actually counts: for a dispatch, the readiness-testing
    baseline plus the dispatch, in the same rolling 12 months. ``pct_of_cap`` and
    ``exceeds_cap`` are computed from ``annual_tpy``, and ``cap_status`` distinguishes
    "within the cap" from "no cap is known" — which ``exceeds_cap=False`` alone cannot.
    """

    model_config = ConfigDict(extra="forbid")

    pollutant: str
    tpy: ProvenancedValue  # this scenario's fleet tons: runtime x per-unit-hr x units / 2000
    annual_tpy: ProvenancedValue | None = None  # tons the cap counts (baseline + dispatch)
    cap_tpy: float | None = None  # synthetic-minor cap, if the pollutant is capped
    pct_of_cap: float | None = None  # annual_tpy / cap_tpy
    exceeds_cap: bool = False
    cap_status: CapStatus = "unknown"


class AirScenarioResult(BaseModel):
    """An evaluated scenario: per-pollutant tonnage, cap check, and the breach summary."""

    model_config = ConfigDict(extra="forbid")

    scenario: AirScenario
    engine_mw: ProvenancedValue
    fleet_size: int  # the identical fleet (the site profile's disclosed genset_count)
    auxiliary_units: int = 0  # units the permit rates separately, modeled at their own rate
    modeled_units: int  # fleet_size + auxiliary_units — the scope the cap is compared against
    fuel: str
    emissions: list[PollutantTonnage]
    caps_known: bool  # the site has a wired air permit, so the cap check could run
    any_cap_exceeded: bool | None  # None when no cap is known — absence is not compliance
    breached_pollutants: list[str] = []
    note: str = ""


class PollutantDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pollutant: str
    baseline_tpy: float
    scenario_tpy: float
    increase_tpy: float


class AirScenarioDiff(BaseModel):
    """Net new annual burden of a scenario over the baseline, per pollutant."""

    model_config = ConfigDict(extra="forbid")

    baseline: str
    scenario: str
    deltas: list[PollutantDelta]
    caps_newly_breached: list[str] = []


def baseline_scenario(*, factors_basis: FactorBasis = "permit") -> AirScenario:
    """The permit-baseline: maintenance + readiness testing only, no reliability event.

    Runs at the **idle** load point — readiness testing is low/no-load, so full-load rates
    would badly overstate it (and the facility demonstrably complies at baseline). Needs
    the permit basis for the idle rate.
    """
    return AirScenario(
        name="baseline",
        description="Emergency fleet at the maintenance & readiness-testing allowance only.",
        runtime_hours=ProvenancedValue.assume(
            _BASELINE_TEST_HOURS,
            "hr/yr",
            why="emergency-engine maintenance & readiness-testing allowance "
            "(40 CFR 60.4211(f) / NFPA 110); per engine",
        ),
        factors_basis=factors_basis,
        load_regime="idle",
        role="baseline",
    )


def reliability_dispatch_scenario(
    runtime_hours: float,
    *,
    band: str = "central",
    citation: str | None = None,
    factors_basis: FactorBasis = "permit",
) -> AirScenario:
    """A forced-runtime scenario from the #1176 dispatch band (runtime is per engine).

    ``runtime_hours`` is the per-engine forced runtime (e.g. ``RuntimeEstimate``'s
    ``runtime_hours_central``); it is `[inference]` until the real event grounds it (#1174).
    A reliability dispatch carries real facility load, so it runs at the **load** point.
    """
    why = citation or (
        f"reliability dispatch-trigger {band} runtime band (#1176) — [inference] pending #1174"
    )
    return AirScenario(
        name=f"reliability_dispatch_{band}",
        description=f"Reliability-forced fleet runtime ({band} band): {runtime_hours:g} hr/yr per engine.",
        runtime_hours=ProvenancedValue.assume(round(runtime_hours, 2), "hr/yr", why=why),
        factors_basis=factors_basis,
        load_regime="load",
    )


def _fleet_size(settings: Settings) -> int:
    # `campus`, not `facility` (#1664): a federal installation is a documented facility with no
    # disclosed genset fleet at all, so it must land in the no-fleet branch rather than the
    # "site-plan-grounded campus" one below, whose message would misdescribe it.
    fac = active_profile(settings).campus
    if fac is None:
        raise ValueError(
            f"site {settings.site!r} has no documented data-center campus — no genset fleet to model"
        )
    if fac.genset_count is None:
        raise ValueError(
            f"site {settings.site!r} has a documented facility but no disclosed gensets "
            "(a site-plan-grounded facility) — no genset fleet to model"
        )
    return fac.genset_count


def auxiliary_units_for(
    factors: GensetEmissionFactors, settings: Settings, caps_known: bool
) -> list[AuxiliaryUnits]:
    """The separately-rated units to add to the fleet (AQ-15).

    The permit basis carries them. AP-42 knows nothing of the permit's unit list, so when a
    permit is wired (``caps_known``) the units and their *permit* rates are borrowed for the
    AP-42 run too — otherwise an AP-42 cap check would compare a 114-unit tonnage to a
    115-unit cap. The borrowing is visible in each value's citation.
    """
    if factors.auxiliary or factors.basis == "permit" or not caps_known:
        return list(factors.auxiliary)
    permit = load_emission_factors(
        basis="permit", load_regime=factors.load_regime, settings=settings
    )
    return list(permit.auxiliary) if permit is not None else []


def _pollutant_lb_per_hr(
    factors: GensetEmissionFactors,
    auxiliary: list[AuxiliaryUnits],
    pol: Pollutant,
    fleet: int,
) -> tuple[float, str] | None:
    """Fleet-wide lb/hr for one pollutant (identical fleet + separately-rated units) + its basis."""
    ef = factors.factor(pol)
    if ef is None:
        return None
    rate = ef.per_engine_hour.value * fleet
    terms = [f"{ef.per_engine_hour.value:g} lb/hr x {fleet}"]
    for aux in auxiliary:
        a = aux.per_engine_hour.get(pol)
        if a is None:
            continue
        rate += a.value * aux.count
        terms.append(f"{a.value:g} lb/hr x {aux.count} ({aux.unit_ids})")
    return rate, " + ".join(terms)


def _testing_baseline_tpy(settings: Settings, fleet: int) -> dict[Pollutant, float]:
    """Annual tons from the readiness-testing allowance alone (idle, permit rates) — AQ-01.

    Only callable where a permit is wired (the idle point exists only on the permit basis,
    and a cap exists only where a permit does).
    """
    idle = load_emission_factors(basis="permit", load_regime="idle", settings=settings)
    if idle is None:
        return {}
    out: dict[Pollutant, float] = {}
    for pol in POLLUTANTS:
        r = _pollutant_lb_per_hr(idle, list(idle.auxiliary), pol, fleet)
        if r is not None:
            out[pol] = _BASELINE_TEST_HOURS * r[0] / LB_PER_TON
    return out


def evaluate(
    scenario: AirScenario,
    *,
    settings: Settings | None = None,
    factors: GensetEmissionFactors | None = None,
) -> AirScenarioResult:
    """Roll the scenario into annual tonnage per pollutant and check the NSR caps.

    ``tpy = runtime_hours x (per-engine factor x fleet + separately-rated units) / 2000``. The
    cap check is cumulative: a dispatch scenario's ``annual_tpy`` adds the readiness-testing
    baseline it shares the rolling 12-month window with. A pollutant whose cap is unknown
    reports ``cap_status="unknown"`` and the result reports ``any_cap_exceeded=None``.
    """
    settings = settings or get_settings()
    factors = factors or load_emission_factors(
        basis=scenario.factors_basis, load_regime=scenario.load_regime, settings=settings
    )
    if factors is None:
        raise ValueError(
            f"site {settings.site!r} has no documented facility — cannot evaluate air scenario"
        )
    fleet = _fleet_size(settings)
    caps = load_nsr_caps(settings=settings)
    caps_known = bool(caps)
    auxiliary = auxiliary_units_for(factors, settings, caps_known)
    n_aux = sum(a.count for a in auxiliary)
    runtime = scenario.runtime_hours.value
    testing = (
        _testing_baseline_tpy(settings, fleet) if caps_known and scenario.role == "dispatch" else {}
    )

    emissions: list[PollutantTonnage] = []
    breached: list[str] = []
    for pol in POLLUTANTS:
        r = _pollutant_lb_per_hr(factors, auxiliary, pol, fleet)
        if r is None:
            continue
        lb_hr, basis = r
        tpy = runtime * lb_hr / LB_PER_TON
        tpy_pv = ProvenancedValue.derived(
            round(tpy, 3),
            "tpy",
            citation=f"{runtime:g} hr/yr x ({basis}) / {LB_PER_TON:g} ({factors.basis} factors)",
        )
        cap = caps.get(pol)
        annual_pv: ProvenancedValue | None = None
        pct: float | None = None
        exceeds = False
        status: CapStatus
        if not caps_known:
            status = "unknown"
        elif cap is None:
            status = "uncapped"
        else:
            if scenario.role == "dispatch":
                base_tpy = testing.get(pol, 0.0)
                annual = base_tpy + tpy
                annual_cite = (
                    f"{base_tpy:.3f} tpy readiness testing ({_BASELINE_TEST_HOURS:g} hr/yr idle, "
                    f"permit rates) + {tpy:.3f} tpy this dispatch — both count against the same "
                    "rolling 12-month cap"
                )
            else:
                annual = tpy
                annual_cite = "the testing allowance alone (no dispatch)"
            annual_pv = ProvenancedValue.derived(round(annual, 3), "tpy", citation=annual_cite)
            pct = round(annual / cap.value * 100.0, 1) if cap.value else None
            exceeds = annual > cap.value
            status = "exceeded" if exceeds else "within"
            if exceeds:
                breached.append(pol)
        emissions.append(
            PollutantTonnage(
                pollutant=pol,
                tpy=tpy_pv,
                annual_tpy=annual_pv,
                cap_tpy=cap.value if cap else None,
                pct_of_cap=pct,
                exceeds_cap=exceeds,
                cap_status=status,
            )
        )

    aux_desc = ", ".join(f"{a.count} x {a.unit_ids}" for a in auxiliary)
    units_note = (
        f"Modeled units = {fleet} identical gensets + {n_aux} rated separately by the permit "
        f"({aux_desc}), at each unit's own rate."
        if auxiliary
        else f"Modeled units = {fleet} gensets at the standard-unit factor (the site's disclosed "
        "count); the permit rates no other unit separately."
    )
    if not caps_known:
        cap_note = (
            "No air permit is wired for this site, so no cap is known: the cap check is UNKNOWN, "
            "not passed."
        )
    elif scenario.role == "dispatch":
        cap_note = (
            "The cap check is cumulative: readiness testing and this dispatch share the "
            "facility-wide rolling 12-month synthetic-minor limit."
        )
    else:
        cap_note = "Caps are the facility-wide rolling 12-month synthetic-minor limits."

    result = AirScenarioResult(
        scenario=scenario,
        engine_mw=factors.engine_mw,
        fleet_size=fleet,
        auxiliary_units=n_aux,
        modeled_units=fleet + n_aux,
        fuel=factors.fuel,
        emissions=emissions,
        caps_known=caps_known,
        any_cap_exceeded=bool(breached) if caps_known else None,
        breached_pollutants=breached,
        note=f"{units_note} {cap_note}",
    )
    log.info(
        "air.scenario.evaluate",
        scenario=scenario.name,
        basis=factors.basis,
        runtime_hr=runtime,
        caps_known=caps_known,
        breached=breached,
    )
    return result


def cap_breach_runtime(
    pollutant: Pollutant,
    *,
    settings: Settings | None = None,
    factors: GensetEmissionFactors | None = None,
) -> float | None:
    """The per-engine dispatch runtime (hr/yr, at load) at which the facility crosses a cap.

    The epic's headline framing — "how much forced generation before this becomes a major
    NSR source." Two-term (AQ-01): the readiness-testing baseline consumes part of the cap
    first, so the threshold is ``(cap - testing tpy) x 2000 / fleet-wide lb/hr at load``,
    including the separately-rated units (AQ-15). ``0.0`` if testing alone already reaches the
    cap; ``None`` if the pollutant is uncapped or no cap is known for this site.
    """
    settings = settings or get_settings()
    factors = factors or load_emission_factors(
        basis="permit", load_regime="load", settings=settings
    )
    if factors is None:
        return None
    caps = load_nsr_caps(settings=settings)
    cap = caps.get(pollutant)
    if cap is None:
        return None
    fleet = _fleet_size(settings)
    r = _pollutant_lb_per_hr(
        factors, auxiliary_units_for(factors, settings, True), pollutant, fleet
    )
    if r is None or r[0] <= 0:
        return None
    headroom = cap.value - _testing_baseline_tpy(settings, fleet).get(pollutant, 0.0)
    return max(0.0, round(headroom * LB_PER_TON / r[0], 1))


def diff(baseline: AirScenarioResult, scenario: AirScenarioResult) -> AirScenarioDiff:
    """Net new annual burden of ``scenario`` over ``baseline``, per pollutant."""
    base = {e.pollutant: e for e in baseline.emissions}
    newly: list[str] = []
    deltas: list[PollutantDelta] = []
    for e in scenario.emissions:
        b = base.get(e.pollutant)
        b_tpy = b.tpy.value if b else 0.0
        deltas.append(
            PollutantDelta(
                pollutant=e.pollutant,
                baseline_tpy=round(b_tpy, 3),
                scenario_tpy=round(e.tpy.value, 3),
                increase_tpy=round(e.tpy.value - b_tpy, 3),
            )
        )
        if e.exceeds_cap and not (b and b.exceeds_cap):
            newly.append(e.pollutant)
    return AirScenarioDiff(
        baseline=baseline.scenario.name,
        scenario=scenario.scenario.name,
        deltas=deltas,
        caps_newly_breached=newly,
    )


def write_scenario(result: AirScenarioResult, *, settings: Settings | None = None) -> str:
    """Persist a scenario result as a committed, slug-scoped, self-auditing YAML artifact."""
    settings = settings or get_settings()
    out_dir = settings.scenarios_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    # Slug-scoped so a second site never clobbers Lima's scenario artifacts (#325).
    path = out_dir / f"{settings.site}.air-{result.scenario.name}.scenario.yaml"
    path.write_text(
        yaml.safe_dump(result.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    log.info("air.scenario.wrote", path=str(path))
    return str(path)
