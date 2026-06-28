"""DDG site-search connector for OEPA/DAM document discovery.

Runs DuckDuckGo ``site:dam.assets.ohio.gov`` searches using a site's place and
county name, parses result URLs, and returns structured :class:`DiscoveredDoc`
entries.  Network-optional: when ``civic_offline`` is set, returns empty (discovery
is inherently online; there is no fixture fallback for search results).

The downstream :mod:`watermark.oepa.fetch` module downloads the discovered PDFs
via the existing civic downloader; this module only identifies them.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import parse_qs, unquote, urlencode, urlparse

import httpx
from pydantic import BaseModel, ConfigDict

from watermark.civic._http import BROWSER_HEADERS
from watermark.config import Settings, get_settings
from watermark.logging import get_logger

log = get_logger(__name__)

_DAM_HOST = "dam.assets.ohio.gov"
_DDG_URL = "https://html.duckduckgo.com/html/"

# Matches the permits path and captures the type-path segment + filename stem.
# Handles both the short form (.../permits/doc/2PH00006.pdf) and the fact-sheet
# dot-suffix form (.../permits/doc/2PH00006.fs.pdf).
_DAM_PERMIT_RE = re.compile(
    r"epa\.ohio\.gov/Portals/35/permits/"
    r"(?P<type_path>[^/?#]+)/"
    r"(?P<stem>[A-Za-z0-9]+)"
    r"(?:\.(?P<suffix>[a-z]+))?\.pdf",
    re.IGNORECASE,
)

_HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.IGNORECASE)

DocType = Literal["permit", "draft_public_notice", "fact_sheet", "dffo", "unknown"]

_TYPE_PATH_MAP: dict[str, DocType] = {
    "doc": "permit",
    "draftpn": "draft_public_notice",
    "dffo": "dffo",
}
_SUFFIX_MAP: dict[str, DocType] = {
    "fs": "fact_sheet",
}


class DiscoveredDoc(BaseModel):
    """One DAM document found via a DDG site-search result."""

    model_config = ConfigDict(extra="forbid")

    url: str
    permit_id: str
    doc_type: DocType
    query: str
    fetched_at: str


def _infer_type(type_path: str, suffix: str | None) -> DocType:
    if suffix and suffix.lower() in _SUFFIX_MAP:
        return _SUFFIX_MAP[suffix.lower()]
    return _TYPE_PATH_MAP.get(type_path.lower(), "unknown")


def _resolve_dam_url(href: str) -> str | None:
    """Return a ``dam.assets.ohio.gov`` URL from an href, or None if not one.

    DDG result links come in two forms:
    - Direct: ``https://dam.assets.ohio.gov/…``
    - Redirect: ``//duckduckgo.com/l/?uddg=<encoded-url>&…``
    """
    parsed = urlparse(href)
    if parsed.netloc == _DAM_HOST:
        return href
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [""])[0]
        decoded = unquote(uddg)
        if _DAM_HOST in decoded:
            return decoded
    return None


def _parse_html(html: str, query: str, fetched_at: str) -> list[DiscoveredDoc]:
    """Extract DiscoveredDoc entries for every DAM permit URL in DDG result HTML."""
    docs: list[DiscoveredDoc] = []
    seen: set[str] = set()
    for m in _HREF_RE.finditer(html):
        url = _resolve_dam_url(m.group(1))
        if not url or url in seen:
            continue
        pm = _DAM_PERMIT_RE.search(url)
        if not pm:
            continue
        seen.add(url)
        docs.append(
            DiscoveredDoc(
                url=url,
                permit_id=pm.group("stem"),
                doc_type=_infer_type(pm.group("type_path"), pm.group("suffix")),
                query=query,
                fetched_at=fetched_at,
            )
        )
    return docs


def _fetch_ddg(query: str, settings: Settings) -> str:
    """GET one DDG HTML search page; returns raw HTML (empty string on error)."""
    url = f"{_DDG_URL}?{urlencode({'q': query})}"
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=settings.civic_request_timeout_s,
            headers=BROWSER_HEADERS,
        )
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPError as exc:
        log.warning("oepa.discovery.fetch_failed", query=query, error=str(exc))
        return ""


def discover_dam_documents(
    place: str,
    county: str,
    *,
    extra_terms: list[str] | None = None,
    settings: Settings | None = None,
) -> list[DiscoveredDoc]:
    """Search DDG for OEPA/DAM documents for a site's place and county.

    Returns an empty list in offline mode — discovery is inherently online.
    ``extra_terms`` appends additional keyword suffixes to the place query
    (e.g. ``["NPDES", "permit"]``) for finer targeting.
    """
    settings = settings or get_settings()
    if settings.civic_offline:
        log.info("oepa.discovery.offline_skip")
        return []

    now = datetime.now(UTC).isoformat()
    queries = [
        f'site:{_DAM_HOST} "{place}"',
        f'site:{_DAM_HOST} "{county}"',
    ]
    if extra_terms:
        for term in extra_terms:
            queries.append(f'site:{_DAM_HOST} "{place}" {term}')

    all_docs: list[DiscoveredDoc] = []
    seen_urls: set[str] = set()
    for query in queries:
        html = _fetch_ddg(query, settings)
        for doc in _parse_html(html, query=query, fetched_at=now):
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                all_docs.append(doc)

    log.info(
        "oepa.discovery.complete",
        place=place,
        queries=len(queries),
        found=len(all_docs),
    )
    return all_docs
