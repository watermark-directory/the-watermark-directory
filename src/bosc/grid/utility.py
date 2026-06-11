"""Derive the grid foundation layer: serving utility + BA profile + campus load share.

Issue #94 (foundation of epic #93). Identifies the campus's electric-service chain
(cited, not asserted), assembles the EIA utility/BA profile, and expresses the campus
load — the first-class ``facility_draw`` from :mod:`bosc.facility.power` (issue #87) —
as a provenance-tagged share of the serving utility's, the balancing authority's, and
the state's retail load.

Data discipline (epic #93): the serving-utility identification is grounded in the
committed corpus (the relator data appendix references the AEP Ohio tariff for this
campus; the Allen County commissioners' minutes reference local AEP service), with the
EIA-861 service territory / PUCO map named as the formal confirmation source. The EIA
state-retail figure is connector-sourced (shared with #91); the utility (EIA-861) and
BA (EIA-930) figures are transcribed published values, ``reference``-tagged and flagged
for verification (see ``data/reference/eia/README.md``).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.config import Settings, get_settings
from bosc.economics.energy import load_consumer_energy
from bosc.facility.power import derive_power_basis
from bosc.grid.model import (
    BalancingAuthorityProfile,
    CitedFact,
    GridLoadShare,
    GridProfile,
    ServingUtility,
    UtilityProfile,
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

# --- Transcribed EIA-861/930 reference figures (verify with a keyed/bulk pull) --
_AEP_RETAIL_GWH = 49000.0  # AEP Ohio (Ohio Power Co) ~2023 retail sales (EIA-861)
_AEP_CUSTOMERS = 1_500_000.0  # AEP Ohio retail customers (EIA-861)
_AEP_PRICE_CENTS = 12.8  # AEP Ohio all-sector average price (EIA-861)
_AEP_CITE = "EIA-861 2023, Ohio Power Company (AEP Ohio); transcribed published figure — verify"
_PJM_LOAD_GWH = 800_000.0  # PJM Interconnection ~2023 total annual load (EIA-930)
_PJM_CITE = "EIA-930 2023, PJM region total annual demand; transcribed published figure — verify"
# Fallback Ohio state retail if the committed #91 dataset is unavailable.
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

    utility_retail = ProvenancedValue.from_reference(
        _AEP_RETAIL_GWH, "GWh/yr", citation=_AEP_CITE, confidence="medium"
    )
    ba_load = ProvenancedValue.from_reference(
        _PJM_LOAD_GWH, "GWh/yr", citation=_PJM_CITE, confidence="medium"
    )
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
            citation=f"campus {consumption_gwh:.0f} GWh / AEP Ohio {utility_retail.value:.0f} GWh "
            "(EIA-861 transcribed; verify)",
            confidence="medium",
        ),
        share_of_ba_pct=ProvenancedValue.derived(
            round(_share(ba_load.value), 3),
            "percent",
            citation=f"campus {consumption_gwh:.0f} GWh / PJM {ba_load.value:.0f} GWh "
            "(EIA-930 transcribed; verify)",
            confidence="medium",
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
        utility_profile=UtilityProfile(
            utility="AEP Ohio (Ohio Power Company)",
            retail_sales_gwh=utility_retail,
            customers=ProvenancedValue.from_reference(
                _AEP_CUSTOMERS, "customers", citation=_AEP_CITE, confidence="medium"
            ),
            avg_price_cents_kwh=ProvenancedValue.from_reference(
                _AEP_PRICE_CENTS, "cents/kWh", citation=_AEP_CITE, confidence="medium"
            ),
        ),
        ba_profile=BalancingAuthorityProfile(ba="PJM Interconnection", annual_load_gwh=ba_load),
        load_share=load_share,
        note=(
            "Grid foundation layer (#94). The state share is connector-grounded (EIA, "
            "shared with #91); the AEP-Ohio and PJM figures are transcribed EIA-861/930 "
            "values flagged for verification. The campus is a single load equal to a "
            "material fraction of its serving utility's entire retail sales."
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
