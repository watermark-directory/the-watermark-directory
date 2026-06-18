"""Catalog the full source-document corpus as a browsable library.

Mission goal (1): *present a downloadable form of each document.* The raw corpus
under ``data/documents`` is ~5 GB across ~1,500 files — far too large to
republish onto a static host — so this renders a complete **catalog** instead:
one index page plus a page per collection, listing every source file with its
size and type. Direct downloads are wired only for the curated
:mod:`bosc.site.exhibits` (already copied/sliced into ``web/exhibits/``); the
rest are catalogued with their repo-relative path so the record is transparent
even when the bytes aren't republished.

Set ``settings.documents_mirror_base_url`` to an external mirror (Archive.org /
S3 / Drive) to turn every catalogued file into a direct download link.

Chain of custody: this only *reads* and *links* source files — it never copies,
renames, or alters a byte under ``data/documents``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

import yaml

from bosc.logging import get_logger
from bosc.site import exhibits as exhibits_mod
from bosc.site.feeds import DocumentCollectionItem, DocumentItem, RenderClass

log = get_logger(__name__)

# Extension -> (MIME, render_class). The fallback when a content sniff can't positively
# identify the file. `render_class` is what the frontend viewer dispatches on (#274/#275):
# image/text/html inline, pdf native+PDF.js, office (doc/docx/odg) download-only.
_EXT_MEDIA: dict[str, tuple[str, RenderClass]] = {
    "pdf": ("application/pdf", "pdf"),
    "png": ("image/png", "image"),
    "jpg": ("image/jpeg", "image"),
    "jpeg": ("image/jpeg", "image"),
    "gif": ("image/gif", "image"),
    "webp": ("image/webp", "image"),
    "bmp": ("image/bmp", "image"),
    "tif": ("image/tiff", "image"),
    "tiff": ("image/tiff", "image"),
    "svg": ("image/svg+xml", "image"),
    "html": ("text/html", "html"),
    "htm": ("text/html", "html"),
    "txt": ("text/plain", "text"),
    "csv": ("text/csv", "text"),
    "json": ("application/json", "text"),
    "md": ("text/markdown", "text"),
    "doc": ("application/msword", "office"),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "office",
    ),
    "odg": ("application/vnd.oasis.opendocument.graphics", "office"),
    "odt": ("application/vnd.oasis.opendocument.text", "office"),
    "ods": ("application/vnd.oasis.opendocument.spreadsheet", "office"),
    "odp": ("application/vnd.oasis.opendocument.presentation", "office"),
    "xls": ("application/vnd.ms-excel", "office"),
    "xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "office",
    ),
    "ppt": ("application/vnd.ms-powerpoint", "office"),
    "pptx": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "office",
    ),
}
_FALLBACK_MEDIA: tuple[str, RenderClass] = ("application/octet-stream", "other")


def _sniff_media(head: bytes) -> tuple[str, RenderClass] | None:
    """Identify a file from its leading magic bytes, or ``None`` if unrecognized.

    Only the signatures we can positively identify — degraded scans and mislabeled
    extensions are common in this corpus, so a confident sniff is trusted over the name.
    """
    if head.startswith(b"%PDF"):
        return ("application/pdf", "pdf")
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("image/png", "image")
    if head.startswith(b"\xff\xd8\xff"):
        return ("image/jpeg", "image")
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return ("image/gif", "image")
    return None


def _media_type_and_render_class(
    path: Path, suffix: str, *, available: bool
) -> tuple[str, RenderClass]:
    """Resolve ``(media_type, render_class)`` for a source file (epic #274 / #275).

    Sniffs the leading bytes and trusts a confident sniff over the extension; falls back
    to the extension table otherwise. A Git-LFS pointer has no real bytes (its content is
    pointer text), so for an unavailable file we trust the extension instead of sniffing.
    """
    by_ext = _EXT_MEDIA.get(suffix, _FALLBACK_MEDIA)
    if not available:
        return by_ext
    try:
        with path.open("rb") as fh:
            head = fh.read(16)
    except OSError:
        return by_ext
    return _sniff_media(head) or by_ext


# Companion / metadata files that describe a collection rather than being source
# documents in their own right — kept out of the catalog (READMEs are surfaced
# separately as collection descriptions).
_SKIP_NAMES = frozenset({".DS_Store", "README.md", "MANIFEST.yaml"})
_SKIP_SUFFIXES = frozenset({".md", ".yaml", ".yml", ".sh"})

# Human labels for collection slugs where title-casing the slug reads wrong.
_COLLECTION_LABELS: dict[str, str] = {
    "aedg": "AEDG (Allen Economic Development Group)",
    "oepa": "Ohio EPA",
    "lacrpc": "LACRPC (regional planning)",
    "maumee-tmdl": "Maumee Watershed Nutrient TMDL",
    "lima": "City of Lima",
    "prr-mandamus": "PRR & mandamus (legal history)",
    "recorder": "County Recorder (deeds)",
    "commissioners": "County Commissioners",
}


@dataclass
class DocumentEntry:
    """One catalogued source file under ``data/documents``."""

    rel: str  # path relative to data/documents (the as-received name, never altered)
    name: str
    size_bytes: int
    suffix: str
    media_type: str  # MIME, from the real file (extension + content sniff)
    render_class: RenderClass  # what the viewer dispatches on (#274/#275)
    available: bool  # the bytes are present locally (not an unpulled Git-LFS pointer)
    download_url: str | None  # exhibit link or external mirror URL, when present


@dataclass
class DocumentCollection:
    """A top-level collection (``data/documents/<slug>/``) and its files."""

    slug: str
    title: str
    description: str
    entries: list[DocumentEntry] = field(default_factory=list)

    @property
    def total_bytes(self) -> int:
        return sum(e.size_bytes for e in self.entries)

    @property
    def n_downloadable(self) -> int:
        return sum(1 for e in self.entries if e.download_url)


@dataclass
class DocumentsResult:
    collections: list[DocumentCollection]

    @property
    def n_documents(self) -> int:
        return sum(len(c.entries) for c in self.collections)

    @property
    def n_downloadable(self) -> int:
        return sum(c.n_downloadable for c in self.collections)


def _human_size(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _is_lfs_pointer(path: Path) -> bool:
    """True if ``path`` is an unresolved Git-LFS pointer rather than the real bytes."""
    try:
        with path.open("rb") as fh:
            head = fh.read(64)
    except OSError:
        return True
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def _collection_title(slug: str) -> str:
    return _COLLECTION_LABELS.get(slug, slug.replace("-", " ").title())


def _collection_description(collection_dir: Path) -> str:
    """First non-heading paragraph of the collection's README, if any."""
    readme = collection_dir / "README.md"
    if not readme.is_file():
        return ""
    para: list[str] = []
    for line in readme.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("<!--"):
            if para:
                break
            continue
        if not stripped:
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para).strip()


