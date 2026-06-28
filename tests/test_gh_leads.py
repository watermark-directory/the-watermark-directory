"""Unit tests for bosc.site.gh_leads — label parsing and merge logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bosc.site.feeds import LeadItem
from bosc.site.gh_leads import GithubIssue, issue_to_lead, merge_leads

_FIXTURE = Path(__file__).parent / "fixtures" / "gh_leads" / "lima.json"


def _load_fixture() -> list[GithubIssue]:
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    from bosc.site.gh_leads import _extract_labels

    return [
        GithubIssue(
            number=item["number"],
            title=item["title"],
            body=item.get("body") or "",
            labels=_extract_labels(item.get("labels", [])),
            state=item["state"],
            html_url=item["html_url"],
        )
        for item in raw
    ]


def _issue(**overrides: object) -> GithubIssue:
    defaults = {
        "number": 7,
        "title": "Test issue",
        "body": "Some body text.",
        "labels": [
            "area:evidence",
            "site:lima",
            "lead:kind:signal",
            "lead:status:unanswered",
            "lead:tag:inference",
        ],
        "state": "open",
        "html_url": "https://github.com/goedelsoup/bosc/issues/7",
    }
    defaults.update(overrides)
    return GithubIssue(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# issue_to_lead
# ---------------------------------------------------------------------------


def test_issue_to_lead_happy_path() -> None:
    issue = _issue()
    lead = issue_to_lead(issue)
    assert lead is not None
    assert lead.id == "GH-7"
    assert lead.kind == "signal"
    assert lead.status == "unanswered"
    assert lead.tag == "inference"
    assert lead.title == "Test issue"
    assert lead.detail == "Some body text."
    assert lead.source == "goedelsoup/bosc#7"
    assert lead.issue == 7
    assert lead.note is None


def test_issue_to_lead_missing_kind() -> None:
    issue = _issue(labels=["area:evidence", "site:lima", "lead:status:unanswered"])
    assert issue_to_lead(issue) is None


def test_issue_to_lead_missing_status() -> None:
    issue = _issue(labels=["area:evidence", "site:lima", "lead:kind:signal"])
    assert issue_to_lead(issue) is None


def test_issue_to_lead_ambiguous_kind() -> None:
    issue = _issue(
        labels=[
            "area:evidence",
            "lead:kind:signal",
            "lead:kind:question",
            "lead:status:unanswered",
        ]
    )
    assert issue_to_lead(issue) is None


def test_issue_to_lead_tag_default() -> None:
    issue = _issue(labels=["area:evidence", "lead:kind:signal", "lead:status:low"])
    lead = issue_to_lead(issue)
    assert lead is not None
    assert lead.tag == "open"


def test_issue_to_lead_detail_truncated() -> None:
    long_body = "x" * 3_000
    issue = _issue(body=long_body)
    lead = issue_to_lead(issue)
    assert lead is not None
    assert len(lead.detail) == 2_001  # 2000 chars + "…"
    assert lead.detail.endswith("…")


# ---------------------------------------------------------------------------
# merge_leads
# ---------------------------------------------------------------------------


def _hand_curated(id: str = "MANUAL-1") -> LeadItem:
    return LeadItem(
        id=id,
        kind="signal",
        status="unanswered",
        tag="open",
        title="A hand-curated lead",
        detail="Curated by hand, no issue link.",
        source="corpus-completeness-audit",
    )


def _gh_lead(number: int = 7, title: str = "GH lead") -> LeadItem:
    return LeadItem(
        id=f"GH-{number}",
        kind="question",
        status="unanswered",
        tag="open",
        title=title,
        detail="Pulled from GitHub.",
        source=f"goedelsoup/bosc#{number}",
        issue=number,
    )


def test_merge_leads_preserves_handcurated() -> None:
    existing = [_hand_curated(), _gh_lead(5)]
    merged = merge_leads([], existing)
    assert len(merged) == 1
    assert merged[0].id == "MANUAL-1"


def test_merge_leads_replaces_gh_backed() -> None:
    old_gh = _gh_lead(7, title="Old title")
    new_gh = _gh_lead(7, title="Updated title")
    existing = [_hand_curated(), old_gh]
    merged = merge_leads([new_gh], existing)
    assert len(merged) == 2
    gh_entry = next(m for m in merged if m.issue == 7)
    assert gh_entry.title == "Updated title"


def test_merge_leads_appends_new() -> None:
    existing = [_hand_curated()]
    new_gh = _gh_lead(9)
    merged = merge_leads([new_gh], existing)
    assert len(merged) == 2
    assert any(m.issue == 9 for m in merged)


def test_merge_leads_gh_sorted_by_issue_number() -> None:
    gh = [_gh_lead(20), _gh_lead(3), _gh_lead(11)]
    merged = merge_leads(gh, [])
    issue_nums = [m.issue for m in merged]
    assert issue_nums == [3, 11, 20]


# ---------------------------------------------------------------------------
# fixture coverage
# ---------------------------------------------------------------------------


def test_fixture_two_valid_one_skipped() -> None:
    issues = _load_fixture()
    leads = [item for issue in issues if (item := issue_to_lead(issue)) is not None]
    assert len(leads) == 2  # issue 44 lacks lead:kind → skipped
    assert {ld.issue for ld in leads} == {42, 43}


@pytest.mark.parametrize(
    "fixture_issue_number,expected_kind", [(42, "question"), (43, "redaction")]
)
def test_fixture_kind_mapping(fixture_issue_number: int, expected_kind: str) -> None:
    issues = _load_fixture()
    issue = next(i for i in issues if i.number == fixture_issue_number)
    lead = issue_to_lead(issue)
    assert lead is not None
    assert lead.kind == expected_kind
