"""A sourced cooling-water design basis for the data-center campus.

Replaces the bare "5 MGD, design basis TBD" assumption with a basis *derived* from
disclosed campus data, by two independent methods that bracket the demand:

* **Top-down (power x WUE).** The Ohio EPA air permit P0138965 lists 114 emergency
  generators at 2,750 ekW = ~313 MW backup; at hyperscale N+1 ratios that implies a
  ~250-300 MW IT load. Evaporative consumptive water = IT energy x a water-use
  effectiveness (WUE). This is the central estimate.
* **Bottom-up (blowdown x cycles).** The documented 2.5 MGD FM-2 industrial
  discharge (CMAR RFQ §A.6), if taken as cooling-tower blowdown at typical cycles of
  concentration, implies the evaporation upper bound (makeup = blowdown x CoC).

The two disagree by ~3x — FM-2 is not purely cooling blowdown — so we report the
range. The conclusion is robust to it: even the low estimate is tens of times the
Ottawa's 0.2 cfs 7Q10. Inputs are document/assumption-tagged; demands are derived.
"""

from __future__ import annotations

from watermark.config import Settings, get_settings
from watermark.hydrology.model import CoolingBasis, ProvenancedValue
from watermark.sites import active_profile

_L_PER_GAL = 3.785411784

# Disclosed / cited inputs.
_GENSET_COUNT = 114
_GENSET_MW = 2.75  # ekW each, per the air permit
_BACKUP_MW = _GENSET_COUNT * _GENSET_MW  # ~313 MW
_IT_LOAD_MW = 275.0  # midpoint of the 250-300 MW estimate (IT ~= backup at N+1)
_AIR_PERMIT_CITE = (
    "OEPA Air PTI P0138965 (Facility 0302022054), committed "
    "data/extracted/permits/4132514.epa.yaml (final, 2026-05-28): "
    "114 hall gensets x 2.75 ekW = ~313 MW backup; IT ~250-300 MW (N+1). "
    "Per-engine ekW is from the draft public notice (3987141/3987144) — engine "
    "size is CBI-redacted in the final permit under a formal Ohio EPA trade-secret "
    "grant (OAC 3745-49-03, 2025-10-08; data/extracted/permits/3859883.epa.yaml), "
    "which also withholds cooling-system flowrates."
)

_WUE_L_PER_KWH = 1.8  # evaporative hyperscale; Google fleet avg ~1.1, evaporative higher
_WUE_CITE = "evaporative-cooled hyperscale WUE ~1.8 L/kWh (Google fleet avg ~1.1; 36 cooling towers on the air permit)"

_CYCLES = 5.0  # cooling-tower cycles of concentration (typical 4-6)
_CYCLES_CITE = "cooling-tower cycles of concentration ~5 (typical 4-6)"

_FM2_BLOWDOWN_MGD = 2.5  # documented FM-2 industrial discharge, as a blowdown upper bound
_FM2_CITE = (
    "bosc-fm2 2.5 MGD industrial discharge (CMAR RFQ §A.6), taken as cooling blowdown upper bound"
)


def _consumptive_mgd_from_power(it_load_mw: float, wue_l_per_kwh: float) -> float:
    """Evaporative consumptive water (MGD) = IT energy x WUE."""
    liters_per_day = it_load_mw * 1_000.0 * 24.0 * wue_l_per_kwh  # kW x h/day x L/kWh
    return liters_per_day / _L_PER_GAL / 1_000_000.0


def derive_cooling_basis(
    settings: Settings | None = None,
    *,
    it_load_mw: float | None = None,
    blowdown_mgd: float | None = None,
    wue_l_per_kwh: float = _WUE_L_PER_KWH,
    cycles: float = _CYCLES,
) -> CoolingBasis:
    """Derive the cooling design basis from the active site's cited inputs (both methods).

    Per-site (#607): IT load, the blowdown cross-check, and their citations come from the
    active site's ``SiteProfile.facility`` (Lima = the air-permit basis; module constants are
    the last-resort fallback). The ``it_load_mw`` / ``blowdown_mgd`` keyword overrides still
    win, for sensitivity sweeps. A facility that discloses no blowdown uses the site's own
    power-derived consumptive as the high bound — so no Lima FM-2 figure leaks into another
    site's estimate.
    """
    settings = settings or get_settings()
    facility = active_profile(settings).facility

    if it_load_mw is None:
        it_load_mw = facility.it_load_mw if facility else _IT_LOAD_MW
    it_load_cite = facility.air_permit_citation if facility else _AIR_PERMIT_CITE
    if blowdown_mgd is None and facility is not None:
        blowdown_mgd = facility.blowdown_mgd
    blowdown_cite = (
        facility.blowdown_citation if (facility and facility.blowdown_citation) else _FM2_CITE
    )

    frac = (cycles - 1.0) / cycles  # evaporation / makeup
    consumptive_low = _consumptive_mgd_from_power(it_load_mw, wue_l_per_kwh)
    makeup = consumptive_low / frac if frac > 0 else consumptive_low
    if blowdown_mgd is not None:
        consumptive_high = blowdown_mgd * (cycles - 1.0)  # blowdown x (CoC-1) = evaporation
        high_cite = f"{blowdown_mgd:g} MGD blowdown x (CoC-1); {blowdown_cite}"
    else:
        # No disclosed discharge for this site — the power-method consumptive is the high bound.
        consumptive_high = consumptive_low
        high_cite = (
            f"{it_load_mw:g} MW x {wue_l_per_kwh:g} L/kWh (power x WUE; no disclosed blowdown)"
        )

    return CoolingBasis(
        it_load=ProvenancedValue.from_document(it_load_mw, "MW", citation=it_load_cite),
        wue=ProvenancedValue.assume(wue_l_per_kwh, "L/kWh", why=_WUE_CITE),
        cycles_of_concentration=ProvenancedValue.assume(cycles, "ratio", why=_CYCLES_CITE),
        consumptive_fraction=ProvenancedValue.derived(
            round(frac, 3), "fraction", citation=f"(CoC-1)/CoC at CoC={cycles:g}"
        ),
        makeup_demand=ProvenancedValue.derived(
            round(makeup, 2),
            "MGD",
            citation=f"{it_load_mw:g} MW x {wue_l_per_kwh:g} L/kWh / evap fraction",
        ),
        consumptive_low=ProvenancedValue.derived(
            round(consumptive_low, 2),
            "MGD",
            citation=f"{it_load_mw:g} MW x {wue_l_per_kwh:g} L/kWh (power x WUE)",
        ),
        consumptive_high=ProvenancedValue.derived(
            round(consumptive_high, 2),
            "MGD",
            citation=high_cite,
        ),
    )
