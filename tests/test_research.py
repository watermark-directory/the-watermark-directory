"""Automated-research runs: orchestration, distillation, manifest persistence.

Hermetic — the Agent SDK ``query`` is monkeypatched and the distiller uses a fake
Anthropic client (the same pattern as ``test_agent`` / ``test_civic_summarize``), so
nothing here hits the network or needs API keys.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock
from pydantic import ValidationError

from watermark.agent import client as client_mod
from watermark.agent.extractor import StructuredExtractor
from watermark.config import Settings
from watermark.research import (
    IssueProposal,
    ResearchRunManifest,
    RunProvenance,
    build_plan,
    existing_keys,
    load_manifest,
    marker,
    run_research,
    run_slug,
    write_run,
)
from watermark.research.run import distill_proposals

_DRAFTS = {
    "proposals": [
        {
            "title": "Verify the Diller roundabout contingency rate",
            "body": "Summary lists 25% but the detail pages imply 20%. Acceptance: reconcile.",
            "rationale": "A discrepancy that moves the program total.",
            "labels": ["extraction"],
        },
        {
            "title": "Extract the missing OPC detail page 327",
            "body": "Page 327 is unextracted. Acceptance: a validated Estimate for it.",
            "rationale": "A corpus gap.",
            "labels": [],
        },
    ]
}


class _FakeMessages:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def create(self, **_: Any) -> Any:
        block = type(
            "B", (), {"type": "tool_use", "name": "record_extraction", "input": self._payload}
        )
        return type("M", (), {"content": [block()]})()


class _FakeClient:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.messages = _FakeMessages(payload)


def _extractor(payload: dict[str, Any] | None = None) -> StructuredExtractor:
    return StructuredExtractor(client=_FakeClient(payload or _DRAFTS), settings=Settings())


async def _fake_query(*, prompt: str, options: Any):  # type: ignore[no-untyped-def]
    yield AssistantMessage(
        content=[TextBlock(text="The Diller estimate uses a 25% contingency. ")], model="m"
    )
    yield AssistantMessage(
        content=[ToolUseBlock(id="t1", name="mcp__bosc__program_overview", input={})], model="m"
    )
    yield ResultMessage(
        subtype="success",
        duration_ms=1,
        duration_api_ms=1,
        is_error=False,
        num_turns=3,
        session_id="s",
        total_cost_usd=0.0321,
        result="Findings: the Diller estimate uses a 25% contingency.",
    )


# --- distillation ----------------------------------------------------------
def test_distill_normalizes_labels_and_dedupe_key() -> None:
    proposals = distill_proposals(
        "some findings", topic="contingency", extractor=_extractor(), max_proposals=5
    )
    assert len(proposals) == 2
    first = proposals[0]
    # process labels are prepended in code; the topical suggestion is preserved, deduped.
    assert first.labels == ["agent-proposed", "needs-triage", "extraction"]
    assert first.dedupe_key == "verify-the-diller-roundabout-contingency-rate"


def test_distill_respects_max_proposals() -> None:
    proposals = distill_proposals("f", topic="t", extractor=_extractor(), max_proposals=1)
    assert len(proposals) == 1


# --- orchestration ---------------------------------------------------------
def test_run_research_builds_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_mod, "query", _fake_query)
    manifest = asyncio.run(
        run_research(
            "Diller contingency",
            generated_at="2026-06-10T12:00:00+00:00",
            settings=Settings(),
            extractor=_extractor(),
            max_proposals=5,
        )
    )
    prov = manifest.provenance
    assert prov.topic == "Diller contingency"
    assert prov.tools_used == ["mcp__bosc__program_overview"]
    assert prov.num_turns == 3
    assert prov.cost_usd == 0.0321
    assert prov.max_turns == Settings().research_max_turns  # taken from the agent
    assert "25% contingency" in manifest.findings
    assert len(manifest.proposals) == 2
    assert manifest.proposals[0].labels[:2] == ["agent-proposed", "needs-triage"]


# --- persistence -----------------------------------------------------------
def test_write_run_persists_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_mod, "query", _fake_query)
    manifest = asyncio.run(
        run_research(
            "Diller contingency",
            generated_at="2026-06-10T12:00:00+00:00",
            settings=Settings(),
            extractor=_extractor(),
            max_proposals=5,
        )
    )
    out = write_run(manifest, tmp_path / "run", settings=Settings(data_dir=tmp_path / "data"))

    findings = (out / "findings.md").read_text(encoding="utf-8")
    assert findings.startswith("---\n")  # YAML frontmatter
    assert "topic: Diller contingency" in findings
    assert "25% contingency" in findings

    doc = yaml.safe_load((out / "manifest.yaml").read_text(encoding="utf-8"))
    assert doc["meta"]["topic"] == "Diller contingency"
    assert doc["meta"]["findings"] == "findings.md"
    assert doc["meta"]["provenance"]["num_turns"] == 3
    first = doc["proposals"][0]
    assert first["dedupe_key"] == "verify-the-diller-roundabout-contingency-rate"
    assert "agent-proposed" in first["labels"]


def test_write_run_refuses_corpus_path() -> None:
    settings = Settings()
    empty = ResearchRunManifest(
        provenance=RunProvenance(topic="t", model="m", generated_at="2026-06-10T00:00:00+00:00"),
        findings="x",
        proposals=[],
    )
    with pytest.raises(ValueError, match="immutable corpus"):
        write_run(empty, settings.documents_dir / "sneaky", settings=settings)


# --- slug ------------------------------------------------------------------
def test_run_slug_is_deterministic() -> None:
    assert (
        run_slug("Diller Contingency Rate!", "2026-06-10T12:00:00+00:00")
        == "diller-contingency-rate-2026-06-10"
    )


# --- dedupe / publish plan -------------------------------------------------
def _manifest() -> ResearchRunManifest:
    return ResearchRunManifest(
        provenance=RunProvenance(
            topic="Diller contingency",
            model="claude-opus-4-8",
            generated_at="2026-06-10T12:00:00+00:00",
            tools_used=["mcp__bosc__program_overview"],
            num_turns=3,
            max_turns=30,
            cost_usd=0.0321,
        ),
        findings="Findings body.",
        proposals=[
            IssueProposal(
                title="Verify the Diller roundabout contingency rate",
                body="Reconcile 25% vs 20%.",
                labels=["agent-proposed", "needs-triage", "extraction"],
                rationale="Moves the total.",
                dedupe_key="verify-the-diller-roundabout-contingency-rate",
            ),
            IssueProposal(
                title="Extract the missing OPC detail page 327",
                body="Page 327 is unextracted.",
                labels=["agent-proposed", "needs-triage"],
                rationale="Corpus gap.",
                dedupe_key="extract-the-missing-opc-detail-page-327",
            ),
        ],
    )


def test_existing_keys_reads_marker_and_title_fallback() -> None:
    keys = existing_keys(
        [
            {"number": 1, "title": "Anything at all", "body": f"x {marker('keyed-by-marker')} y"},
            {"number": 2, "title": "Extract the missing OPC detail page 327", "body": "no marker"},
        ]
    )
    assert "keyed-by-marker" in keys  # from the embedded marker
    assert "extract-the-missing-opc-detail-page-327" in keys  # from the title slug
    assert "anything-at-all" in keys


def test_build_plan_dedupes_and_embeds_marker() -> None:
    # An open issue already covers proposal #2 (by title slug).
    existing = [{"number": 9, "title": "Extract the missing OPC detail page 327", "body": ""}]
    plan = build_plan(_manifest(), existing=existing, run_ref="data/research/run-1")

    assert plan.pr_title == "research: Diller contingency"
    assert "$0.0321" in plan.pr_body  # provenance + cost embedded (#79 PR template)
    assert "1 opened" in plan.pr_body and "1 skipped" in plan.pr_body
    assert plan.duplicates == ["extract-the-missing-opc-detail-page-327"]
    assert [i.dedupe_key for i in plan.issues] == ["verify-the-diller-roundabout-contingency-rate"]
    # The opened issue's body carries the dedupe marker so a later run won't re-propose.
    assert marker("verify-the-diller-roundabout-contingency-rate") in plan.issues[0].body
    assert "data/research/run-1" in plan.issues[0].body


def test_build_plan_skips_same_run_collision() -> None:
    m = _manifest()
    m.proposals[1].dedupe_key = m.proposals[0].dedupe_key  # force a within-run collision
    plan = build_plan(m, existing=[], run_ref="data/research/run-2")
    assert len(plan.issues) == 1
    assert plan.duplicates == [m.proposals[0].dedupe_key]


def test_load_manifest_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_mod, "query", _fake_query)
    manifest = asyncio.run(
        run_research(
            "Diller contingency",
            generated_at="2026-06-10T12:00:00+00:00",
            settings=Settings(),
            extractor=_extractor(),
            max_proposals=5,
        )
    )
    out = write_run(manifest, tmp_path / "run", settings=Settings(data_dir=tmp_path / "data"))
    loaded = load_manifest(out)
    assert loaded.provenance.topic == "Diller contingency"
    assert loaded.provenance.num_turns == 3
    assert loaded.provenance.cost_usd == 0.0321
    assert [p.dedupe_key for p in loaded.proposals] == [p.dedupe_key for p in manifest.proposals]


def test_proposal_drafts_coerces_json_string_list() -> None:
    """Forced tool use sometimes returns `proposals` as a JSON *string* — tolerate it."""
    from watermark.research.models import ProposalDrafts

    drafts = [{"title": "T", "body": "B", "rationale": "R", "labels": ["extraction"]}]
    # native list (the normal path) and a JSON-encoded string both validate identically
    native = ProposalDrafts(proposals=drafts)
    coerced = ProposalDrafts.model_validate({"proposals": json.dumps(drafts)})
    assert coerced == native
    assert coerced.proposals[0].title == "T"


def test_proposal_drafts_coerces_stringified_list_with_control_chars() -> None:
    """The stringified `proposals` array routinely carries unescaped LITERAL newlines in the
    long body/rationale text — the quirk that broke the first Urbana onboarding run. The default
    strict JSON parser rejects those control chars; the coercion uses strict=False so the run
    isn't lost."""
    from watermark.research.models import ProposalDrafts

    # A model-emitted stringified array with a real newline inside `body` (not "\\n", an actual \n).
    raw = '[{"title": "T", "body": "para one\npara two", "rationale": "R", "labels": ["grid"]}]'
    drafts = ProposalDrafts.model_validate({"proposals": raw})
    assert len(drafts.proposals) == 1
    assert drafts.proposals[0].body == "para one\npara two"


