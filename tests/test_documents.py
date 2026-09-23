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
    PollutantLimit,
    PretreatmentAnnualReport,
    PretreatmentExtraction,
    SosExtraction,
)
from watermark.pipeline.extract import (
    _page_window,
    _read_doc,
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
    def __init__(self, pages: int = 3) -> None:
        self._n = pages

    @property
    def page_count(self) -> int:
        return self._n

    def page_text(self, index: int) -> str:
        return f"text {index}"

    def render_page_png(self, index: int, *, dpi: int | None = None) -> bytes:
        return b"\x89PNG-fake"

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
    text, images, pages, image_pages = _read_doc(
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
    _text, images, pages, image_pages = _read_doc(
        _doc(),
        text_pages=6,
        image_pages=1,
        dpi=200,
        pdf=_FakePdf(pages=30),  # type: ignore[arg-type]
    )
    assert pages == list(range(6))
    assert image_pages == [0]
    assert len(images) == 1


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
