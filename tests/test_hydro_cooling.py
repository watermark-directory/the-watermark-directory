"""The sourced cooling design basis (replaces the bare assumption knob)."""

from __future__ import annotations

import pytest

from watermark.config import Settings
from watermark.hydrology import scenario
from watermark.hydrology.cooling import derive_cooling_basis


def test_basis_is_derived_from_cited_power() -> None:
    b = derive_cooling_basis()
    # IT load traces to the air permit genset count (document-sourced).
    assert b.it_load.value == pytest.approx(275.0)
    assert b.it_load.source == "document" and "P0138965" in (b.it_load.citation or "")
    # WUE and cycles are explicit assumptions, not silent constants.
    assert b.wue.source == "assumption"
    assert b.cycles_of_concentration.source == "assumption"


def test_basis_two_methods_bracket_demand() -> None:
    b = derive_cooling_basis()
    # Power x WUE central vs blowdown x cycles upper bound — both derived.
    assert b.consumptive_low.value == pytest.approx(3.14, abs=0.05)
    assert b.consumptive_high.value == pytest.approx(10.0, abs=0.1)
    assert b.consumptive_low.value < b.consumptive_high.value
    assert b.makeup_demand.source == "derived"
    # Evaporation/makeup fraction follows cycles of concentration: (CoC-1)/CoC.
    assert b.consumptive_fraction.value == pytest.approx(0.8)


def test_basis_scales_with_inputs() -> None:
    base = derive_cooling_basis()
    hotter = derive_cooling_basis(it_load_mw=350.0, wue_l_per_kwh=2.2)
    assert hotter.consumptive_low.value > base.consumptive_low.value


def test_buildout_defaults_to_sourced_basis() -> None:
    s = scenario.buildout_scenario()
    # Default knobs come from the basis (derived), not a bare assumption.
    assert s.cooling_demand.source == "derived"
    assert s.consumptive_fraction.source == "derived"
    assert s.basis is not None and s.basis.it_load.source == "document"


def test_override_tags_as_assumption() -> None:
    s = scenario.buildout_scenario(cooling_demand_mgd=8.0, consumptive_fraction=0.75)
    assert s.cooling_demand.value == 8.0 and s.cooling_demand.source == "assumption"
    assert s.consumptive_fraction.value == 0.75 and s.consumptive_fraction.source == "assumption"


def test_sourced_buildout_still_dwarfs_7q10(hydro_settings: Settings) -> None:
    from watermark.pipeline.hydrology import run_scenarios

    _base, _build, delta = run_scenarios(settings=hydro_settings, live=True)
    # Even the conservative power-based central estimate is ~24x the Ottawa 7Q10.
    assert delta.multiple_of_7q10 is not None and delta.multiple_of_7q10 > 15
