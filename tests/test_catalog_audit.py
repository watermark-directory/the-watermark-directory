"""Tests for ``bosc catalog audit`` — the generated integrity audit (epic #631 Phase 3 / #659)."""

from __future__ import annotations

import textwrap
from pathlib import Path

from bosc.catalog_audit import (
    AUDIT_RELPATH,
    _state,
    audit_drift,
    build_audit,
    render_audit,
    write_audit,
)
from bosc.catalog_reconcile import ObservedEntry
from bosc.config import Settings


def _settings(tmp_path: Path) -> Settings:
    (tmp_path / "data").mkdir()
    return Settings(data_dir=tmp_path / "data")


def _entry(settings: Settings, name: str, scope: str, body: str) -> None:
    path = settings.catalog_dir / scope / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


def _observed(settings: Settings, body: str) -> None:
    (settings.catalog_dir).mkdir(parents=True, exist_ok=True)
    (settings.catalog_dir / "_observed.yaml").write_text(textwrap.dedent(body), encoding="utf-8")


def _ref_entry(settings: Settings, name: str, relpath: str) -> None:
    _entry(
        settings,
        name,
        "reference",
        f"""\
        id: {name}
        title: {name}
        scope: reference
        site_scope: basin-shared
        producer:
          kind: connector
          source: x
        refresh:
          cadence: static
        storage:
        - relpath: {relpath}
          media_type: application/x-yaml
        """,
    )
    disk = settings.data_dir / relpath
    disk.parent.mkdir(parents=True, exist_ok=True)
    disk.write_text("{}\n", encoding="utf-8")


# --- state reduction ----------------------------------------------------------------------
def test_state_reduction() -> None:
    def obs(**kw: object) -> ObservedEntry:
        base = {
            "exists": True,
            "sha256": None,
            "size_bytes": 1,
            "lfs_materialized": True,
            "file_count": 1,
        }
        return ObservedEntry.model_validate({**base, **kw})

    assert _state(None) == "unobserved"
    assert _state(obs(exists=False)) == "missing"
    assert _state(obs(lfs_materialized=False)) == "unmaterialized"
    assert _state(obs(stale=True)) == "stale"
    assert _state(obs()) == "present"


# --- build_audit --------------------------------------------------------------------------
def test_build_audit_headline_and_collections(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _ref_entry(settings, "echo-a", "reference/echo/a.yaml")
    _ref_entry(settings, "echo-b", "reference/echo/b.yaml")
    _ref_entry(settings, "eia-c", "reference/eia/c.yaml")
    _observed(
        settings,
        """\
        reconciled_at: '2026-06-24T00:00:00+00:00'
        entries:
          echo-a:
            exists: true
            sha256: null
            size_bytes: 1
            lfs_materialized: true
            file_count: 1
          echo-b:
            exists: true
            sha256: null
            size_bytes: 1
            lfs_materialized: true
            file_count: 1
            stale: true
          eia-c:
            exists: false
            sha256: null
            size_bytes: 0
            lfs_materialized: true
            file_count: 0
        """,
    )
    report = build_audit(settings=settings)
    assert report.total == 3
    assert report.present == 1 and report.stale == 1 and report.missing == 1
    assert report.reconciled_at == "2026-06-24T00:00:00+00:00"
    echo = next(c for c in report.collections if c.collection == "echo")
    assert echo.total == 2 and echo.present == 1 and echo.stale == 1
    # integrity gaps list carries the stale + missing rows
    gap_ids = {d.id for d in report.datasets if d.state in ("stale", "missing", "unobserved")}
    assert gap_ids == {"echo-b", "eia-c"}


def test_unobserved_when_no_snapshot(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _ref_entry(settings, "echo-a", "reference/echo/a.yaml")
    report = build_audit(settings=settings)
    assert report.reconciled_at is None
    assert report.total == 1 and report.unobserved == 1 and report.present == 0


# --- render + drift -----------------------------------------------------------------------
def test_render_is_deterministic(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _ref_entry(settings, "echo-a", "reference/echo/a.yaml")
    report = build_audit(settings=settings)
    assert render_audit(report) == render_audit(build_audit(settings=settings))


def test_audit_drift_lifecycle(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _ref_entry(settings, "echo-a", "reference/echo/a.yaml")
    # no committed report yet -> nothing to drift against
    assert audit_drift(settings=settings) is None
    # after writing, in sync
    relpath, changed = write_audit(settings=settings)
    assert relpath == AUDIT_RELPATH and changed is True
    assert audit_drift(settings=settings) is None
    # tamper -> drift detected
    (settings.data_dir / AUDIT_RELPATH).write_text("stale hand edit\n", encoding="utf-8")
    assert audit_drift(settings=settings) == AUDIT_RELPATH


# --- regression guard against the real committed catalog ----------------------------------
def test_committed_audit_is_in_sync() -> None:
    """The committed COMPLETENESS.md must match a fresh render (the `check` gate's invariant)."""
    assert audit_drift(settings=Settings()) is None
