"""Civic discovery pure logic (#620): platform classification + records-link scraping.

`classify_platform`/`find_records_links`/`_pick_records_url` are pure (no fixtures); the
networked `discover` (403/406 WAF branches) is exercised by the fetcher integration tests.
"""

from __future__ import annotations

from watermark.civic.discovery import (
    _pick_records_url,
    classify_platform,
    find_records_links,
)
from watermark.civic.models import Platform


def test_classify_platform_matches_signatures_and_url() -> None:
    plat, sigs = classify_platform('<a href="/AgendaCenter/ViewFile">x</a>')
    assert plat is Platform.CIVICPLUS and "/agendacenter" in sigs
    # final_url is matched too (a redirect to the vendor host).
    plat2, _ = classify_platform("<html>nothing</html>", final_url="https://x.civicplus.com/")
    assert plat2 is Platform.CIVICPLUS
    plat3, _ = classify_platform("<html>powered by Revize</html>")
    assert plat3 is Platform.REVIZE


def test_classify_platform_unknown_is_not_fabricated() -> None:
    plat, sigs = classify_platform("<html><body>Township home</body></html>")
    assert plat is Platform.UNKNOWN and sigs == []


def test_find_records_links_dedupes_and_resolves_absolute() -> None:
    html = """
      <a href="/minutes/2025.pdf">January Minutes</a>
      <a href="/agenda/jan.pdf">Agenda</a>
      <a href="/minutes/2025.pdf">dup link</a>
      <a href="/about">About us</a>
      <a href="/docs/x.pdf">Meeting packet</a>
    """
    links = find_records_links(html, base_url="https://twp.example/")
    assert links == [
        "https://twp.example/minutes/2025.pdf",
        "https://twp.example/agenda/jan.pdf",
        "https://twp.example/docs/x.pdf",
    ]
    assert "https://twp.example/about" not in links  # no records keyword


def test_pick_records_url_prefers_minutes_then_agenda() -> None:
    assert _pick_records_url(["https://x/agenda/a", "https://x/minutes/m"]) == "https://x/minutes/m"
    assert _pick_records_url(["https://x/agenda/a", "https://x/meeting/p"]) == "https://x/agenda/a"
    assert _pick_records_url(["https://x/meeting/p"]) == "https://x/meeting/p"
    assert _pick_records_url([]) is None
