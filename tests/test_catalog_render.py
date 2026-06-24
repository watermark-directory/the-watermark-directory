"""Tests for ``bosc catalog render`` (epic #631, issue #627).

Render generates a marker-delimited facts block into a reference collection's README and
preserves all other prose; the block is markdownlint-clean and idempotent; opting in puts the
README under the ``render-drift`` gate (which self-limits to marker-bearing READMEs).
"""

from __future__ import annotations

from pathlib import Path

from bosc.catalog_check import check, errors
from bosc.catalog_render import (
    BEGIN,
    END,
    has_block,
    render,
    render_drift,
    splice_block,
)
from bosc.config import Settings


def _settings(tmp_path: Path) -> Settings:
    (tmp_path / "data").mkdir()
    return Settings(data_dir=tmp_path / "data")


def _data(settings: Settings, relpath: str, body: str = "x: 1\n") -> None:
    path = settings.data_dir / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _entry(settings: Settings, name: str, relpath: str, **fields: str) -> None:
    lines = [
        f"id: {name}",
        "title: A Title",
        "scope: reference",
        "producer:",
        "  kind: connector",
        "  source: EPA ECHO",
        *(f"  command: {fields['command']}" for _ in [0] if "command" in fields),
        "storage:",
        f"- relpath: {relpath}",
        "  media_type: application/x-yaml",
        "refresh:",
        "  cadence: static",
        *(f"license: {fields['license']}" for _ in [0] if "license" in fields),
    ]
    path = settings.catalog_dir / "reference" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _readme(settings: Settings, collection: str, body: str) -> Path:
    path = settings.reference_dir / collection / "README.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# --- splice / block ------------------------------------------------------------------------
def test_block_is_appended_and_prose_preserved() -> None:
    prose = "# Title\n\nA paragraph of curated narrative.\n"
    out = splice_block(prose, f"{BEGIN}\nbody\n{END}")
    assert out.startswith("# Title\n\nA paragraph of curated narrative.\n\n")
    assert out.endswith(f"{BEGIN}\nbody\n{END}\n")
    assert has_block(out)


def test_splice_is_idempotent_and_replaces_in_place() -> None:
    prose = "# Title\n\nProse.\n"
    once = splice_block(prose, f"{BEGIN}\nv1\n{END}")
    # a second render with a new block replaces, never stacks
    twice = splice_block(once, f"{BEGIN}\nv2\n{END}")
    assert twice.count(BEGIN) == 1
    assert "v1" not in twice and "v2" in twice
    assert twice.startswith("# Title\n\nProse.\n\n")
    # same block in -> byte-identical out
    assert splice_block(once, f"{BEGIN}\nv1\n{END}") == once


# --- render writer -------------------------------------------------------------------------
def test_render_adds_then_is_unchanged(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _entry(settings, "echo-x", "reference/echo/x.yaml", command="npdes", license="Public domain")
    readme = _readme(settings, "echo", "# Echo\n\nHand-written intro.\n")

    first = render(settings=settings, apply=True)
    assert [(a.collection, a.action) for a in first] == [("echo", "added")]
    text = readme.read_text(encoding="utf-8")
    assert "Hand-written intro." in text  # prose preserved
    assert "Regenerate: `bosc npdes`" in text
    assert "License: Public domain" in text
    assert "`reference/echo/x.yaml`" in text

    second = render(settings=settings, apply=True)
    assert [a.action for a in second] == ["unchanged"]


def test_missing_readme_is_reported_not_invented(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _entry(settings, "echo-x", "reference/echo/x.yaml")
    # no README on disk
    actions = render(settings=settings, apply=True)
    assert [a.action for a in actions] == ["no-readme"]
    assert not (settings.reference_dir / "echo" / "README.md").exists()


def test_only_filter(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _data(settings, "reference/rsei/y.yaml")
    _entry(settings, "echo-x", "reference/echo/x.yaml")
    _entry(settings, "rsei-y", "reference/rsei/y.yaml")
    _readme(settings, "echo", "# Echo\n")
    _readme(settings, "rsei", "# RSEI\n")
    actions = render(settings=settings, only="echo", apply=True)
    assert {a.collection for a in actions} == {"echo"}
    assert has_block((settings.reference_dir / "echo" / "README.md").read_text("utf-8"))
    assert not has_block((settings.reference_dir / "rsei" / "README.md").read_text("utf-8"))


# --- the render-drift gate -----------------------------------------------------------------
def test_render_drift_self_limits_to_opted_in_readmes(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _data(settings, "reference/rsei/y.yaml")
    _entry(settings, "echo-x", "reference/echo/x.yaml")
    _entry(settings, "rsei-y", "reference/rsei/y.yaml")
    _readme(settings, "echo", "# Echo\n")  # will be rendered (opts in)
    _readme(settings, "rsei", "# RSEI — not rendered\n")  # no marker -> not gated
    render(settings=settings, only="echo", apply=True)
    assert render_drift(settings=settings) == []  # echo is in sync, rsei not gated


def test_render_drift_fires_when_rendered_readme_edited(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _data(settings, "reference/echo/x.yaml")
    _entry(settings, "echo-x", "reference/echo/x.yaml", license="Public domain")
    readme = _readme(settings, "echo", "# Echo\n")
    render(settings=settings, apply=True)
    # tamper inside the generated block
    readme.write_text(
        readme.read_text("utf-8").replace("License: Public domain", "License: TAMPERED"),
        encoding="utf-8",
    )
    drift = render_drift(settings=settings)
    assert [c for c, _ in drift] == ["echo"]
    # and the check gate raises it as an error
    rendered_errors = [f for f in check(settings=settings) if f.kind == "render-drift"]
    assert rendered_errors and rendered_errors[0].severity == "error"
    assert errors(check(settings=settings))


def test_committed_exemplar_readmes_are_render_clean() -> None:
    """The committed reference READMEs that opted in stay in sync (the CI invariant)."""
    assert "render-drift" not in {f.kind for f in check()}


def test_committed_render_is_idempotent() -> None:
    """Re-rendering the real catalog changes nothing already committed."""
    changed = [a for a in render(apply=False) if a.action in ("added", "updated")]
    # only un-rendered collections may show 'added'; none should show 'updated' (drift)
    assert [a.collection for a in changed if a.action == "updated"] == []
