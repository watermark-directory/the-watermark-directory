"""Corpus ingestion: chunk source documents, reference data, and extracted YAMLs (#809).

Yields :class:`~watermark.retrieval.store.Chunk` objects for each indexed fragment.
The full source document tree is indexed (not just extracted artifacts) so the agent
can surface genuinely unextracted context and report it as a lead rather than silently
missing it.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from watermark.retrieval.store import Chunk

_MAX_CHUNK_CHARS = 4_000
_CORPUS_HOME = "lima"


def _chunk_id(*parts: str) -> str:
    return "::".join(parts)


def _split_text(text: str, *, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    """Split *text* on paragraph boundaries into chunks of at most *max_chars*."""
    if len(text) <= max_chars:
        return [text]
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        if current_len + len(para) > max_chars and current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para) + 2  # account for \n\n
    if current:
        chunks.append("\n\n".join(current))
    return chunks or [text[:max_chars]]


def _prov(**kw: Any) -> dict[str, Any]:
    return {k: v for k, v in kw.items() if v is not None}


def iter_document_chunks(documents_dir: Path) -> Iterator[Chunk]:
    """Yield one chunk per PDF page (pypdf text layer) under *documents_dir*.

    Documents are corpus-global (not site-scoped); the agent retrieves them with
    no site filter when looking for any site's source context.
    """
    import pypdf  # already a core dep

    for pdf_path in sorted(documents_dir.rglob("*.pdf")):
        rel = pdf_path.relative_to(documents_dir)
        collection = rel.parts[0] if len(rel.parts) > 1 else ""
        source_rel = str(rel)

        try:
            reader = pypdf.PdfReader(str(pdf_path), strict=False)
        except Exception:
            continue

        for page_idx, page in enumerate(reader.pages):
            try:
                text = (page.extract_text() or "").strip()
            except Exception:
                text = ""

            if not text:
                text = (
                    f"[image-only page; no text layer — source: {pdf_path.name} p.{page_idx + 1}]"
                )

            yield Chunk(
                chunk_id=_chunk_id("document", source_rel, str(page_idx)),
                text=text[:_MAX_CHUNK_CHARS],
                site="",
                collection=collection,
                doc_kind="document",
                source_path=source_rel,
                page=page_idx,
                provenance=_prov(
                    filename=pdf_path.name,
                    page_1indexed=page_idx + 1,
                    collection=collection or None,
                ),
            )


def iter_reference_chunks(reference_dir: Path) -> Iterator[Chunk]:
    """Yield chunks from data/reference/ (README summaries, CSVs, YAMLs)."""
    if not reference_dir.exists():
        return

    for path in sorted(reference_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(reference_dir)
        collection = rel.parts[0] if len(rel.parts) > 1 else str(rel.parent)
        source_rel = str(rel)
        suffix = path.suffix.lower()

        if suffix not in {".csv", ".md", ".yaml", ".yml", ".txt", ".json"}:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if suffix == ".csv":
            lines = text.splitlines()
            if not lines:
                continue
            header = lines[0]
            for row_idx, row in enumerate(lines[1:], start=1):
                if not row.strip():
                    continue
                yield Chunk(
                    chunk_id=_chunk_id("reference", source_rel, str(row_idx)),
                    text=f"{header}\n{row}",
                    site="",
                    collection=collection,
                    doc_kind="reference",
                    source_path=source_rel,
                    page=-1,
                    provenance=_prov(file=path.name, row=row_idx),
                )
        else:
            for chunk_idx, chunk_text in enumerate(_split_text(text)):
                yield Chunk(
                    chunk_id=_chunk_id("reference", source_rel, str(chunk_idx)),
                    text=chunk_text,
                    site="",
                    collection=collection,
                    doc_kind="reference",
                    source_path=source_rel,
                    page=-1,
                    provenance=_prov(file=path.name, chunk=chunk_idx if chunk_idx else None),
                )


def iter_extracted_chunks(extracted_dir: Path, *, site: str) -> Iterator[Chunk]:
    """Yield chunks from the *site*'s extracted YAML artifacts under *extracted_dir*.

    Lima's artifacts live at the root; every other site lives under its slug subdir.
    """
    root = extracted_dir if site == _CORPUS_HOME else extracted_dir / site
    if not root.exists():
        return

    for path in sorted(root.rglob("*.yaml")):
        rel_to_root = path.relative_to(root)
        collection = rel_to_root.parts[0] if len(rel_to_root.parts) > 1 else ""
        source_rel = str(path.relative_to(extracted_dir))

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for chunk_idx, chunk_text in enumerate(_split_text(text)):
            yield Chunk(
                chunk_id=_chunk_id("extracted", source_rel, str(chunk_idx)),
                text=chunk_text,
                site=site,
                collection=collection,
                doc_kind="extracted",
                source_path=source_rel,
                page=-1,
                provenance=_prov(
                    file=path.name,
                    chunk=chunk_idx if chunk_idx else None,
                    collection=collection or None,
                ),
            )
