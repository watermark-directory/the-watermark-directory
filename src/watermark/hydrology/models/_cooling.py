"""Cooling-basis + scenario models for the Tier-0 hydrology subsystem."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from watermark.hydrology.models._core import ProvenancedValue, WaterBalance
from watermark.hydrology.models._lowflow import AssimilativeCheck


class CoolingBasis(BaseModel):
    """A sourced cooling-water design basis, derived from disclosed campus data.

    Two independent estimates bracket the demand: a top-down power x WUE balance
    (disclosed backup generation -> IT load -> evaporative makeup) and a bottom-up
    blowdown x cycles-of-concentration check (documented FM-2 discharge). The
    inputs are document/assumption-tagged; the demands are ``derived``.
    """

    model_config = ConfigDict(extra="forbid")

    it_load: ProvenancedValue  # MW (from the air-permit genset count)
    wue: ProvenancedValue  # L/kWh, consumptive water per IT energy
    cycles_of_concentration: ProvenancedValue  # cooling-tower CoC
    consumptive_fraction: ProvenancedValue  # (CoC-1)/CoC, derived
    makeup_demand: ProvenancedValue  # MGD, the cooling intake (power-based central)
    consumptive_low: ProvenancedValue  # MGD, power x WUE
    consumptive_high: ProvenancedValue  # MGD, full-blowdown x cycles upper bound
    method: str = "power x WUE (central); blowdown x cycles (upper bound)"


class Scenario(BaseModel):
    """A what-if over the municipal loop, parameterized by the cooling knob.

    The data-center campus draws cooling water from the same Ottawa/Auglaize supply
    the WWTPs discharge to; the evaporated (consumptive) fraction is a net loss to
    the basin. The knobs default to the sourced :class:`CoolingBasis` but remain
    overridable — this is a sensitivity, not a forecast.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    cooling_demand: ProvenancedValue  # campus cooling intake (MGD)
    consumptive_fraction: ProvenancedValue  # fraction evaporated (0..1)
    basis: CoolingBasis | None = None  # the sourced derivation, when used


class ScenarioResult(BaseModel):
    """A scenario evaluated against the water balance + cited low flows."""

    model_config = ConfigDict(extra="forbid")

    scenario: Scenario
    consumptive_loss: ProvenancedValue  # net basin loss (cfs), derived from the knobs
    ottawa_7q10: ProvenancedValue | None = None  # cited Ottawa mainstem low flow
    ottawa_live: ProvenancedValue | None = None  # live Ottawa streamflow, for context
    balance: WaterBalance
    assimilative: list[AssimilativeCheck]


class ScenarioDiff(BaseModel):
    """Baseline vs buildout: the net new consumptive draw and its low-flow scale."""

    model_config = ConfigDict(extra="forbid")

    baseline: str
    scenario: str
    consumptive_increase_cfs: float
    ottawa_7q10_cfs: float | None = None
    multiple_of_7q10: float | None = None


class MonthlyWithdrawal(BaseModel):
    """One month: the cooling draw vs the season-appropriate cited low flow.

    The consumptive draw is constant year-round; what changes by month is the
    receiving stream's *available* low flow and whether rainfall offsets atmospheric
    demand. In the growing season the draw is read against the cited summer design low
    flow (30Q10), not the annual 7Q10 — and arrives when reference ET exceeds precip,
    so there is no rainfall buffer.
    """

    model_config = ConfigDict(extra="forbid")

    month: str  # JAN..DEC
    growing_season: bool  # ET0 > precip this month
    et0_mm_day: float
    precip_mm_day: float
    net_atmospheric_mm_day: float  # ET0 - precip (positive = deficit, no rainfall buffer)
    low_flow_cfs: float  # the cited design low flow applied this month
    low_flow_basis: str  # "30Q10 summer" | "7Q10 annual"
    consumptive_cfs: float  # the scenario's net consumptive draw (constant)
    multiple: float | None  # consumptive / low_flow (None when the floor is 0)


class SeasonalWithdrawal(BaseModel):
    """The cooling draw screened month-by-month against the Ottawa's seasonal low flow.

    Bridges the climate baseline (reference ET vs precip) and the cooling scenario: the
    annual-7Q10 multiple understates the growing-season pinch, when the river sits at its
    summer design low flow *and* ET exceeds precip. All low-flow figures are cited
    (`data/reference/hydrology/low-flow-7q10.yaml`); no monthly statistic is fabricated.
    """

    model_config = ConfigDict(extra="forbid")

    scenario: str
    consumptive_cfs: float
    months: list[MonthlyWithdrawal]
    growing_season_months: list[str]
    annual_7q10_cfs: float
    summer_30q10_cfs: float | None = None
    one_q10_cfs: float | None = None  # absolute design low flow (often 0)
    annual_multiple: float | None = None  # draw / annual 7Q10
    summer_multiple: float | None = None  # draw / summer 30Q10 — the seasonal headline
