"""Build EPA SWMM5 ``.inp`` models from our data.

Two models, both driven by the SCS Type-II design storm as a rainfall timeseries:

* :func:`stormwater_inp` — the campus subcatchment routed to an outfall, optionally
  through a detention basin (storage node + bottom orifice) for the post-development
  case. Sizing the orifice controls the released peak.
* :func:`sanitary_inp` — a sanitary junction carrying the dry-weather base flow plus
  rainfall-derived inflow & infiltration (RDII, an RTK unit hydrograph) to a WWTP
  outfall, for the wet-weather surcharge check.

Network and hydraulic parameters (widths, slopes, Manning's n, infiltration, RDII
R-T-K, basin geometry) are screening **assumptions** — we lack the as-built drainage
network. The footprint area and storm depth are document/connector-sourced.
"""

from __future__ import annotations

from dataclasses import dataclass

from bosc.hydrology.solver.rainfall import scs_type_ii_hyetograph

_SQFT_PER_ACRE = 43560.0


@dataclass(frozen=True)
class DetentionGeom:
    """Detention basin: a flat storage of ``area`` with a circular bottom orifice."""

    basin_area_ft2: float
    max_depth_ft: float
    orifice_diam_ft: float


def _hhmm(hours: float) -> str:
    total_min = round(hours * 60.0)
    return f"{total_min // 60:d}:{total_min % 60:02d}"


def _hyetograph_lines(ts_name: str, depth_in: float, dt_hr: float) -> list[str]:
    """SWMM TIMESERIES lines of rainfall intensity (in/hr) for the design storm."""
    _, _, incremental = scs_type_ii_hyetograph(depth_in, dt_hr=dt_hr)
    lines = []
    for i, inc in enumerate(incremental.tolist()):
        intensity = inc / dt_hr  # in per hr over this interval
        lines.append(f"{ts_name}  {_hhmm(i * dt_hr)}  {intensity:.4f}")
    return lines


def _header(end_hr: float, dt_hr: float, *, infiltration: str = "HORTON") -> str:
    rg_interval = _hhmm(dt_hr)
    return f"""[OPTIONS]
FLOW_UNITS           CFS
INFILTRATION         {infiltration}
FLOW_ROUTING         DYNWAVE
START_DATE           01/01/2026
START_TIME           00:00:00
END_DATE             01/0{1 + int(end_hr // 24)}/2026
END_TIME             {_hhmm(end_hr % 24)}:00
REPORT_STEP          00:05:00
WET_STEP             00:01:00
DRY_STEP             00:05:00
ROUTING_STEP         0:00:15
ALLOW_PONDING        YES

[EVAPORATION]
CONSTANT             0.0

[RAINGAGES]
RG1 INTENSITY {rg_interval} 1.0 TIMESERIES TS1
"""


# Horton infiltration for Allen County HSG-C soils (assumption, in/hr + hr).
_HORTON = "3.0 0.1 4.0 7 0"


def stormwater_inp(
    *,
    area_acres: float,
    pct_imperv: float,
    depth_in: float,
    detention: DetentionGeom | None = None,
    dt_hr: float = 0.1,
    end_hr: float = 30.0,
) -> tuple[str, str, str, str]:
    """Build a stormwater ``.inp``. Returns (text, outfall, orifice_link, storage_node)."""
    width = (area_acres * _SQFT_PER_ACRE) ** 0.5  # square-catchment width (ft)
    outfall = "OUT1"
    storage = "DET"
    orifice = "OR1"
    drains_to = storage if detention else outfall

    inp = _header(end_hr, dt_hr)
    inp += f"""
[SUBCATCHMENTS]
S1 RG1 {drains_to} {area_acres:.2f} {pct_imperv:.1f} {width:.1f} 1.0 0

[SUBAREAS]
S1 0.015 0.10 0.05 0.05 25 OUTLET

[INFILTRATION]
S1 {_HORTON}

[OUTFALLS]
{outfall} 0 FREE NO
"""
    if detention:
        inp += f"""
[STORAGE]
{storage} 0 {detention.max_depth_ft:.1f} 0 FUNCTIONAL 0 0 {detention.basin_area_ft2:.1f}

[ORIFICES]
{orifice} {storage} {outfall} BOTTOM 0 0.65 NO

[XSECTIONS]
{orifice} CIRCULAR {detention.orifice_diam_ft:.3f} 0 0 0
"""
    inp += "\n[TIMESERIES]\n" + "\n".join(_hyetograph_lines("TS1", depth_in, dt_hr)) + "\n"
    inp += "\n[REPORT]\nINPUT NO\nNODES ALL\nLINKS ALL\n"
    return inp, outfall, orifice, storage


def sanitary_inp(
    *,
    base_mgd: float,
    sewershed_acres: float,
    rdii_r: float,
    depth_in: float,
    dt_hr: float = 0.1,
    end_hr: float = 36.0,
) -> tuple[str, str]:
    """Build a sanitary ``.inp`` with DWF + RDII. Returns (text, wwtp_outfall)."""
    base_cfs = base_mgd * 1.547
    wwtp = "WWTP"
    junction = "J1"

    inp = _header(end_hr, dt_hr)
    inp += f"""
[JUNCTIONS]
{junction} 0 10 0 0 0

[OUTFALLS]
{wwtp} 0 FREE NO

[CONDUITS]
C1 {junction} {wwtp} 200 0.013 0 0 0 0

[XSECTIONS]
C1 CIRCULAR 6.5 0 0 0

[DWF]
{junction} FLOW {base_cfs:.4f}

[HYDROGRAPHS]
UH1 RG1
UH1 All SHORT {rdii_r:.3f} 1.0 2.0
UH1 All MEDIUM {rdii_r / 2:.3f} 3.0 2.0

[RDII]
{junction} UH1 {sewershed_acres:.2f}
"""
    inp += "\n[TIMESERIES]\n" + "\n".join(_hyetograph_lines("TS1", depth_in, dt_hr)) + "\n"
    inp += "\n[REPORT]\nINPUT NO\nNODES ALL\nLINKS ALL\n"
    return inp, wwtp
