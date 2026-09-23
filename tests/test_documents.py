"""Tests for document-level extraction (deeds, NPDES permits)."""

from __future__ import annotations

import io
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from PIL import Image

from watermark.agent.extractor import ExtractionError, StructuredExtractor
from watermark.config import Settings
from watermark.documents import IMAGE_SUFFIXES, read_image_png
from watermark.models import (
    BusinessFiling,
    Deed,
    DeedExtraction,
    EpaExtraction,
    EpaPermitAction,
    IdpExtraction,
    IndustrialDischargePermit,
    LimitTable,
    NoticeExtraction,
    NoticeOfCommencement,
    NpdesExtraction,
    NpdesPermit,
    PermitExtension,
    PermitExtensionExtraction,
    PollutantLimit,
    PretreatmentAnnualReport,
    PretreatmentExtraction,
    ProgramCount,
    SosExtraction,
)
from watermark.pipeline.extract import (
    _IDP_SPEC,
    _MAX_REQUEST_BYTES,
    _MIN_RENDER_DPI,
    _PRETREATMENT_SPEC,
    _fitted_dpi,
    _page_window,
    _read_doc,
    _render_within_budget,
    extract_deed,
    extract_document,
    extract_epa,
    extract_idp,
    extract_notice,
    extract_npdes,
    extract_pretreatment,
    extract_sos,
    save_doc_extraction,
)
from watermark.pipeline.ingest import SOURCE_SUFFIXES, SourceDocument

REPO_ROOT = Path(__file__).resolve().parents[1]


# --- fakes -----------------------------------------------------------------
class _Block:
    def __init__(self, type: str, name: str | None = None, input: Any = None) -> None:
        self.type, self.name, self.input = type, name, input


class _FakeClient:
    def __init__(self, blocks: list[_Block]) -> None:
        self.capture: dict[str, Any] = {}
        outer = self

        class _Messages:
            def create(self, **kwargs: Any) -> Any:
                outer.capture = kwargs
                return SimpleNamespace(content=blocks)

        self.messages = _Messages()


class _FakePdf:
    def __init__(self, pages: int = 3, *, text: bool = True, bytes_per_px2: float = 0.0) -> None:
        self._n = pages
        self._text = text
        self._bytes_per_px2 = bytes_per_px2

    @property
    def page_count(self) -> int:
        return self._n

    def page_text(self, index: int) -> str:
        # `text=False` is a PURE SCAN — pypdf yields "" on every page, which is what
        # eleven of the thirteen City of Lima industrial discharge permits do.
        return f"text {index}" if self._text else ""

    def page_size_points(self, index: int) -> tuple[float, float]:
        return (612.0, 792.0)  # US Letter, what the City prints on

    def render_page_png(self, index: int, *, dpi: int | None = None) -> bytes:
        if not self._bytes_per_px2:
            return b"\x89PNG-fake"
        # Size scales with pixel count, as a real scan's PNG does — so a test can drive
        # the payload budget without rendering anything.
        return b"\x89" * max(1, int((dpi or 200) ** 2 * self._bytes_per_px2))

    def close(self) -> None:  # pragma: no cover
        pass


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


def _doc(name: str = "PRR.pdf") -> SourceDocument:
    return SourceDocument(
        path=Path(f"/data/documents/recorder/{name}"),
        doc_id="abc-1234",
        suffix=".pdf",
        size_bytes=10,
        collection="recorder",
    )


# --- models ----------------------------------------------------------------
def test_deed_consideration_coercion() -> None:
    d = Deed(consideration="$1,250,000", grantees=["Tilted Gate LLC"])
    assert d.consideration == 1250000
    assert d.confidence == "medium"  # default from the _Extracted mixin


def test_str_list_fields_tolerate_a_bare_string() -> None:
    # The LLM sometimes returns a list field as a single string; wrap, don't fail.
    d = Deed(grantors="Lone Grantor", warnings="one warning")
    assert d.grantors == ["Lone Grantor"]
    assert d.warnings == ["one warning"]
    assert Deed(grantors="").grantors == []  # empty string -> empty list


