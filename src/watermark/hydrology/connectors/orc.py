"""Ohio Revised Code (ORC) full-text connector.

Pulls statutory full text from the Ohio LSC code portal at ``codes.ohio.gov``,
which serves the ORC as HTML (there is no JSON API). The corpus cites specific ORC
sections (149.43 public records, 121.22 open meetings, 122.175 / 5709.85 / 3735.671
tax-incentive provisions, ...); this connector scans those citations, resolves each
to its **Title**, and can pull the full text of the cited sections, their chapters,
or the whole titles they belong to.

Page structure (verified against ``section-149.43``):

* a **section** page (``/ohio-revised-code/section-<n>``) carries the section number
  + heading in an ``<h1>``, a breadcrumb naming its Title and Chapter, the statute
  text in ``<section class="laws-body">``, and amendment history in
  ``<section class="laws-history">``;
* a **chapter** page (``/ohio-revised-code/chapter-<n>``) inlines every section's
  full text (one ``<h1>`` + ``laws-body`` per section) — so a chapter is one fetch;
* a **title** page (``/ohio-revised-code/title-<n>``) lists its chapters as
  relative ``chapter-<n>`` links.

Like the other connectors this reuses :func:`_cache.cached_get` (on-disk cache +
TTL + offline/committed-fixture fallback); the cached/fixture artifact is the
**parsed** JSON, never the heavy HTML. Text is taken verbatim from the portal —
nothing is summarized or fabricated. Synchronous (``httpx``).
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any, cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict

from watermark.config import Settings, get_settings
from watermark.hydrology.connectors._cache import cached_get
from watermark.logging import get_logger

log = get_logger(__name__)

# A citation marker (R.C./O.R.C./ORC/Ohio Revised Code/§/section) followed by a
# chapter.section number. Requiring the marker avoids matching version strings and
# unrelated "Section 8.3" cross-refs; candidates are still validated by a live fetch.
_CITATION_RE = re.compile(
    r"(?:R\.?C\.?|O\.?R\.?C\.?|Ohio\s+Revised\s+Code|§|[Ss]ection)\s*§?\s*"
    r"(\d{1,4}\.\d{1,4}[A-Za-z]?)"
)

# A section's number + heading appears two ways: as the page <h1> on a section
# page, and as a ``content-head-text`` anchor per section on a chapter page (which
# inlines every section). Both are matched; bare cross-reference links in the body
# are not (they lack these wrappers).
_PIPE = r"(?:<span[^>]*>\s*\|\s*</span>|\|)?"
_H1_HEADER_RE = re.compile(rf"<h1>\s*Section\s+([\d.]+[A-Za-z]?)\s*{_PIPE}\s*(.*?)</h1>", re.S)
_CHAPTER_HEADER_RE = re.compile(
    rf'content-head-text">\s*<a href="section-[\d.]+[A-Za-z]?">\s*'
    rf"Section\s+([\d.]+[A-Za-z]?)\s*{_PIPE}\s*(.*?)</a>",
    re.S,
)
_BREADCRUMB_NODE_RE = re.compile(
    r'<div class="breadcrumbs-node">\s*<a href="([^"]+)"[^>]*>(.*?)</a>', re.S
)
_CHAPTER_LINK_RE = re.compile(
    rf'href="(?:/ohio-revised-code/)?chapter-(\d+)"[^>]*>\s*Chapter\s+\d+\s*{_PIPE}\s*([^<]+?)\s*</a>'
)
_LAWS_BODY_RE = re.compile(r'<section class="laws-body">(.*?)</section>', re.S)
_LAWS_HISTORY_RE = re.compile(r'<section class="laws-history">(.*?)</section>', re.S)
# A "Last updated <date> at <time>" footer the portal appends inside the body —
# page metadata, not statute text.
_LAST_UPDATED_RE = re.compile(r"\n*Last updated\b.*?(?:AM|PM)\s*$", re.S | re.I)


def _body_text(fragment: str) -> str:
    """Body text with the trailing 'Last updated …' page footer removed."""
    return _LAST_UPDATED_RE.sub("", _strip_html(fragment)).strip()


class OrcSection(BaseModel):
    """One ORC section's full text, with its place in the Title/Chapter tree."""

    model_config = ConfigDict(extra="forbid")

    number: str  # "149.43"
    heading: str | None
    title_num: str | None  # "1"
    title_name: str | None  # "State Government"
    chapter_num: str | None  # "149"
    chapter_name: str | None  # "Documents, Reports, and Records"
    text: str  # statute body, verbatim
    history: str | None  # amendment/effective-date history
    url: str


