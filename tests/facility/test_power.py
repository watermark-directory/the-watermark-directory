"""The air-permit-derived facility power basis + its consistency with cooling.py."""

from __future__ import annotations

import pytest

from bosc.facility.power import _IT_LOAD_MW, derive_power_basis


def test_power_basis_traces_to_air_permit() -> None:
    b = derive_power_basis()
    assert b.it_load.value == pytest.approx(275.0)
    assert b.it_load.source == "document" and "P0138965" in (b.it_load.citation or "")
    # Backup power is the genset count x rating, derived (not asserted).
    assert b.backup_power.source == "derived"
    assert b.backup_power.value == pytest.approx(313.5, abs=0.1)  # 114 x 2.75
    # The N+1 range brackets the central figure.
    assert b.it_load_low.value < b.it_load.value < b.it_load_high.value


def test_facility_power_matches_cooling_it_load() -> None:
    """Guard against the duplicated air-permit constant silently diverging.

    bosc.facility.power deliberately re-states cooling.py's private IT-load constant
    rather than importing the private name; this test is the seam that keeps them
    equal until the FUTURE DEDUP noted in power.py lands.
    """
    from bosc.hydrology import cooling

    assert _IT_LOAD_MW == cooling._IT_LOAD_MW
    assert derive_power_basis().it_load.value == pytest.approx(cooling._IT_LOAD_MW)


def test_generation_cycle_efficiency_coefficient() -> None:
    """Issue #90: simple- vs combined-cycle net efficiency (the power-loss coefficient)."""
    b = derive_power_basis()
    simple = b.generation_config("simple")
    combined = b.generation_config("combined")
    assert simple is not None and combined is not None

    # The net-efficiency coefficient is a banded assumption, and the combined cycle
    # (heat-recovery) is materially more efficient than the simple cycle.
    for g in (simple, combined):
        assert g.net_efficiency.source == "assumption"
        assert 0.0 < g.net_efficiency.value < 1.0
    assert combined.net_efficiency.value > simple.net_efficiency.value

    # Heat rate is the derived inverse (fuel per MWh) — lower for the efficient cycle.
    assert simple.heat_rate_mmbtu_per_mwh.source == "derived"
    assert combined.heat_rate_mmbtu_per_mwh.value < simple.heat_rate_mmbtu_per_mwh.value
    assert simple.heat_rate_mmbtu_per_mwh.value == pytest.approx(
        3.412142 / simple.net_efficiency.value, abs=0.01
    )


def test_combined_cycle_steam_water_cross_refs_cooling() -> None:
    """Issue #90: the steam loop is an additional water pathway, cross-ref to cooling."""
    b = derive_power_basis()
    simple = b.generation_config("simple")
    combined = b.generation_config("combined")
    assert simple is not None and combined is not None

    # Only the combined cycle recovers exhaust heat and carries a steam-water pathway.
    assert simple.recovers_exhaust_heat is False
    assert simple.steam_cycle_water is None
    assert combined.recovers_exhaust_heat is True
    assert combined.steam_cycle_water is not None
    assert combined.steam_cycle_water.unit == "MGD"
    assert combined.steam_cycle_water.value > 0.0
    # The water implication is an assumption that cross-references the cooling subsystem.
    assert combined.steam_cycle_water.source == "assumption"
    assert "cooling" in (combined.steam_cycle_water.citation or "").lower()

    # The cycle is honestly framed as an open evidence question (disclosed = backup).
    assert "OPEN EVIDENCE QUESTION" in b.generation_note


def test_cooling_pue_overhead_and_facility_draw() -> None:
    """Issue #87: PUE is a banded assumption and facility_draw = IT load x PUE."""
    b = derive_power_basis()

    # PUE is a banded assumption; the ceiling admits cooling-dominated designs (~1.43).
    assert b.pue_low.source == "assumption" and b.pue_high.source == "assumption"
    assert b.pue_low.value < b.pue_high.value
    assert b.pue_high.value == pytest.approx(1.43, abs=0.01)
    # Cooling share at the high PUE is ~30% of facility power (the call's figure).
    assert b.cooling_share_high.value == pytest.approx(
        (b.pue_high.value - 1.0) / b.pue_high.value, abs=1e-3
    )
    assert b.cooling_share_high.value == pytest.approx(0.30, abs=0.01)

    # The IT <-> total-facility-draw relationship: draw = IT central x PUE, banded.
    assert b.facility_draw.source == "derived"
    assert b.facility_draw_low.value == pytest.approx(b.it_load.value * b.pue_low.value, abs=0.1)
    assert b.facility_draw_high.value == pytest.approx(b.it_load.value * b.pue_high.value, abs=0.1)
    assert b.facility_draw_low.value < b.facility_draw.value < b.facility_draw_high.value
    # Facility draw exceeds IT load by exactly the cooling/mechanical overhead.
    assert b.facility_draw.value > b.it_load.value
    assert b.cooling_overhead_mw == pytest.approx(b.facility_draw.value - b.it_load.value, abs=0.1)


def test_facility_draw_vs_backup_n_plus_one_crosscheck() -> None:
    """Issue #87/#33: the N+1 backup covers the facility draw only at the efficient PUE."""
    b = derive_power_basis()

    # The PUE implied if the genset backup is sized to the full IT + mechanical load.
    implied = b.implied_pue_from_backup
    assert implied.source == "derived"
    assert implied.value == pytest.approx(b.backup_power.value / b.it_load.value, abs=0.01)
    assert implied.value == pytest.approx(1.14, abs=0.02)

    # That implied PUE sits at the efficient end of the band: the backup envelope
    # covers the low-PUE draw but is exceeded by the cooling-dominated draw.
    assert b.facility_draw_low.value <= b.backup_power.value < b.facility_draw_high.value
    assert "#33" in b.cooling_overhead_note
