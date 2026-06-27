"""Tests for the reconciliation logic and ingest stage."""

from __future__ import annotations

from pathlib import Path

from bosc.models import OPCSummary
from bosc.pipeline import analyze, ingest


def test_reconcile_runs_all_checks(summary_path: Path) -> None:
    summary = OPCSummary.from_yaml(summary_path)
    findings = analyze.reconcile(summary)
    # 3 per-sub-estimate checks x 6 + 1 program-level check.
    assert len(findings) == 6 * 3 + 1
    by_check = {f.check for f in findings}
    assert {"section-rollup", "contingency-25pct", "total", "program-total"} <= by_check


def test_total_checks_pass(summary_path: Path) -> None:
    """subtotal + 25% should reconcile to the stated total for every estimate."""
    summary = OPCSummary.from_yaml(summary_path)
    total_checks = [f for f in analyze.reconcile(summary) if f.check == "total"]
    assert total_checks and all(f.ok for f in total_checks)


def test_discover_handles_missing_dir(tmp_path: Path) -> None:
    from bosc.config import Settings

    settings = Settings(data_dir=tmp_path / "nope")
    assert ingest.discover(settings) == []


def test_discover_finds_only_extractable_sources(tmp_path: Path) -> None:
    from bosc.config import Settings

    coll = tmp_path / "documents" / "aedg"
    coll.mkdir(parents=True)
    (coll / "exhibit.pdf").write_bytes(b"%PDF-1.4 stub")
    (coll / "drawing.odg").write_bytes(b"PK\x03\x04 stub")
    # Raster scans now have an extractor path (read straight into the vision model,
    # no text layer), so they're back in the inventory (#703, reversing #619's #).
    (coll / "scan.png").write_bytes(b"\x89PNG stub")
    (coll / "agenda.jpg").write_bytes(b"\xff\xd8\xff stub")
    # …but a .txt / .csv still has no vision path and stays out.
    (coll / "notes.txt").write_text("hello")
    (coll / "ignore.csv").write_text("a,b")

    settings = Settings(data_dir=tmp_path)
    docs = ingest.discover(settings)
    assert {d.path.name for d in docs} == {"exhibit.pdf", "drawing.odg", "scan.png", "agenda.jpg"}
    assert all(d.collection == "aedg" for d in docs)
    assert next(d for d in docs if d.is_pdf)
    assert {d.path.name for d in docs if d.is_image} == {"scan.png", "agenda.jpg"}