def test_npdes_basic_model() -> None:
    p = NpdesPermit(
        permit_no="2PH00006*LD", facility_name="American II WWTP", receiving_water="Pike Run"
    )
    assert p.permit_no == "2PH00006*LD"
    assert p.warnings == []


# --- extractor multi-image -------------------------------------------------
def test_extractor_sends_multiple_images() -> None:
    client = _FakeClient([_Block("tool_use", "record_extraction", {"instrument_type": "Deed"})])
    StructuredExtractor(client=client).extract(
        Deed, instructions="read", images=[b"a", b"b", b"c"], context_text="ctx"
    )
    content = client.capture["messages"][0]["content"]
    assert sum(1 for c in content if c["type"] == "image") == 3
    assert content[-1]["type"] == "text" and "read" in content[-1]["text"]


def test_extractor_flags_max_tokens_truncation() -> None:
    # A max_tokens stop with no tool call raises a distinct, actionable error rather
    # than the opaque "did not call tool" (#613).
    from watermark.agent.extractor import _first_tool_input

    msg = SimpleNamespace(content=[_Block("text")], stop_reason="max_tokens")
    with pytest.raises(ExtractionError, match="max_tokens"):
        _first_tool_input(msg, "record_extraction")
    # A non-truncation non-call still raises, now naming the stop_reason.
    msg2 = SimpleNamespace(content=[_Block("text")], stop_reason="end_turn")
    with pytest.raises(ExtractionError, match="end_turn"):
        _first_tool_input(msg2, "record_extraction")


# --- pipeline --------------------------------------------------------------
def test_page_window_prefix_is_unchanged_without_a_tail() -> None:
    # tail=0 is the behaviour every pre-existing genre relies on: a plain prefix, clamped
    # to the document. Nothing below may drift, or twelve genres change read silently.
    assert _page_window(6, 0, 30) == list(range(6))
    assert _page_window(8, 0, 6) == list(range(6))  # clamped to a short document
    assert _page_window(0, 0, 4) == []


def test_page_window_reaches_an_appendix_a_prefix_budget_cannot() -> None:
    # The three permits this exists for, at their real page counts. The limits table sits
    # on p20 of 22 (P&G), p19 of 20 (Ford) and pp23-24 of 25 (Lima Tank Wash); a prefix
    # budget of 3 reads none of them and reports nothing wrong.
    assert _page_window(3, 2, 22) == [0, 1, 2, 20, 21]
    assert _page_window(3, 2, 20) == [0, 1, 2, 18, 19]
    assert _page_window(3, 3, 25) == [0, 1, 2, 22, 23, 24]
    for count, table_page in ((22, 20), (20, 19), (25, 23)):
        assert table_page in _page_window(3, 3, count)


def test_page_window_collapses_an_overlapping_tail() -> None:
    # A head that already reaches the back absorbs the tail — no page is rendered twice,
    # which on a 300 DPI vision read is a real cost, and no index repeats in pages_read.
    assert _page_window(3, 2, 4) == [0, 1, 2, 3]
    assert _page_window(3, 2, 3) == [0, 1, 2]
    assert _page_window(30, 4, 6) == list(range(6))
    window = _page_window(5, 5, 8)
    assert window == sorted(set(window)) == list(range(8))


def test_read_doc_tail_records_the_pages_it_actually_saw() -> None:
    # The tail must show up in BOTH the union and the honest image subset (#613): an
    # artifact that claims a page it never rendered is the failure this whole pair of
    # fields exists to prevent.
    text, images, pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=2,
        image_pages=2,
        dpi=200,
        pdf=_FakePdf(pages=22),  # type: ignore[arg-type]
        text_tail_pages=1,
        image_tail_pages=2,
    )
    assert pages == [0, 1, 20, 21]
    assert image_pages == [0, 1, 20, 21]
    assert len(images) == 4
    # The text tail is narrower than the image tail, and reads its own window only.
    assert "text 21" in text
    assert "text 20" not in text


def test_read_doc_without_a_tail_matches_the_old_prefix_read() -> None:
    # Pin the equivalence directly: pages_read used to be range(max(text, image)), and a
    # no-tail call must still produce exactly that.
    _text, images, pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=6,
        image_pages=1,
        dpi=200,
        pdf=_FakePdf(pages=30),  # type: ignore[arg-type]
    )
    assert pages == list(range(6))
    assert image_pages == [0]
    assert len(images) == 1


