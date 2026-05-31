"""Tier-0 hydrological simulation of the Lima municipal water loop.

BOSC's first three stages *deconstruct* records; this subpackage *forecasts* —
it models water, stormwater, and sewage as one closed flow loop on the Auglaize
and Ottawa rivers:

    Auglaize/Ottawa -> Lima reservoirs + WTP (abstraction) -> municipal +
    data-center demand (consumptive use) -> county/Lima WWTPs (return) ->
    Ottawa River (receiving).

The binding constraint is the Ottawa's (and its small tributaries') *low flow*:
abstraction upstream removes dilution water, WWTP discharge downstream adds load,
and stormwater surges perturb both — all squeezing the same assimilative capacity.

Design discipline (mirrors the rest of BOSC): every numeric input is a
:class:`~bosc.hydrology.model.ProvenancedValue` tagged ``document`` / ``connector``
/ ``assumption`` / ``derived`` so a result is self-auditing. Computed hydrology is
never written under ``data/extracted`` (reviewed transcription only). This is a
*Tier-0* model — simplified, screening-grade, and always labelled as such.

Increment 1 ships the water-balance spine + low-flow assimilative check, grounded
by live USGS streamflow. The SCS-CN stormwater solver and scenario diffing follow.
"""

from __future__ import annotations

from bosc.hydrology.assimilative import assimilative_findings, check_assimilative
from bosc.hydrology.balance import build_water_balance
from bosc.hydrology.model import (
    AssimilativeCheck,
    HydroFinding,
    Node,
    ProvenancedValue,
    WaterBalance,
    WaterBalanceNode,
)

__all__ = [
    "AssimilativeCheck",
    "HydroFinding",
    "Node",
    "ProvenancedValue",
    "WaterBalance",
    "WaterBalanceNode",
    "assimilative_findings",
    "build_water_balance",
    "check_assimilative",
]
