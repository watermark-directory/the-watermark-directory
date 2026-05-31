"""Stage 2 — extract.

Turn a scanned cost-estimate page into a reviewed, structured extraction.

The flow is **hybrid** (see the read-mode decision):

1. Pull the page's embedded OCR text via :class:`PdfDocument` — a cheap
   *structural* hint (section names, item ordering). Its digits are unreliable.
2. Render the page to a 300 DPI image — the *authoritative* source.
3. Resolve a format :class:`~bosc.profiles.Profile` (explicit or auto-detected
   from the OCR text), build its prompt, and force a Claude model to populate a
   contractor-agnostic :class:`~bosc.models.Estimate` (tool use + validation).
4. Wrap the result with provenance into a :class:`PageExtraction`.

Extraction is dispatched by *document kind* (``opc`` today) via
:data:`EXTRACTORS`, leaving room for other public-records genres later.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from bosc import profiles
from bosc.config import Settings, get_settings
from bosc.documents import DEFAULT_DPI, PdfDocument
from bosc.logging import get_logger
from bosc.models import (
    BusinessFiling,
    Deed,
    DeedExtraction,
    DocExtraction,
    EpaExtraction,
    EpaPermitAction,
    Estimate,
    NpdesExtraction,
    NpdesPermit,
    OPCSummary,
    PageExtraction,
    SosExtraction,
)
from bosc.pipeline.ingest import SourceDocument

if TYPE_CHECKING:
    # Imported lazily at call time to avoid a bosc.agent <-> bosc.pipeline cycle.
    from bosc.agent.extractor import StructuredExtractor

log = get_logger(__name__)

# Token budgets: detail extractions can carry dozens of line items.
_SUMMARY_MAX_TOKENS = 4096
_DETAIL_MAX_TOKENS = 8192


def _read_page(
    doc: SourceDocument, page_index: int, dpi: int, pdf: PdfDocument | None
) -> tuple[str, bytes]:
    """Return ``(ocr_text, png_bytes)`` for a page, closing only a pdf we opened."""
    owns_pdf = pdf is None
    pdf = pdf or PdfDocument(doc.path, dpi=dpi)
    try:
        return pdf.page_text(page_index), pdf.render_page_png(page_index, dpi=dpi)
    finally:
        if owns_pdf:
            pdf.close()


def extract_opc_page(
    doc: SourceDocument,
    page_index: int,
    *,
    profile: str | None = None,
    detail: bool = False,
    extractor: StructuredExtractor | None = None,
    pdf: PdfDocument | None = None,
    dpi: int = DEFAULT_DPI,
    settings: Settings | None = None,
) -> PageExtraction:
    """Extract one Opinion-of-Probable-Cost page into a validated :class:`PageExtraction`.

    ``profile`` is a profile id, ``"auto"``/``None`` to auto-detect from the page,
    and ``detail`` toggles full line-item extraction. ``pdf``/``extractor`` are
    injectable for reuse across pages and for tests.
    """
    from bosc.agent.extractor import StructuredExtractor

    settings = settings or get_settings()
    max_tokens = _DETAIL_MAX_TOKENS if detail else _SUMMARY_MAX_TOKENS
    extractor = extractor or StructuredExtractor(settings=settings, max_tokens=max_tokens)

    text, image = _read_page(doc, page_index, dpi, pdf)
    prof = profiles.resolve(profile, text)

    log.info(
        "extract.page.start",
        doc_id=doc.doc_id,
        page_index=page_index,
        dpi=dpi,
        profile=prof.id,
        detail=detail,
    )
    estimate = extractor.extract(
        Estimate,
        instructions=prof.prompt(detail=detail),
        image_png=image,
        context_text=text,
    )
    estimate.profile = prof.id

    extraction = PageExtraction(
        doc_id=doc.doc_id,
        source_path=str(doc.path),
        page_index=page_index,
        pdf_page=page_index + 1,
        dpi=dpi,
        estimate=estimate,
        source_text_excerpt=text[:600],
    )
    log.info(
        "extract.page.done",
        doc_id=doc.doc_id,
        page_index=page_index,
        profile=prof.id,
        name=estimate.name,
        sections=len(estimate.sections),
        confidence=estimate.confidence,
        reconciles=estimate.reconciles(),
        warnings=len(estimate.warnings),
    )
    return extraction


# Document-kind dispatch. Add other public-records genres here later.
PageExtractor = Callable[..., PageExtraction]
EXTRACTORS: dict[str, PageExtractor] = {"opc": extract_opc_page}


def extract_page(
    doc: SourceDocument, page_index: int, *, kind: str = "opc", **kwargs: object
) -> PageExtraction:
    """Dispatch a page extraction to the handler for ``kind`` (default ``opc``)."""
    if kind not in EXTRACTORS:
        raise ValueError(f"unknown document kind {kind!r}; known: {sorted(EXTRACTORS)}")
    return EXTRACTORS[kind](doc, page_index, **kwargs)


def _collection_dir(source_path: str, settings: Settings) -> Path:
    """Sub-directory of ``extracted`` mirroring the source's collection.

    The extracted tree parallels ``data/documents``: an artifact lands under the
    same first-level collection as its source (e.g. ``recorder``, ``oepa``),
    mirroring :func:`ingest.discover` (``collection = rel.parts[0]``). Sources that
    sit directly under ``documents`` — or outside it entirely (tests) — map to the
    root of ``extracted``. The directory is created.
    """
    target = settings.extracted_dir
    try:
        rel = Path(source_path).resolve().relative_to(settings.documents_dir.resolve())
    except ValueError:
        rel = None
    if rel is not None and len(rel.parts) > 1:
        target = target / rel.parts[0]
    target.mkdir(parents=True, exist_ok=True)
    return target


def save_extraction(extraction: PageExtraction, *, settings: Settings | None = None) -> Path:
    """Write a page extraction to ``data/extracted`` as YAML; return the path.

    The file lands under a collection sub-directory mirroring its source (see
    :func:`_collection_dir`). Files with line items get a ``.detail.opc.yaml``
    suffix; subtotal-only ones get ``.opc.yaml``.
    """
    settings = settings or get_settings()
    target = _collection_dir(extraction.source_path, settings)
    kind = "detail.opc" if extraction.estimate.has_line_items() else "opc"
    slug = extraction.estimate.name.lower().replace("/", "-").replace(" ", "_")
    path = target / f"{slug}.p{extraction.pdf_page}.{kind}.yaml"
    path.write_text(extraction.to_yaml(), encoding="utf-8")
    log.info("extract.saved", path=str(path))
    return path


def validate_summary(path: str | Path) -> OPCSummary:
    """Load and validate an assembled summary extraction (legacy Tetra Tech shape)."""
    summary = OPCSummary.from_yaml(path)
    log.info("extract.validated", path=str(path), sub_estimates=len(summary.sub_estimates))
    return summary


# ---------------------------------------------------------------------------
# Document-level extraction (deeds, NPDES permits).
#
# Unlike OPC sheets (one estimate per page), these read across the first several
# pages of a document and produce one record. Deeds are usually scanned (vision-
# primary); NPDES fact sheets have clean text layers (text-primary).
# ---------------------------------------------------------------------------

_DEED_DPI = 200
_NPDES_DPI = 150
_SOS_DPI = 200
_EPA_DPI = 150

DEED_INSTRUCTIONS = """\
You are reading a recorded land instrument (a deed, easement, or similar) from a
county recorder. The page images are authoritative; the OCR text layer may be
absent or garbled. Record into the tool:
  * instrument_type: e.g. "General Warranty Deed", "Quitclaim Deed", "Easement".
  * instrument_no: the recorder's instrument / document number (often stamped at
    the top of page 1).
  * recording_date: ISO yyyy-mm-dd if legible.
  * grantors: the party/parties conveying; grantees: the party/parties receiving.
    List each name exactly as printed.
  * consideration: the stated dollar amount (e.g. "for the sum of $..."); null if
    nominal or not stated.
  * parcel_ids: auditor's / permanent parcel numbers.
  * county; legal_description: a SHORT summary or the opening line only (do NOT
    transcribe the full metes-and-bounds).