def test_read_doc_reads_a_text_less_source_whole_instead_of_its_window() -> None:
    # The head/tail window is a bargain: skip pages because the text layer is still
    # reading them. A pure scan has no text layer, so the same window is the ENTIRE read
    # and the model cannot report the pages it was never shown. Measured on
    # `Metokote_PPG_2021_PPG_Permit.pdf` (24 pages, zero text): 8 rendered, one limit
    # table returned at `confidence: high`, and a warning about a Table 2 it had only
    # seen cross-referenced.
    _text, images, pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=4,
        image_pages=3,
        dpi=200,
        pdf=_FakePdf(pages=24, text=False),  # type: ignore[arg-type]
        text_tail_pages=8,
        image_tail_pages=5,
        scan_image_pages=26,
    )
    assert image_pages == list(range(24))
    assert pages == list(range(24))
    assert len(images) == 24


def test_read_doc_keeps_the_window_when_the_source_carries_text() -> None:
    # The widening must be keyed on the SOURCE, not the genre: the two text-bearing
    # permits in the same production keep the 8-page read `_page_window` was calibrated
    # for, unchanged, at the same spec.
    _text, _images, _pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=4,
        image_pages=3,
        dpi=200,
        pdf=_FakePdf(pages=24, text=True),  # type: ignore[arg-type]
        text_tail_pages=8,
        image_tail_pages=5,
        scan_image_pages=26,
    )
    assert image_pages == [0, 1, 2, 19, 20, 21, 22, 23]


def test_read_doc_scan_budget_is_a_cap_and_truncates_visibly() -> None:
    # `scan_image_pages` is a bound, not a promise. A scan longer than it is still
    # truncated — but in `image_pages_read`, where the next reader can see it, rather
    # than behind a window that looks deliberate.
    _text, _images, _pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=4,
        image_pages=3,
        dpi=200,
        pdf=_FakePdf(pages=40, text=False),  # type: ignore[arg-type]
        image_tail_pages=5,
        scan_image_pages=26,
    )
    assert image_pages == list(range(26))


def test_read_doc_leaves_every_genre_that_declines_the_widening_alone() -> None:
    # scan_image_pages=0 is the default, and fourteen of the sixteen genres take it.
    # A text-less source must then read exactly what it read before this existed.
    _text, _images, _pages, image_pages, _dpi = _read_doc(
        _doc(),
        text_pages=6,
        image_pages=1,
        dpi=200,
        pdf=_FakePdf(pages=30, text=False),  # type: ignore[arg-type]
    )
    assert image_pages == [0]


def test_a_many_image_read_is_rendered_smaller_rather_than_shorter() -> None:
    # Past 20 images in one request the API caps each at 2000px per side, and a Letter
    # page at 200 DPI is 1700x2200 — the request 400s. The answer is fewer pixels, not
    # fewer pages: a dropped page is gone, 181 DPI is legible.
    assert _fitted_dpi(_FakePdf(pages=24), list(range(24)), 200) == 181  # type: ignore[arg-type]
    assert 792 * 181 / 72 <= 2000
    # Under the threshold the requested DPI is untouched, so no existing genre re-renders.
    assert _fitted_dpi(_FakePdf(pages=24), list(range(8)), 200) == 200  # type: ignore[arg-type]
    assert _fitted_dpi(_FakePdf(pages=20), list(range(20)), 300) == 300  # type: ignore[arg-type]


def test_render_backs_off_until_the_request_fits_rather_than_dropping_pages() -> None:
    # Page COUNT and payload SIZE are separate limits. Two 19-page scans of the same
    # template at the same DPI weighed 17.5 MB and 44.0 MB; only the denser one 400s, so
    # size is measured, not predicted, and the retry shrinks the render, not the read.
    pdf = _FakePdf(pages=19, text=False, bytes_per_px2=55.0)  # ~44 MB base64 at 200 DPI
    images, dpi = _render_within_budget(pdf, list(range(19)), 200)  # type: ignore[arg-type]
    assert len(images) == 19  # every page still read
    assert dpi < 200
    assert sum(len(b) for b in images) * 4 // 3 <= _MAX_REQUEST_BYTES


