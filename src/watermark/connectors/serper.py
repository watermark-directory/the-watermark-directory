"""Google Search via the Serper.dev API — shared discovery connector.

Call :func:`serper_search` from any subsystem that needs to find targets on a
known domain or of a specific file type.  Results are cached under
``settings.civic_cache_dir/{cache_ns}/`` so repeated queries are free.

Serper free-tier operator constraints (return 400 otherwise):
- ``site:`` and ``inurl:`` — blocked; pass ``domain=`` instead (keyword match)
- Quoted strings (``"..."``) — blocked; keep ``keywords`` unquoted
- ``filetype:`` — allowed; pass ``filetype=`` to append it
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from watermark.connectors._cache import DEFAULT_CACHE_TTL_HOURS, cached_get
from watermark.logging import get_logger

if TYPE_CHECKING:
    from watermark.config import Settings

log = get_logger(__name__)

_SERPER_URL = "https://google.serper.dev/search"


def serper_search(
    keywords: str,
    *,
    domain: str | None = None,
    filetype: str | None = None,
    num: int = 20,
    gl: str = "us",
    hl: str = "en",
    cache_ns: str = "serper",
    ttl_hours: int = DEFAULT_CACHE_TTL_HOURS,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    """Search Google via Serper and return the organic results list.

    Builds query as ``{keywords}[ {domain}][ filetype:{filetype}]``.
    Results are cached; returns ``[]`` on missing API key or HTTP error.

    Args:
        keywords:  Core search terms (no quoted strings — free-tier restriction).
        domain:    Hostname to add as a keyword (e.g. ``"dam.assets.ohio.gov"``).
                   *Not* a ``site:`` operator — free tier blocks that.
        filetype:  Extension without dot (e.g. ``"pdf"``); appended as ``filetype:X``.
        num:       Max results to request (Serper cap: 100).
        gl/hl:     Country/language codes passed to Google.
        cache_ns:  Connector name used as the cache sub-directory.
        ttl_hours: Cache freshness window (default: 7 days).
        settings:  Supply explicitly in tests; omit to use ``get_settings()``.
    """
    from watermark.config import get_settings

    settings = settings or get_settings()

    if not settings.serper_api_key:
        log.warning("serper.no_api_key", note="set WATERMARK_SERPER_API_KEY")
        return []

    parts = [keywords]
    if domain:
        parts.append(domain)
    if filetype:
        parts.append(f"filetype:{filetype}")
    query = " ".join(parts)

    params: dict[str, Any] = {"q": query, "num": num, "gl": gl, "hl": hl}

    def _live() -> list[dict[str, Any]]:
        try:
            resp = httpx.post(
                _SERPER_URL,
                json=params,
                headers={"X-API-KEY": settings.serper_api_key},
                timeout=settings.civic_request_timeout_s,
            )
            resp.raise_for_status()
            return cast("list[dict[str, Any]]", resp.json().get("organic", []))
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("serper.fetch_failed", query=query, error=str(exc))
            return []

    return cast(
        "list[dict[str, Any]]",
        cached_get(
            cache_ns,
            params,
            _live,
            cache_dir=settings.civic_cache_dir,
            ttl_hours=ttl_hours,
        ),
    )