def _strip_html(fragment: str) -> str:
    """Plain text from an HTML fragment, keeping block breaks as newlines."""
    text = re.sub(r"(?i)</(p|div|li|h\d)>|<br\s*/?>", "\n", fragment)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _breadcrumb(page_html: str) -> tuple[str | None, str | None, str | None, str | None]:
    """``(title_num, title_name, chapter_num, chapter_name)`` from a page breadcrumb.

    Handles both numbered titles (``title-1`` → "State Government") and the named
    pseudo-titles that use a slug (``general-provisions`` → "General Provisions",
    which has no number).
    """
    i = page_html.find('class="breadcrumbs"')
    block = page_html[i : i + 1400] if i != -1 else ""
    title_num = title_name = chapter_num = chapter_name = None
    for href, label in _BREADCRUMB_NODE_RE.findall(block):
        text = _strip_html(label)
        if href.rstrip("/").endswith("ohio-revised-code"):
            continue  # the ORC root node
        mc = re.search(r"chapter-(\d+)", href)
        mt = re.search(r"title-(\d+)", href)
        if mc:
            chapter_num = mc.group(1)
            chapter_name = re.sub(r"^Chapter\s+\d+\s*", "", text).strip() or None
        elif mt:
            title_num = mt.group(1)
            title_name = re.sub(r"^Title\s+\d+\s*", "", text).strip() or None
        elif title_name is None:  # named-slug title (e.g. general-provisions)
            title_name = text or None
    return title_num, title_name, chapter_num, chapter_name


def parse_sections(page_html: str, *, base_url: str) -> list[OrcSection]:
    """Parse every section on a section- or chapter- page (chapter pages inline many).

    Pairs each ``<h1>Section ...</h1>`` with the next ``laws-body`` after it; a
    single page-level breadcrumb supplies the Title/Chapter for all of them.
    """
    title_num, title_name, chapter_num, chapter_name = _breadcrumb(page_html)
    # On a chapter page the chapter is the page itself (not in the breadcrumb); take
    # its name from the page <h1> and fall back to the number encoded in each section.
    if chapter_name is None:
        ch_h1 = re.search(rf"<h1>\s*Chapter\s+(\d+)\s*{_PIPE}\s*(.*?)</h1>", page_html, re.S)
        if ch_h1:
            chapter_num, chapter_name = ch_h1.group(1), _strip_html(ch_h1.group(2)) or None
    headers = sorted(
        [*_H1_HEADER_RE.finditer(page_html), *_CHAPTER_HEADER_RE.finditer(page_html)],
        key=lambda m: m.start(),
    )
    bodies = list(_LAWS_BODY_RE.finditer(page_html))
    histories = list(_LAWS_HISTORY_RE.finditer(page_html))

    out: list[OrcSection] = []
    for idx, h in enumerate(headers):
        number = h.group(1)
        heading = _strip_html(h.group(2)).rstrip(".") or None
        # The matching body is the first laws-body that starts after this header
        # (and before the next header, when there is one).
        next_start = headers[idx + 1].start() if idx + 1 < len(headers) else len(page_html)
        body = next((b for b in bodies if h.end() <= b.start() < next_start), None)
        hist = next((x for x in histories if h.end() <= x.start() < next_start), None)
        out.append(
            OrcSection(
                number=number,
                heading=heading,
                title_num=title_num,
                title_name=title_name,
                chapter_num=chapter_num or chapter_of(number),
                chapter_name=chapter_name,
                text=_body_text(body.group(1)) if body else "",
                history=_strip_html(hist.group(1)) if hist else None,
                url=f"{base_url}/ohio-revised-code/section-{number}",
            )
        )
    return out


def _get_html(path: str, *, settings: Settings) -> str:
    """Fetch (or replay) one codes.ohio.gov page; cache the raw HTML keyed by path."""

    def fetch() -> Any:
        url = f"{settings.orc_base_url}{path}"
        log.info("orc.fetch", path=path)
        resp = httpx.get(url, timeout=settings.hydro_request_timeout_s, follow_redirects=True)
        resp.raise_for_status()
        return {"html": resp.text}

    payload = cast("dict[str, Any]", cached_get("orc", {"path": path}, fetch, settings=settings))
    return str(payload.get("html", ""))


