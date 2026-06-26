"""Typed models for the Tier-0 hydrology subsystem.

Unlike the extraction models in :mod:`bosc.models` (``extra="allow"`` because the
LLM emits unanticipated keys), these are **computed by our own code**, so they use
``extra="forbid"`` to catch bugs early.

The cornerstone is :class:`ProvenancedValue`: every number that enters the water
balance carries where it came from, so a result is self-auditing. The ``source``
tag maps onto the dossier's evidence discipline:

    document, connector  ->  [verified]   (read from a record or a live gauge)
    assumption, derived  ->  [inference]  (asserted, or computed from the above)

The models are grouped into cluster modules (``_core``, ``_routed``, ``_supply``,
``_lowflow``, ``_stormwater``, ``_cooling``, ``_sanitary``, ``_findings``) and
re-exported here. :mod:`bosc.hydrology.model` (singular) re-exports this package for
back-compat; new code may import from either.
"""

from __future__ import annotations

from bosc.hydrology.models._cooling import (
    CoolingBasis as CoolingBasis,
)
from bosc.hydrology.models._cooling import (
    MonthlyWithdrawal as MonthlyWithdrawal,
)
from bosc.hydrology.models._cooling import (
    Scenario as Scenario,
)
from bosc.hydrology.models._cooling import (
    ScenarioDiff as ScenarioDiff,
)
from bosc.hydrology.models._cooling import (
    ScenarioResult as ScenarioResult,
)
from bosc.hydrology.models._cooling import (
    SeasonalWithdrawal as SeasonalWithdrawal,
)
from bosc.hydrology.models._core import (
    Node as Node,
)
from bosc.hydrology.models._core import (
    NodeRole as NodeRole,
)
from bosc.hydrology.models._core import (
    ProvenancedValue as ProvenancedValue,
)
from bosc.hydrology.models._core import (
    SourceKind as SourceKind,
)
from bosc.hydrology.models._core import (
    WaterBalance as WaterBalance,
)
from bosc.hydrology.models._core import (
    WaterBalanceNode as WaterBalanceNode,
)
from bosc.hydrology.models._findings import (
    HydroFinding as HydroFinding,
)
from bosc.hydrology.models._lowflow import (
    DILUTION_TIGHT as DILUTION_TIGHT,
)
from bosc.hydrology.models._lowflow import (
    DILUTION_VIOLATION as DILUTION_VIOLATION,
)
from bosc.hydrology.models._lowflow import (
    AnnualMinimum as AnnualMinimum,
)
from bosc.hydrology.models._lowflow import (
    AssimilativeCheck as AssimilativeCheck,
)
from bosc.hydrology.models._lowflow import (
    Flag as Flag,
)
from bosc.hydrology.models._lowflow import (
    LowFlowFrequency as LowFlowFrequency,
)
from bosc.hydrology.models._lowflow import (
    LowFlowStatistic as LowFlowStatistic,
)
from bosc.hydrology.models._routed import (
    NetworkNode as NetworkNode,
)
from bosc.hydrology.models._routed import (
    NetworkNodeKind as NetworkNodeKind,
)
from bosc.hydrology.models._routed import (
    NetworkTheory as NetworkTheory,
)
from bosc.hydrology.models._routed import (
    ReachFlow as ReachFlow,
)
from bosc.hydrology.models._routed import (
    RoutedNetwork as RoutedNetwork,
)
from bosc.hydrology.models._routed import (
    RoutedNetworkDiff as RoutedNetworkDiff,
)
from bosc.hydrology.models._sanitary import (
    DetentionDesign as DetentionDesign,
)
from bosc.hydrology.models._sanitary import (
    MaumeeTmdl as MaumeeTmdl,
)
from bosc.hydrology.models._sanitary import (
    SanitaryBasis as SanitaryBasis,
)
from bosc.hydrology.models._sanitary import (
    SanitaryPlant as SanitaryPlant,
)
from bosc.hydrology.models._sanitary import (
    SanitarySurcharge as SanitarySurcharge,
)
from bosc.hydrology.models._sanitary import (
    StormPlanInventory as StormPlanInventory,
)
from bosc.hydrology.models._sanitary import (
    SwmmDeck as SwmmDeck,
)
from bosc.hydrology.models._sanitary import (
    Tier1Result as Tier1Result,
)
from bosc.hydrology.models._sanitary import (
    TmdlWla as TmdlWla,
)
from bosc.hydrology.models._stormwater import (
    CampusDischargeScreen as CampusDischargeScreen,
)
from bosc.hydrology.models._stormwater import (
    DesignStorm as DesignStorm,
)
from bosc.hydrology.models._stormwater import (
    DischargePeak as DischargePeak,
)
from bosc.hydrology.models._stormwater import (
    Hydrograph as Hydrograph,
)
from bosc.hydrology.models._stormwater import (
    OutfallCapacity as OutfallCapacity,
)
from bosc.hydrology.models._stormwater import (
    RoundaboutFlow as RoundaboutFlow,
)
from bosc.hydrology.models._stormwater import (
    RoundaboutStormPeak as RoundaboutStormPeak,
)
from bosc.hydrology.models._stormwater import (
    SiteFootprint as SiteFootprint,
)
from bosc.hydrology.models._stormwater import (
    StormRunoff as StormRunoff,
)
from bosc.hydrology.models._supply import (
    DroughtDrawdown as DroughtDrawdown,
)
from bosc.hydrology.models._supply import (
    PumpStation as PumpStation,
)
from bosc.hydrology.models._supply import (
    RefillAdequacy as RefillAdequacy,
)
from bosc.hydrology.models._supply import (
    Reservoir as Reservoir,
)
from bosc.hydrology.models._supply import (
    RiverFlowStat as RiverFlowStat,
)
from bosc.hydrology.models._supply import (
    WaterBudget as WaterBudget,
)
from bosc.hydrology.models._supply import (
    WaterSupplySystem as WaterSupplySystem,
)

__all__ = [
    "DILUTION_TIGHT",
    "DILUTION_VIOLATION",
    "AnnualMinimum",
    "AssimilativeCheck",
    "CampusDischargeScreen",
    "CoolingBasis",
    "DesignStorm",
    "DetentionDesign",
    "DischargePeak",
    "DroughtDrawdown",
    "Flag",
    "HydroFinding",
    "Hydrograph",
    "LowFlowFrequency",
    "LowFlowStatistic",
    "MaumeeTmdl",
    "MonthlyWithdrawal",
    "NetworkNode",
    "NetworkNodeKind",
    "NetworkTheory",
    "Node",
    "NodeRole",
    "OutfallCapacity",
    "ProvenancedValue",
    "PumpStation",
    "ReachFlow",
    "RefillAdequacy",
    "Reservoir",
    "RiverFlowStat",
    "RoundaboutFlow",
    "RoundaboutStormPeak",
    "RoutedNetwork",
    "RoutedNetworkDiff",
    "SanitaryBasis",
    "SanitaryPlant",
    "SanitarySurcharge",
    "Scenario",
    "ScenarioDiff",
    "ScenarioResult",
    "SeasonalWithdrawal",
    "SiteFootprint",
    "SourceKind",
    "StormPlanInventory",
    "StormRunoff",
    "SwmmDeck",
    "Tier1Result",
    "TmdlWla",
    "WaterBalance",
    "WaterBalanceNode",
    "WaterBudget",
    "WaterSupplySystem",
]
