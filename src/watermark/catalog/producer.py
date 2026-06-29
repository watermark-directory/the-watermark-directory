"""The producer→entry drift gate (epic #631, issue #629).

Keeps the catalog honest as the code evolves: if you change a dataset-producing connector
without touching its catalog entry, CI fails. The mechanism (periplus ``catalog:check``): map a
changed source file → the catalog entries that name it as their ``producer.connector_ref``; if a
producer changed in the diff but **none** of its entries did, that's drift.

Keyed on ``connector_ref`` (a precise dotted module → file mapping). ``producer.command`` is not
used as a trigger yet — commands live in the ``cli.py`` monolith, so a change can't be attributed
to one command until that's split (#595/#596, paired with #630). The gate is pure over
``(entries, changed_paths)`` so it is fully testable; the git plumbing + the
``[catalog-waiver: …]`` escape hatch live in the thin CLI wrapper.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from watermark.catalog import CatalogEntry, load_entries
from watermark.config import Settings, get_settings

_CATALOG_PREFIX = "data/catalog/"
_WAIVER = re.compile(r"\[catalog-waiver:\s*(.+?)\]", re.IGNORECASE)


def _ref_source_paths(connector_ref: str) -> set[str]:
    """The candidate source files a dotted module ref resolves to (module + package init)."""
    base = "src/" + connector_ref.replace(".", "/")
    return {f"{base}.py", f"{base}/__init__.py"}


def _entry_catalog_path(entry: CatalogEntry) -> str:
    return f"{_CATALOG_PREFIX}{entry.scope}/{entry.id}.yaml"


class ProducerFinding(BaseModel):
    """A producer that changed without any of its catalog entries being touched."""

    model_config = ConfigDict(extra="forbid")

    connector_ref: str
    source: str  # the changed source path that triggered it
    expected_entries: list[str]  # one of these entry yamls should have been in the diff
    detail: str = ""


def producer_drift(entries: list[CatalogEntry], changed_paths: set[str]) -> list[ProducerFinding]:
    """Findings for producers that changed without their catalog entries (pure, no git).

    For each ``connector_ref`` referenced by ≥1 entry: if one of its source files is in
    ``changed_paths`` but none of its entries' ``data/catalog/**`` files are, that's drift.
    """
    by_ref: dict[str, list[CatalogEntry]] = {}
    for entry in entries:
        ref = entry.producer.connector_ref
        if ref:
            by_ref.setdefault(ref, []).append(entry)

    findings: list[ProducerFinding] = []
    for ref, ref_entries in sorted(by_ref.items()):
        touched_source = _ref_source_paths(ref) & changed_paths
        if not touched_source:
            continue
        entry_paths = {_entry_catalog_path(e) for e in ref_entries}
        if entry_paths & changed_paths:
            continue  # at least one of this producer's entries was updated — honest
        findings.append(
            ProducerFinding(
                connector_ref=ref,
                source=sorted(touched_source)[0],
                expected_entries=sorted(e.id for e in ref_entries),
                detail=(
                    f"{ref} changed but no catalog entry was touched — update one of "
                    f"{sorted(e.id for e in ref_entries)} (or add a [catalog-waiver: reason])"
                ),
            )
        )
    return findings


# --- git plumbing (thin, impure) -----------------------------------------------------------
def _git(args: list[str], *, cwd: Path) -> str | None:
    """Run a git command, returning stdout (stripped) or ``None`` on any failure."""
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout.strip()


def changed_paths_vs(base: str, *, repo_root: Path) -> set[str] | None:
    """Repo-relative paths changed on this branch vs ``base`` (committed + working tree).

    Returns ``None`` when ``base`` can't be resolved (e.g. a shallow CI checkout without the
    ref) so the caller can skip rather than false-fail.
    """
    if _git(["rev-parse", "--verify", "--quiet", base], cwd=repo_root) is None:
        return None
    merge_base = _git(["merge-base", base, "HEAD"], cwd=repo_root)
    if merge_base is None:
        return None
    committed = _git(["diff", "--name-only", merge_base, "HEAD"], cwd=repo_root) or ""
    working = _git(["diff", "--name-only", "HEAD"], cwd=repo_root) or ""
    return {p for p in (committed + "\n" + working).splitlines() if p}


def waiver_reason(base: str, *, repo_root: Path) -> str | None:
    """The ``[catalog-waiver: …]`` reason from any commit message since ``base``, if present."""
    merge_base = _git(["merge-base", base, "HEAD"], cwd=repo_root)
    if merge_base is None:
        return None
    log = _git(["log", f"{merge_base}..HEAD", "--format=%B"], cwd=repo_root) or ""
    match = _WAIVER.search(log)
    return match.group(1).strip() if match else None


class ProducerCheckResult(BaseModel):
    """The outcome of a producer-drift check run (for the CLI)."""

    model_config = ConfigDict(extra="forbid")

    status: str  # "clean" | "drift" | "waived" | "skipped"
    findings: list[ProducerFinding] = []
    detail: str = ""


def run_producer_check(
    *, base: str = "origin/main", settings: Settings | None = None
) -> ProducerCheckResult:
    """Resolve the diff vs ``base`` and gate on producer drift (waiver- and skip-aware)."""
    settings = settings or get_settings()
    repo_root = settings.data_dir.parent
    changed = changed_paths_vs(base, repo_root=repo_root)
    if changed is None:
        return ProducerCheckResult(status="skipped", detail=f"base {base!r} unavailable")
    waiver = waiver_reason(base, repo_root=repo_root)
    findings = producer_drift(load_entries(settings=settings), changed)
    if not findings:
        return ProducerCheckResult(status="clean")
    if waiver:
        return ProducerCheckResult(status="waived", findings=findings, detail=waiver)
    return ProducerCheckResult(status="drift", findings=findings)