def test_render_leaves_a_request_that_already_fits_completely_alone() -> None:
    pdf = _FakePdf(pages=19, text=False, bytes_per_px2=0.5)
    images, dpi = _render_within_budget(pdf, list(range(19)), 200)  # type: ignore[arg-type]
    assert dpi == 200
    assert len(images) == 19


def test_render_stops_backing_off_at_the_legibility_floor() -> None:
    # An unreadable render is worse than a failed request: the request says so. A
    # document that cannot fit even at the floor is sent anyway and allowed to fail.
    pdf = _FakePdf(pages=40, text=False, bytes_per_px2=5000.0)
    _images, dpi = _render_within_budget(pdf, list(range(40)), 200)  # type: ignore[arg-type]
    assert dpi == _MIN_RENDER_DPI


def test_read_doc_reports_the_dpi_it_actually_rendered_at() -> None:
    # The extraction stamps this into its `dpi` provenance field. An artifact naming a
    # DPI it did not use is the same class of lie as one naming a page it did not read.
    _text, _images, _pages, image_pages, dpi = _read_doc(
        _doc(),
        text_pages=4,
        image_pages=3,
        dpi=200,
        pdf=_FakePdf(pages=24, text=False),  # type: ignore[arg-type]
        image_tail_pages=5,
        scan_image_pages=26,
    )
    assert len(image_pages) == 24
    assert dpi == 181


def test_the_scan_budget_covers_the_longest_permit_the_city_produced() -> None:
    # The budgets are sized against real documents, so pin the documents. The longest
    # text-less IDP in the 2026-09 production is EOLM at 23 pages; the longest annual
    # report is CY2025 at 4 — whose own footer reads "Page 1 of 3".
    assert _IDP_SPEC.scan_image_pages >= 23
    assert _PRETREATMENT_SPEC.scan_image_pages >= 4


def test_extract_deed_attaches_provenance() -> None:
    deed = Deed(
        instrument_type="General Warranty Deed",
        instrument_no="202511180011830",
        grantees=["Anonymous LLC"],
        parcel_ids=["P1", "P2"],
    )
    extraction = extract_deed(_doc(), extractor=_FakeExtractor(deed), pdf=_FakePdf(pages=6))  # type: ignore[arg-type]
    assert isinstance(extraction, DeedExtraction)
    assert extraction.kind == "deed"
    assert extraction.deed.instrument_no == "202511180011830"
    assert extraction.pages_read == list(range(6))  # all 6 pages read
    assert extraction.image_pages_read == list(range(6))  # deed is vision-primary (#613)


def test_extract_npdes_attaches_provenance() -> None:
    permit = NpdesPermit(permit_no="2PH00006*LD", facility_name="American II WWTP")
    extraction = extract_npdes(_doc(), extractor=_FakeExtractor(permit), pdf=_FakePdf(pages=30))  # type: ignore[arg-type]
    assert isinstance(extraction, NpdesExtraction)
    assert extraction.permit.permit_no == "2PH00006*LD"
    assert extraction.pages_read == list(range(6))  # text_pages=6 dominates the 1 image page
    # …but only page 0 was rendered as an image and sent to the model (#613).
    assert extraction.image_pages_read == [0]


def test_extract_sos_attaches_provenance() -> None:
    filing = BusinessFiling(
        entity_name="Tilted Gate LLC",
        entity_type="foreign LLC",
        jurisdiction="Delaware",
        registered_agent="Corporation Service Company",
        organizer="Michael Montfort",
    )
    extraction = extract_sos(_doc(), extractor=_FakeExtractor(filing), pdf=_FakePdf(pages=4))  # type: ignore[arg-type]
    assert isinstance(extraction, SosExtraction)
    assert extraction.kind == "sos"
    assert extraction.filing.jurisdiction == "Delaware"
    assert extraction.pages_read == list(range(4))


