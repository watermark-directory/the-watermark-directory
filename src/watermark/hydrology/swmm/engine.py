"""Run an EPA SWMM5 model via pyswmm, with graceful degradation.

The native SWMM engine can fail to load (missing wheel, or macOS hardened-runtime
killing an ad-hoc-signed bundle with SIGKILL — uncatchable in-process). So we never
``import pyswmm`` at module load: :func:`swmm_available` probes it in a *subprocess*
(a SIGKILL there is observable, not fatal here), and :func:`simulate` imports lazily
only after a successful probe.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from watermark.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class SwmmResult:
    """Peaks/volumes from one SWMM run (empty + ``available=False`` if the engine is missing)."""

    available: bool
    node_peak_cfs: dict[str, float] = field(default_factory=dict)
    node_flood_acft: dict[str, float] = field(default_factory=dict)
    link_peak_cfs: dict[str, float] = field(default_factory=dict)
    storage_peak_acft: dict[str, float] = field(default_factory=dict)
    continuity_error_pct: float = 0.0
    note: str = ""


@lru_cache(maxsize=1)
def swmm_available() -> bool:
    """True if ``import pyswmm`` succeeds in a clean subprocess (cached)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", "import pyswmm"],
            capture_output=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        log.info("swmm.probe_failed", error=type(exc).__name__)
        return False
    ok = proc.returncode == 0
    if not ok:
        log.info("swmm.unavailable", returncode=proc.returncode)
    return ok


def engine_version() -> str:
    """The pyswmm version behind a run (for result provenance), or ``""`` if absent."""
    if not swmm_available():
        return ""
    try:
        import pyswmm  # lazy: only after the probe passed

        return f"pyswmm {pyswmm.__version__}"
    except Exception:  # pragma: no cover - defensive
        return "pyswmm (version unknown)"


def simulate(
    inp_text: str,
    *,
    nodes: list[str] | None = None,
    links: list[str] | None = None,
    storages: list[str] | None = None,
) -> SwmmResult:
    """Run a SWMM ``.inp`` and return peak inflows/flows for the named elements.

    Returns ``SwmmResult(available=False)`` if the engine cannot be loaded.
    """
    if not swmm_available():
        return SwmmResult(available=False, note="SWMM engine unavailable (pyswmm did not load)")

    from pyswmm import Links, Nodes, Simulation  # lazy: only after the probe passed

    nodes = nodes or []
    links = links or []
    storages = storages or []

    with tempfile.TemporaryDirectory() as tmp:
        inp_path = Path(tmp) / "model.inp"
        inp_path.write_text(inp_text, encoding="utf-8")
        node_peak: dict[str, float] = dict.fromkeys(nodes + storages, 0.0)
        link_peak: dict[str, float] = dict.fromkeys(links, 0.0)
        storage_peak: dict[str, float] = dict.fromkeys(storages, 0.0)

        with Simulation(str(inp_path)) as sim:
            node_objs = {n: Nodes(sim)[n] for n in node_peak}
            link_objs = {ln: Links(sim)[ln] for ln in links}
            for _ in sim:
                for n, obj in node_objs.items():
                    node_peak[n] = max(node_peak[n], obj.total_inflow)
                    if n in storage_peak:
                        # storage volume (ft^3) -> acre-feet
                        storage_peak[n] = max(storage_peak[n], obj.volume / 43560.0)
                for ln, obj in link_objs.items():
                    link_peak[ln] = max(link_peak[ln], abs(obj.flow))
            continuity = float(getattr(sim, "flow_routing_error", 0.0) or 0.0)

    return SwmmResult(
        available=True,
        node_peak_cfs=node_peak,
        link_peak_cfs=link_peak,
        storage_peak_acft=storage_peak,
        continuity_error_pct=continuity,
    )
