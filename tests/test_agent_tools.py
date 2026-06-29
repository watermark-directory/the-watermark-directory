"""Unit tests for agent tools — hermetic, no network, no API keys."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from watermark.agent.tools import ALL_TOOLS, list_site_issues
from watermark.config import Settings


def _settings_with_token(token: str = "tok") -> Settings:
    return Settings.model_validate({"GITHUB_TOKEN": token})


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# list_site_issues — registration
# ---------------------------------------------------------------------------


def test_list_site_issues_in_all_tools() -> None:
    names = [t.name for t in ALL_TOOLS]
    assert "list_site_issues" in names


# ---------------------------------------------------------------------------
# list_site_issues — no token degrades gracefully
# ---------------------------------------------------------------------------


def test_list_site_issues_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert not settings.github_token
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    result = _run(list_site_issues.handler({}))
    text = result["content"][0]["text"]
    assert "No GITHUB_TOKEN" in text
    assert "list_site_issues" in text


# ---------------------------------------------------------------------------
# list_site_issues — returns compact issue list
# ---------------------------------------------------------------------------


def _mock_response(issues: list[dict[str, Any]], *, link: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = issues
    resp.headers = {"link": link}
    return resp


def test_list_site_issues_open(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    issues = [
        {
            "number": 42,
            "title": "Extract missing parcel layer",
            "state": "open",
            "html_url": "https://github.com/example/repo/issues/42",
            "labels": [{"name": "site:lima"}, {"name": "area:evidence"}],
        }
    ]

    async def _fake_get(url: str, headers: dict[str, str]) -> MagicMock:
        return _mock_response(issues)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=_fake_get)

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        result = _run(list_site_issues.handler({"state": "open"}))

    text = result["content"][0]["text"]
    assert "#42" in text
    assert "Extract missing parcel layer" in text
    assert "open" in text
    assert "site:lima" in text


def test_list_site_issues_all_states(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    issues = [
        {
            "number": 10,
            "title": "Closed finding",
            "state": "closed",
            "html_url": "https://github.com/example/repo/issues/10",
            "labels": [{"name": "site:lima"}],
        },
        {
            "number": 11,
            "title": "Open finding",
            "state": "open",
            "html_url": "https://github.com/example/repo/issues/11",
            "labels": [{"name": "site:lima"}],
        },
    ]

    async def _fake_get(url: str, headers: dict[str, str]) -> MagicMock:
        assert "state=all" in url
        return _mock_response(issues)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=_fake_get)

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        result = _run(list_site_issues.handler({"state": "all"}))

    text = result["content"][0]["text"]
    assert "2 issue(s)" in text
    assert "#10" in text
    assert "#11" in text


def test_list_site_issues_default_state_is_all(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    seen_urls: list[str] = []

    async def _fake_get(url: str, headers: dict[str, str]) -> MagicMock:
        seen_urls.append(url)
        return _mock_response([])

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=_fake_get)

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        _run(list_site_issues.handler({}))

    assert seen_urls and "state=all" in seen_urls[0]


# ---------------------------------------------------------------------------
# list_site_issues — pagination follows Link rel="next"
# ---------------------------------------------------------------------------


def test_list_site_issues_paginates(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    page1 = [
        {
            "number": 1,
            "title": "First",
            "state": "open",
            "html_url": "https://github.com/x/y/issues/1",
            "labels": [],
        }
    ]
    page2 = [
        {
            "number": 2,
            "title": "Second",
            "state": "open",
            "html_url": "https://github.com/x/y/issues/2",
            "labels": [],
        }
    ]
    page2_url = "https://api.github.com/repos/x/y/issues?page=2"
    link_header = f'<{page2_url}>; rel="next"'

    call_count = 0

    async def _fake_get(url: str, headers: dict[str, str]) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _mock_response(page1, link=link_header)
        return _mock_response(page2)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=_fake_get)

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        result = _run(list_site_issues.handler({"state": "open"}))

    assert call_count == 2
    text = result["content"][0]["text"]
    assert "2 issue(s)" in text
    assert "#1" in text
    assert "#2" in text


# ---------------------------------------------------------------------------
# list_site_issues — API error is surfaced cleanly
# ---------------------------------------------------------------------------


def test_list_site_issues_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    resp = MagicMock()
    resp.status_code = 403
    resp.text = "rate limit exceeded"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=resp)

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        result = _run(list_site_issues.handler({"state": "open"}))

    text = result["content"][0]["text"]
    assert "403" in text
    assert "rate limit exceeded" in text


def test_list_site_issues_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_with_token()
    monkeypatch.setattr("watermark.agent.tools.get_settings", lambda: settings)

    import httpx as _httpx

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=_httpx.ConnectError("connection refused"))

    with patch("watermark.agent.tools.httpx.AsyncClient", return_value=mock_client):
        result = _run(list_site_issues.handler({}))

    text = result["content"][0]["text"]
    assert "Request failed" in text
