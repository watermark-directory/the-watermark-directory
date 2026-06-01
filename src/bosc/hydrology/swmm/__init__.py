"""Tier-1 escalation: the EPA SWMM5 engine (via pyswmm).

Tier-0 (``bosc.hydrology.solver``) is a lumped SCS screening method. Tier-1 runs
the real EPA Stormwater Management Model — dynamic-wave routing through a defined
network — to answer questions Tier-0 only approximates: the **detention volume**
that holds the post-development peak to the pre-development rate, and the
**wet-weather surcharge** of storm-driven inflow & infiltration on the sanitary
plants.

The SWMM engine is a native extension that may be unavailable (not installed, or
blocked by macOS hardened-runtime on some wheels). Everything here degrades
gracefully: :func:`engine.swmm_available` probes in a subprocess, and the pipeline
returns a clear "unavailable" result rather than crashing. Network and hydraulic
parameters are **assumptions** (we lack the as-built drainage geometry) — the
footprint, design storm, and plant capacities remain document/connector-sourced.
"""

from __future__ import annotations

from bosc.hydrology.swmm.engine import SwmmResult, simulate, swmm_available

__all__ = ["SwmmResult", "simulate", "swmm_available"]
