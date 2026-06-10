"""Tests for USACE Wetland Determination Data Form extraction (kind=wetland)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bosc.models import WetlandDetermination, WetlandExtraction
from bosc.pipeline.extract import extract_wetland
from bosc.pipeline.ingest import SourceDocument


class _FakePdf:
    def __init__(self, text: str = "Wetland Determination Data Form", page_count: int = 2) -> None:
        self.text = text
        self.page_count = page_count
        self.closed = False

    def page_text(self, index: int) -> str:
        return f"{self.text} (page {index})"

    def render_page_png(self, index: int, *, dpi: int | None = None) -> bytes:
        return b"PNG" + bytes([index])

    def close(self) -> None:
        self.closed = True


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
        self.calls.append({"target": target, "images": images, "instructions": instructions})
        return self.result


def _doc() -> SourceDocument:
    return SourceDocument(
        path=Path("/data/documents/permits/bistrozzi-permits/3727950.pdf"),
        doc_id="w-1",
        suffix=".pdf",
        size_bytes=10,
        collection="permits",
    )


def test_extract_wetland_attaches_provenance() -> None:
    det = WetlandDetermination(
        applicant="Bistrozzi LLC",
        city_county="Sugar Creek Township/Allen",
        sampling_point="WD-1",
        sampling_date="2024-08-15",
        hydrophytic_vegetation_present=False,
        hydric_soil_present=False,
        wetland_hydrology_present=False,
        is_wetland=False,
        confidence="high",
    )
    pdf, extractor = _FakePdf(), _FakeExtractor(det)
    extraction = extract_wetland(_doc(), extractor=extractor, pdf=pdf)  # type: ignore[arg-type]

    assert isinstance(extraction, WetlandExtraction)
    assert extraction.kind == "wetland"
    assert extraction.determination.sampling_point == "WD-1"
    assert extraction.determination.is_wetland is False
    # Both pages of the form are rendered and sent as images, under the WETLAND prompt.
    assert extractor.calls[0]["target"] is WetlandDetermination
    assert len(extractor.calls[0]["images"]) == 2
    assert "Wetland Determination" in extractor.calls[0]["instructions"]
    assert extraction.pages_read == [0, 1]


def test_wetland_determination_booleans_default_null() -> None:
    """An unread criterion stays null — the schema never guesses a determination."""
    det = WetlandDetermination(sampling_point="WE-1")
    assert det.is_wetland is None
    assert det.hydric_soil_present is None
    assert det.confidence == "medium"  # _Extracted default
