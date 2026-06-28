"""OEPA/DAM document discovery — ECHO reference + Serper.

Two-path discovery:

1. **ECHO reference** (permits only, no API key needed):
   Loads the committed ECHO basin POTW reference YAML, filters by the site's
   county, and HEAD-probes the DAM permit URL for each NPDES ID.  Returns
   ``doc_type="permit"`` entries that the DAM confirms exist.  Requires
   ``basin`` (e.g. ``"maumee"``) and a downloaded
   ``data/reference/echo/{basin}-wwtp.potw.yaml``.

2. **Serper keyword search** (all doc types, requires ``WATERMARK_SERPER_API_KEY``):
   Calls :func:`watermark.connectors.serper_search` with ``domain=dam.assets.ohio.gov``
   and ``filetype="pdf"`` to surface permit documents, fact sheets, draft PNs, etc.
   Keyword + ``filetype:`` queries are used because the Serper free tier blocks
   ``site:``, ``inurl:``, and quoted-string operators.

Both paths feed the same :class:`DiscoveredDoc` output and respect the
``civic_offline`` flag.  ``_parse_html`` / ``_resolve_dam_url`` are kept as
utilities for any future HTML-based source.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import yaml
from pydantic import BaseModel, ConfigDict

from watermark.civic._http import BROWSER_HEADERS
from watermark.config import Settings, get_settings
from watermark.connectors import serper_search
from watermark.logging import get_logger

log = get_logger(__name__)

_DAM_HOST = "dam.assets.ohio.gov"
_DAM_PERMIT_URL = (
    "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/{id}.pdf"
)

# 7-day cache — OEPA permits and Serper results are slow-moving.
_DISCOVERY_CACHE_TTL_HOURS = 168

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
    """One DAM document found via discovery."""

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
    """Return a ``dam.assets.ohio.gov`` URL from a DDG-style href, or None if not one.

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
    """Extract DiscoveredDoc entries for every DAM permit URL in an HTML page."""
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
    """Collapse non-ASCII and punctuation/symbol chars to spaces for a search keyword.

    Handles place names like 'Troy · Piqua' (middle-dot separator) where the
    non-ASCII character would otherwise be percent-encoded in the query string.
    """
    cleaned = "".join(
        " " if ord(c) >= 128 or unicodedata.category(c).startswith(("P", "S")) else c for c in term
    )
    return " ".join(cleaned.split())


# ---------------------------------------------------------------------------
# ECHO reference path (permits only)
# ---------------------------------------------------------------------------


