"""Higher-level GitHub API operations, authenticated via GitHubAppClient."""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from watermark.github._client import GitHubAppClient

if TYPE_CHECKING:
    from watermark.config import Settings

# The Watermark Directory repository.
_GH_REPO = "watermark-directory/the-watermark-directory"


@dataclass
class GHResult:
    """Outcome of a single GitHub API operation."""

    ok: bool
    url: str | None = None
    error: str | None = None


async def _request(
    method: str,
    url: str,
    settings: Settings,
    **kwargs: Any,
) -> httpx.Response:
    """Make an authenticated GitHub API request."""
    client = GitHubAppClient(settings)
    headers = await client.get_headers()
    async with httpx.AsyncClient(timeout=30.0) as http:
        return await http.request(method, url, headers=headers, **kwargs)


def _repo_url(settings: Settings, path: str) -> str:
    return f"{settings.github_base_url}/repos/{_GH_REPO}/{path}"


async def comment_on_pr(settings: Settings, pr_number: int, body: str) -> GHResult:
    """Post a comment on a PR (or issue — GitHub uses the same comments endpoint)."""
    url = _repo_url(settings, f"issues/{pr_number}/comments")
    try:
        resp = await _request("POST", url, settings, json={"body": body})
        if resp.status_code == 201:
            data: dict[str, Any] = resp.json()
            html_url: str = data.get("html_url", "")
            return GHResult(ok=True, url=html_url)
        return GHResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return GHResult(ok=False, error=str(exc))


async def add_label(settings: Settings, issue_number: int, label: str) -> GHResult:
    """Add a single label to an issue or PR."""
    url = _repo_url(settings, f"issues/{issue_number}/labels")
    try:
        resp = await _request("POST", url, settings, json={"labels": [label]})
        if resp.status_code in (200, 201):
            return GHResult(ok=True)
        return GHResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return GHResult(ok=False, error=str(exc))


async def remove_label(settings: Settings, issue_number: int, label: str) -> GHResult:
    """Remove a label from an issue or PR."""
    encoded = urllib.parse.quote(label, safe="")
    url = _repo_url(settings, f"issues/{issue_number}/labels/{encoded}")
    try:
        resp = await _request("DELETE", url, settings)
        if resp.status_code in (200, 204):
            return GHResult(ok=True)
        return GHResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return GHResult(ok=False, error=str(exc))


async def set_issue_state(
    settings: Settings,
    issue_number: int,
    state: str,
) -> GHResult:
    """Open or close an issue (state must be 'open' or 'closed')."""
    if state not in ("open", "closed"):
        return GHResult(ok=False, error=f"Invalid state {state!r}; must be 'open' or 'closed'.")
    url = _repo_url(settings, f"issues/{issue_number}")
    try:
        resp = await _request("PATCH", url, settings, json={"state": state})
        if resp.status_code == 200:
            data = resp.json()
            html_url = data.get("html_url", "")
            return GHResult(ok=True, url=html_url)
        return GHResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return GHResult(ok=False, error=str(exc))


async def set_labels(
    settings: Settings,
    issue_number: int,
    labels: list[str],
) -> GHResult:
    """Replace all labels on an issue or PR with the given list."""
    url = _repo_url(settings, f"issues/{issue_number}/labels")
    try:
        resp = await _request("PUT", url, settings, json={"labels": labels})
        if resp.status_code == 200:
            return GHResult(ok=True)
        return GHResult(ok=False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        return GHResult(ok=False, error=str(exc))
