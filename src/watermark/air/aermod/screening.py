"""Wire the Tier-0 emissions inventory into an AERMOD screening deck (#1178, #2099).

This is the seam between :mod:`watermark.air.emissions` (permit-certified per-engine rates)
and :mod:`watermark.air.aermod.inp` (the dispersion deck). :func:`build_screening_run` emits
**one ``POINT`` per permitted unit** (the identical fleet plus any unit the permit rates
separately, e.g. Lima's P115) on flat terrain with canned met. It used to emit a single
representative engine, which answered a different question: the Tier-0 premise is that a
reliability dispatch fires the fleet *together*, and one engine is 1/115th of that source term
(#2099, AQ-04).

Grounded vs assumed: every unit's emission rate is grounded (permit lb/hr → g/s); the stack
geometry and the array layout are ``assumption``s, because no record places or dimensions the
stacks (the permit redacts engine specs as CBI).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from watermark.air.aermod.inp import (
    build_aermod_inp,
    genset_point_source,
    stack_params_from_profile,
)
from watermark.air.aermod.model import (
    AermodControl,
    AermodSource,
    AveragePeriod,
    FleetLayout,
    GensetStackParams,
    ReceptorGrid,
)
from watermark.air.emissions import expand_unit_ids, load_emission_factors
from watermark.air.model import AuxiliaryUnits, FactorBasis, LoadRegime, Pollutant
from watermark.air.scenario import auxiliary_units_for
from watermark.config import Settings, get_settings
from watermark.hydrology.model import ProvenancedValue
from watermark.logging import get_logger
from watermark.sites import active_profile

log = get_logger(__name__)

# The permit's id range for the identical fleet. When it names exactly the profile's
# ``genset_count`` units, the deck uses the permit's own unit labels as source ids.
_HALL_IDS = "P001-P114"

# Centre-to-centre spacing of the assumed array. Stated, not sourced: no document in the
# corpus places the stacks.
ARRAY_SPACING_M = 15.0
_LAYOUT_WHY = (
    "no record places the genset stacks (engine specs are redacted as CBI and no site plan "
    "locates them), so the fleet is modeled as a uniform square array centred on the model "
    "origin — a screening layout, not a site-plan reading"
)


@dataclass(frozen=True)
class ScreeningDeck:
    """A built screening deck and what it models, for the callers that report on it."""

    inp_text: str
    plotfiles: dict[str, str]
    sources: list[AermodSource]
    layout: FleetLayout
    stack: GensetStackParams
    unit_rate_g_s: float  # one identical-fleet unit's rate (g/s)
    fleet_rate_g_s: float  # every modeled source summed (g/s)
    auxiliary_ids: list[str]  # source ids of the separately-rated units


def array_positions(n: int, spacing_m: float) -> tuple[int, int, list[tuple[float, float]]]:
    """``(columns, rows, [(x, y), ...])`` for ``n`` units on a near-square grid about the origin.

    Row-major, west→east then south→north, centred so the array's midpoint is ``(0, 0)`` — the
    point the receptor grid (and the field's ``geo_ref``) is anchored on.
    """
    if n < 1:
        raise ValueError("an array needs at least one unit")
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    x0 = -(cols - 1) * spacing_m / 2
    y0 = -(rows - 1) * spacing_m / 2
    pts = [(x0 + (i % cols) * spacing_m, y0 + (i // cols) * spacing_m) for i in range(n)]
    return cols, rows, [(round(x, 3), round(y, 3)) for x, y in pts]


def _fleet_ids(count: int, *, basis: FactorBasis) -> list[str]:
    """Source ids for the identical fleet: the permit's own labels when they fit, else ``G###``."""
    if basis == "permit":
        ids = expand_unit_ids(_HALL_IDS)
        if len(ids) == count and all(len(i) <= 8 for i in ids):
            return ids
    return [f"G{i:03d}" for i in range(1, count + 1)]


def _auxiliary_ids(aux: AuxiliaryUnits, taken: set[str]) -> list[str]:
    """Source ids for one separately-rated group — its permit labels, else ``A###``."""
    ids = expand_unit_ids(aux.unit_ids)
    if len(ids) == aux.count and all(len(i) <= 8 and i not in taken for i in ids):
        return ids
    start = len([t for t in taken if t.startswith("A")]) + 1
    return [f"A{i:03d}" for i in range(start, start + aux.count)]


def build_screening_run(
    *,
    pollutant: Pollutant = "NOx",
    basis: FactorBasis = "permit",
    load_regime: LoadRegime = "load",
    averaging_periods: tuple[AveragePeriod, ...] = ("1", "ANNUAL"),
    grid_half_extent_m: float = 2500.0,
    grid_spacing_m: float = 100.0,
    surface_file: str = "canned.sfc",
    profile_file: str = "canned.pfl",
    spacing_m: float = ARRAY_SPACING_M,
    settings: Settings | None = None,
) -> ScreeningDeck | None:
    """Build the fleet screening deck for the active site — one ``POINT`` per permitted unit.

    Returns ``None`` if the site has no disclosed genset fleet or the pollutant isn't grounded
    on the chosen basis. The modeled scope matches the Tier-0 cap check
    (:mod:`watermark.air.scenario`): the profile's identical fleet plus every unit the permit
    rates separately, each at its own rate.
    """
    settings = settings or get_settings()
    campus = active_profile(settings).campus
    if campus is None or not campus.genset_count:
        log.info("aermod.screening.no_fleet", site=settings.site)
        return None
    factors = load_emission_factors(basis=basis, load_regime=load_regime, settings=settings)
    if factors is None:
        log.info("aermod.screening.no_facility", site=settings.site)
        return None
    ef = factors.factor(pollutant)
    if ef is None:
        log.info("aermod.screening.pollutant_ungrounded", site=settings.site, pollutant=pollutant)
        return None

    stack = stack_params_from_profile(settings)
    rate_cite = f"{factors.basis} per-engine {pollutant} at {factors.load_regime} load"
    fleet = campus.genset_count
    planned: list[tuple[str, float, str]] = [
        (sid, ef.per_engine_hour.value, rate_cite) for sid in _fleet_ids(fleet, basis=basis)
    ]
    aux_ids: list[str] = []
    caps_known = campus.air_permit_relpath is not None
    for aux in auxiliary_units_for(factors, settings, caps_known):
        rate = aux.per_engine_hour.get(pollutant)
        if rate is None:
            continue
        ids = _auxiliary_ids(aux, {p[0] for p in planned})
        aux_ids += ids
        cite = f"permit {aux.unit_ids} {pollutant} (rated separately; {rate.citation})"
        planned += [(sid, rate.value, cite) for sid in ids]

    cols, rows, positions = array_positions(len(planned), spacing_m)
    sources = [
        genset_point_source(
            src_id=sid,
            pollutant=pollutant,
            per_engine_lb_per_hr=lb_hr,
            rate_citation=cite,
            stack=stack,
            x_m=x,
            y_m=y,
        )
        for (sid, lb_hr, cite), (x, y) in zip(planned, positions, strict=True)
    ]
    layout = FleetLayout(
        units=len(sources),
        columns=cols,
        rows=rows,
        spacing_m=ProvenancedValue.assume(spacing_m, "m", why=_LAYOUT_WHY),
        unit_ids=[s.src_id for s in sources],
    )
    control = AermodControl(
        title=(
            f"Watermark AERMOD screening: {settings.site} {pollutant} ({factors.basis}), "
            f"{len(sources)} units"
        ),
        pollutant=pollutant,
        averaging_periods=averaging_periods,
        terrain="FLAT",
    )
    grid = ReceptorGrid.centered(half_extent_m=grid_half_extent_m, spacing_m=grid_spacing_m)
    plotfiles: dict[str, str] = {str(ave): f"{ave.lower()}.plt" for ave in averaging_periods}
    inp_text = build_aermod_inp(
        control=control,
        sources=sources,
        grid=grid,
        surface_file=surface_file,
        profile_file=profile_file,
        plotfiles=plotfiles,
    )
    return ScreeningDeck(
        inp_text=inp_text,
        plotfiles=plotfiles,
        sources=sources,
        layout=layout,
        stack=stack,
        unit_rate_g_s=sources[0].emission_g_s.value,
        fleet_rate_g_s=round(sum(s.emission_g_s.value for s in sources), 6),
        auxiliary_ids=aux_ids,
    )


def build_screening_deck(
    *,
    pollutant: Pollutant = "NOx",
    basis: FactorBasis = "permit",
    load_regime: LoadRegime = "load",
    averaging_periods: tuple[AveragePeriod, ...] = ("1", "ANNUAL"),
    grid_half_extent_m: float = 2500.0,
    grid_spacing_m: float = 100.0,
    surface_file: str = "canned.sfc",
    profile_file: str = "canned.pfl",
    settings: Settings | None = None,
) -> tuple[str, dict[str, str]] | None:
    """``(inp_text, plotfiles)`` from :func:`build_screening_run` — the deck text alone."""
    built = build_screening_run(
        pollutant=pollutant,
        basis=basis,
        load_regime=load_regime,
        averaging_periods=averaging_periods,
        grid_half_extent_m=grid_half_extent_m,
        grid_spacing_m=grid_spacing_m,
        surface_file=surface_file,
        profile_file=profile_file,
        settings=settings,
    )
    return (built.inp_text, built.plotfiles) if built is not None else None
