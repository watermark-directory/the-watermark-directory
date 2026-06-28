"""Typed models for the grid & regulatory stack (epic #93).

The layer **above** the facility power model (:mod:`watermark.facility.power`): the campus
load's serving electric utility, its balancing authority / RTO, and the load expressed
as a share of each. Like the other computed subsystems these use ``extra="forbid"`` and
carry provenance — numeric figures as :class:`watermark.hydrology.model.ProvenancedValue`,
string identifications as :class:`CitedFact` (the non-numeric analogue), so a serving
utility is *cited*, never asserted.

Issue #94 is the foundation layer (serving utility + BA profile + load share); #95-#98
(interchange, PJM market, FERC, federal policy) build on top.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from watermark.hydrology.model import ProvenancedValue, SourceKind


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
    ownership: str = (
        ""  # EIA-861 ownership ("Investor Owned" / "Municipal" / "Cooperative"); "" if unread
    )
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
    ``facility_draw``, :mod:`watermark.facility.power`, issue #87) against three cited
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
    """The assembled grid foundation layer (issue #94): identity + profiles + load share.

    ``load_share`` is ``None`` for a site with no documented data-center facility
    (``SiteProfile.facility is None``): the grid backdrop (serving utility + EIA utility/BA
    profiles) is real per-site data, but there is no campus load to express as a share of it
    until that site's facility is disclosed (the data-center dimension).
    """

    model_config = ConfigDict(extra="forbid")

    serving_utility: ServingUtility
    utility_profile: UtilityProfile
    ba_profile: BalancingAuthorityProfile
    load_share: GridLoadShare | None = None
    note: str = ""


class BAInterchange(BaseModel):
    """Reduced EIA-930 hourly interchange profile for one balancing authority (#95).

    The "interchange layer": the BA's hourly **demand**, **net generation**, and
    **total net interchange** (``TI``; sign convention + = net exports, - = net
    imports) summarized over a representative window from the EIA-930 Hourly Electric
    Grid Monitor. The point is to situate the campus load against where the BA's
    marginal electrons come from — in-BA generation vs net imports. Connector-sourced.
    """

    model_config = ConfigDict(extra="forbid")

    ba: str  # "PJM"
    period_start: str  # ISO date of the window start
    period_end: str
    hours: int  # hourly samples in the window
    demand_mean_mw: ProvenancedValue  # connector
    demand_peak_mw: ProvenancedValue
    net_generation_mean_mw: ProvenancedValue
    total_interchange_mean_mw: ProvenancedValue  # + = net exports, - = net imports
    interchange_min_mw: ProvenancedValue  # most-importing hour (most negative TI)
    interchange_max_mw: ProvenancedValue  # most-exporting hour
    net_import_hours_fraction: ProvenancedValue  # share of hours with TI < 0 (importing)
    source: str = "EIA-930 Hourly Electric Grid Monitor (region-data: D / NG / TI)"
    note: str = ""


class CampusInterchangeComparison(BaseModel):
    """Campus load situated against the BA's interchange & in-BA generation (#95, derived).

    Answers the call's question — does the added ~275 MW plausibly come from in-BA
    generation or net imports? The headline is the in-BA generation **headroom** (mean
    net generation minus mean demand): when it exceeds the campus load, the added draw
    is comfortably within the BA's own generation and does not require net imports. The
    campus is also sized against the mean net-interchange magnitude (the swing it eats
    into). A screening comparison over mean conditions, not an hourly dispatch model.
    """

    model_config = ConfigDict(extra="forbid")

    ba: str
    campus_load_mw: ProvenancedValue  # total facility draw, central (#87)
    ba_demand_mean_mw: ProvenancedValue  # connector (EIA-930)
    ba_net_generation_mean_mw: ProvenancedValue
    ba_interchange_mean_mw: ProvenancedValue
    campus_share_of_demand_pct: ProvenancedValue  # derived: campus / BA mean demand
    campus_vs_interchange_pct: ProvenancedValue  # derived: campus / |BA mean interchange|
    in_ba_generation_headroom_mw: ProvenancedValue  # derived: net generation - demand (mean)
    met_by_in_ba_generation: bool  # headroom >= campus load (no net imports needed)
    interpretation: str = ""
    caveats: list[str] = []
