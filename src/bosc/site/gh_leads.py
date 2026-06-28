"""Pull open leads for a site from GitHub issues.

Issues are the source of truth for GH-backed leads. An issue qualifies when it carries
both ``area:evidence`` and ``site:<slug>`` labels, plus the lead-vocabulary labels
(``lead:kind:*``, ``lead:status:*``, optionally ``lead:tag:*``). Hand-curated leads
with no ``issue`` field in the existing store are preserved verbatim through
:func:`merge_leads`; GH-backed entries (those with a matching ``issue`` number) are
replaced wholesale on each sync.
"""

from __future__ import annotations

import re
from typing import Any

import httpx
from pydantic import BaseModel

from bosc.config import Settings, get_settings
from bosc.logging import get_logger
from bosc.site.feeds import LeadItem

log = get_logger(__name__)

_LINK_RE = re.compile(r'<([^>]+)>;\s*rel="next"')
_REPO = "goedelsoup/bosc"
_DETAIL_MAX = 2_000


class GithubLeadsError(RuntimeError):
    """Raised on a non-200 GitHub API response or a fatal mapping failure."""


class GithubIssue(BaseModel):
    """Minimal representation of a GitHub issue from the REST API."""

    number: int
    title: str
    body: str
    labels: list[str]
    state: str
    html_url: str


def _extract_labels(raw: list[dict[str, Any]]) -> list[str]:
    return [item["name"] for item in raw if isinstance(item.get("name"), str)]


def _next_url(link_header: str | None) -> str | None:
    if not link_header:
        return None
    m = _LINK_RE.search(link_header)
    return m.group(1) if m else None


def fetch_site_issues(slug: str, *, settings: Settings | None = None) -> list[GithubIssue]:
    """Fetch open GitHub issues tagged ``area:evidence`` + ``site:<slug>`` for *slug*.

    Paginates via the ``Link: rel="next"`` header. Raises :class:`GithubLeadsError`
    on any non-200 response. Passes ``Authorization: Bearer <token>`` when
    ``settings.github_token`` is set; works anonymously (lower rate limit) when empty.
    """
    settings = settings or get_settings()
    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    url: str | None = (
        f"{settings.github_base_url}/repos/{_REPO}/issues"
        f"?labels=area:evidence,site:{slug}&state=open&per_page=100"
    )
    issues: list[GithubIssue] = []
    while url:
        resp = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        if resp.status_code != 200:
            raise GithubLeadsError(
                f"GitHub API returned {resp.status_code} for {url}: {resp.text[:200]}"
            )
        for raw in resp.json():
            issues.append(
                GithubIssue(
                    number=raw["number"],
                    title=raw["title"],
                    body=raw.get("body") or "",
                    labels=_extract_labels(raw.get("labels", [])),
                    state=raw["state"],
                    html_url=raw["html_url"],
                )
            )
        url = _next_url(resp.headers.get("link"))

    log.info("gh_leads.fetched", slug=slug, count=len(issues))
    return issues


def issue_to_lead(issue: GithubIssue) -> LeadItem | None:
    """Map a :class:`GithubIssue` to a :class:`LeadItem`, or ``None`` if labels are invalid.

    Required labels: exactly one ``lead:kind:*`` and one ``lead:status:*``. The tag
    defaults to ``"open"`` when no ``lead:tag:*`` label is present.
    """
    kinds = [lbl.removeprefix("lead:kind:") for lbl in issue.labels if lbl.startswith("lead:kind:")]
    statuses = [
        lbl.removeprefix("lead:status:") for lbl in issue.labels if lbl.startswith("lead:status:")
    ]
    tags = [lbl.removeprefix("lead:tag:") for lbl in issue.labels if lbl.startswith("lead:tag:")]

    if len(kinds) != 1:
        log.warning(
            "gh_leads.skip_missing_kind",
            issue=issue.number,
            kinds=kinds,
        )
        return None
    if len(statuses) != 1:
        log.warning(
            "gh_leads.skip_missing_status",
            issue=issue.number,
            statuses=statuses,
        )
        return None

    detail = issue.body
    if len(detail) > _DETAIL_MAX:
        detail = detail[:_DETAIL_MAX] + "…"

    return LeadItem(
        id=f"GH-{issue.number}",
        kind=kinds[0],
        status=statuses[0],
        tag=tags[0] if tags else "open",
        title=issue.title,
        detail=detail,
        source=f"goedelsoup/bosc#{issue.number}",
        issue=issue.number,
        note=None,
    )


def merge_leads(
    gh_items: list[LeadItem],
    existing: list[LeadItem],
) -> list[LeadItem]:
    """Merge GH-fetched leads with a site's existing store.

    - *preserved*: existing leads with ``issue is None`` (hand-curated) — kept verbatim.
    - *gh_items*: the fresh GH-sourced set — replaces any prior GH-backed entries wholesale.

    Result: ``preserved + sorted(gh_items, key=issue_number)``.
    """
    preserved = [item for item in existing if item.issue is None]
    gh_sorted = sorted(gh_items, key=lambda x: x.issue or 0)
    log.info(
        "gh_leads.merged",
        preserved=len(preserved),
        gh=len(gh_sorted),
    )
    return preserved + gh_sorted