Rules: read names and numbers carefully; if a field is illegible, give your best
read AND add a warning naming it; never invent parties or parcels; set confidence.
"""

NPDES_INSTRUCTIONS = """\
You are reading an Ohio EPA NPDES discharge permit or fact sheet. The text layer
is generally reliable for this document, but verify against the page image.
Record into the tool:
  * facility_name; permit_no exactly as printed (e.g. 2PH00006*LD);
    permit_action: one of renewal | modification | new | draft.
  * applicant; application_no (e.g. OH0037338).
  * public_notice_no; public_notice_date; comment_period_end (ISO dates).
  * facility_address (where the discharge occurs); discharge_address if distinct.
  * receiving_water; stream_network: the downstream chain if stated
    (e.g. "Ottawa River to Auglaize River to Maumee River to Lake Erie").
  * outfalls: outfall identifiers if listed.
Rules: copy permit/application numbers exactly; dates as ISO; leave a field null
if not present; never invent; set confidence and warnings.
"""


SOS_INSTRUCTIONS = """\
You are reading a Secretary of State business filing (e.g. an Ohio Articles of
Organization for a domestic LLC, or a Registration of a Foreign LLC). The page
images are authoritative; the text layer is usually just a stamped document id.
Record into the tool:
  * entity_name: the LLC / business name exactly as printed.
  * filing_id: the SoS document / filing number (often stamped "DOC ID" or at the
    top of the form).
  * filing_type: e.g. "Articles of Organization", "Registration of a Foreign
    Limited Liability Company".
  * entity_type: "domestic LLC", "foreign LLC", etc.
  * jurisdiction: the formation state. For a foreign registration this is the
    home state (e.g. Delaware); for a domestic Ohio filing this is Ohio.
  * filing_date and effective_date: ISO yyyy-mm-dd if legible.
  * registered_agent: the statutory / registered agent NAME; agent_address: their
    address. (A commercial agent such as "CT Corporation System" is common.)
  * organizer: the organizer / authorized representative / signer NAME;
    organizer_address if shown.
  * principal_address: the principal office address, if stated.
  * officers: any members / managers / officers disclosed (Ohio often discloses
    none — leave empty rather than guessing).
