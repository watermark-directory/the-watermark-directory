"""Toxic-load x assimilative-capacity screen over the committed RSEI/ECHO/7Q10 data."""

from __future__ import annotations

from watermark.config import Settings
from watermark.hydrology import toxics
from watermark.hydrology.model import ProvenancedValue


def _by_name(inv: toxics.ToxicDischargeInventory, needle: str) -> toxics.ToxicDischargeScreen:
    return next(s for s in inv.screens if needle in s.facility)


def test_screen_builds_from_committed_data() -> None:
    inv = toxics.build_screen(Settings())
    assert inv.meta["water_releaser_count"] == len(inv.screens)
    assert inv.screens, "expected at least one water releaser"
    # The three refinery-complex majors are the headline: highest toxic load on the
    # Ottawa reach with essentially no assimilative capacity.
    for name in ("INEOS", "LIMA REFINING", "PCS NITROGEN"):
        assert _by_name(inv, name).flag == "critical"
    assert inv.meta["critical_count"] == len(inv.flagged) == 3


def test_lima_refining_receiving_water_is_echo_cited() -> None:
    """Lima Refining resolves via an ECHO-cited receiving water, not an inference."""
    s = _by_name(toxics.build_screen(Settings()), "LIMA REFINING")
    assert s.receiving_water_source == "connector"
    assert s.npdes_id == "OH0002623"
    assert s.receiving_water is not None and "OTTAWA" in s.receiving_water.upper()


def test_corridor_inference_is_tagged_and_cited() -> None:
    """INEOS/PCS have no ECHO receiving water -> Ottawa-corridor inference, flagged."""
    for name in ("INEOS", "PCS NITROGEN"):
        s = _by_name(toxics.build_screen(Settings()), name)
        assert s.receiving_water_source == "assumption"
        assert s.receiving_water == "Ottawa River"
        assert s.receiving_water_citation is not None
        assert "corridor" in s.receiving_water_citation.lower()
        assert "not independently cited" in s.receiving_water_citation.lower()


def test_low_flow_is_the_cited_7q10() -> None:
    s = _by_name(toxics.build_screen(Settings()), "LIMA REFINING")
    assert s.low_flow_7q10 is not None
    assert s.low_flow_7q10.source == "document"  # cited from an OEPA fact sheet
    assert s.low_flow_7q10.value == 0.2


def test_flag_bands_track_the_water_pathway_not_total_score() -> None:
    """Teledyne has a large RSEI Score but trace water pounds -> not critical."""
    inv = toxics.build_screen(Settings())
    teledyne = _by_name(inv, "TELEDYNE")
    assert teledyne.water_pounds < 10  # air-driven score, negligible to water
    assert teledyne.flag in ("context", "elevated")  # never critical on 5 lb to water
    # The critical facilities are the heavy water dischargers.
    for s in inv.flagged:
        assert s.screening_concentration is not None
        assert s.screening_concentration.value >= 1.0


def test_uncharacterized_when_no_receiving_water() -> None:
    """A water releaser outside the corridor with no ECHO receiving water is uncharacterized."""
    inv = toxics.build_screen(Settings())
    unchar = [s for s in inv.screens if s.flag == "uncharacterized"]
    assert unchar, "expected some facilities we cannot place on a cited reach"
    for s in unchar:
        assert s.receiving_water is None
        assert s.receiving_water_source is None
        assert s.low_flow_7q10 is None
        assert s.screening_concentration is None


def test_screening_concentration_conversion() -> None:
    """1 lb/day into 1 cfs is the textbook ~0.186 mg/L; confirm the mass balance."""
    q7 = ProvenancedValue.from_document(1.0, "cfs", "test")
    conc = toxics._screening_concentration(365.0, q7)  # 365 lb/yr == 1 lb/day
    assert conc is not None
    assert abs(conc.value - 0.186) < 0.002
    assert conc.source == "derived"
    assert conc.confidence == "low"


def test_zero_flow_or_zero_load_yields_no_concentration() -> None:
    q7 = ProvenancedValue.from_document(0.0, "cfs", "test")
    assert toxics._screening_concentration(1000.0, q7) is None
    good = ProvenancedValue.from_document(0.2, "cfs", "test")
    assert toxics._screening_concentration(0.0, good) is None


def test_write_load_roundtrip(tmp_path: object) -> None:
    from pathlib import Path

    ref = Path(str(tmp_path))
    inv = toxics.build_screen(Settings())
    # write_screen drops the file in <out>; load_screen reads <ref>/rsei/... — mirror it.
    path = toxics.write_screen(inv, ref / "rsei")
    assert path.is_file()
    reloaded = toxics.load_screen(ref)
    assert reloaded is not None
    assert len(reloaded.screens) == len(inv.screens)
    assert reloaded.meta["critical_count"] == inv.meta["critical_count"]
    assert toxics.load_screen(ref / "nonexistent") is None