def test_proposal_drafts_coerces_fenced_prose_and_trailing_commas() -> None:
    """Three more stringified-array quirks that broke a Sidney onboarding run: a wrapping
    markdown code fence, prose around the array, and a trailing comma before ``]``/``}`` (valid
    JS, invalid JSON). The coercion strips/repairs all three rather than lose the run."""
    from watermark.research.models import ProposalDrafts

    fenced = '```json\n[{"title": "T", "body": "B", "rationale": "R"}]\n```'
    prose = 'Here are the proposals:\n[{"title": "T", "body": "B", "rationale": "R"}]\nDone.'
    trailing = '[{"title": "T", "body": "B", "rationale": "R", "labels": ["x",]},]'
    for raw in (fenced, prose, trailing):
        drafts = ProposalDrafts.model_validate({"proposals": raw})
        assert len(drafts.proposals) == 1
        assert drafts.proposals[0].title == "T"


def test_proposal_draft_coerces_stringified_labels() -> None:
    """The model also stringifies the nested `labels` array — coerce it back too (the other
    failure mode the Urbana run surfaced)."""
    from watermark.research.models import ProposalDrafts

    drafts = ProposalDrafts.model_validate(
        {
            "proposals": [
                {"title": "T", "body": "B", "rationale": "R", "labels": '["energy", "urbana"]'}
            ]
        }
    )
    assert drafts.proposals[0].labels == ["energy", "urbana"]


