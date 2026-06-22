"""Typed models for automated-research runs.

A run investigates a topic over the corpus (read-only) and distills its findings
into a reviewable *issue-proposal manifest*: provenance + cost + a set of concrete,
actionable follow-up issues, each carrying a stable dedupe key. The manifest is the
machine-actionable artifact the research workflow (and a human reviewer) consume; the
prose findings live alongside it as ``findings.md``.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Process labels every agent-proposed issue carries: provenance (``agent-proposed``)
# plus inert-until-triaged (``needs-triage``). These are the runtime labels managed in
# ``.github/config`` (Pulumi, Epic 5.4); a proposal stays inert until a maintainer
# triages it. They are added in code, never by the distillation model.
RUNTIME_LABELS: tuple[str, ...] = ("agent-proposed", "needs-triage")


def _coerce_json_list(v: Any) -> Any:
    """Tolerate the distillation model emitting a list field as a JSON-encoded *string*.

    Forced-tool-use occasionally returns an array field (``proposals``, or a nested
    ``labels``) as a stringified JSON array instead of a native list. That string routinely
    carries one or more model quirks that trip a plain ``json.loads``:
      - **unescaped control characters** (literal newlines in long body / rationale text) →
        parse with ``strict=False``;
      - a wrapping **markdown code fence** (```` ```json … ``` ````) → strip it;
      - **prose around the array** → trim to the outermost ``[ … ]``;
      - a **trailing comma** before ``]``/``}`` (valid JS, invalid JSON) → repair it.
    We try the cleaned candidate first, then the raw string, so a whole research run isn't
    lost to that quirk (the costly prose findings already succeeded by this point). On a
    genuinely unparseable string, return it unchanged and let validation raise a clear error.
    """
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s.startswith("```"):  # a wrapping markdown code fence
        s = re.sub(r"^```[a-zA-Z0-9]*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s).strip()
    start, end = s.find("["), s.rfind("]")
    candidates = [s[start : end + 1]] if 0 <= start < end else []
    candidates.append(s)
    for c in candidates:
        # Try as-is, then with trailing commas (before } or ]) stripped.
        for attempt in (c, re.sub(r",(\s*[}\]])", r"\1", c)):
            try:
                return json.loads(attempt, strict=False)
            except json.JSONDecodeError:
                continue
    return v


class ProposalDraft(BaseModel):
    """One issue proposal as drafted by the distillation model (pre-normalization).

    The forced-tool-use schema the model fills. ``labels`` here are *topical*
    suggestions only (e.g. ``extraction``); the process labels are added downstream.
    """

    model_config = ConfigDict(extra="forbid")

    title: str
    body: str
    rationale: str
    labels: list[str] = Field(default_factory=list)

    @field_validator("labels", mode="before")
    @classmethod
    def _coerce_labels(cls, v: Any) -> Any:
        """The model sometimes stringifies the nested ``labels`` array too — coerce it back."""
        return _coerce_json_list(v)


class ProposalDrafts(BaseModel):
    """The distillation target: the full set of drafts from one findings pass."""

    model_config = ConfigDict(extra="forbid")

    proposals: list[ProposalDraft]

    @field_validator("proposals", mode="before")
    @classmethod
    def _coerce_proposals(cls, v: Any) -> Any:
        """Coerce a stringified ``proposals`` array (the forced-tool-use quirk) back to a list."""
        return _coerce_json_list(v)


class IssueProposal(BaseModel):
    """A normalized, ready-to-open issue proposal (runtime labels + dedupe key)."""

    model_config = ConfigDict(extra="forbid")

    title: str
    body: str
    labels: list[str]
    rationale: str
    # Stable slug used to dedupe a proposal against existing open issues (Epic 5.5).
    dedupe_key: str


class RunProvenance(BaseModel):
    """How a run was produced — the audit trail embedded in the manifest."""

    model_config = ConfigDict(extra="forbid")

    topic: str
    model: str
    generated_at: str  # ISO-8601; injected by the caller (keeps runs deterministic)
    tools_used: list[str] = Field(default_factory=list)
    num_turns: int = 0
    max_turns: int = 0
    cost_usd: float | None = None
    is_error: bool = False


class ResearchRunManifest(BaseModel):
    """A complete research run: provenance, prose findings, and issue proposals."""

    model_config = ConfigDict(extra="forbid")

    provenance: RunProvenance
    findings: str
    proposals: list[IssueProposal]
