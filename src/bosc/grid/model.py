"""Typed models for the grid & regulatory stack (epic #93).

The layer **above** the facility power model (:mod:`bosc.facility.power`): the campus
load's serving electric utility, its balancing authority / RTO, and the load expressed
as a share of each. Like the other computed subsystems these use ``extra="forbid"`` and
carry provenance — numeric figures as :class:`bosc.hydrology.model.ProvenancedValue`,
string identifications as :class:`CitedFact` (the non-numeric analogue), so a serving
utility is *cited*, never asserted.

Issue #94 is the foundation layer (serving utility + BA profile + load share); #95-#98
(interchange, PJM market, FERC, federal policy) build on top.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from bosc.hydrology.model import ProvenancedValue, SourceKind


class CitedFact(BaseModel):
    """A non-numeric identification carrying provenance — the string analogue of
    :class:`ProvenancedValue`. ``source`` maps onto the same evidence discipline
    (``document``/``connector`` → verified; ``reference``/``assumption`` → asserted).
    """

    model_config = ConfigDict(extra="forbid")

    value: str  # "AEP Ohio (Ohio Power Company)"
    source: SourceKind
    citation: str
    confidence: Literal["high", "medium", "low"] = "medium"

    @property
    def verified(self) -> bool:
        return self.source in ("document", "connector")


class ServingUtility(BaseModel):
    """The cited identification of the campus's electric-service chain.

    Bottom of the regulatory stack: who delivers retail power (the utility, PUCO-
    regulated), within which balancing authority / RTO (PJM, FERC-jurisdictional), and
    its holding company. Each field is a :class:`CitedFact` — the working identification
    is corpus- or authoritative-source-grounded, with the EIA-861 service territory /
    PUCO map named as the formal confirmation source.
    """

    model_config = ConfigDict(extra="forbid")

    utility: CitedFact  # the retail electric utility serving the parcels
    holding_company: CitedFact  # its parent (e.g. American Electric Power)
    balancing_authority: CitedFact  # the BA / RTO that balances the load
    rto: CitedFact  # the wholesale-market RTO/ISO (FERC-jurisdictional)
    retail_regulator: CitedFact  # the state retail regulator (PUCO)
    note: str = ""


class UtilityProfile(BaseModel):
    """EIA-861 annual profile for the serving utility (retail sales / customers / price).

    Transcribed published EIA-861 figures (``reference``), not a facility disclosure;
    the per-utility EIA-861 entity file is the authoritative source (see the README) —
    figures here are flagged for verification with a keyed/bulk pull.
    """

    model_config = ConfigDict(extra="forbid")

    utility: str  # "AEP Ohio (Ohio Power Company)"
    eia_source: str = "EIA-861 utility annual electric sales (transcribed; verify)"
    retail_sales_gwh: ProvenancedValue  # reference
    customers: ProvenancedValue | None = None  # reference
    avg_price_cents_kwh: ProvenancedValue | None = None  # reference


class BalancingAuthorityProfile(BaseModel):
    """EIA-930 annual profile for the balancing authority / RTO (PJM)."""

    model_config = ConfigDict(extra="forbid")

    ba: str  # "PJM Interconnection"
    eia_source: str = "EIA-930 hourly grid monitor, annual demand (transcribed; verify)"
    annual_load_gwh: ProvenancedValue  # reference


class GridLoadShare(BaseModel):
    """The campus load expressed as a share of utility / BA / state load.

    Sizes the campus annual electricity demand (from the first-class
    ``facility_draw``, :mod:`bosc.facility.power`, issue #87) against three cited
    denominators. The state share is the most robust (the EIA state figure is
    connector-sourced); the utility and BA shares use transcribed EIA-861/930 figures
    flagged for verification, so their confidence is lower.
    """

    model_config = ConfigDict(extra="forbid")

    campus_load_mw: ProvenancedValue  # total facility draw, central (#87)
    load_factor: ProvenancedValue  # assumption: capacity utilization
    annual_consumption_gwh: ProvenancedValue  # derived: draw x 8760 x load factor
    utility_retail_gwh: ProvenancedValue  # AEP Ohio retail sales (reference)
    ba_load_gwh: ProvenancedValue  # PJM annual load (reference)
    state_retail_gwh: ProvenancedValue  # Ohio retail sales (connector, shared with #91)
    share_of_utility_pct: ProvenancedValue  # derived
    share_of_ba_pct: ProvenancedValue  # derived
    share_of_state_pct: ProvenancedValue  # derived


class GridProfile(BaseModel):
    """The assembled grid foundation layer (issue #94): identity + profiles + load share."""

    model_config = ConfigDict(extra="forbid")

    serving_utility: ServingUtility
    utility_profile: UtilityProfile
    ba_profile: BalancingAuthorityProfile
    load_share: GridLoadShare
    note: str = ""
