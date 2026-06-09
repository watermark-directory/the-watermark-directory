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
