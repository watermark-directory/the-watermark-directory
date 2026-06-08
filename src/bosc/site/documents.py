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

from bosc.logging import get_logger
from bosc.site import exhibits as exhibits_mod

log = get_logger(__name__)

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
        coll.entries.append(
            DocumentEntry(
                rel=rel,
                name=path.name,
                size_bytes=size,
                suffix=path.suffix.lower().lstrip("."),
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
