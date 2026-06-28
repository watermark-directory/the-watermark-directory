"""Storm-plan drainage inventory: loader + findings (hermetic) and parser regexes.

The committed artifact (``data/extracted/plans/lma1a.storm-inventory.yaml``) is plain
text, so the loader path needs no LFS. The full ODG parse is gated on the 9 MB source
actually being materialized (skipped when only an LFS pointer is present).
"""

from __future__ import annotations

import zipfile

import pytest

from watermark.config import Settings
from watermark.hydrology import stormplan
from watermark.hydrology.model import StormPlanInventory


def test_load_inventory_grounds_the_real_sheet(hydro_settings: Settings) -> None:
    inv = stormplan.load_inventory(settings=hydro_settings)
    assert inv is not None
    assert inv.sheet_id == "1A-C-3104"
    assert "95%" in inv.phase
    # The headline grounded fact: the 95% design shows no on-site storage.
    assert inv.detention_shown is False
    assert "Detention" in inv.storage_terms_searched  # the negative is auditable
    # Graded surface read off the storm-structure rims.
    assert inv.rim_labels > 100
    assert 815.0 < inv.rim_min.value < inv.rim_max.value < 835.0
    assert inv.relief.value == pytest.approx(inv.rim_max.value - inv.rim_min.value, abs=0.01)
    # Pipe callouts are plausible nominal sizes (garbled CAD digits filtered out).
    assert inv.pipe_sizes_in and all(2 <= s <= 48 for s in inv.pipe_sizes_in)
    assert "Catch Basin" in inv.structure_types


def test_rim_elevations_are_document_sourced(hydro_settings: Settings) -> None:
    inv = stormplan.load_inventory(settings=hydro_settings)
    assert inv is not None
    assert inv.rim_min.source == "document" and inv.rim_min.citation
    assert inv.rim_max.source == "document"
    assert inv.relief.source == "derived"  # max - min, not directly read


def test_findings_flag_absent_detention(hydro_settings: Settings) -> None:
    inv = stormplan.load_inventory(settings=hydro_settings)
    assert inv is not None
    findings = stormplan.storm_plan_findings(inv)
    detn = next(f for f in findings if f.check == "on-site-detention")
    assert detn.ok is False  # no on-site storage shown -> not ok
    assert "no detention" in detn.detail.lower()
    relief = next(f for f in findings if f.check == "graded-relief")
    assert relief.ok is True


def test_pipe_size_regex_drops_garbled_digits() -> None:
    # The CAD path data glues long digit runs onto real callouts; only sane sizes survive.
    text = '16515" HDPE and 15" INLINE DRAIN and 12" TRENCH DRAIN'
    sizes = {int(m) for m in stormplan._PIPE_SIZE_RE.findall(text) if 2 <= int(m) <= 48}
    assert sizes == {15, 12}


def test_rim_regex_reads_decimal_elevations() -> None:
    rims = [float(x) for x in stormplan._RIM_RE.findall("RIM=828.75 foo RIM = 820.50")]
    assert rims == [828.75, 820.50]


def test_refresh_matches_committed_artifact(hydro_settings: Settings) -> None:
    """Re-parsing the real drawing reproduces the committed inventory (no drift)."""
    src = hydro_settings.data_dir / stormplan._SOURCE_REL
    if not (src.exists() and zipfile.is_zipfile(src)):
        pytest.skip("source ODG not materialized (LFS pointer only)")
    fresh = stormplan.refresh_inventory(settings=hydro_settings, write=False)
    committed = stormplan.load_inventory(settings=hydro_settings)
    assert committed is not None
    assert isinstance(fresh, StormPlanInventory)
    assert fresh.model_dump() == committed.model_dump()
