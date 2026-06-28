"""Shared page fetch for the civic subsystem (discovery + fetchers + downloader).

One browser-like request policy (headers, timeout, redirects) lives in
:func:`_browser_request`, so every civic network call — the cached JSON page fetch
(:func:`get_page`) and the downloader's raw-bytes stream — gets the same
WAF-dodging User-Agent, brotli decoding, and ``civic_*`` timeout/cache/offline
discipline.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

import httpx

from watermark.config import Settings
from watermark.connectors import cached_get

# A real browser User-Agent + Accept: several county CMS/WAFs (Sucuri, the Duda CDN,
# Drupal bot rules) reflexively 403/406 an unknown UA, which would otherwise hide a
# body's records. The `brotli` dep lets httpx decode the `br` responses those same
# servers force, so we let httpx negotiate Accept-Encoding itself.
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@contextmanager
def _browser_request(
    method: str, url: str, settings: Settings, *, stream: bool = False
) -> Iterator[httpx.Response]:
    """Yield a raised-for-status browser-like httpx response (one redirect/timeout policy).

    The single home for the civic header/timeout/``follow_redirects`` policy: the cached
    page fetch reads ``resp.text`` (``stream=False``), the downloader streams
    ``resp.read()`` bytes (``stream=True``).
    """
    kwargs: dict[str, Any] = {
        "follow_redirects": True,
        "timeout": settings.civic_request_timeout_s,
        "headers": BROWSER_HEADERS,
    }
    if stream:
        with httpx.stream(method, url, **kwargs) as resp:
            resp.raise_for_status()
            yield resp
    else:
        resp = httpx.request(method, url, **kwargs)
        resp.raise_for_status()
        yield resp


def get_page(url: str, *, connector: str, settings: Settings) -> dict[str, Any]:
    """Fetch (or replay) one page; return ``{html, final_url, status_code}``.

    ``connector`` namespaces the cache/fixture directory (e.g. ``subdivision_discovery``,
    ``civicplus``). Raises ``httpx.HTTPStatusError`` on a 4xx/5xx live response and
    :class:`~watermark.connectors.OfflineError` on an offline cache/fixture miss.
    """

    def fetch() -> Any:
        with _browser_request("GET", url, settings) as resp:
            return {"html": resp.text, "final_url": str(resp.url), "status_code": resp.status_code}

    return cast(
        "dict[str, Any]",
        cached_get(
            connector,
            {"url": url},
            fetch,
            cache_dir=settings.civic_cache_dir,
            offline=settings.civic_offline,
            fixtures_dir=settings.civic_fixtures_dir,
            ttl_hours=settings.civic_cache_ttl_hours,
        ),
    )
