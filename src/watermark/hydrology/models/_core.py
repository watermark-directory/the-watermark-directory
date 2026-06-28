"""Core provenance + water-balance models for the Tier-0 hydrology subsystem.

The cornerstone is :class:`ProvenancedValue`: every number that enters the water
balance carries where it came from, so a result is self-auditing. The ``source``
tag maps onto the dossier's evidence discipline:

    document, connector  ->  [verified]   (read from a record or a live gauge)
    assumption, derived  ->  [inference]  (asserted, or computed from the above)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from watermark.provenance import SourceKind as SourceKind
from watermark.provenance import source_is_verified

NodeRole = Literal["abstraction", "demand", "wwtp", "receiving"]


class ProvenancedValue(BaseModel):
    """A single numeric quantity tagged with its provenance.

    Construct via the classmethods (:meth:`from_document`, :meth:`from_connector`,
    :meth:`assume`, :meth:`derived`) so the ``source`` tag is never forgotten.
    """

    model_config = ConfigDict(extra="forbid")

    value: float
    unit: str  # "cfs" | "MGD" | "sqmi" | "acre" | "in" | ...
    source: SourceKind
    citation: str | None = None  # rel_path, geojson feature id, NWIS site, or rationale
    confidence: Literal["high", "medium", "low"] = "medium"
    asof: str | None = None  # ISO datetime, for connector (live) values

    @classmethod
    def from_document(
        cls,
        value: float,
        unit: str,
        citation: str,
        *,
        confidence: Literal["high", "medium", "low"] = "high",
    ) -> ProvenancedValue:
        """A value read from a source record (cite the file / feature id)."""
        return cls(
            value=value, unit=unit, source="document", citation=citation, confidence=confidence
        )

    @classmethod
    def from_connector(
        cls,
        value: float,
        unit: str,
        citation: str,
        *,
        asof: str | None = None,
        confidence: Literal["high", "medium", "low"] = "high",
    ) -> ProvenancedValue:
        """A value fetched live from an external service (cite the site/endpoint)."""
        return cls(
            value=value,
            unit=unit,
            source="connector",
            citation=citation,
            confidence=confidence,
            asof=asof,
        )

    @classmethod
    def from_reference(
        cls,
        value: float,
        unit: str,
        citation: str,
        *,
        confidence: Literal["high", "medium", "low"] = "medium",
    ) -> ProvenancedValue:
        """A value from committed authoritative external reference data.

        Distinct from a record about *this* facility (``document``) and from an
        asserted modeling input (``assumption``): a published spec / table vendored
        under ``data/reference`` (e.g. an accelerator datasheet). Cite the file.
        """
        return cls(
            value=value, unit=unit, source="reference", citation=citation, confidence=confidence
        )

    @classmethod
    def assume(
        cls,
        value: float,
        unit: str,
        why: str,
        *,
        confidence: Literal["high", "medium", "low"] = "low",
    ) -> ProvenancedValue:
        """An asserted value not derivable from any record (state the rationale)."""
        return cls(value=value, unit=unit, source="assumption", citation=why, confidence=confidence)

    @classmethod
    def derived(
        cls,
        value: float,
        unit: str,
        citation: str,
        *,
        confidence: Literal["high", "medium", "low"] = "medium",
    ) -> ProvenancedValue:
        """A value computed from other provenanced inputs (cite the derivation)."""
        return cls(
            value=value, unit=unit, source="derived", citation=citation, confidence=confidence
        )

    @property
    def verified(self) -> bool:
        """True when the value is grounded in a record or a live gauge.

        ``reference`` (a vendored published spec) is authoritative but is *not* a
        record about this facility, so it is not "verified" in the dossier sense.
        """
        return source_is_verified(self.source)

    def __str__(self) -> str:
        tag = {
            "document": "doc",
            "connector": "live",
            "reference": "ref",
            "assumption": "assume",
            "derived": "calc",
        }[self.source]
        return f"{self.value:,.2f} {self.unit} [{tag}]"


class Node(BaseModel):
    """A point in the municipal water loop (a plant, a demand center, a stream)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    role: NodeRole
    receiving_water: str | None = None  # for wwtp nodes: where the discharge goes
    lat: float | None = None
    lon: float | None = None


class WaterBalanceNode(BaseModel):
    """One node's flow terms. Conservation: inflow + stormwater = return + consumptive.

    Terms are optional — a node carries only what's known/relevant (an abstraction
    node has ``inflow``; a demand node has ``consumptive_use`` + ``return_flow``).
    All flows are in **cfs**. ``stormwater`` is the Increment-2 seam: a cited zero
    today, filled by the SCS-CN solver later.
    """

    model_config = ConfigDict(extra="forbid")

    node: Node
    inflow: ProvenancedValue | None = None
    consumptive_use: ProvenancedValue | None = None
    return_flow: ProvenancedValue | None = None
    stormwater: ProvenancedValue | None = None

    def all_values(self) -> list[ProvenancedValue]:
        return [
            v for v in (self.inflow, self.consumptive_use, self.return_flow, self.stormwater) if v
        ]


class WaterBalance(BaseModel):
    """The assembled source -> use -> WWTP -> receiving loop."""

    model_config = ConfigDict(extra="forbid")

    nodes: list[WaterBalanceNode]
    tier: Literal["tier0"] = "tier0"
    warnings: list[str] = []

    def node(self, node_id: str) -> WaterBalanceNode | None:
        return next((n for n in self.nodes if n.node.id == node_id), None)

    def by_role(self, role: NodeRole) -> list[WaterBalanceNode]:
        return [n for n in self.nodes if n.node.role == role]

    def all_values(self) -> list[ProvenancedValue]:
        return [v for n in self.nodes for v in n.all_values()]

    def closes(self, *, rel_tol: float = 0.05) -> bool:
        """True if, where all terms are present, each node conserves mass within tol."""
        for n in self.nodes:
            if n.inflow is None or n.return_flow is None:
                continue
            storm = n.stormwater.value if n.stormwater else 0.0
            consume = n.consumptive_use.value if n.consumptive_use else 0.0
            lhs = n.inflow.value + storm
            rhs = n.return_flow.value + consume
            if abs(lhs - rhs) > max(0.01, abs(lhs) * rel_tol):
                return False
        return True
