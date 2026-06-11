"""PJM wholesale-market context for the campus load (#96, epic #93).

The "RTO / wholesale market" layer of the grid & regulatory stack: above the
serving-utility / BA identification (#94) and the EIA-930 interchange layer (#95),
this situates the campus load against the three price signals a large new load in
PJM actually sees -

  - zonal **LMP** (locational marginal price - the energy price signal),
  - the **capacity market** (RPM - the Base Residual Auction clearing price, which
    drives the capacity obligation a large new load implies), and
  - the **large-load interconnection queue** (the data-center / large-load interest
    PJM has reported, against which the campus is sized).

Data discipline (epic #93): NO live PJM connector is provided here - PJM Data Miner 2
needs no key but is not reachable from this environment, so the published figures are
**transcribed** into a committed reference YAML (``data/reference/pjm/pjm-market.yaml``)
as :class:`bosc.hydrology.model.ProvenancedValue` at ``confidence="medium"``, each
citation naming its source (PJM Data Miner 2, PJM Base Residual Auction reports, PJM
interconnection-queue reporting) and flagged *verify / regenerate via PJM Data Miner 2*.
The derived scenario is a **screening** view in the "bracket, don't overclaim" idiom -
LMP varies by node and hour, the RPM clearing price is not the campus's contracted
rate, and the queue figure is order-of-magnitude. **Nothing here is a facility
disclosure**: the campus draw is the first-class ``facility_draw`` from
:mod:`bosc.facility.power` (#87); everything else is published market data.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.facility.power import derive_power_basis
from bosc.grid.model import CitedFact
from bosc.hydrology.model import ProvenancedValue
from bosc.logging import get_logger

log = get_logger(__name__)

_HOURS_PER_YEAR = 8760.0
_LOAD_FACTOR = 0.9  # data centers run near-flat (shared convention with #91/#94/#95)
_LOAD_FACTOR_CITE = (
    "data-center capacity utilization ~0.9 (near-flat 24x7); assumption (cf. #91/#94/#95)"
)
_DAYS_PER_YEAR = 365.0

# --- Transcribed PJM published figures (verify / regenerate via PJM Data Miner 2) ----
# Zonal LMP: AEP zone average annual locational marginal price.
_AEP_LMP_USD_MWH = 35.0
_AEP_LMP_CITE = (
    "PJM Data Miner 2 da_hrl_lmps, AEP zone ~2024 annual average ($/MWh); "
    "transcribed published figure - verify (regenerate via PJM Data Miner 2)"
)
# Capacity (RPM): 2025/2026 Base Residual Auction RTO-wide clearing price, a major
# spike from the prior 2024/2025 delivery year.
_RPM_CLEARING_USD_MW_DAY = 269.92
_RPM_PRIOR_USD_MW_DAY = 28.92
_RPM_CLEARING_CITE = (
    "PJM 2025/2026 Base Residual Auction, RTO-wide clearing price ($/MW-day); "
    "transcribed published figure - verify (PJM RPM BRA report)"
)
_RPM_PRIOR_CITE = (
    "PJM 2024/2025 Base Residual Auction, RTO-wide clearing price ($/MW-day) - "
    "the prior-year level, for context; transcribed - verify (PJM RPM BRA report)"
)
# Large-load / interconnection queue: PJM-reported large-load / data-center interest.
# Order-of-magnitude only - do not overstate precision.
_LARGE_LOAD_QUEUE_GW = 50.0
_LARGE_LOAD_QUEUE_CITE = (
    "PJM large-load / data-center interconnection interest, order-of-magnitude "
    "(tens of GW) ~2024; transcribed - verify (PJM interconnection-queue reporting)"
)


class PjmMarketReference(BaseModel):
    """The transcribed PJM published market figures (the reference inputs, #96).

    Each numeric figure is a :class:`ProvenancedValue` tagged ``reference`` at
    ``confidence="medium"`` whose citation names its PJM source and is flagged for
    verification - none is asserted as ground truth. The non-numeric BA/zone/RTO
    identifications are :class:`CitedFact`. Regenerate by re-reading PJM Data Miner 2 /
    the RPM Base Residual Auction reports / the interconnection-queue reporting.
    """

    model_config = ConfigDict(extra="forbid")

    rto: CitedFact  # "PJM Interconnection (RTO/ISO)"
    lmp_zone: CitedFact  # the LMP pricing zone the campus sits in (AEP)
    zonal_lmp_usd_mwh: ProvenancedValue  # reference: AEP-zone annual average LMP
    rpm_clearing_usd_mw_day: ProvenancedValue  # reference: RTO-wide BRA clearing price
    rpm_prior_year_usd_mw_day: ProvenancedValue  # reference: prior-year clearing, for context
    large_load_queue_gw: (
        ProvenancedValue  # reference: large-load / data-center queue (order-of-mag)
    )
    source: str = (
        "PJM Data Miner 2 / PJM RPM Base Residual Auction reports / PJM queue (transcribed; verify)"
    )
    note: str = ""


class PjmMarketScenario(BaseModel):
    """The campus load's marginal-price / capacity footprint in PJM (#96, derived).

    A provenance-tagged screening scenario: the campus annual energy cost at the zonal
    LMP, its annual capacity-market (RPM) obligation at the clearing price, and the
    campus sized against the large-load interconnection queue. The campus draw is the
    first-class ``facility_draw`` (#87); the prices are transcribed PJM reference
    figures. **Not** a settlement, dispatch, or RPM-bidding model - a bracketed view.
    """

    model_config = ConfigDict(extra="forbid")

    rto: str  # "PJM Interconnection (RTO/ISO)"
    lmp_zone: str  # "AEP zone"
    campus_load_mw: ProvenancedValue  # total facility draw, central (#87)
    load_factor: ProvenancedValue  # assumption: capacity utilization
    annual_consumption_gwh: ProvenancedValue  # derived: draw x 8760 x load factor
    zonal_lmp_usd_mwh: ProvenancedValue  # reference: AEP-zone annual average LMP
    rpm_clearing_usd_mw_day: ProvenancedValue  # reference: RTO-wide BRA clearing price
    annual_energy_cost_musd: ProvenancedValue  # derived: consumption x LMP -> $M/yr
    annual_capacity_cost_musd: ProvenancedValue  # derived: draw x clearing x 365 -> $M/yr
    large_load_queue_gw: ProvenancedValue  # reference: large-load queue (order-of-magnitude)
    campus_share_of_queue_pct: ProvenancedValue  # derived: campus MW / queue GW
    interpretation: str = ""
    caveats: list[str] = []


def _market_reference() -> PjmMarketReference:
    """Assemble the transcribed PJM published figures (reference inputs)."""
    return PjmMarketReference(
        rto=CitedFact(
            value="PJM Interconnection (RTO/ISO)",
            source="reference",
            citation="PJM is the FERC-jurisdictional wholesale-market RTO for AEP Ohio (#94)",
            confidence="high",
        ),
        lmp_zone=CitedFact(
            value="AEP zone",
            source="reference",
            citation="AEP Ohio's transmission zone within PJM; the campus's LMP pricing zone (#94)",
            confidence="medium",
        ),
        zonal_lmp_usd_mwh=ProvenancedValue.from_reference(
            _AEP_LMP_USD_MWH, "USD/MWh", citation=_AEP_LMP_CITE, confidence="medium"
        ),
        rpm_clearing_usd_mw_day=ProvenancedValue.from_reference(
            _RPM_CLEARING_USD_MW_DAY,
            "USD/MW-day",
            citation=_RPM_CLEARING_CITE,
            confidence="medium",
        ),
        rpm_prior_year_usd_mw_day=ProvenancedValue.from_reference(
            _RPM_PRIOR_USD_MW_DAY, "USD/MW-day", citation=_RPM_PRIOR_CITE, confidence="medium"
        ),
        large_load_queue_gw=ProvenancedValue.from_reference(
            _LARGE_LOAD_QUEUE_GW, "GW", citation=_LARGE_LOAD_QUEUE_CITE, confidence="medium"
        ),
        note=(
            "Transcribed PJM published figures (#96): zonal LMP is the energy price "
            "signal (congestion is a component - LMP = energy + congestion + losses); "
            "the RPM clearing price drives a large new load's capacity obligation; the "
            "large-load queue is order-of-magnitude. Verify / regenerate via PJM Data "
            "Miner 2 and the RPM Base Residual Auction reports. Not a facility disclosure."
        ),
    )


def derive_pjm_market_scenario(*, settings: Settings | None = None) -> PjmMarketScenario:
    """Derive the campus load's PJM marginal-price / capacity footprint (#96).

    Links the first-class ``facility_draw`` (#87) to the transcribed PJM LMP / RPM /
    queue reference figures: annual energy cost at the zonal LMP, the annual RPM
    capacity obligation at the clearing price, and the campus sized against the
    large-load interconnection queue. A bracketed screening view, not a settlement model.
    """
    settings = settings or get_settings()
    power = derive_power_basis(settings=settings)
    ref = _market_reference()

    draw_mw = power.facility_draw.value
    consumption_mwh = draw_mw * _HOURS_PER_YEAR * _LOAD_FACTOR
    consumption_gwh = consumption_mwh / 1000.0

    lmp = ref.zonal_lmp_usd_mwh.value
    clearing = ref.rpm_clearing_usd_mw_day.value
    queue_gw = ref.large_load_queue_gw.value

    # Energy cost: consumption (MWh/yr) x LMP ($/MWh) -> $/yr -> $M/yr.
    annual_energy_cost_musd = consumption_mwh * lmp / 1_000_000.0
    # Capacity cost: draw (MW) x clearing ($/MW-day) x 365 days -> $/yr -> $M/yr.
    annual_capacity_cost_musd = draw_mw * clearing * _DAYS_PER_YEAR / 1_000_000.0
    # Campus MW as a fraction of the large-load queue (GW -> MW).
    share_of_queue_pct = draw_mw / (queue_gw * 1000.0) * 100.0 if queue_gw else 0.0

    interp = (
        f"At the AEP-zone average LMP (~${lmp:g}/MWh) the campus's ~{consumption_gwh:,.0f} "
        f"GWh/yr of energy costs on the order of ${annual_energy_cost_musd:,.0f}M/yr; its "
        f"RPM capacity footprint at the 2025/2026 BRA clearing price (${clearing:g}/MW-day) "
        f"is on the order of ${annual_capacity_cost_musd:,.0f}M/yr for {draw_mw:g} MW of "
        f"unforced capacity. That capacity figure tracks an ~{clearing / ref.rpm_prior_year_usd_mw_day.value:.0f}x "
        f"clearing-price spike over the prior year. The campus ({draw_mw:g} MW) is "
        f"~{share_of_queue_pct:.1f}% of the reported large-load interconnection queue "
        f"(~{queue_gw:g} GW, order-of-magnitude) - one campus, a small slice of a very "
        "large pipeline. Bracketing figures, not the campus's contracted costs."
    )

    log.info(
        "grid.pjm_market",
        lmp_usd_mwh=lmp,
        rpm_usd_mw_day=clearing,
        energy_cost_musd=round(annual_energy_cost_musd, 1),
        capacity_cost_musd=round(annual_capacity_cost_musd, 1),
        share_of_queue_pct=round(share_of_queue_pct, 2),
    )
    return PjmMarketScenario(
        rto=ref.rto.value,
        lmp_zone=ref.lmp_zone.value,
        campus_load_mw=ProvenancedValue.derived(
            round(draw_mw, 1),
            "MW",
            citation=f"PowerBasis.facility_draw central (#87): {power.facility_draw.citation or ''}",
        ),
        load_factor=ProvenancedValue.assume(_LOAD_FACTOR, "fraction", why=_LOAD_FACTOR_CITE),
        annual_consumption_gwh=ProvenancedValue.derived(
            round(consumption_gwh, 1),
            "GWh/yr",
            citation=f"{draw_mw:g} MW x {_HOURS_PER_YEAR:g} h x {_LOAD_FACTOR:g} load factor",
        ),
        zonal_lmp_usd_mwh=ref.zonal_lmp_usd_mwh,
        rpm_clearing_usd_mw_day=ref.rpm_clearing_usd_mw_day,
        annual_energy_cost_musd=ProvenancedValue.derived(
            round(annual_energy_cost_musd, 1),
            "USD_million/yr",
            citation=f"{consumption_gwh:,.0f} GWh x ${lmp:g}/MWh (AEP-zone LMP, transcribed; verify)",
            confidence="medium",
        ),
        annual_capacity_cost_musd=ProvenancedValue.derived(
            round(annual_capacity_cost_musd, 1),
            "USD_million/yr",
            citation=f"{draw_mw:g} MW x ${clearing:g}/MW-day x {_DAYS_PER_YEAR:g} d "
            "(2025/2026 BRA clearing, transcribed; verify)",
            confidence="medium",
        ),
        large_load_queue_gw=ref.large_load_queue_gw,
        campus_share_of_queue_pct=ProvenancedValue.derived(
            round(share_of_queue_pct, 2),
            "percent",
            citation=f"campus {draw_mw:g} MW / large-load queue {queue_gw:g} GW "
            "(order-of-magnitude, transcribed; verify)",
            confidence="medium",
        ),
        interpretation=interp,
        caveats=[
            "A SCREENING price/capacity footprint, not a settlement or dispatch model - "
            "energy and capacity are settled hourly/by delivery year against the campus's "
            "actual contracts, not these annualized averages.",
            "LMP varies by NODE and HOUR (LMP = energy + congestion + losses); the AEP-zone "
            "annual average is a single point, not the campus's bus-specific or peak-hour price.",
            "The RPM clearing price is an RTO-wide CLEARING price, not the campus's contracted "
            "capacity rate; the 2025/2026 spike may not persist, and obligations depend on the "
            "campus's coincident-peak contribution, not nameplate MW.",
            "The large-load / interconnection-queue figure is ORDER-OF-MAGNITUDE (tens of GW) "
            "and not all queued load is built; the campus share is illustrative.",
            "All PJM figures are TRANSCRIBED published values at medium confidence, flagged "
            "for verification - regenerate via PJM Data Miner 2 / the RPM BRA reports. None "
            "is a facility disclosure.",
        ],
    )


def _reference_path(reference_dir: Path) -> Path:
    return reference_dir / "pjm" / "pjm-market.yaml"


def write_pjm_market(reference: PjmMarketReference, *, settings: Settings | None = None) -> str:
    """Persist the transcribed PJM market reference as committed YAML; return the path."""
    settings = settings or get_settings()
    path = _reference_path(settings.reference_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(reference.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    log.info("grid.pjm_market.wrote", path=str(path))
    return str(path)


def load_pjm_market(reference_dir: Path) -> PjmMarketReference | None:
    """Read the committed PJM market reference YAML, or ``None`` if absent."""
    path = _reference_path(reference_dir)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    return PjmMarketReference.model_validate(data)