def test_proposal_drafts_rejects_non_json_string() -> None:
    """A non-JSON string still fails validation (no silent swallow)."""
    from watermark.research.models import ProposalDrafts

    with pytest.raises(ValueError):
        ProposalDrafts.model_validate({"proposals": "not json at all"})


class _FlakyExtractor:
    """Duck-typed extractor: raises a real ValidationError the first ``fail_times`` calls."""

    def __init__(self, drafts: Any, fail_times: int) -> None:
        self._drafts = drafts
        self._fail_times = fail_times
        self.calls = 0

    def extract_from_text(self, target: Any, *, instructions: str, text: str) -> Any:
        from watermark.research.models import ProposalDrafts

        self.calls += 1
        if self.calls <= self._fail_times:
            ProposalDrafts.model_validate(
                {"proposals": "truncated-not-json"}
            )  # raises ValidationError
        return self._drafts


def test_distill_retries_then_succeeds() -> None:
    """The distiller re-rolls the model on a malformed draw rather than losing the run."""
    from watermark.research.models import ProposalDrafts

    drafts = ProposalDrafts(
        proposals=[{"title": "T", "body": "B", "rationale": "R", "labels": ["hydrology"]}]
    )
    ex = _FlakyExtractor(drafts, fail_times=2)  # fails twice, succeeds on the 3rd
    out = distill_proposals("findings", topic="t", extractor=ex, max_proposals=5)  # type: ignore[arg-type]
    assert ex.calls == 3
    assert out[0].title == "T"
    assert "agent-proposed" in out[0].labels


def test_distill_raises_after_exhausting_retries() -> None:
    """If every attempt fails, the last error propagates (no silent empty run)."""
    ex = _FlakyExtractor(None, fail_times=99)
    with pytest.raises(ValidationError):
        distill_proposals("findings", topic="t", extractor=ex, max_proposals=5)  # type: ignore[arg-type]
    assert ex.calls == 3


