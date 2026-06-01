"""Tier-1 SWMM escalation: detention sizing + sanitary wet-weather surcharge.

Runs the real EPA SWMM5 engine on the campus footprint under the design storm to
answer two questions Tier-0 only approximated:

* **Detention sizing** — bisect the basin's bottom-orifice diameter until the
  released post-development peak matches the pre-development peak (the regulatory
  "no net increase" rule); report the storage volume that requires.
* **Sanitary surcharge** — the storm-driven wet-weather peak (dry-weather base +
  RDII) versus each plant's documented peak hydraulic capacity.

Everything degrades gracefully if the SWMM engine is unavailable.
"""

from __future__ import annotations

from bosc.config import Settings, get_settings
from bosc.hydrology.model import (
    DetentionDesign,
    HydroFinding,
    ProvenancedValue,
    SanitaryBasis,
    SanitarySurcharge,
    Tier1Result,
)
from bosc.hydrology.stormwater import _parcels_path
from bosc.hydrology.swmm import engine, inp
from bosc.hydrology.units import cfs_to_mgd
from bosc.logging import get_logger

log = get_logger(__name__)

# Land-cover imperviousness (assumptions): cropland vs near-impervious campus.
_PRE_IMPERV = 5.0
_POST_IMPERV = 90.0
# Detention basin footprint as a fraction of the campus, and max depth (assumptions).
_BASIN_FRAC = 0.04
_BASIN_DEPTH_FT = 12.0
# RDII fraction of rainfall entering the new sanitary system as inflow/infiltration.
_RDII_R = 0.05

# Documented WWTP peak hydraulic capacities (MGD), from our corpus.
_PLANT_CAPACITY: list[tuple[str, float, str]] = [
    ("American II WWTP", 3.6, "Ohio EPA fact sheet 2PH00006: peak hydraulic capacity 3.6 MGD"),
    ("Shawnee II WWTP", 12.6, "watch-items: Shawnee II Phase 2 peak 12.6 MGD (NPDES OH0023850)"),
]


def _design_depth_in(settings: Settings, *, return_period_yr: int, live: bool) -> float:
    from bosc.hydrology.stormwater import _resolve_storm

    return _resolve_storm(return_period_yr, settings=settings, live=live).depth.value


def _peak(area: float, imperv: float, depth: float, det: inp.DetentionGeom | None) -> float:
    text, outfall, orifice, storage = inp.stormwater_inp(
        area_acres=area, pct_imperv=imperv, depth_in=depth, detention=det
    )
    extra = {"links": [orifice], "storages": [storage]} if det else {}
    res = engine.simulate(text, nodes=[outfall], **extra)
    return res.node_peak_cfs.get(outfall, 0.0)


def _size_detention(area: float, depth: float, pre_peak: float) -> tuple[float, float, float]:
    """Bisect orifice diameter so the released peak ~= pre peak. Returns (diam, release, storage)."""
    basin_area = area * 43560.0 * _BASIN_FRAC
    lo, hi = 0.25, 12.0
    diam = hi
    release = pre_peak
    storage = 0.0
    for _ in range(10):
        diam = 0.5 * (lo + hi)
        det = inp.DetentionGeom(basin_area, _BASIN_DEPTH_FT, diam)
        text, outfall, _orifice, sto = inp.stormwater_inp(
            area_acres=area, pct_imperv=_POST_IMPERV, depth_in=depth, detention=det
        )
        res = engine.simulate(text, nodes=[outfall], storages=[sto])
        release = res.node_peak_cfs.get(outfall, 0.0)
        storage = res.storage_peak_acft.get(sto, 0.0)
        if release > pre_peak:  # too much release -> smaller orifice
            hi = diam
        else:
            lo = diam
    return diam, release, storage


def _build_surcharge(
    basis: SanitaryBasis | None, wet_peak_mgd: float, wet_pv: ProvenancedValue
) -> list[SanitarySurcharge]:
    """Judge the campus wet-weather contribution against each plant's documented headroom.

    With the cited basis, the comparison is campus contribution vs *wet-weather headroom*
    (peak hydraulic capacity - permitted average) — the margin the plant actually has above
    its dry-weather load. Without it, fall back to the legacy capacity comparison.
    """
    if basis is None:
        return [
            SanitarySurcharge(
                plant=name,
                capacity=ProvenancedValue.from_document(cap, "MGD", citation=cite),
                wet_weather_peak=wet_pv,
                exceeds=wet_peak_mgd > cap,
                margin_mgd=round(cap - wet_peak_mgd, 2),
            )
            for name, cap, cite in _PLANT_CAPACITY
        ]
    out: list[SanitarySurcharge] = []
    for p in basis.plants:
        headroom = p.headroom_mgd
        if p.peak_capacity is None or headroom is None:
            continue  # need a cited peak capacity to judge wet-weather headroom
        out.append(
            SanitarySurcharge(
                plant=p.plant,
                capacity=p.peak_capacity,
                avg_design_flow=p.avg_design_flow,
                peaking_factor=p.peaking_factor,
                headroom_mgd=headroom,
                wet_weather_peak=wet_pv,
                exceeds=wet_peak_mgd > headroom,
                margin_mgd=round(headroom - wet_peak_mgd, 2),
            )
        )
    return out


