"""Tests for the watershed-point onboarding flow (#326).

Hermetic: a synthetic second site (slug-scoped output relpaths) is monkeypatched into the
registry and onboarded against an empty ``tmp_path`` data dir, offline. A brand-new site
has no committed fixtures and no seed data, so the orchestrator must scaffold cleanly and
record each connector step as a non-crashing dry-run/skipped — never raise.
"""

from __future__ import annotations

from pathlib import Path

from bosc.config import Settings
from bosc.onboard import onboard_site, scaffold_dirs
from bosc.sites import SITES


def _fw(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Register a synthetic Fort-Wayne-shaped site with slug-scoped output paths."""
    fw = SITES["lima"].model_copy(
        update={
            "slug": "fw",
            "place": "Fort Wayne",
            "basin": "maumee",
            "climatology_relpath": "reference/hydrology/fw/nasa-power-climatology.yaml",
            "corridor_ddf_relpath": "reference/hydrology/fw/atlas14-corridor-ddf.yaml",
        }
    )
    monkeypatch.setitem(SITES, "fw", fw)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        site="fw",
        data_dir=tmp_path,
        hydro_offline=True,
        hydro_fixtures_dir=tmp_path / "no-fixtures",  # deliberately empty -> offline misses
    )


def test_scaffold_creates_per_site_dirs_with_readmes(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _fw(monkeypatch)
    dirs, written = scaffold_dirs(_settings(tmp_path))
    assert set(dirs) == {"reference/fw", "extracted/fw", "reference/hydrology/fw"}
    for rel in dirs:
        readme = tmp_path / rel / "README.md"
        assert readme.is_file()
        assert "Fort Wayne" in readme.read_text(encoding="utf-8")
    assert len(written) == 3


def test_scaffold_is_idempotent(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _fw(monkeypatch)
    settings = _settings(tmp_path)
    scaffold_dirs(settings)
    # A reviewer's edits to a scaffolded README must survive a re-run.
    edited = tmp_path / "reference" / "fw" / "README.md"
    edited.write_text("EDITED BY A HUMAN\n", encoding="utf-8")
    _, written_again = scaffold_dirs(settings)
    assert written_again == []  # nothing re-written
    assert edited.read_text(encoding="utf-8") == "EDITED BY A HUMAN\n"


def test_onboard_run_is_resilient_offline(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _fw(monkeypatch)
    report = onboard_site(settings=_settings(tmp_path))

    assert report.slug == "fw"
    assert report.place == "Fort Wayne"
    # Scaffold always succeeds; the run never raises despite no fixtures / no seed data.
    names = {s.name: s.status for s in report.steps}
    assert names["scaffold"] == "ok"
    # Every connector step resolved to a recorded, non-fatal status.
    for step in report.steps:
        assert step.status in {"ok", "skipped", "dry-run", "error"}
    # The blocking review gate is always emitted, and never auto-promotes.
    assert any("PROMOTION IS A SEPARATE MANUAL EDIT" in c for c in report.review_checklist)
    assert any("#247" in c for c in report.review_checklist)  # the self-research seam


def test_onboard_writes_under_slug_not_lima(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # Whatever a connector step would write lands under the slug-scoped path, never Lima's.
    _fw(monkeypatch)
    onboard_site(settings=_settings(tmp_path))
    assert not (tmp_path / "reference" / "hydrology" / "nasa-power-climatology.yaml").exists()
    assert not (tmp_path / "reference" / "hydrology" / "atlas14-corridor-ddf.yaml").exists()
