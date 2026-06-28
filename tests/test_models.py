"""Tests for the OPC data models, exercised against the real extraction."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from watermark.models import (
    Deed,
    Estimate,
    OPCSummary,
    SubEstimate,
    _coerce_number,
    _coerce_number_keep,
)


def test_coerce_number_handles_approx_and_separators() -> None:
    assert _coerce_number("~307043") == 307043
    assert _coerce_number("1,535,218") == 1535218
    assert _coerce_number("$50000") == 50000
    assert _coerce_number(120000) == 120000
    assert _coerce_number(None) is None


def test_coerce_number_rounds_not_truncates() -> None:
    # int(float("17.9")) silently dropped to 17; round keeps the nearer whole number (#612).
    assert _coerce_number("17.9") == 18
    assert _coerce_number("$108,307.89") == 108308
    assert _coerce_number("~17.4") == 17


def test_coercers_reject_bool() -> None:
    # isinstance(True, int) is True, so without the guard a stray bool became 1/0 (#612).
    for coerce in (_coerce_number, _coerce_number_keep):
        with pytest.raises(ValueError, match="boolean"):
            coerce(True)
        with pytest.raises(ValueError, match="boolean"):
            coerce(False)
    with pytest.raises(ValidationError):
        SubEstimate(name="x", construction_subtotal=True, total=1)  # type: ignore[arg-type]


def test_coerce_number_keep_preserves_int_vs_float() -> None:
    assert _coerce_number_keep("~17.0") == 17.0
    assert isinstance(_coerce_number_keep("~17.0"), float)
    assert _coerce_number_keep("~2,490") == 2490
    assert isinstance(_coerce_number_keep("2490"), int)


def test_coercers_treat_a_bare_marker_as_empty() -> None:
    # "~" with nothing after it is not a number — it cleans to "" → None, not a crash (#620).
    assert _coerce_number("~") is None
    assert _coerce_number_keep("~") is None
    assert _coerce_number("  ") is None
    assert _coerce_number_keep(None) is None
    # An unparseable string passes through unchanged so Pydantic raises a clear error.
    assert _coerce_number("not a number") == "not a number"


def test_approximate_sidecar_records_tilde_fields() -> None:
    # The ~ marker is coerced away to a number, but which fields arrived approximate
    # is preserved in the .approximate sidecar — not silently dropped (#612).
    se = SubEstimate(name="Cole St", construction_subtotal="~307043", total=307043)  # type: ignore[arg-type]
    assert se.construction_subtotal == 307043  # ~ stripped, coerced
    assert se.approximate == {"construction_subtotal"}  # …but recorded
    # A precise (non-~) field is not flagged.
    assert "total" not in se.approximate


def test_approximate_sidecar_is_not_serialized_or_in_schema() -> None:
    # The sidecar is a PrivateAttr: it must not pollute the committed YAML shape
    # (model_dump) nor the LLM extraction tool schema (#612).
    est = Estimate(name="OPC", total="~14223081")  # type: ignore[arg-type]
    assert est.approximate == {"total"}
    assert "approximate" not in est.model_dump()
    assert "approximate" not in Estimate.model_json_schema().get("properties", {})


def test_approximate_sidecar_on_doc_models() -> None:
    deed = Deed(consideration="~600000")  # type: ignore[arg-type]
    assert deed.consideration == 600000
    assert deed.approximate == {"consideration"}


def test_loads_real_summary(summary_path: Path) -> None:
    summary = OPCSummary.from_yaml(summary_path)
    # Six sub-estimates: four roundabouts + two corridors.
    assert len(summary.sub_estimates) == 6
    names = {se.name for se in summary.sub_estimates}
    assert "Cole Street / Diller Road Roundabout" in names


def test_program_headline_total_matches_meta(summary_path: Path) -> None:
    summary = OPCSummary.from_yaml(summary_path)
    stated = summary.meta.summary_construction_total
    assert stated is not None
    # The meta headline equals the sum of the six summary-sheet line costs,
    # which are post-contingency *totals* — so it reconciles with grand_total(),
    # not the sum of construction subtotals. Within 1%.
    assert abs(summary.grand_total() - stated) <= round(stated * 0.01)
    # And the two are genuinely different figures (contingency makes up the gap).
    assert summary.construction_total() < stated


def test_diller_total_is_corrected_figure(summary_path: Path) -> None:
    summary = OPCSummary.from_yaml(summary_path)
    diller = next(se for se in summary.sub_estimates if "Diller" in se.name)
    # OCR-corrected: 1.535M, not 4.535M (see reconciliation notes).
    assert diller.total == 1535218