def _echo_reference_ids(basin: str, county: str, settings: Settings) -> list[str]:
    """Return NPDES permit IDs for ``county`` from the committed ECHO reference YAML.

    Loads ``data/reference/echo/{basin}-wwtp.potw.yaml`` and filters by county.
    Returns ``[]`` if the file doesn't exist or the county has no matches — never raises.
    ECHO stores county as ``"ALLEN"`` or ``"ALLEN COUNTY"``; both are matched.
    """
    ref_path = settings.data_dir / "reference" / "echo" / f"{basin}-wwtp.potw.yaml"
    if not ref_path.exists():
        log.info("oepa.echo.reference_missing", path=str(ref_path))
        return []
    try:
        data = yaml.safe_load(ref_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        log.warning("oepa.echo.reference_read_error", path=str(ref_path), error=str(exc))
        return []

    # Normalise: "Allen County" → "ALLEN"; "Van Wert County" → "VAN WERT"
    county_key = county.removesuffix(" County").removesuffix(" county").upper()
    ids: list[str] = []
    for fac in data.get("facilities", []):
        fac_county = (fac.get("county") or "").upper()
        if fac_county.startswith(county_key):
            pid = fac.get("npdes_id")
            if pid and str(pid) not in ids:
                ids.append(str(pid))

    log.info("oepa.echo.county_ids", county=county, found=len(ids))
    return ids


def _probe_dam_permit(permit_id: str, settings: Settings) -> str | None:
    """HEAD-probe the standard DAM permit URL for ``permit_id``; return it if it exists."""
    url = _DAM_PERMIT_URL.format(id=permit_id)
    try:
        resp = httpx.head(
            url,
            follow_redirects=True,
            timeout=settings.civic_request_timeout_s,
            headers=BROWSER_HEADERS,
        )
        return url if resp.status_code == 200 else None
    except httpx.HTTPError as exc:
        log.debug("oepa.probe.error", url=url, error=str(exc))
        return None


# ---------------------------------------------------------------------------
# Serper path (all doc types)
# ---------------------------------------------------------------------------


def _parse_serper_json(
    organic: list[dict[str, Any]], query: str, fetched_at: str
) -> list[DiscoveredDoc]:
    """Extract DiscoveredDoc entries from a Serper organic-results list."""
    docs: list[DiscoveredDoc] = []
    seen: set[str] = set()
    for item in organic:
        url = str(item.get("link", ""))
        if not url or url in seen or _DAM_HOST not in url:
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


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def discover_dam_documents(
    place: str,
    county: str,
    *,
    basin: str | None = None,
    extra_terms: list[str] | None = None,
    settings: Settings | None = None,
) -> list[DiscoveredDoc]:
    """Discover OEPA/DAM documents for a site via two independent paths.

    **ECHO** (``basin`` required): logs the known POTW NPDES IDs for ``county``
    from the committed basin reference YAML.  DAM HEAD-probing is skipped because
    ECHO stores federal IDs (``OH0020192``) while the DAM uses Ohio EPA internal
    IDs (``2PH00006``), causing every probe to 404.

    **Serper** (``settings.serper_api_key`` required): calls
    :func:`~watermark.connectors.serper_search` with ``domain=dam.assets.ohio.gov``
    and ``filetype="pdf"`` and parses direct DAM result URLs — permits, fact
    sheets, draft PNs, and other document types.

    Both paths are skipped in offline mode.
    """
    settings = settings or get_settings()
    if settings.civic_offline:
        log.info("oepa.discovery.offline_skip")
        return []

    now = datetime.now(UTC).isoformat()
    all_docs: list[DiscoveredDoc] = []
    seen_urls: set[str] = set()

    def _add(docs: list[DiscoveredDoc]) -> None:
        for doc in docs:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                all_docs.append(doc)

    # --- ECHO path: log known POTW IDs for context (probing skipped — ECHO stores
    # federal NPDES IDs like OH0020192, but the DAM uses Ohio EPA internal IDs like
    # 2PH00006, so HEAD probes against the DAM URL template always 404). ---
    if basin:
        echo_ids = _echo_reference_ids(basin, county, settings)
        if echo_ids:
            log.info(
                "oepa.echo.reference_ids",
                county=county,
                ids=echo_ids,
                note="federal IDs only — DAM probing skipped (format mismatch)",
            )

    # --- Serper path: all doc types via Google keyword search + filetype:pdf ---
    if settings.serper_api_key:
        place_clean = _sanitize_search_term(place)
        county_clean = _sanitize_search_term(county)
        keyword_sets = [place_clean, county_clean]
        if extra_terms:
            keyword_sets += [f"{place_clean} {t}" for t in extra_terms]
        for kw in keyword_sets:
            organic = serper_search(
                kw,
                domain=_DAM_HOST,
                filetype="pdf",
                cache_ns="oepa_discovery",
                ttl_hours=_DISCOVERY_CACHE_TTL_HOURS,
                settings=settings,
            )
            _add(
                _parse_serper_json(
                    organic,
                    query=f"{kw} {_DAM_HOST} filetype:pdf",
                    fetched_at=now,
                )
            )
    elif not basin:
        log.warning(
            "oepa.discovery.no_source",
            note="set WATERMARK_SERPER_API_KEY or provide basin to enable ECHO path",
        )

    log.info("oepa.discovery.complete", place=place, found=len(all_docs))
    return all_docs