Rules: copy names and the filing id exactly; dates as ISO; leave a field null if
not present; NEVER invent an agent, organizer, or officer; set confidence and add
a warning for any field you had to strain to read.
"""


EPA_INSTRUCTIONS = """\
You are reading an Ohio EPA (Division of Surface Water) or U.S. Army Corps of
Engineers permit action or correspondence letter for a development project. The
text layer is reliable; verify against the page image. These letters carry a
header "Re:" block (applicant, permit type, program, county, permit number) and a
"Subject:" line. Record into the tool:
  * agency (e.g. "Ohio EPA", "U.S. Army Corps of Engineers");
    program: the permit program — e.g. "Surface Water Permit-to-Install",
    "401 Water Quality Certification", "Isolated Wetland Permit", "Section 404".
  * permit_no exactly as printed (e.g. DSWPTI-260294, DSW401252260W, or an
    "Ohio EPA ID No." like 252260W).
  * action: what the letter does — one of issued | approved | denied | incomplete
    | comments | application | correspondence.
  * action_date: the letter date (ISO); plans_received_date; expiration_date if any.
  * applicant and applicant_address (copy the mailing address as printed).
  * contact_name: the addressee or submitter; contact_email; contact_firm (the
    law firm or engineering firm, e.g. Vorys, EMH&T) if discernible.
  * project_name (e.g. "Project Bosc", "BOSC-1A"); site_address;
    affected_resource (e.g. "private sanitary sewer", "isolated wetland").
  * parcel_ids if listed.
