"""Self-correcting reconcile loop + the pinned ROADWAY/PAVEMENT discrepancies (#40).

The committed hand-authored detail reconciles 7/10; the 3 fails are the known
pre-existing ROADWAY/PAVEMENT transcription gaps. These tests pin that count (no test
did before), characterize the gaps, and exercise `reconcile_with_repair` both as a
no-op (characterize, don't rewrite) and with a stub re-extractor (the loop converges).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.models import Estimate
from bosc.pipeline import analyze
from bosc.pipeline.corpus import _estimate_from_legacy_page

REPO_ROOT = Path(__file__).resolve().parents[1]
_DETAIL = REPO_ROOT / "data" / "extracted" / "aedg" / "roundabouts.detail.opc.yaml"


def _committed_cole_diller() -> Estimate:
    """The one fully-detailed sub-estimate in the committed detail YAML."""
    data = yaml.safe_load(_DETAIL.read_text(encoding="utf-8"))
    template = data.get("estimate_template") or {}
    page = next(
        v
        for k, v in data.items()
        if k.startswith("page_") and isinstance(v, dict) and "line_items" in v
    )
    return _estimate_from_legacy_page("page", page, template)


def test_committed_detail_discrepancy_count_is_pinned() -> None:
    """The regression pin: 10 checks, 7 pass, 3 fail (2 line-item + 1 section rollup)."""
    findings = analyze.reconcile_estimate(_committed_cole_diller())
    assert len(findings) == 10
    fails = [f for f in findings if not f.ok]
    assert len(fails) == 3
    # The 3 fails: ROADWAY + PAVEMENT line-item rollups, plus the section-rollup gap.
    assert sorted(f.check for f in fails) == [
        "line-item-rollup",
        "line-item-rollup",
        "section-rollup",
    ]
    assert set(analyze.failing_section_keys(fails)) == {"roadway", "pavement"}


def test_repair_is_a_noop_without_reextractor() -> None:
    """No re-extractor -> the loop characterizes the gaps and rewrites nothing."""
    result = analyze.reconcile_with_repair(_committed_cole_diller())
    assert not result.converged
    assert len(result.failures) == 3
    assert result.rounds == []  # nothing acted; the reviewed artifact is untouched


def test_repair_loop_converges_with_a_reextractor() -> None:
    """With a re-extractor that re-reads the offending sections, the loop converges."""

    def reextract(est: Estimate, findings: list[analyze.Finding]) -> Estimate:
        # Stand-in for a higher-fidelity re-read: correct the failing sections'
        # subtotals to their line-item sums, then recompute the rollups consistently.
        keys = set(analyze.failing_section_keys(findings))
        sections = [
            (
                s.model_copy(update={"subtotal": round(s.items_total())})
                if s.key in keys and s.line_items
                else s
            )
            for s in est.sections
        ]
        cs = round(sum(float(s.subtotal or 0) for s in sections))
        markups = [m.model_copy(update={"amount": round(cs * (m.rate or 0))}) for m in est.markups]
        total = cs + sum(float(m.amount or 0) for m in markups)
        return est.model_copy(
            update={
                "sections": sections,
                "construction_subtotal": cs,
                "markups": markups,
                "total": int(total),
            }
        )

    result = analyze.reconcile_with_repair(
        _committed_cole_diller(), reextract=reextract, max_rounds=2
    )
    assert result.converged
    assert result.failures == []
    assert len(result.rounds) >= 1
    first = result.rounds[0]
    assert first.failures_before == 3
    assert set(first.sections) == {"roadway", "pavement"}


def test_repair_respects_max_rounds() -> None:
    """A re-extractor that never fixes anything stops at max_rounds (no infinite loop)."""
    result = analyze.reconcile_with_repair(
        _committed_cole_diller(), reextract=lambda est, findings: est, max_rounds=2
    )
    assert not result.converged
    assert len(result.rounds) == 2
