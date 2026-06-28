"""Tests for ODG site-plan reading and extraction."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from watermark.documents import OdgContent, read_odg
from watermark.models import DesignFirm, PlanExtraction, SitePlan
from watermark.pipeline.extract import extract_plan
from watermark.pipeline.ingest import SourceDocument

_CONTENT = (
    '<?xml version="1.0"?><doc xmlns:text="urn:t">'
    "<text:p>AMERICAN INDUSTRIAL PARK SITE</text:p>"
    "<text:span>GRADING &amp; STORM PLAN</text:span>"
    "<text:p>EMH&amp;T</text:p>"
    "<text:span>EMH&amp;T</text:span>"  # repeated -> ranks higher
    "<text:p>825.10</text:p>"  # pure survey number -> filtered
    "<text:span>RIM=828.75</text:span>"  # survey code -> filtered (no 3-letter word)
    "</doc>"
)


def _make_odg(tmp_path: Path) -> Path:
    p = tmp_path / "sheet.odg"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/vnd.oasis.opendocument.graphics")
        z.writestr("content.xml", _CONTENT)
        z.writestr("Thumbnails/thumbnail.png", b"\x89PNG-thumb")
    return p


def test_read_odg_extracts_meaningful_labels_and_thumbnail(tmp_path: Path) -> None:
    content = read_odg(_make_odg(tmp_path))
    assert content.thumbnail_png == b"\x89PNG-thumb"
    assert "EMH&T" in content.labels  # entity unescaped
    assert "GRADING & STORM PLAN" in content.labels
    # Pure survey numbers are dropped as noise (codes with a word like RIM= stay).
    assert "825.10" not in content.labels
    # Repeated label ranks first (titleblock text repeats across sheets).
    assert content.labels[0] == "EMH&T"


class _FakeExtractor:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.calls: list[dict[str, Any]] = []

    def extract(
        self,
        target: Any,
        *,
        instructions: str,
        images: list[bytes] | None = None,
        image_png: bytes | None = None,
        context_text: str = "",
    ) -> Any:
        self.calls.append({"images": images, "context": context_text})
        return self.result


def _doc() -> SourceDocument:
    return SourceDocument(
        path=Path("/data/documents/plans/x.odg"),
        doc_id="p-1",
        suffix=".odg",
        size_bytes=10,
        collection="plans",
    )


def test_extract_plan_attaches_provenance() -> None:
    plan = SitePlan(
        project_name="American Industrial Park Site",
        discipline="Grading & Storm Plan",
        prepared_by=[DesignFirm(name="EMH&T", discipline="Civil")],
        key_features=["substation", "anti-ram barrier"],
    )
    odg = OdgContent(labels=["EMH&T", "SUBSTATION"], thumbnail_png=b"\x89PNG")
    extractor = _FakeExtractor(plan)
    extraction = extract_plan(_doc(), extractor=extractor, odg=odg)  # type: ignore[arg-type]
    assert isinstance(extraction, PlanExtraction)
    assert extraction.kind == "plan"
    assert extraction.plan.prepared_by[0].name == "EMH&T"
    # The thumbnail is sent as the single image; labels as context text.
    assert extractor.calls[0]["images"] == [b"\x89PNG"]
    assert "SUBSTATION" in extractor.calls[0]["context"]
