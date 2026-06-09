"""The air-permit-derived facility power basis.

The canonical ~275 MW IT-load figure that anchors the compute-capacity methods,
expressed as provenance-tagged :class:`ProvenancedValue`s. It traces to the same
disclosed inputs as :mod:`bosc.hydrology.cooling` — Ohio EPA Air PTI **P0138965**
(Facility 0302022054): 114 emergency generators at 2.75 ekW each ≈ 313 MW backup,
which at hyperscale N+1 ratios implies a ~250-300 MW IT load.

The genset count and IT-load constants are deliberately **duplicated** from
``cooling.py``'s private constants here rather than imported, because ``cooling``
hides them as module-private (``_GENSET_COUNT`` etc.) and importing private names
across subsystems is brittle. To keep the two from silently diverging,
``tests/facility/test_power.py`` asserts this module's IT load equals
``cooling.py``'s ``_IT_LOAD_MW``. FUTURE DEDUP: lift the air-permit constants into a
single shared module (e.g. ``bosc.facility.power`` re-exported into hydrology) once
``cooling.py``'s tests can be migrated without churn.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from bosc.hydrology.model import ProvenancedValue

# --- Air-permit-disclosed constants (mirror bosc.hydrology.cooling) ----------
_GENSET_COUNT = 114
_GENSET_MW = 2.75  # ekW each, per the air permit
_BACKUP_MW = _GENSET_COUNT * _GENSET_MW  # ~313 MW
_IT_LOAD_MW = 275.0  # midpoint of the 250-300 MW estimate (IT ~= backup at N+1)
_IT_LOAD_LOW_MW = 250.0
_IT_LOAD_HIGH_MW = 300.0
_AIR_PERMIT_CITE = (
    "OEPA Air PTI P0138965 (Facility 0302022054): 114 gensets x 2.75 ekW = "
    "~313 MW backup; IT ~250-300 MW (N+1)"
)


class PowerBasis(BaseModel):
    """The disclosed-power basis for the campus, all provenance-tagged.

    ``it_load`` is the central document-anchored IT load (the N+1 backup ≈ IT
    convention from the air permit); ``it_load_low``/``it_load_high`` bracket the
    250-300 MW range the genset count supports. Mirrors the shape of
    :class:`bosc.hydrology.model.CoolingBasis` so the two subsystems read alike.
    """

    model_config = ConfigDict(extra="forbid")

    genset_count: ProvenancedValue  # count (document)
    genset_rating: ProvenancedValue  # MW each (document)
    backup_power: ProvenancedValue  # MW total backup (derived)
    it_load: ProvenancedValue  # MW central (document-anchored)
    it_load_low: ProvenancedValue  # MW low end of the N+1 range
    it_load_high: ProvenancedValue  # MW high end
    method: str = "air-permit genset count x rating -> N+1 backup -> IT load (250-300 MW)"


def derive_power_basis() -> PowerBasis:
    """Derive the campus power basis from the cited air-permit genset count."""
    return PowerBasis(
        genset_count=ProvenancedValue.from_document(
            float(_GENSET_COUNT), "count", citation=_AIR_PERMIT_CITE
        ),
        genset_rating=ProvenancedValue.from_document(_GENSET_MW, "MW", citation=_AIR_PERMIT_CITE),
        backup_power=ProvenancedValue.derived(
            round(_BACKUP_MW, 1),
            "MW",
            citation=f"{_GENSET_COUNT} gensets x {_GENSET_MW:g} ekW (air permit P0138965)",
        ),
        it_load=ProvenancedValue.from_document(_IT_LOAD_MW, "MW", citation=_AIR_PERMIT_CITE),
        it_load_low=ProvenancedValue.derived(
            _IT_LOAD_LOW_MW,
            "MW",
            citation="low end of the N+1 IT estimate from ~313 MW backup",
        ),
        it_load_high=ProvenancedValue.derived(
            _IT_LOAD_HIGH_MW,
            "MW",
            citation="high end of the N+1 IT estimate from ~313 MW backup",
        ),
    )
