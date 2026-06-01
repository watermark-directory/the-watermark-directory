"""Cited sanitary design basis: loader + provenance (hermetic, no engine)."""

from __future__ import annotations

from bosc.config import Settings
from bosc.hydrology.sanitary import load_sanitary_basis


def test_basis_loads_cited_plant_flows(hydro_settings: Settings) -> None:
    basis = load_sanitary_basis(settings=hydro_settings)
    assert basis is not None
    names = {p.plant for p in basis.plants}
    assert {"American II", "Shawnee II", "American Bath"} <= names
    am2 = basis.plant("American II")
    assert am2 is not None
    assert am2.avg_design_flow.value == 1.2
    assert am2.peak_capacity is not None and am2.peak_capacity.value == 3.6
    assert am2.avg_design_flow.source == "document" and am2.avg_design_flow.citation


def test_peaking_factor_and_headroom_are_derived(hydro_settings: Settings) -> None:
    basis = load_sanitary_basis(settings=hydro_settings)
    assert basis is not None
    sh2 = basis.plant("Shawnee II")
    assert sh2 is not None and sh2.peak_capacity is not None
    # peaking factor = peak / avg, tagged derived (not document)
    assert sh2.peaking_factor is not None and sh2.peaking_factor.source == "derived"
    assert sh2.peaking_factor.value == round(sh2.peak_capacity.value / sh2.avg_design_flow.value, 2)
    # headroom = peak - avg
    assert sh2.headroom_mgd == round(sh2.peak_capacity.value - sh2.avg_design_flow.value, 2)


def test_uncited_peak_is_omitted_not_guessed(hydro_settings: Settings) -> None:
    basis = load_sanitary_basis(settings=hydro_settings)
    assert basis is not None
    bath = basis.plant("American Bath")
    # No peak hydraulic capacity is cited for Bath -> omitted, so no headroom/peaking invented.
    assert bath is not None
    assert bath.peak_capacity is None
    assert bath.peaking_factor is None
    assert bath.headroom_mgd is None


def test_regulatory_context_is_present(hydro_settings: Settings) -> None:
    basis = load_sanitary_basis(settings=hydro_settings)
    assert basis is not None
    assert basis.campus_industrial.value == 2.5
    assert basis.campus_industrial.source == "document"
    assert basis.ii_remediation_musd.value == 11.8
    assert "2015" in basis.decree_note and "bypassing" in basis.decree_note.lower()