Rules: copy permit numbers, names, and the address exactly; dates as ISO; leave a
field null if absent; never invent; set confidence and add warnings for strained
reads.
"""


def _read_doc(
    doc: SourceDocument,
    *,
    text_pages: int,
    image_pages: int,
    dpi: int,
    pdf: PdfDocument | None,
) -> tuple[str, list[bytes], list[int]]:
    """Read the first pages of a document: ``(text, page_images, pages_touched)``."""
    owns_pdf = pdf is None
    pdf = pdf or PdfDocument(doc.path, dpi=dpi)
    try:
        n_text = min(text_pages, pdf.page_count)
        n_img = min(image_pages, pdf.page_count)
        text = "\n\n".join(pdf.page_text(i) for i in range(n_text))
        images = [pdf.render_page_png(i, dpi=dpi) for i in range(n_img)]
        return text, images, list(range(max(n_text, n_img)))
    finally:
        if owns_pdf:
            pdf.close()


def extract_deed(
    doc: SourceDocument,
    *,
    extractor: StructuredExtractor | None = None,
    pdf: PdfDocument | None = None,
    dpi: int = _DEED_DPI,
    settings: Settings | None = None,
    max_pages: int = 8,
) -> DeedExtraction:
    """Extract a recorded deed (vision-primary across its first pages)."""
    from bosc.agent.extractor import StructuredExtractor

    settings = settings or get_settings()
    extractor = extractor or StructuredExtractor(settings=settings, max_tokens=4096)
    text, images, pages = _read_doc(
        doc, text_pages=max_pages, image_pages=max_pages, dpi=dpi, pdf=pdf
    )

    log.info("extract.doc.start", doc_id=doc.doc_id, kind="deed", pages=len(pages), dpi=dpi)
    deed = extractor.extract(Deed, instructions=DEED_INSTRUCTIONS, images=images, context_text=text)
    extraction = DeedExtraction(
        doc_id=doc.doc_id,
        source_path=str(doc.path),
        kind="deed",
        pages_read=pages,
        dpi=dpi,
        deed=deed,
        source_text_excerpt=text[:600],
    )
    log.info(
        "extract.doc.done",
        doc_id=doc.doc_id,
        kind="deed",
        grantees=len(deed.grantees),
        parcels=len(deed.parcel_ids),
        confidence=deed.confidence,
        warnings=len(deed.warnings),
    )
    return extraction


def extract_npdes(
    doc: SourceDocument,
    *,
    extractor: StructuredExtractor | None = None,
    pdf: PdfDocument | None = None,
    dpi: int = _NPDES_DPI,
    settings: Settings | None = None,
    text_pages: int = 6,
) -> NpdesExtraction:
    """Extract an NPDES permit / fact sheet (text-primary, page-1 image as backup)."""
    from bosc.agent.extractor import StructuredExtractor

    settings = settings or get_settings()
    extractor = extractor or StructuredExtractor(settings=settings, max_tokens=4096)
    text, images, pages = _read_doc(doc, text_pages=text_pages, image_pages=1, dpi=dpi, pdf=pdf)

    log.info("extract.doc.start", doc_id=doc.doc_id, kind="npdes", pages=len(pages), dpi=dpi)
    permit = extractor.extract(
        NpdesPermit, instructions=NPDES_INSTRUCTIONS, images=images, context_text=text
    )
    extraction = NpdesExtraction(
        doc_id=doc.doc_id,
        source_path=str(doc.path),
        kind="npdes",
        pages_read=pages,
        dpi=dpi,
        permit=permit,
        source_text_excerpt=text[:600],
    )
    log.info(
        "extract.doc.done",
        doc_id=doc.doc_id,
        kind="npdes",
        permit_no=permit.permit_no,
        facility=permit.facility_name,
        confidence=permit.confidence,
        warnings=len(permit.warnings),
    )
    return extraction


def extract_sos(
    doc: SourceDocument,
    *,
    extractor: StructuredExtractor | None = None,
    pdf: PdfDocument | None = None,
    dpi: int = _SOS_DPI,
    settings: Settings | None = None,
    max_pages: int = 6,
) -> SosExtraction:
    """Extract a Secretary-of-State business filing (vision-primary)."""
    from bosc.agent.extractor import StructuredExtractor

    settings = settings or get_settings()
    extractor = extractor or StructuredExtractor(settings=settings, max_tokens=4096)
    text, images, pages = _read_doc(
        doc, text_pages=max_pages, image_pages=max_pages, dpi=dpi, pdf=pdf
    )

    log.info("extract.doc.start", doc_id=doc.doc_id, kind="sos", pages=len(pages), dpi=dpi)
    filing = extractor.extract(
        BusinessFiling, instructions=SOS_INSTRUCTIONS, images=images, context_text=text
    )
    extraction = SosExtraction(
        doc_id=doc.doc_id,
        source_path=str(doc.path),
        kind="sos",
        pages_read=pages,
        dpi=dpi,
        filing=filing,
        source_text_excerpt=text[:600],
    )
    log.info(
        "extract.doc.done",
        doc_id=doc.doc_id,
        kind="sos",
        entity=filing.entity_name,
        agent=filing.registered_agent,
        jurisdiction=filing.jurisdiction,
        confidence=filing.confidence,
        warnings=len(filing.warnings),
    )
    return extraction


def extract_epa(
    doc: SourceDocument,
    *,
    extractor: StructuredExtractor | None = None,
    pdf: PdfDocument | None = None,
    dpi: int = _EPA_DPI,
    settings: Settings | None = None,
    text_pages: int = 3,
) -> EpaExtraction:
    """Extract an Ohio EPA / USACE permit action letter (text-first, page-1 image)."""
    from bosc.agent.extractor import StructuredExtractor

    settings = settings or get_settings()
    extractor = extractor or StructuredExtractor(settings=settings, max_tokens=4096)
    text, images, pages = _read_doc(doc, text_pages=text_pages, image_pages=1, dpi=dpi, pdf=pdf)

    log.info("extract.doc.start", doc_id=doc.doc_id, kind="epa", pages=len(pages), dpi=dpi)
    action = extractor.extract(
        EpaPermitAction, instructions=EPA_INSTRUCTIONS, images=images, context_text=text
    )
    extraction = EpaExtraction(
        doc_id=doc.doc_id,
        source_path=str(doc.path),
        kind="epa",
        pages_read=pages,
        dpi=dpi,
        action=action,
        source_text_excerpt=text[:600],
    )
    log.info(
        "extract.doc.done",
        doc_id=doc.doc_id,
        kind="epa",
        program=action.program,
        permit_no=action.permit_no,
        applicant=action.applicant,
        confidence=action.confidence,
        warnings=len(action.warnings),
    )
    return extraction


# Document-level kind dispatch (parallel to the page-level EXTRACTORS above).
DocumentExtractor = Callable[..., DocExtraction]
DOC_EXTRACTORS: dict[str, DocumentExtractor] = {
    "deed": extract_deed,
    "npdes": extract_npdes,
    "sos": extract_sos,
    "epa": extract_epa,
}


def extract_document(doc: SourceDocument, *, kind: str, **kwargs: object) -> DocExtraction:
    """Dispatch a document-level extraction to the handler for ``kind``."""
    if kind not in DOC_EXTRACTORS:
        raise ValueError(f"unknown document kind {kind!r}; known: {sorted(DOC_EXTRACTORS)}")
    return DOC_EXTRACTORS[kind](doc, **kwargs)


def save_doc_extraction(extraction: DocExtraction, *, settings: Settings | None = None) -> Path:
    """Write a document-level extraction under its collection sub-directory.

    The artifact mirrors its source's collection (see :func:`_collection_dir`),
    named ``<stem>.<kind>.yaml``.
    """
    settings = settings or get_settings()
    target = _collection_dir(extraction.source_path, settings)
    stem = Path(extraction.source_path).stem
    path = target / f"{stem}.{extraction.kind}.yaml"
    path.write_text(extraction.to_yaml(), encoding="utf-8")
    log.info("extract.saved", path=str(path))
    return path
