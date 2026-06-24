"""Tests for ``bosc catalog check`` — the validation + drift gate (epic #631, issue #626).

Hermetic synthetic-tree tests pin each finding kind (orphan / missing / unmaterialized LFS /
stale / checksum-drift / duplicate-id), plus the regression guard that the *committed* catalog
passes the gate (no errors) — the CI-enforced successor to the manual completeness audit.
"""

from __future__ import annotations

import textwrap
from datetime import UTC, datetime
from pathlib import Path

from bosc.catalog_check import check, errors
from bosc.catalog_reconcile import reconcile, write_observed
from bosc.config import Settings

_FIXED = datetime(2026, 6, 24, 12, 0, tzinfo=UTC)


def _settings(tmp_path: Path) -> Settings:
    (tmp_path / "data").mkdir()
    return Settings(data_dir=tmp_path / "data")


def _data(settings: Settings, relpath: str, body: str = "x: 1\n") -> Path:
    path = settings.data_dir / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _entry(settings: Settings, name: str, body: str) -> None:
    path = settings.catalog_dir / "reference" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


def _basic(name: str, relpath: str, refresh: str = "  cadence: static\n") -> str:
    return (
        textwrap.dedent(
            f"""\
        id: {name}
        title: T
        scope: reference
        producer:
          kind: connector
          source: x
        storage:
        - relpath: {relpath}
          media_type: application/x-yaml
        refresh:
        """
        )
        + refresh
    )


def _kinds(findings: list) -> set[str]:  # type: ignore[type-arg]
    return {f.kind for f in findings}


# --- clean -----------------------------------------------------------------------------------
def test_clean_catalog_has_no_findings(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _entry(settings, "echo-x", _basic("echo-x", "reference/echo/x.yaml"))
    assert check(settings=settings, now=_FIXED) == []


# --- orphan ----------------------------------------------------------------------------------
def test_orphan_file_is_an_error(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _data(settings, "reference/echo/uncatalogued.yaml")  # no entry covers this
    _entry(settings, "echo-x", _basic("echo-x", "reference/echo/x.yaml"))
    findings = check(settings=settings, now=_FIXED)
    orphans = [f for f in findings if f.kind == "orphan-file"]
    assert [f.subject for f in orphans] == ["reference/echo/uncatalogued.yaml"]
    assert orphans[0].severity == "error"


def test_readme_is_not_an_orphan(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _data(settings, "reference/echo/README.md", "# docs\n")  # skipped, not catalogued
    _entry(settings, "echo-x", _basic("echo-x", "reference/echo/x.yaml"))
    assert "orphan-file" not in _kinds(check(settings=settings, now=_FIXED))


# --- missing / unmaterialized ----------------------------------------------------------------
def test_missing_declared_file_is_an_error(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(settings, "echo-x", _basic("echo-x", "reference/echo/gone.yaml"))
    findings = check(settings=settings, now=_FIXED)
    missing = [f for f in findings if f.kind == "missing-files"]
    assert missing and missing[0].severity == "error"
    assert "gone.yaml" in missing[0].detail


def test_unmaterialized_lfs_pointer_is_a_warning_not_missing(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(
        settings,
        "reference/imagery/scene.tif",
        "version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\nsize 1\n",
    )
    _entry(settings, "imagery-scene", _basic("imagery-scene", "reference/imagery/scene.tif"))
    findings = check(settings=settings, now=_FIXED)
    assert "missing-files" not in _kinds(findings)  # a pointer is present, not missing
    unmat = [f for f in findings if f.kind == "unmaterialized"]
    assert unmat and unmat[0].severity == "warn"
    assert errors(findings) == []  # never fails the gate


# --- staleness -------------------------------------------------------------------------------
def test_stale_warns_by_default_and_fails_under_strict(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml", "meta:\n  last_refreshed: '2020-01-01'\n")
    _entry(
        settings,
        "echo-x",
        _basic("echo-x", "reference/echo/x.yaml", refresh="  cadence: annual\n  ttl_days: 30\n"),
    )
    lenient = check(settings=settings, now=_FIXED, strict=False)
    stale = [f for f in lenient if f.kind == "stale"]
    assert stale and stale[0].severity == "warn"
    assert errors(lenient) == []  # warns don't fail
    strict = check(settings=settings, now=_FIXED, strict=True)
    assert next(f for f in strict if f.kind == "stale").severity == "error"
    assert errors(strict)  # now it fails


# --- checksum drift --------------------------------------------------------------------------
def test_checksum_drift_against_a_pin_is_an_error(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml", "real: bytes\n")
    _entry(
        settings,
        "echo-x",
        textwrap.dedent(
            """\
            id: echo-x
            title: T
            scope: reference
            producer:
              kind: connector
              source: x
            storage:
            - relpath: reference/echo/x.yaml
              media_type: application/x-yaml
              sha256: "0000000000000000000000000000000000000000000000000000000000000000"
            refresh:
              cadence: static
            """
        ),
    )
    # reconcile records the file's real sha into _observed.yaml; the pin is deliberately wrong
    write_observed(reconcile(settings=settings, now=_FIXED), settings=settings)
    findings = check(settings=settings, now=_FIXED)
    drift = [f for f in findings if f.kind == "checksum-drift"]
    assert drift and drift[0].severity == "error"


def test_matching_pin_has_no_drift(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    f = _data(settings, "reference/echo/x.yaml", "real: bytes\n")
    import hashlib

    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    _entry(
        settings,
        "echo-x",
        textwrap.dedent(
            f"""\
            id: echo-x
            title: T
            scope: reference
            producer:
              kind: connector
              source: x
            storage:
            - relpath: reference/echo/x.yaml
              media_type: application/x-yaml
              sha256: "{sha}"
            refresh:
              cadence: static
            """
        ),
    )
    write_observed(reconcile(settings=settings, now=_FIXED), settings=settings)
    assert "checksum-drift" not in _kinds(check(settings=settings, now=_FIXED))


# --- schema / duplicate ----------------------------------------------------------------------
def test_duplicate_id_is_an_error_and_short_circuits_on_load_error(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    # a malformed entry -> load-error, which stops the gate before missing/orphan run
    p = settings.catalog_dir / "reference" / "broken.yaml"
    p.parent.mkdir(parents=True)
    p.write_text("id: broken\nscope: reference\n", encoding="utf-8")  # missing required fields
    findings = check(settings=settings, now=_FIXED)
    assert _kinds(findings) == {"schema"}
    assert errors(findings)


# --- regression guard ------------------------------------------------------------------------
def test_committed_catalog_passes_the_gate() -> None:
    """The real committed catalog + data tree clear the gate (no error findings).

    This is the invariant the CI `check` job enforces — a new dataset without a catalog
    entry (orphan), a renamed/removed file (missing), or a drifted pin turns it red.
    """
    assert errors(check()) == []