def _download_url(rel: str, *, exhibit_links: dict[str, str], mirror_base_url: str) -> str | None:
    """Resolve a download link for a source file: exhibit first, then mirror."""
    if rel in exhibit_links:
        # From documents/<collection>.md up to exhibits/<name>.
        return f"../exhibits/{exhibit_links[rel]}"
    if mirror_base_url:
        base = mirror_base_url.rstrip("/")
        return f"{base}/{quote(rel)}"
    return None


def build_documents(
    documents_dir: Path,
    *,
    exhibits: list[exhibits_mod.Exhibit] | None = None,
    mirror_base_url: str = "",
) -> DocumentsResult:
    """Walk ``data/documents`` and assemble the per-collection catalog."""
    # Source path -> published exhibit filename, for direct-download cross-links.
    exhibit_links: dict[str, str] = {
        ex.source: ex.out_name
        for ex in (exhibits or [])
        if ex.available and ex.out_name is not None
    }

    collections: dict[str, DocumentCollection] = {}
    if not documents_dir.is_dir():
        log.warning("site.documents.no_dir", path=str(documents_dir))
        return DocumentsResult(collections=[])

    for path in sorted(documents_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in _SKIP_NAMES or path.suffix.lower() in _SKIP_SUFFIXES:
            continue
        rel_path = path.relative_to(documents_dir)
        slug = rel_path.parts[0]
        rel = str(rel_path)
        coll = collections.get(slug)
        if coll is None:
            coll = DocumentCollection(
                slug=slug,
                title=_collection_title(slug),
                description=_collection_description(documents_dir / slug),
            )
            collections[slug] = coll
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        available = not _is_lfs_pointer(path)
        suffix = path.suffix.lower().lstrip(".")
        media_type, render_class = _media_type_and_render_class(path, suffix, available=available)
        coll.entries.append(
            DocumentEntry(
                rel=rel,
                name=path.name,
                size_bytes=size,
                suffix=suffix,
                media_type=media_type,
                render_class=render_class,
                available=available,
                download_url=(
                    _download_url(rel, exhibit_links=exhibit_links, mirror_base_url=mirror_base_url)
                    if available
                    else None
                ),
            )
        )

    ordered = [collections[s] for s in sorted(collections)]
    result = DocumentsResult(collections=ordered)
    log.info(
        "site.documents.cataloged",
        collections=len(ordered),
        documents=result.n_documents,
        downloadable=result.n_downloadable,
    )
    return result


def _access_cell(entry: DocumentEntry) -> str:
    """The 'Access' column: a download link, a mirror link, or a catalog note."""
    if entry.download_url:
        label = "Download" if entry.download_url.startswith("../exhibits/") else "Mirror"
        return f"[{label}]({entry.download_url})"
    if not entry.available:
        return "_unpulled — `git lfs pull`_"
    return "_in the evidence corpus_"


def render_collection_page(collection: DocumentCollection) -> str:
    """Render ``documents/<slug>.md`` — every file in one collection."""
    lines = [
        f"# Documents — {collection.title}",
        "",
    ]
    if collection.description:
        lines += [collection.description, ""]
    lines += [
        f"{len(collection.entries)} document(s) · {_human_size(collection.total_bytes)} total. "
        "Files are listed by their **as-received name** (never renamed — chain of "
        "custody). Curated exhibits download directly; the rest are catalogued by "
        "their corpus path.",
        "",
        "[← All collections](index.md)",
        "",
        "| Document | Type | Size | Access |",
        "|---|---|---|---|",
    ]
    for e in sorted(collection.entries, key=lambda x: x.rel):
        lines.append(
            f"| `{e.rel}` | {e.suffix or '—'} | {_human_size(e.size_bytes)} | {_access_cell(e)} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_index(result: DocumentsResult, *, mirror_configured: bool) -> str:
    """Render ``documents/index.md`` — the collection-level catalog overview."""
    n_docs = result.n_documents
    n_dl = result.n_downloadable
    lines = [
        "# Documents",
        "",
        "The complete catalog of primary-source documents behind Project BOSC — "
        f"**{n_docs}** files across **{len(result.collections)}** collections, every "
        "one read into the structured record under [Records](../records/index.md).",
        "",
    ]
    if mirror_configured:
        lines += [
            '!!! note "Downloads"',
            f"    All {n_docs} documents link to the full-corpus mirror; the "
            f"{n_dl} curated exhibits also download directly here.",
            "",
        ]
    else:
        lines += [
            '!!! note "Why most documents are catalog-only"',
            "    The source corpus is ~5 GB — too large to republish on a static "
            f"host. The **{n_dl}** curated [exhibits](../exhibits.md) download "
            "directly; every other document is catalogued by its corpus path and "
            "available on request. Each file keeps its **as-received name** — "
            "nothing is renamed (chain of custody).",
            "",
        ]
    lines += ["| Collection | Documents | Size | Direct downloads |", "|---|---|---|---|"]
    for c in result.collections:
        lines.append(
            f"| [{c.title}]({c.slug}.md) | {len(c.entries)} | "
            f"{_human_size(c.total_bytes)} | {c.n_downloadable or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_documents(
    documents_dir: Path,
    documents_out_dir: Path,
    *,
    exhibits: list[exhibits_mod.Exhibit] | None = None,
    mirror_base_url: str = "",
) -> DocumentsResult:
    """Write ``documents/index.md`` + ``documents/<slug>.md`` and return the catalog."""
    result = build_documents(documents_dir, exhibits=exhibits, mirror_base_url=mirror_base_url)
    documents_out_dir.mkdir(parents=True, exist_ok=True)
    (documents_out_dir / "index.md").write_text(
        render_index(result, mirror_configured=bool(mirror_base_url)), encoding="utf-8"
    )
    for collection in result.collections:
        (documents_out_dir / f"{collection.slug}.md").write_text(
            render_collection_page(collection), encoding="utf-8"
        )
    return result


def export_documents(
    documents_dir: Path,
    *,
    exhibits: list[exhibits_mod.Exhibit] | None = None,
    mirror_base_url: str = "",
) -> list[DocumentCollectionItem]:
    """Export the source-document catalog as :class:`DocumentCollectionItem` items.

    Reuses :func:`build_documents` (the same enumeration the renderer uses) without
    writing any markdown — each file keeps its as-received corpus path (chain of custody).
    """
    result = build_documents(documents_dir, exhibits=exhibits, mirror_base_url=mirror_base_url)
    return [
        DocumentCollectionItem(
            slug=c.slug,
            title=c.title,
            description=c.description,
            entries=[
                DocumentItem(
                    rel=e.rel,
                    name=e.name,
                    size_bytes=e.size_bytes,
                    suffix=e.suffix,
                    media_type=e.media_type,
                    render_class=e.render_class,
                    available=e.available,
                    download_url=e.download_url,
                )
                for e in c.entries
            ],
        )
        for c in result.collections
    ]


def load_published_allowlist(path: Path) -> set[str]:
    """The default-deny public publish allowlist (epic #274; populated by C1 / #280).

    Returns the set of ``data/documents``-relative paths cleared for *public* serving.
    A missing file means nothing is published yet (default-deny) — the allowlist is
    filled in only after a redaction/PII pass (#281). Tolerates a bare YAML list of rels
    or a mapping with a top-level ``published:`` list.
    """
    if not path.is_file():
        return set()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        log.warning("site.documents.bad_allowlist", path=str(path), error=str(exc).splitlines()[0])
        return set()
    rels = data.get("published") if isinstance(data, dict) else data
    if not isinstance(rels, list):
        return set()
    return {str(r).strip() for r in rels if str(r).strip()}


def build_doc_index(
    collections: list[DocumentCollectionItem], *, published: set[str]
) -> dict[str, tuple[RenderClass, bool]]:
    """``rel -> (render_class, is_published)`` for every catalogued source file.

    The join target for records (#274 / #276): a record resolves its real source
    document only when that file is actually in the catalog, so a stale or removed
    ``source_path`` yields no link rather than a broken one.
    """
    index: dict[str, tuple[RenderClass, bool]] = {}
    for coll in collections:
        for e in coll.entries:
            index[e.rel] = (e.render_class, e.rel in published)
    return index
