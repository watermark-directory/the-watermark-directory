"""Stage 1 — ingest.

Discover source documents under ``data/documents`` and produce a manifest of
:class:`SourceDocument` records. This stage deliberately does *no* parsing; it
just inventories what raw material exists so later stages have a stable handle.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from watermark.config import Settings, get_settings
from watermark.documents import IMAGE_SUFFIXES
from watermark.logging import get_logger

log = get_logger(__name__)

# Extensions the extract stage can actually read: PDF (pdfium render + pypdf text),
# OpenDocument Drawing (read_odg), and raster scans (read_image_png → straight to the
# vision model, no text layer; #703). `discover` is the *extraction* inventory, so it
# admits only what has an extractor path. Discovery only inventories — extraction is
# kind-dispatched (`extract_document(doc, kind=…)`), so an admitted image isn't
# auto-extracted; it just becomes a handle. A `.txt` source has no vision path and stays
# out. (Reference/evidence files under data/documents/ remain immutable corpus and are
# surfaced by the site documents feed, which walks the tree independently.)
SOURCE_SUFFIXES = {".pdf", ".odg", *IMAGE_SUFFIXES}


@dataclass(frozen=True)
class SourceDocument:
    """A raw source document discovered during ingest."""

    path: Path
    doc_id: str
    suffix: str
    size_bytes: int
    collection: str = field(default="")

    @property
    def is_pdf(self) -> bool:
        return self.suffix == ".pdf"

    @property
    def is_image(self) -> bool:
        """A raster source (.png/.jpg/.tif) read straight into the vision model (#703)."""
        return self.suffix in IMAGE_SUFFIXES


def _doc_id(path: Path) -> str:
    """Stable short id from the path (not the contents — files may be huge)."""
    digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    return f"{path.stem}-{digest[:8]}"


def discover(settings: Settings | None = None) -> list[SourceDocument]:
    """Walk ``documents_dir`` and return a manifest of source documents.

    ``collection`` is the first sub-directory under ``documents`` (e.g.
    ``aedg``), letting you group documents by their origin/request batch.
    """
    settings = settings or get_settings()
    root = settings.documents_dir
    if not root.exists():
        log.warning("documents_dir missing", path=str(root))
        return []

    docs: list[SourceDocument] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        collection = rel.parts[0] if len(rel.parts) > 1 else ""
        docs.append(
            SourceDocument(
                path=path,
                doc_id=_doc_id(path),
                suffix=path.suffix.lower(),
                size_bytes=path.stat().st_size,
                collection=collection,
            )
        )
    log.info("ingest.discovered", count=len(docs), root=str(root))
    return docs
