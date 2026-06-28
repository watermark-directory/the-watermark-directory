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
import time
import unicodedata
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from pydantic import BaseModel, ConfigDict

from watermark.civic._http import BROWSER_HEADERS
from watermark.config import Settings, get_settings
from watermark.connectors import cached_get
from watermark.logging import get_logger

log = get_logger(__name__)

_DAM_HOST = "dam.assets.ohio.gov"
_DDG_URL = "https://html.duckduckgo.com/html/"

# DDG HTML form submission headers — POST is the native method of the DDG HTML page;
# GET requests receive a 202 bot-check response that contains no result links.
_DDG_HEADERS = {
    **BROWSER_HEADERS,
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://html.duckduckgo.com",
    "Referer": "https://html.duckduckgo.com/",
}

# Seconds to pause between consecutive DDG queries to avoid rate-limiting.
_DDG_INTER_QUERY_DELAY = 1.5

# Cache TTL for DDG responses — permit documents are issued infrequently; 7 days avoids
# redundant queries on repeat discover runs and reduces rate-limit exposure.
_DDG_CACHE_TTL_HOURS = 168

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


def _sanitize_search_term(term: str) -> str:
    """Collapse non-ASCII and punctuation/symbol chars to spaces for a DDG keyword.

    Handles place names like 'Troy · Piqua' (middle-dot separator) where the
    non-ASCII character would otherwise be percent-encoded in the query string.
    """
    cleaned = "".join(
        " " if ord(c) >= 128 or unicodedata.category(c).startswith(("P", "S")) else c for c in term
    )
    return " ".join(cleaned.split())


def _fetch_ddg(query: str, settings: Settings) -> str:
    """POST one DDG HTML search page (cached _DDG_CACHE_TTL_HOURS hours); returns HTML or ''.

    Uses POST (``application/x-www-form-urlencoded``), the native DDG HTML form method.
    Any 2xx response is accepted — DDG sometimes returns 202 with valid result HTML.
    Responses are cached under the civic cache dir so repeated discover runs skip the
    network entirely, and the raw HTML is inspectable for debugging.
    """

    def _live() -> dict[str, object]:
        try:
            resp = httpx.post(
                _DDG_URL,
                data={"q": query},
                follow_redirects=True,
                timeout=settings.civic_request_timeout_s,
                headers=_DDG_HEADERS,
            )
            if not (200 <= resp.status_code < 300):
                log.warning(
                    "oepa.discovery.unexpected_status",
                    query=query,
                    status=resp.status_code,
                    html_bytes=len(resp.content),
                )
                return {"html": "", "status_code": resp.status_code}
            log.info(
                "oepa.discovery.fetched",
                query=query,
                status=resp.status_code,
                html_bytes=len(resp.content),
            )
            return {"html": resp.text, "status_code": resp.status_code}
        except httpx.HTTPError as exc:
            log.warning("oepa.discovery.fetch_failed", query=query, error=str(exc))
            return {"html": "", "status_code": 0}

    result: dict[str, object] = cached_get(
        "oepa_discovery",
        {"q": query},
        _live,
        cache_dir=settings.civic_cache_dir,
        ttl_hours=_DDG_CACHE_TTL_HOURS,
    )
    return str(result.get("html", ""))


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
    place_clean = _sanitize_search_term(place)
    county_clean = _sanitize_search_term(county)
    queries = [
        f'site:{_DAM_HOST} "{place_clean}"',
        f'site:{_DAM_HOST} "{county_clean}"',
    ]
    if extra_terms:
        for term in extra_terms:
            queries.append(f'site:{_DAM_HOST} "{place_clean}" {term}')

    all_docs: list[DiscoveredDoc] = []
    seen_urls: set[str] = set()
    for i, query in enumerate(queries):
        if i > 0:
            time.sleep(_DDG_INTER_QUERY_DELAY)
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
