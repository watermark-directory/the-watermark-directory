"""Derive the grid foundation layer: serving utility + BA profile + campus load share.

Issue #94 (foundation of epic #93). Identifies the campus's electric-service chain
(cited, not asserted), assembles the EIA utility/BA profile, and expresses the campus
load — the first-class ``facility_draw`` from :mod:`bosc.facility.power` (issue #87) —
as a provenance-tagged share of the serving utility's, the balancing authority's, and
the state's retail load.

Data discipline (epic #93): the serving-utility identification is grounded in the
committed corpus (the relator data appendix references the AEP Ohio tariff for this
campus; the Allen County commissioners' minutes reference local AEP service), with the
EIA-861 service territory / PUCO map named as the formal confirmation source. All three
load denominators are connector-sourced: the Ohio state-retail figure from EIA (shared
with #91), the AEP-Ohio per-utility retail from the EIA-861 bulk "Sales to Ultimate
Customers" file (:mod:`bosc.grid.eia861`), and the PJM annual demand from EIA-930
(:func:`bosc.grid.interchange.fetch_ba_annual_load`). See ``data/reference/eia/README.md``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.config import Settings, get_settings
from bosc.economics.energy import load_consumer_energy
from bosc.facility.power import derive_power_basis
from bosc.grid.eia861 import fetch_utility_retail
from bosc.grid.interchange import fetch_ba_annual_load
from bosc.grid.model import (
    BalancingAuthorityProfile,
    CitedFact,
    GridLoadShare,
    GridProfile,
    ServingUtility,
)
from bosc.hydrology.model import ProvenancedValue
from bosc.logging import get_logger

log = get_logger(__name__)

_HOURS_PER_YEAR = 8760.0
_LOAD_FACTOR = 0.9  # data centers run near-flat (shared convention with #91)
_LOAD_FACTOR_CITE = "data-center capacity utilization ~0.9 (near-flat 24x7); assumption (cf. #91)"

# --- Serving-utility identification citations (corpus + authoritative) --------
_APPENDIX = (
    "data/extracted/legal/select-committee-2026/relator-testimony/bosc-data-appendix-2026-06-01.md"
)
_UTILITY_CITE = (
    f"relator data appendix ({_APPENDIX}): the 25 MW threshold 'matches the AEP Ohio "
    "tariff'; corroborated by Allen County commissioners' minutes (local AEP 3-phase "
    "service, Res #974-25). Formal confirmation: EIA-861 service territory / PUCO map."
)

# The AEP-Ohio (EIA-861 per-utility) and PJM (EIA-930 annual) figures are now LIVE
# connector pulls — fetch_utility_retail (bosc.grid.eia861) + fetch_ba_annual_load
# (bosc.grid.interchange). Only the Ohio state-retail fallback stays a transcribed const.
_OH_STATE_RETAIL_GWH = 149_003.0
_OH_STATE_CITE = "EIA ELEC.SALES.OH-ALL.A 2023 (Ohio total retail electricity sales)"


def _serving_utility() -> ServingUtility:
    return ServingUtility(
        utility=CitedFact(
            value="AEP Ohio (Ohio Power Company)",
            source="document",
            citation=_UTILITY_CITE,
            confidence="high",
        ),
        holding_company=CitedFact(
            value="American Electric Power (AEP)",
            source="reference",
            citation="AEP Ohio is the Ohio operating company of American Electric Power",
            confidence="high",
        ),
        balancing_authority=CitedFact(
            value="PJM Interconnection",
            source="reference",
            citation="AEP's Ohio (AEP/APS) transmission zone is within the PJM RTO footprint",
            confidence="high",
        ),
        rto=CitedFact(
            value="PJM Interconnection (RTO/ISO)",
            source="reference",
            citation="PJM is the FERC-jurisdictional wholesale-market RTO for AEP Ohio",
            confidence="high",
        ),
        retail_regulator=CitedFact(
            value="Public Utilities Commission of Ohio (PUCO)",
            source="reference",
            citation="Ohio retail electric service is PUCO-regulated (intrastate)",
            confidence="high",
        ),
        note=(
            "Serving utility is corpus-grounded (AEP Ohio tariff referenced for this "
            "campus); RTO=PJM is authoritative. The retail service-territory boundary is "
            "formally confirmed against the EIA-861 territory file / PUCO map (#94)."
        ),
    )


def _state_retail_gwh(settings: Settings) -> ProvenancedValue:
    """Ohio total retail sales from the committed #91 EIA dataset (connector), or a
    transcribed reference fallback. EIA 'million kWh' is numerically GWh.
    """
    costs = load_consumer_energy(settings.reference_dir)
    if costs is not None:
        sales = costs.by_metric("electricity", "sales")
        if sales is not None:
            return ProvenancedValue.from_connector(
                round(sales.value.value, 1),
                "GWh/yr",
                citation=f"EIA {sales.series_id} ({sales.period}); shared with #91",
            )
    return ProvenancedValue.from_reference(_OH_STATE_RETAIL_GWH, "GWh/yr", citation=_OH_STATE_CITE)


def derive_grid_profile(*, settings: Settings | None = None) -> GridProfile:
    """Assemble the serving utility, the EIA utility/BA profile, and the campus load share."""
    settings = settings or get_settings()
    power = derive_power_basis(settings=settings)

    draw_mw = power.facility_draw.value
    consumption_gwh = draw_mw * _HOURS_PER_YEAR * _LOAD_FACTOR / 1000.0  # MWh -> GWh

    # Live connector pulls (#94/#120): AEP-Ohio per-utility EIA-861 + PJM annual EIA-930.
    utility_profile = fetch_utility_retail(settings=settings)
    utility_retail = utility_profile.retail_sales_gwh
    ba_load = fetch_ba_annual_load(settings=settings)
    state_retail = _state_retail_gwh(settings)

    def _share(denom: float) -> float:
        return consumption_gwh / denom * 100.0 if denom else 0.0

    load_share = GridLoadShare(
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
        utility_retail_gwh=utility_retail,
        ba_load_gwh=ba_load,
        state_retail_gwh=state_retail,
        share_of_utility_pct=ProvenancedValue.derived(
            round(_share(utility_retail.value), 2),
            "percent",
            citation=f"campus {consumption_gwh:.0f} GWh / AEP Ohio {utility_retail.value:,.0f} GWh "
            f"(EIA-861 {settings.eia861_year} per-utility)",
        ),
        share_of_ba_pct=ProvenancedValue.derived(
            round(_share(ba_load.value), 3),
            "percent",
            citation=f"campus {consumption_gwh:.0f} GWh / PJM {ba_load.value:,.0f} GWh "
            "(EIA-930 annual demand)",
        ),
        share_of_state_pct=ProvenancedValue.derived(
            round(_share(state_retail.value), 2),
            "percent",
            citation=f"campus {consumption_gwh:.0f} GWh / Ohio {state_retail.value:.0f} GWh",
        ),
    )

    log.info(
        "grid.profile",
        utility="AEP Ohio",
        ba="PJM",
        consumption_gwh=round(consumption_gwh, 1),
        share_utility_pct=load_share.share_of_utility_pct.value,
    )
    return GridProfile(
        serving_utility=_serving_utility(),
        utility_profile=utility_profile,
        ba_profile=BalancingAuthorityProfile(
            ba="PJM Interconnection",
            eia_source="EIA-930 daily demand sum, annual (connector)",
            annual_load_gwh=ba_load,
        ),
        load_share=load_share,
        note=(
            "Grid foundation layer (#94). The state, AEP-Ohio, and PJM denominators are "
            "now all connector-sourced — Ohio retail from EIA (shared with #91), AEP-Ohio "
            "retail from the EIA-861 per-utility file, and PJM annual demand from EIA-930. "
            "The campus is a single load equal to a material fraction of its serving "
            "utility's entire retail sales."
        ),
    )


def _reference_path(reference_dir: Path) -> Path:
    return reference_dir / "eia" / "grid-profile.yaml"


def write_grid_profile(profile: GridProfile, *, settings: Settings | None = None) -> str:
    """Persist the grid profile as committed reference YAML; return the path."""
    settings = settings or get_settings()
    path = _reference_path(settings.reference_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(profile.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    log.info("grid.profile.wrote", path=str(path))
    return str(path)


def load_grid_profile(reference_dir: Path) -> GridProfile | None:
    """Read the committed grid-profile YAML, or ``None`` if absent."""
    path = _reference_path(reference_dir)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    return GridProfile.model_validate(data)
