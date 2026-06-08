"""Assemble the municipal water-balance loop from cited records + live gauges.

The spine is the four county/Lima WWTP discharges (document-sourced design flows
from ``watch-items.geojson``), each routed to its cited receiving water. The
forcing function — the BOSC data-center campus — contributes its documented FM-2
discharge plus an *assumption* knob for consumptive cooling demand. The abstraction
end is grounded with *live* NWIS river flow when available.

Everything the headline assimilative check depends on (WWTP discharge -> named
receiving water) is ``document``-sourced; the abstraction/demand context is clearly
``connector``/``assumption``-tagged so it never masquerades as fact.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bosc.config import Settings, get_settings
from bosc.hydrology.connectors.nwis import DISCHARGE_CFS, fetch_streamflow
from bosc.hydrology.model import Node, ProvenancedValue, WaterBalance, WaterBalanceNode
from bosc.hydrology.routing import RoutingTable, load_routing
from bosc.hydrology.units import mgd_to_cfs
from bosc.logging import get_logger

log = get_logger(__name__)

# Fallback receiving waters per plant, read from the Ohio EPA NPDES fact sheets in
# our corpus. The authoritative source is now data/reference/hydrology/routing.yaml
# (loaded into a RoutingTable); this dict is only used if that file is absent, so the
# existing balance never breaks during rollout.
_PLANT_RECEIVING: dict[str, tuple[str, str]] = {
    "watch-american-ii-wwtp": ("Dug Run", "Ohio EPA fact sheet 2PH00006 (American II WWTP)"),
    "watch-american-bath-wwtp": ("Pike Run", "Ohio EPA fact sheet 2PH00007 (American Bath WWTP)"),
    "watch-shawnee-ii-wwtp": ("Ottawa River", "Ohio EPA fact sheet 2PK00002 (Shawnee II WWTP)"),
}

# The Ottawa-at-Lima gauge — the abstraction/dilution reach the WWTPs return to.
_OTTAWA_AT_LIMA = "04187100"

_MGD_RE = re.compile(r"(\d+(?:\.\d+)?)\s*MGD", re.IGNORECASE)


def _features(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("features", []) if isinstance(data, dict) else []


def _default_watch_items(settings: Settings) -> Path:
    return settings.data_dir / "reference" / "periplus" / "watch-items.geojson"


def _design_mgd(summary: str) -> tuple[float | None, bool]:
    """First design flow (MGD) stated in a summary; flag if more than one (expansion)."""
    found = [float(m) for m in _MGD_RE.findall(summary)]
    if not found:
        return None, False
    return found[0], len(found) > 1


def _receiving_for(fid: str, routing: RoutingTable | None) -> tuple[str | None, str]:
    """Resolve a WWTP's receiving water from the routing table, falling back to the dict."""
    if routing is not None and fid in routing.wwtp_receiving:
        return routing.receiving_for(fid)
    return _PLANT_RECEIVING.get(fid, (None, ""))


def _surface_bosc_routing(routing: RoutingTable | None, warnings: list[str]) -> None:
    """Record where BOSC's wastewater goes — and flag theorized routes as excluded.

    Encodes the standing requirement: BOSC output is routed to Lima (FM-2) and the
    American plants (FM-1) only; Shawnee II's FM-3 is theorized and held out of the
    balance, so its lack of a known route is explicit rather than silently assumed.
    """
    if routing is None:
        return
    for route in routing.confirmed_bosc_routes():
        log.info("hydro.bosc_routing.confirmed", via=route.via, to=route.to)
    for route in routing.theorized_bosc_routes():
        warnings.append(
            f"BOSC routing via {route.via} to {', '.join(route.to)} is THEORIZED "
            "(unconfirmed) — excluded from the balance; Shawnee II has no known BOSC routing."
        )