def fetch_section(number: str, *, settings: Settings | None = None) -> OrcSection | None:
    """Fetch one ORC section; ``None`` if the portal has no such section (404 / no body)."""
    settings = settings or get_settings()
    try:
        page = _get_html(f"/ohio-revised-code/section-{number}", settings=settings)
    except httpx.HTTPStatusError:
        return None
    sections = parse_sections(page, base_url=settings.orc_base_url)
    return sections[0] if sections else None


def fetch_chapter(chapter: str, *, settings: Settings | None = None) -> list[OrcSection]:
    """Fetch every section in a chapter (one request — chapter pages inline the text)."""
    settings = settings or get_settings()
    page = _get_html(f"/ohio-revised-code/chapter-{chapter}", settings=settings)
    return parse_sections(page, base_url=settings.orc_base_url)


def list_title_chapters(title: str, *, settings: Settings | None = None) -> list[tuple[str, str]]:
    """``[(chapter_num, chapter_name), ...]`` for a Title, from its index page."""
    settings = settings or get_settings()
    page = _get_html(f"/ohio-revised-code/title-{title}", settings=settings)
    seen: dict[str, str] = {}
    for m in _CHAPTER_LINK_RE.finditer(page):
        seen.setdefault(m.group(1), _strip_html(m.group(2)))
    return list(seen.items())


def fetch_title(title: str, *, settings: Settings | None = None) -> list[OrcSection]:
    """Fetch the **whole** Title: every section of every chapter in it (a heavy pull)."""
    settings = settings or get_settings()
    chapters = list_title_chapters(title, settings=settings)
    out: list[OrcSection] = []
    for chapter_num, _name in chapters:
        out.extend(fetch_chapter(chapter_num, settings=settings))
    return out


# --- Citations -------------------------------------------------------------


def scan_citations(*roots: Path) -> list[str]:
    """Distinct ORC section numbers cited under the given roots (marker-qualified)."""
    found: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            found.update(m.group(1) for m in _CITATION_RE.finditer(text))
    return sorted(found, key=_section_sort_key)


def _section_sort_key(number: str) -> tuple[int, float]:
    chapter, _, rest = number.partition(".")
    try:
        return (int(chapter), float(f"0.{rest}") if rest else 0.0)
    except ValueError:
        return (0, 0.0)


def chapter_of(number: str) -> str:
    """The chapter portion of a section number ("149.43" -> "149")."""
    return number.split(".", 1)[0]


# --- Reference dataset assembly --------------------------------------------


def _section_doc(sec: OrcSection) -> dict[str, Any]:
    return {
        "number": sec.number,
        "heading": sec.heading,
        "title": {"num": sec.title_num, "name": sec.title_name},
        "chapter": {"num": sec.chapter_num, "name": sec.chapter_name},
        "text": sec.text,
        "history": sec.history,
        "url": sec.url,
    }


def write_sections(sections: list[OrcSection], out_dir: Path, *, scope: str) -> Path:
    """Write a set of sections to one YAML file with a provenance ``meta`` block."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ordered = sorted(sections, key=lambda s: _section_sort_key(s.number))
    path = out_dir / f"orc.{scope}.yaml"
    doc = {
        "meta": {
            "subject": "Ohio Revised Code — full text",
            "scope": scope,
            "source": "Ohio LSC code portal — codes.ohio.gov",
            "count": len(ordered),
            "caveats": [
                "Text is verbatim from codes.ohio.gov; nothing is summarized or inferred.",
                "Statutes change — cite the section URL and verify the current text.",
            ],
        },
        "sections": [_section_doc(s) for s in ordered],
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def write_citation_index(resolved: list[OrcSection], unresolved: list[str], out_dir: Path) -> Path:
    """Write the citations manifest: each cited section -> its Title/Chapter/heading."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "citations.yaml"
    doc = {
        "meta": {
            "subject": "ORC sections cited in the BOSC corpus",
            "source": "Ohio LSC code portal — codes.ohio.gov",
            "resolved": len(resolved),
            "unresolved": len(unresolved),
        },
        "citations": [
            {
                "number": s.number,
                "heading": s.heading,
                "title": f"{s.title_num} {s.title_name}".strip() if s.title_num else None,
                "chapter": f"{s.chapter_num} {s.chapter_name}".strip() if s.chapter_num else None,
                "url": s.url,
            }
            for s in sorted(resolved, key=lambda s: _section_sort_key(s.number))
        ],
        "unresolved": unresolved,  # marker-matched numbers the portal had no section for
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