# --- recipes (the ResearchRecipe seam) -------------------------------------
_ASSESS_DRAFT = {
    "signal": "anchor",
    "tag": "verified",
    "group": "arsenal",
    "fields": {"nexus": "Lima Army Tank Plant (JSMC)", "linkage": "Co-located", "stray": "dropped"},
    "citations": [{"source": "docs/defense-nexus.md", "source_kind": "reference"}],
    "rationale": "JSMC is co-located with the campus.",
}


def test_recipes_registry_defaults_to_issue_proposal() -> None:
    from watermark.research import ISSUE_PROPOSAL_RECIPE, RECIPES

    assert set(RECIPES) == {"issue-proposal", "hypothesis-assessment", "site-onboard"}
    assert RECIPES["issue-proposal"] is ISSUE_PROPOSAL_RECIPE


def test_hypothesis_assessment_recipe_produces_a_cell(monkeypatch: pytest.MonkeyPatch) -> None:
    from watermark.research import HYPOTHESIS_ASSESSMENT_RECIPE

    monkeypatch.setattr(client_mod, "query", _fake_query)
    manifest = asyncio.run(
        run_research(
            "assess springfield x defense",
            generated_at="2026-06-22T00:00:00+00:00",
            settings=Settings(),
            extractor=_extractor(_ASSESS_DRAFT),
            recipe=HYPOTHESIS_ASSESSMENT_RECIPE,
            context={"hypothesis": "defense", "site": "springfield"},
        )
    )
    assert manifest.proposals == []  # the assessment recipe fills assessments, not proposals
    assert len(manifest.assessments) == 1
    cell = manifest.assessments[0]
    assert cell.site == "springfield"
    assert cell.hypothesis == "defense"
    assert cell.signal == "anchor"
    assert cell.tag == "verified"
    # fields are filtered to the hypothesis's declared columns — the stray key is dropped.
    assert cell.fields == {"nexus": "Lima Army Tank Plant (JSMC)", "linkage": "Co-located"}
    assert cell.citations[0].source == "docs/defense-nexus.md"


def test_assessment_recipe_validates_context() -> None:
    from watermark.research import HYPOTHESIS_ASSESSMENT_RECIPE

    with pytest.raises(ValueError, match="hypothesis"):
        asyncio.run(
            run_research(
                "bad",
                generated_at="2026-06-22T00:00:00+00:00",
                settings=Settings(),
                extractor=_extractor(_ASSESS_DRAFT),
                recipe=HYPOTHESIS_ASSESSMENT_RECIPE,
                context={"hypothesis": "ghost", "site": "springfield"},
            )
        )


def test_write_and_load_run_round_trips_assessment_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from watermark.hypotheses import HypothesisAssessment
    from watermark.research import HYPOTHESIS_ASSESSMENT_RECIPE

    monkeypatch.setattr(client_mod, "query", _fake_query)
    manifest = asyncio.run(
        run_research(
            "assess springfield x defense",
            generated_at="2026-06-22T00:00:00+00:00",
            settings=Settings(),
            extractor=_extractor(_ASSESS_DRAFT),
            recipe=HYPOTHESIS_ASSESSMENT_RECIPE,
            context={"hypothesis": "defense", "site": "springfield"},
        )
    )
    out = write_run(manifest, tmp_path / "run", settings=Settings(data_dir=tmp_path / "data"))

    # The candidate cell is a ready-to-promote data/hypotheses/ file: it re-validates, and the
    # computed `verified` field is NOT serialized (extra='forbid' would reject it on reload).
    cell_path = out / "assessments" / "defense-springfield.yaml"
    raw = yaml.safe_load(cell_path.read_text(encoding="utf-8"))
    assert "verified" not in raw["citations"][0]
    HypothesisAssessment.model_validate(raw)  # the committed-store schema accepts it

    doc = yaml.safe_load((out / "manifest.yaml").read_text(encoding="utf-8"))
    assert doc["assessments"][0]["file"] == "assessments/defense-springfield.yaml"

    loaded = load_manifest(out)
    assert [c.site for c in loaded.assessments] == ["springfield"]
    assert loaded.assessments[0].fields["nexus"] == "Lima Army Tank Plant (JSMC)"


def test_assessment_draft_coerces_stringified_citations_and_fields() -> None:
    """Forced tool use sometimes stringifies the nested `citations`/`fields` — tolerate both."""
    from watermark.research.models import AssessmentDraft

    draft = AssessmentDraft.model_validate(
        {
            "signal": "moderate",
            "tag": "inference",
            "fields": '{"nexus": "X", "linkage": "Y"}',
            "citations": '[{"source": "docs/x.md", "source_kind": "assumption"}]',
        }
    )
    assert draft.fields == {"nexus": "X", "linkage": "Y"}
    assert draft.citations[0].source == "docs/x.md"
    assert draft.citations[0].verified is False  # 'assumption' is not [verified]