def run_tier1(
    *,
    return_period_yr: int = 25,
    settings: Settings | None = None,
    live: bool = True,
) -> Tier1Result:
    """Run the SWMM detention-sizing + sanitary-surcharge analyses."""
    settings = settings or get_settings()
    if not engine.swmm_available():
        return Tier1Result(available=False, note="SWMM engine unavailable (pyswmm did not load)")

    from bosc.hydrology import geo

    area = geo.parcels_total_acres(_parcels_path(settings), settings=settings)
    depth = _design_depth_in(settings, return_period_yr=return_period_yr, live=live)

    # --- Stormwater detention sizing ---
    pre_peak = _peak(area, _PRE_IMPERV, depth, None)
    post_peak = _peak(area, _POST_IMPERV, depth, None)
    diam, controlled, storage = _size_detention(area, depth, pre_peak)
    detention = DetentionDesign(
        pre_peak_cfs=round(pre_peak, 1),
        post_peak_cfs=round(post_peak, 1),
        controlled_peak_cfs=round(controlled, 1),
        orifice_diam_ft=round(diam, 2),
        required_storage_acft=round(storage, 1),
        basin_area_acres=round(area * _BASIN_FRAC, 1),
    )

    # --- Sanitary wet-weather surcharge ---
    # The campus dry-weather base is the documented FM-2 industrial discharge (cited via
    # the sanitary basis); RDII over the sewershed remains an assumption (no calibrated R).
    from bosc.hydrology.sanitary import load_sanitary_basis

    basis = load_sanitary_basis(settings=settings)
    campus_base = basis.campus_industrial.value if basis is not None else 2.5
    text, wwtp = inp.sanitary_inp(
        base_mgd=campus_base, sewershed_acres=area, rdii_r=_RDII_R, depth_in=depth
    )
    wet_peak_mgd = cfs_to_mgd(engine.simulate(text, nodes=[wwtp]).node_peak_cfs.get(wwtp, 0.0))
    wet_pv = ProvenancedValue.derived(
        round(wet_peak_mgd, 2),
        "MGD",
        citation=(
            f"SWMM RDII (R={_RDII_R}, assumption) over {area:.0f} ac + {campus_base:g} MGD "
            f"campus dry base (FM-2, document), {return_period_yr}-yr storm"
        ),
    )
    surcharge = _build_surcharge(basis, wet_peak_mgd, wet_pv)

    # Ground the detention result in the real 95% SPS drainage design, if extracted.
    from bosc.hydrology.stormplan import load_inventory

    inventory = load_inventory(settings=settings)

    log.info(
        "hydro.tier1",
        pre_peak=detention.pre_peak_cfs,
        post_peak=detention.post_peak_cfs,
        storage_acft=detention.required_storage_acft,
        wet_peak_mgd=round(wet_peak_mgd, 1),
    )
    return Tier1Result(
        available=True,
        detention=detention,
        surcharge=surcharge,
        inventory=inventory,
        sanitary_basis=basis,
    )


def tier1_findings(result: Tier1Result) -> list[HydroFinding]:
    """Render the Tier-1 result as findings."""
    if not result.available:
        return [HydroFinding("SWMM", "engine", False, result.note)]
    findings: list[HydroFinding] = []

    # Lead with the document-grounded drainage facts when the sheet has been extracted.
    if result.inventory is not None:
        from bosc.hydrology.stormplan import storm_plan_findings

        findings.extend(storm_plan_findings(result.inventory))

    d = result.detention
    if d is not None:
        # When the real 95% design shows no on-site storage, the SWMM-sized basin is the
        # *absent* control — say so, citing the sheet, rather than implying a redesign.
        absent = result.inventory is not None and not result.inventory.detention_shown
        frame = (
            f"the {result.inventory.phase} ({result.inventory.sheet_id}) provides no "
            f"on-site detention, so SWMM sizes the absent control: "
            if absent and result.inventory is not None
            else "SWMM: "
        )
        findings.append(
            HydroFinding(
                "BOSC campus",
                "detention-sizing",
                not absent,  # an absent required control is a gap, not an OK
                f"{frame}post-dev peak {d.post_peak_cfs:.0f} cfs vs pre-dev {d.pre_peak_cfs:.0f} cfs; "
                f"a {d.required_storage_acft:.0f} ac-ft basin (orifice {d.orifice_diam_ft:.1f} ft) "
                f"holds release to {d.controlled_peak_cfs:.0f} cfs",
            )
        )
    for s in result.surcharge:
        if s.headroom_mgd is not None and s.avg_design_flow is not None:
            pf = f", {s.peaking_factor.value:g}x peaking" if s.peaking_factor else ""
            detail = (
                f"campus wet-weather contribution {s.wet_weather_peak.value:.1f} MGD vs "
                f"{s.headroom_mgd:g} MGD wet-weather headroom "
                f"(peak {s.capacity.value:g} - avg {s.avg_design_flow.value:g} MGD{pf}, document) "
                f"({'EXCEEDS' if s.exceeds else 'within'}, margin {s.margin_mgd:+.1f} MGD)"
            )
        else:
            detail = (
                f"storm wet-weather peak {s.wet_weather_peak.value:.1f} MGD vs peak capacity "
                f"{s.capacity.value:g} MGD ({'EXCEEDS' if s.exceeds else 'within'}, "
                f"margin {s.margin_mgd:+.1f} MGD)"
            )
        findings.append(HydroFinding(s.plant, "wet-weather-surcharge", not s.exceeds, detail))

    # The decisive context is regulatory: the system is already under an SSO-elimination
    # mandate with active I/I remediation, so the documented headroom is effectively spent.
    b = result.sanitary_basis
    if b is not None and b.decree_note:
        findings.append(
            HydroFinding(
                "Allen County collection system",
                "sso-mandate",
                False,
                f"already under an SSO-elimination mandate (eliminate all bypassing by 2015) "
                f"with ${b.ii_remediation_musd.value:g}M of documented storm-water I/I remediation; "
                f"the campus load lands on a system with no wet-weather headroom to spare",
            )
        )
    return findings