def test_extract_epa_attaches_provenance() -> None:
    action = EpaPermitAction(
        agency="Ohio EPA",
        program="Surface Water Permit-to-Install",
        permit_no="DSWPTI-260294",
        action="approved",
        action_date="2026-04-07",
        applicant="Bistrozzi LLC",
        project_name="BOSC-1A",
        contact_name="Scott Ziance",
        contact_firm="Vorys",
    )
    extraction = extract_epa(_doc(), extractor=_FakeExtractor(action), pdf=_FakePdf(pages=5))  # type: ignore[arg-type]
    assert isinstance(extraction, EpaExtraction)
    assert extraction.kind == "epa"
    assert extraction.action.permit_no == "DSWPTI-260294"
    assert extraction.pages_read == list(range(3))  # text_pages=3 dominates the 1 image page


def test_extract_notice_attaches_provenance() -> None:
    notice = NoticeOfCommencement(
        project_name="Project BOSC",
        building_footprint_sf=283497,
        parcel_ids=["36-1200-03-001.000"],
        original_contractors=["Turner Construction Company"],
        contract_execution_date="2025-05-15",
        instrument_no="202606250006699",
    )
    doc = _doc()
    extractor = _FakeExtractor(notice)
    extraction = extract_notice(doc, extractor=extractor, pdf=_FakePdf(pages=21))  # type: ignore[arg-type]
    assert isinstance(extraction, NoticeExtraction)
    assert extraction.kind == "notice"
    assert extraction.doc_id == doc.doc_id
    assert extraction.source_path == str(doc.path)
    assert extraction.dpi == 200  # _NOTICE_DPI; doc is a PDF, not a raster source
    assert extraction.notice.building_footprint_sf == 283497
    assert extraction.notice.contract_execution_date == "2025-05-15"
    # notice is vision-primary but reads only its own substantive pages, not an
    # attached exhibit re-recording prior deeds (#1491) — text_pages=2 dominates
    # the 21-page source.
    assert extraction.pages_read == [0, 1]
    assert extraction.image_pages_read == [0, 1]
    # The extractor received exactly the first 2 pages' text/images (#613: an
    # honest image_pages_read means the model only ever saw what's recorded there).
    assert len(extractor.calls) == 1
    assert extractor.calls[0]["images"] == [b"\x89PNG-fake", b"\x89PNG-fake"]
    assert extractor.calls[0]["context"] == "text 0\n\ntext 1"


def test_extract_document_dispatch_and_unknown() -> None:
    permit = NpdesPermit(permit_no="X")
    ex = extract_document(_doc(), kind="npdes", extractor=_FakeExtractor(permit), pdf=_FakePdf())  # type: ignore[arg-type]
    assert isinstance(ex, NpdesExtraction)
    filing = BusinessFiling(entity_name="Acme LLC")
    sos = extract_document(
        _doc(), kind="sos", extractor=_FakeExtractor(filing), pdf=_FakePdf(pages=4)
    )  # type: ignore[arg-type]
    assert isinstance(sos, SosExtraction)
    with pytest.raises(ValueError, match="unknown document kind"):
        extract_document(_doc(), kind="invoice")