def _wwtp_nodes(
    path: Path, warnings: list[str], routing: RoutingTable | None
) -> list[WaterBalanceNode]:
    nodes: list[WaterBalanceNode] = []
    for feat in _features(path):
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        fid = str(props.get("id", ""))
        title = str(props.get("title", ""))
        is_wwtp = props.get("status") == "bosc_fm1_receiver" or title.endswith("WWTP")
        if not is_wwtp or geom.get("type") != "Point":
            continue

        receiving, recv_cite = _receiving_for(fid, routing)
        mgd, expanding = _design_mgd(str(props.get("summary", "")))
        lon, lat = geom["coordinates"][0], geom["coordinates"][1]
        node = Node(
            id=fid or title,
            name=title,
            role="wwtp",
            receiving_water=receiving,
            lat=float(lat),
            lon=float(lon),
        )
        return_flow = None
        if mgd is not None:
            return_flow = ProvenancedValue.from_document(
                mgd_to_cfs(mgd),
                "cfs",
                citation=f"{fid} ({mgd} MGD design)",
            )
            if expanding:
                warnings.append(
                    f"{title}: summary states a flow expansion; used the first value ({mgd} MGD)."
                )
        else:
            warnings.append(f"{title}: no design flow found in watch-items summary.")
        if receiving is None:
            warnings.append(
                f"{title}: receiving water not mapped; assimilative check will skip it."
            )
        else:
            log.info("hydro.wwtp", plant=title, receiving=receiving, citation=recv_cite)
        nodes.append(WaterBalanceNode(node=node, return_flow=return_flow))
    return nodes


def _campus_node(path: Path, warnings: list[str]) -> WaterBalanceNode:
    """The BOSC data-center campus: documented FM-2 discharge + an assumption demand knob."""
    fm2_mgd: float | None = None
    for feat in _features(path):
        props = feat.get("properties") or {}
        if props.get("id") == "bosc-fm2":
            fm2_mgd, _ = _design_mgd(str(props.get("summary", "")))
            break

    return_flow = None
    if fm2_mgd is not None:
        return_flow = ProvenancedValue.from_document(
            mgd_to_cfs(fm2_mgd),
            "cfs",
            citation=f"bosc-fm2 ({fm2_mgd} MGD industrial discharge to Lima)",
        )
    else:
        warnings.append("BOSC campus: FM-2 discharge not found in watch-items.")

    # Cooling demand and consumptive loss are NOT in any record — the dominant
    # uncertainty, carried as an explicit assumption knob (the scenario lever).
    consumptive = ProvenancedValue.assume(
        0.0,
        "cfs",
        why="data-center evaporative cooling consumptive loss — design basis TBD; "
        "placeholder zero until a cooling spec is sourced (Increment 3 scenario knob)",
    )
    warnings.append(
        "BOSC campus consumptive cooling demand is an unsourced assumption (0 cfs placeholder)."
    )
    node = Node(id="bosc-campus", name="BOSC data-center campus", role="demand")
    return WaterBalanceNode(node=node, return_flow=return_flow, consumptive_use=consumptive)


def _abstraction_node(settings: Settings, warnings: list[str]) -> WaterBalanceNode:
    """Lima WTP intake reach, grounded with live Ottawa-at-Lima streamflow when available."""
    node = Node(
        id="lima-wtp",
        name="Lima WTP intake (Ottawa/Auglaize)",
        role="abstraction",
        receiving_water="Ottawa River",
    )
    inflow: ProvenancedValue | None = None
    try:
        readings = fetch_streamflow(sites=[_OTTAWA_AT_LIMA], settings=settings)
        flow = next(
            (r for r in readings if r.parameter_cd == DISCHARGE_CFS and r.value is not None),
            None,
        )
        if flow is not None and flow.value is not None:
            inflow = ProvenancedValue.from_connector(
                flow.value, "cfs", citation=f"NWIS {flow.site_no} ({flow.name})", asof=flow.datetime
            )
    except Exception as exc:
        warnings.append(f"live Ottawa streamflow unavailable: {type(exc).__name__}")
    warnings.append(
        "Lima WTP withdrawal rate is not documented; abstraction shown as river-flow context only."
    )
    return WaterBalanceNode(node=node, inflow=inflow)


def build_water_balance(
    *,
    settings: Settings | None = None,
    watch_items_path: Path | None = None,
    live: bool = True,
) -> WaterBalance:
    """Assemble the source -> use -> WWTP -> receiving loop.

    ``live=False`` skips the NWIS abstraction grounding (a pure document/assumption
    balance); ``live=True`` adds the gauge reading (offline-aware via the cache).
    """
    settings = settings or get_settings()
    path = watch_items_path or _default_watch_items(settings)
    warnings: list[str] = []

    routing = load_routing(settings=settings)
    nodes = _wwtp_nodes(path, warnings, routing)
    _surface_bosc_routing(routing, warnings)
    nodes.append(_campus_node(path, warnings))
    if live:
        nodes.append(_abstraction_node(settings, warnings))

    log.info("hydro.balance", nodes=len(nodes), wwtp=sum(1 for n in nodes if n.node.role == "wwtp"))
    return WaterBalance(nodes=nodes, warnings=warnings)
