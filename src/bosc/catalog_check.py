"""``bosc catalog check`` — the validation + drift gate (epic #631, issue #626).

The capstone of Phase 1: turns the manual ``corpus-completeness-audit.md`` pass into a
CI-enforced invariant. Wired into ``mise run check`` and the CI ``check`` job, it fails
(non-zero) when the catalog and the data tree have drifted apart:

* **schema** — a ``data/catalog/**.yaml`` that doesn't validate, or a duplicate ``id``
  (delegated to :func:`bosc.catalog.validate_entries`).
* **missing-files** — an entry whose declared concrete storage doesn't exist on disk. A
  Git-LFS *pointer* counts as present-but-unmaterialized (reported distinctly, not missing).
* **orphan-file** — a file under a catalogued scope (``reference``/``extracted``) with **no**
  catalog entry: the "we added data but never catalogued it" leak this gate exists to catch.
* **stale** — an entry past ``refresh.ttl_days`` (warn by default; ``--strict`` makes it fail).
* **checksum-drift** — a pinned single-file entry whose observed sha256 ≠ its pin.

Offline and hermetic (it observes the filesystem via :func:`bosc.catalog_reconcile.reconcile`;
no network). It is **LFS-aware**: CI checks out without LFS bytes, so unmaterialized pointers
are never treated as missing or drift — only as an informational ``unmaterialized`` note.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from bosc.catalog import CatalogEntry, load_entries, validate_entries
from bosc.catalog_backfill import BACKFILL_SCOPES, _is_data_file
from bosc.catalog_reconcile import load_observed, reconcile
from bosc.config import Settings, get_settings
from bosc.sites import SITES

Severity = Literal["error", "warn"]
CheckKind = Literal[
    "schema",
    "duplicate-id",
    "missing-files",
    "orphan-file",
    "stale",
    "checksum-drift",
    "render-drift",
    "unmaterialized",
    "no-snapshot",
]


class CheckFinding(BaseModel):
    """One gate finding. ``severity='error'`` fails the gate; ``'warn'`` is informational."""

    model_config = ConfigDict(extra="forbid")

    kind: CheckKind
    severity: Severity
    subject: str  # the entry id or the orphan file's relpath
    detail: str = ""


def _covered_relpaths(entries: list[CatalogEntry], settings: Settings) -> set[str]:
    """Every data-tree relpath claimed by some entry's storage (``{site}`` templates expanded)."""
    covered: set[str] = set()
    for entry in entries:
        for item in entry.storage:
            rel = item.relpath
            if "{site}" in rel:
                for slug in sorted(SITES):
                    actual = rel.replace("{site}", slug)
                    if (settings.data_dir / actual).exists():
                        covered.add(actual)
            else:
                covered.add(rel)
    return covered


def _all_data_files(settings: Settings) -> set[str]:
    """Every catalogue-eligible file under the catalogued scopes (same skip rules as backfill)."""
    found: set[str] = set()
    for scope in BACKFILL_SCOPES:
        root = settings.data_dir / scope
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if _is_data_file(path):
                found.add(str(path.relative_to(settings.data_dir)))
    return found


def check(
    *,
    settings: Settings | None = None,
    strict: bool = False,
    now: datetime | None = None,
) -> list[CheckFinding]:
    """Run every catalog invariant and return the findings (errors fail the gate).

    ``strict`` promotes staleness from a warning to a failure. ``now`` drives the freshness
    check (defaults to the current time, injectable for deterministic tests).
    """
    settings = settings or get_settings()
    findings: list[CheckFinding] = []

    # 1. schema + duplicate id — if the catalog can't even load, stop here (nothing else is safe).
    schema_findings = validate_entries(settings=settings)
    for f in schema_findings:
        kind: CheckKind = "duplicate-id" if f.kind == "duplicate-id" else "schema"
        findings.append(
            CheckFinding(kind=kind, severity="error", subject=f.entry_id, detail=f.detail)
        )
    if any(f.kind == "load-error" for f in schema_findings):
        return findings  # the tree is unparseable; missing/orphan/drift can't be trusted

    entries = load_entries(settings=settings)

    # 2 + 3. missing files / unmaterialized LFS / staleness — from a live observation.
    snapshot = reconcile(settings=settings, now=now)
    for eid, obs in snapshot.entries.items():
        if not obs.exists:
            findings.append(
                CheckFinding(
                    kind="missing-files",
                    severity="error",
                    subject=eid,
                    detail=f"declared file(s) absent on disk: {', '.join(obs.missing) or '(no storage)'}",
                )
            )
        elif not obs.lfs_materialized:
            findings.append(
                CheckFinding(
                    kind="unmaterialized",
                    severity="warn",
                    subject=eid,
                    detail="present but Git-LFS bytes not materialized (expected in a no-LFS checkout)",
                )
            )
        if obs.stale:
            findings.append(
                CheckFinding(
                    kind="stale",
                    severity="error" if strict else "warn",
                    subject=eid,
                    detail=f"past refresh.ttl_days (asof {obs.asof})",
                )
            )

    # 4. orphan files — committed data under a catalogued scope with no entry.
    orphans = _all_data_files(settings) - _covered_relpaths(entries, settings)
    for rel in sorted(orphans):
        findings.append(
            CheckFinding(
                kind="orphan-file",
                severity="error",
                subject=rel,
                detail="no catalog entry — run `bosc catalog backfill --apply`",
            )
        )

    # 5. checksum drift — a pinned single-file entry whose observed sha ≠ its pin.
    findings.extend(_checksum_findings(entries, settings))

    # 6. render drift — a README that opted into `bosc catalog render` but fell out of sync.
    from bosc.catalog_render import render_drift

    for collection, relpath in render_drift(settings=settings):
        findings.append(
            CheckFinding(
                kind="render-drift",
                severity="error",
                subject=relpath,
                detail=f"{collection} README out of sync — run `bosc catalog render --apply`",
            )
        )

    return findings


def _checksum_findings(entries: list[CatalogEntry], settings: Settings) -> list[CheckFinding]:
    """Compare each pinned single-file entry's committed-observed sha against its pin."""
    observed = load_observed(settings=settings)
    out: list[CheckFinding] = []
    pinned = [e for e in entries if len(e.storage) == 1 and e.storage[0].sha256]
    if pinned and observed is None:
        out.append(
            CheckFinding(
                kind="no-snapshot",
                severity="warn",
                subject="_observed.yaml",
                detail="pinned entries exist but no snapshot — run `bosc catalog reconcile`",
            )
        )
        return out
    if observed is None:
        return out
    for entry in pinned:
        pin = entry.storage[0].sha256
        if pin is None:  # narrowed for the type checker (the `pinned` filter guarantees it)
            continue
        obs = observed.entries.get(entry.id)
        if obs is None or obs.sha256 is None:
            continue  # unreconciled or an unmaterialized LFS pointer — can't verify
        if obs.sha256 != pin:
            out.append(
                CheckFinding(
                    kind="checksum-drift",
                    severity="error",
                    subject=entry.id,
                    detail=f"observed sha256 {obs.sha256[:12]}… ≠ pinned {pin[:12]}…",
                )
            )
    return out


def errors(findings: list[CheckFinding]) -> list[CheckFinding]:
    """The gate-failing subset."""
    return [f for f in findings if f.severity == "error"]