def test_save_doc_extraction_filename(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    extraction = NpdesExtraction(
        doc_id="d",
        source_path="/x/oepa-2PH00006-american-ii-permit.pdf",
        kind="npdes",
        dpi=150,
        permit=NpdesPermit(permit_no="2PH00006"),
    )
    path = save_doc_extraction(extraction, settings=settings)
    # Source lives outside data/documents -> lands at the extracted root.
    assert path.parent == settings.extracted_dir
    assert path.name == "oepa-2PH00006-american-ii-permit.npdes.yaml"
    data = yaml.safe_load(path.read_text())
    assert data["permit"]["permit_no"] == "2PH00006"


def test_save_doc_extraction_mirrors_collection(tmp_path: Path) -> None:
    """A source under documents/<collection> lands under extracted/<collection>."""
    settings = Settings(data_dir=tmp_path)
    src = settings.documents_dir / "recorder" / "202511180011830-amazon-deed.pdf"
    src.parent.mkdir(parents=True)
    src.write_bytes(b"%PDF-fake")
    extraction = DeedExtraction(
        doc_id="d",
        source_path=str(src),
        kind="deed",
        dpi=200,
        deed=Deed(instrument_no="202511180011830"),
    )
    path = save_doc_extraction(extraction, settings=settings)
    assert path.parent == settings.extracted_dir / "recorder"
    assert path.name == "202511180011830-amazon-deed.deed.yaml"


# --- raster image sources (#703) -------------------------------------------
def _img_doc(path: Path) -> SourceDocument:
    return SourceDocument(path=path, doc_id="img-1234", suffix=path.suffix.lower(), size_bytes=0)


def test_image_suffixes_are_admitted_to_the_extraction_inventory() -> None:
    # #619 dropped images from the inventory because no path existed; #703 re-admits them.
    assert IMAGE_SUFFIXES <= SOURCE_SUFFIXES
    assert {".png", ".jpg", ".jpeg", ".tif", ".tiff"} <= SOURCE_SUFFIXES
    assert _img_doc(Path("/x/scan.png")).is_image
    assert not _img_doc(Path("/x/scan.png")).is_pdf
    assert not _doc().is_image  # a .pdf is not an image


def test_read_image_png_reencodes_non_png_to_png(tmp_path: Path) -> None:
    # A .jpg / .tif source must come back as valid PNG bytes (the extractor pins image/png).
    for name, fmt in [("scan.jpg", "JPEG"), ("scan.tif", "TIFF")]:
        src = tmp_path / name
        Image.new("RGB", (8, 8), (200, 100, 50)).save(src, format=fmt)
        out = read_image_png(src)
        assert out[:8] == b"\x89PNG\r\n\x1a\n"  # PNG signature
        assert Image.open(io.BytesIO(out)).format == "PNG"


def test_read_image_png_flattens_cmyk_and_alpha(tmp_path: Path) -> None:
    # CMYK TIFF and RGBA PNG modes flatten to RGB rather than failing the PNG encode.
    cmyk = tmp_path / "cmyk.tif"
    Image.new("CMYK", (4, 4)).save(cmyk, format="TIFF")
    rgba = tmp_path / "alpha.png"
    Image.new("RGBA", (4, 4), (1, 2, 3, 128)).save(rgba, format="PNG")
    for src in (cmyk, rgba):
        assert Image.open(io.BytesIO(read_image_png(src))).mode == "RGB"


def test_extract_deed_from_image_source_sends_raw_image_no_text(tmp_path: Path) -> None:
    # The headline #703 path: a .png scan extracts through the same extract_deed as a PDF,
    # but with the single image and NO OCR text hint, and an honest dpi=0.
    src = tmp_path / "deed-scan.png"
    Image.new("RGB", (16, 16), (255, 255, 255)).save(src, format="PNG")
    deed = Deed(instrument_no="202511180011830", grantees=["Anonymous LLC"])
    extractor = _FakeExtractor(deed)
    extraction = extract_deed(_img_doc(src), extractor=extractor)  # type: ignore[arg-type]

    assert isinstance(extraction, DeedExtraction)
    assert extraction.deed.instrument_no == "202511180011830"
    assert extraction.pages_read == [0]
    assert extraction.image_pages_read == [0]
    assert extraction.dpi == 0  # a raster source isn't rendered at a DPI
    # the extractor saw exactly one image and no text hint
    (call,) = extractor.calls
    assert call["context"] == ""
    assert call["images"] is not None and len(call["images"]) == 1
    assert call["images"][0][:8] == b"\x89PNG\r\n\x1a\n"


# --- the municipal-pretreatment genres (#2172) ------------------------------
def test_extract_idp_reads_the_appendix_and_records_which_pages() -> None:
    # The whole reason the genre exists: a 22-page City permit whose limits tables are at the
    # back. Head 3 + tail 5 must reach pages 17-21 and say so, so a short read is detectable.
    permit = IndustrialDischargePermit(
        permittee="The Procter & Gamble Company",
        permit_no="PGM*011",
        limit_tables=[LimitTable(kind="local", appendix="Appendix B", table_no="Table 1")],
    )
    extractor = _FakeExtractor(permit)
    extraction = extract_idp(_doc(), extractor=extractor, pdf=_FakePdf(pages=22))  # type: ignore[arg-type]

    assert isinstance(extraction, IdpExtraction)
    assert extraction.industrial_permit.permit_no == "PGM*011"
    assert extraction.image_pages_read == [0, 1, 2, 17, 18, 19, 20, 21]
    # text_pages=4 + text_tail_pages=8 widens the union past the rendered set: the text layer is
    # cheap, so the genre takes a wider tail of it than it pays to rasterize.
    assert extraction.pages_read == [0, 1, 2, 3, *range(14, 22)]
    (call,) = extractor.calls
    assert call["images"] is not None and len(call["images"]) == 8


def test_extract_idp_on_a_permit_shorter_than_its_budget_reads_each_page_once() -> None:
    # A 5-page permit: head 3 and tail 5 overlap completely. Nothing is rendered twice.
    extraction = extract_idp(
        _doc(),
        extractor=_FakeExtractor(IndustrialDischargePermit(permittee="Nickles Bakery")),  # type: ignore[arg-type]
        pdf=_FakePdf(pages=5),
    )
    assert extraction.image_pages_read == [0, 1, 2, 3, 4]


def test_industrial_permit_limit_cells_survive_as_printed() -> None:
    # The three non-numeric states a limits cell actually takes. None of them may become None:
    # "Monitor" is an obligation, "n/a" is its absence, and a pH range is neither.
    table = LimitTable(
        kind="categorical",
        appendix="Appendix A",
        table_no="Table 2",
        authority="40 CFR 442 Subpart A",
        sample_stations=["LTW 01"],
        columns=["Pollutant", "Daily Maximum", "Monthly Average"],
        limits=[
            PollutantLimit(pollutant="Total Copper", daily_maximum="0.42", monthly_average="0.21"),
            PollutantLimit(pollutant="Total Zinc", daily_maximum="Monitor"),
            PollutantLimit(pollutant="Total Cyanide", daily_maximum="n/a"),
            PollutantLimit(pollutant="pH", daily_maximum="6.0 to 11.0", unit="pH units"),
        ],
    )
    cells = {limit.pollutant: limit.daily_maximum for limit in table.limits}
    assert cells == {
        "Total Copper": "0.42",
        "Total Zinc": "Monitor",
        "Total Cyanide": "n/a",
        "pH": "6.0 to 11.0",
    }
    # A categorical table's second column is a MONTHLY AVERAGE and must not land in the local
    # table's instantaneous-maximum field, which tolerates no excursion at all.
    copper = table.limits[0]
    assert copper.monthly_average == "0.21"
    assert copper.instantaneous_maximum is None


def test_extract_pretreatment_attaches_provenance() -> None:
    report = PretreatmentAnnualReport(
        reporting_authority="City of Lima",
        npdes_permit_no="2PE00000*PD",
        reporting_period="CY2023",
        significant_industrial_users=15,
        effective_control_documents=9,
        attachments=["2023 IU Report Form_City of Lima.xlsm"],
    )
    extraction = extract_pretreatment(
        _doc(), extractor=_FakeExtractor(report), pdf=_FakePdf(pages=3)
    )  # type: ignore[arg-type]
    assert isinstance(extraction, PretreatmentExtraction)
    # The gap this genre exists to make answerable: more SIUs than control documents.
    assert extraction.pretreatment_report.significant_industrial_users == 15
    assert extraction.pretreatment_report.effective_control_documents == 9
    assert extraction.pages_read == [0, 1, 2]  # read whole; the form IS the summary table


def test_pretreatment_report_keeps_a_printed_zero_distinct_from_a_blank() -> None:
    # A reported 0 is a finding ("no SIU was in significant non-compliance"); a blank is the
    # program not answering. Collapsing them would publish the flattering reading of a silence.
    report = PretreatmentAnnualReport(users_in_snc=0)
    assert report.users_in_snc == 0
    assert PretreatmentAnnualReport().users_in_snc is None


def test_a_summary_row_that_pairs_two_figures_survives_as_the_pair() -> None:
    # Lima's CY2023 form prints "Number of SIU's in SNC (Categorical/Non-Categorical): 0/0"
    # and "Amount of Penalties Collected (Total dollars/# IU's assessed): $0.00" — one cell
    # answering a two-part question. Until this, `count: Number` REJECTED "0/0" and the whole
    # read failed validation, which is how three annual reports went unextracted. The cell is
    # kept verbatim rather than halved or summed: the POTW asserted a pair, not a total.
    rows = [
        ProgramCount(
            label="Number of SIU's in SNC (Categorical/Non-Categorical)", count_as_printed="0/0"
        ),
        ProgramCount(label="Users inspected", count=10),
    ]
    assert rows[0].count is None and rows[0].count_as_printed == "0/0"
    # A row that IS a plain number still lands in `count`; the verbatim field is not a
    # substitute for one, so a count stays comparable across reporting years.
    assert rows[1].count == 10


def test_a_paired_cell_is_found_by_a_null_count_not_by_the_verbatim_field() -> None:
    # Asserted over the committed reads rather than hand-built rows, because the thing at
    # risk is a property of what the extractor actually writes: it fills `count_as_printed`
    # for EVERY row, plain numbers included. So the verbatim field does not discriminate,
    # and a consumer filtering on it being set would select all thirteen rows and conclude
    # the form holds no numbers at all. `count is None` is the signal, and it is a stable
    # one — the same two cells are paired in all three reporting years.
    reports = sorted((REPO_ROOT / "data" / "extracted" / "legal").glob("*.pretreatment.yaml"))
    assert len(reports) == 3, "expected the CY2023-CY2025 Lima pretreatment series"
    for path in reports:
        report = yaml.safe_load(path.read_text())["pretreatment_report"]
        rows = (report.get("counts") or []) + (report.get("enforcement_actions") or [])
        paired = [r for r in rows if r.get("count") is None]
        assert [r["label"] for r in paired] == [
            "Number of SIU's in SNC (Categorical/Non-Categorical)",
            "Amount of Penalties Collected (Total dollars/# IU's assessed)",
        ], f"{path.name}: the paired cells moved"
        # Each survives as the pair the City printed, never halved or summed to a total.
        assert [r["count_as_printed"] for r in paired] == ["0/0", "$0.00"]
        # And the scalar the form asks for separately stays null rather than taking a half.
        assert report["users_in_snc"] is None


def test_a_permit_extension_is_not_routed_through_a_permit_or_an_agency_model() -> None:
    # The four Lima extension letters were first read as `notice` (R.C. 1311.04 Notice of
    # Commencement). The model correctly refused, and the refusal cost everything: four
    # extractions with every field null and the operative dates surviving only as prose in
    # `note`. The two dates a letter carries are different facts and must both survive.
    ext = PermitExtension(
        issuing_authority="City of Lima Department of Utilities",
        permittee="Procter & Gamble Manufacturing Co.",
        facility="P&G Main Facility",
        letter_date="2026-07-08",
        extended_to="2026-09-13",
        signatory="Amy Staley",
    )
    assert ext.letter_date != ext.extended_to
    # A letter that prints no permit number leaves it null. Filling it from a sibling
    # document would assert an identification the City never made on this page.
    assert ext.permit_no is None


def test_a_permit_extension_dispatches_by_kind() -> None:
    extraction = extract_document(
        _doc(),
        kind="permit-extension",
        extractor=_FakeExtractor(PermitExtension(extended_to="2026-09-11")),  # type: ignore[arg-type]
        pdf=_FakePdf(pages=1),
    )
    assert isinstance(extraction, PermitExtensionExtraction)
    assert extraction.kind == "permit-extension"
    assert extraction.permit_extension.extended_to == "2026-09-11"


def test_both_new_genres_dispatch_by_kind() -> None:
    for kind, result, cls in (
        ("idp", IndustrialDischargePermit(permittee="Ford Lima Engine Plant"), IdpExtraction),
        (
            "pretreatment",
            PretreatmentAnnualReport(reporting_period="CY2025"),
            PretreatmentExtraction,
        ),
    ):
        extraction = extract_document(
            _doc(),
            kind=kind,
            extractor=_FakeExtractor(result),  # type: ignore[arg-type]
            pdf=_FakePdf(pages=20),
        )
        assert isinstance(extraction, cls)
        assert extraction.kind == kind
