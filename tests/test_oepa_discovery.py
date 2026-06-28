"""Unit tests for watermark.oepa.discovery — URL parsing and doc-type inference.

All tests are offline: they parse against the committed HTML fixture or
synthetic snippets and never touch the network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from watermark.oepa.discovery import (
    DiscoveredDoc,
    _infer_type,
    _parse_html,
    _parse_serper_json,
    _resolve_dam_url,
    _sanitize_search_term,
    discover_dam_documents,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "oepa" / "ddg-lima-response.html"


# ---------------------------------------------------------------------------
# _resolve_dam_url
# ---------------------------------------------------------------------------


def test_resolve_direct_dam_url() -> None:
    url = (
        "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.pdf"
    )
    assert _resolve_dam_url(url) == url


def test_resolve_ddg_redirect() -> None:
    import urllib.parse

    target = (
        "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.pdf"
    )
    encoded = urllib.parse.quote(target, safe="")
    href = f"//duckduckgo.com/l/?uddg={encoded}&rut=abc"
    assert _resolve_dam_url(href) == target


def test_resolve_unrelated_returns_none() -> None:
    assert _resolve_dam_url("https://www.epa.ohio.gov/divisions/surface-water") is None
    assert _resolve_dam_url("//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com") is None


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "type_path,suffix,expected",
    [
        ("doc", None, "permit"),
        ("doc", "fs", "fact_sheet"),
        ("DraftPN", None, "draft_public_notice"),
        ("dffo", None, "dffo"),
        ("unknown_segment", None, "unknown"),
    ],
)
def test_infer_type(type_path: str, suffix: str | None, expected: str) -> None:
    assert _infer_type(type_path, suffix) == expected


# ---------------------------------------------------------------------------
# _parse_html — against the committed fixture
# ---------------------------------------------------------------------------


def test_parse_html_fixture_yields_expected_docs() -> None:
    html = _FIXTURE.read_text(encoding="utf-8")
    docs = _parse_html(
        html, query='site:dam.assets.ohio.gov "Lima"', fetched_at="2026-06-28T00:00:00+00:00"
    )

    assert len(docs) == 4, f"expected 4 docs, got {len(docs)}: {[d.url for d in docs]}"
    by_id: dict[str, DiscoveredDoc] = {}
    for d in docs:
        by_id.setdefault(d.permit_id, d)

    assert "2PH00006" in by_id
    assert "2PK00002" in by_id
    assert "2PH00007" in by_id


def test_parse_html_infers_fact_sheet() -> None:
    html = _FIXTURE.read_text(encoding="utf-8")
    docs = _parse_html(html, query="q", fetched_at="t")
    fact_sheets = [d for d in docs if d.doc_type == "fact_sheet"]
    assert len(fact_sheets) == 1
    assert fact_sheets[0].permit_id == "2PH00006"


def test_parse_html_infers_draft_pn() -> None:
    html = _FIXTURE.read_text(encoding="utf-8")
    docs = _parse_html(html, query="q", fetched_at="t")
    drafts = [d for d in docs if d.doc_type == "draft_public_notice"]
    assert len(drafts) == 1
    assert drafts[0].permit_id == "2PH00007"


def test_parse_html_deduplicates_urls() -> None:
    """Duplicate hrefs in the HTML should not produce duplicate DiscoveredDoc entries."""
    url = (
        "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.pdf"
    )
    html = f'<a href="{url}">x</a><a href="{url}">x</a>'
    docs = _parse_html(html, query="q", fetched_at="t")
    assert len(docs) == 1


def test_parse_html_unrelated_links_ignored() -> None:
    html = '<a href="https://www.epa.ohio.gov/other">Ohio EPA</a>'
    docs = _parse_html(html, query="q", fetched_at="t")
    assert docs == []


# ---------------------------------------------------------------------------
# _sanitize_search_term
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Lima", "Lima"),
        ("Allen County", "Allen County"),
        ("Troy · Piqua", "Troy Piqua"),
        ("  extra   spaces  ", "extra spaces"),
        ("Fort Wayne", "Fort Wayne"),
    ],
)
def test_sanitize_search_term(raw: str, expected: str) -> None:
    assert _sanitize_search_term(raw) == expected


# ---------------------------------------------------------------------------
# _parse_serper_json
# ---------------------------------------------------------------------------


def test_parse_serper_json_finds_permit() -> None:
    organic = [
        {
            "link": "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.pdf",
            "title": "Lima WWTP Permit",
        },
        {"link": "https://www.google.com/not-a-dam-link", "title": "Unrelated"},
    ]
    docs = _parse_serper_json(organic, query="test", fetched_at="t")
    assert len(docs) == 1
    assert docs[0].permit_id == "2PH00006"
    assert docs[0].doc_type == "permit"


def test_parse_serper_json_infers_fact_sheet() -> None:
    organic = [
        {
            "link": "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.fs.pdf",
            "title": "Fact Sheet",
        }
    ]
    docs = _parse_serper_json(organic, query="q", fetched_at="t")
    assert docs[0].doc_type == "fact_sheet"


def test_parse_serper_json_deduplicates() -> None:
    url = (
        "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PH00006.pdf"
    )
    organic = [{"link": url}, {"link": url}]
    docs = _parse_serper_json(organic, query="q", fetched_at="t")
    assert len(docs) == 1


def test_parse_serper_json_empty_result() -> None:
    assert _parse_serper_json([], query="q", fetched_at="t") == []


# ---------------------------------------------------------------------------
# discover_dam_documents — offline mode
# ---------------------------------------------------------------------------


def test_discover_returns_empty_offline() -> None:
    from watermark.config import Settings

    settings = Settings(civic_offline=True)
    docs = discover_dam_documents("Lima", "Allen County", basin="maumee", settings=settings)
    assert docs == []
