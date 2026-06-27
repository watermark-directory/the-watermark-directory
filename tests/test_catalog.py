"""Tests for the data-catalog model + store (epic #631, issue #623).

The model layer everything else builds on: a typed :class:`CatalogEntry` per dataset at
``data/catalog/<scope>/<id>.yaml``, a ``data/`` loader that cross-checks scope/id against the
path, and a structural validator (the model-layer half of the future ``bosc catalog check``).
The committed-store tests pin that the hand-written fixtures load and validate clean.
"""

from __future__ import annotations

import textwrap

import pytest
from pydantic import ValidationError

from bosc.catalog import (
    CatalogEntry,
    Producer,
    Refresh,
    StorageItem,
    entries_for_scope,
    entry_path,
    get_entry,
    load_entries,
    validate_entries,
)
from bosc.config import Settings


def _entry(**over: object) -> CatalogEntry:
    base: dict[str, object] = {
        "id": "sample-set",
        "title": "A sample dataset",
        "scope": "reference",
        "producer": Producer(kind="connector", source="Some upstream"),
        "refresh": Refresh(cadence="annual"),
    }
    base.update(over)
    return CatalogEntry.model_validate(base)


# --- model ---------------------------------------------------------------------------------
def test_entry_round_trips() -> None:
    e = _entry(storage=[StorageItem(relpath="reference/x/y.yaml", media_type="application/x-yaml")])
    again = CatalogEntry.model_validate(e.model_dump())
    assert again == e
    assert again.status == "needs-review"  # default review state
    assert again.access_tier == "public"
    assert again.site_scope == "basin-shared"


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        _entry(unexpected="nope")


def test_id_must_be_kebab_slug() -> None:
    for bad in ("Has_Caps", "white space", "under_score", ""):
        with pytest.raises(ValidationError):
            _entry(id=bad)
    # a clean kebab slug is accepted
    assert _entry(id="echo-maumee-npdes").id == "echo-maumee-npdes"


def test_sub_models_are_frozen() -> None:
    p = Producer(kind="connector", source="x")
    with pytest.raises(ValidationError):
        p.source = "y"  # type: ignore[misc]


# --- committed store -----------------------------------------------------------------------
def test_committed_catalog_loads_and_validates() -> None:
    """The hand-written fixtures load, cross-check their path, and lint clean."""
    entries = load_entries()
    ids = {e.id for e in entries}
    assert {"echo-maumee-npdes", "aedg-roundabouts-opc"} <= ids
    assert validate_entries() == []


def test_get_entry_and_scope_filter() -> None:
    entry = get_entry("echo-maumee-npdes")
    assert entry is not None
    assert entry.scope == "reference"
    assert entry.producer.command == "npdes --basin maumee"
    assert get_entry("does-not-exist") is None
    assert "echo-maumee-npdes" in {e.id for e in entries_for_scope("reference")}
    assert "aedg-roundabouts-opc" not in {e.id for e in entries_for_scope("reference")}


def test_entry_path_mirrors_scope_and_id() -> None:
    settings = Settings()
    e = _entry(id="my-id", scope="derived")
    assert entry_path(e, settings=settings) == settings.catalog_dir / "derived" / "my-id.yaml"


# --- loader cross-checks + validator -------------------------------------------------------
def test_load_empty_when_no_catalog(tmp_path) -> None:  # type: ignore[no-untyped-def]
    assert load_entries(settings=Settings(data_dir=tmp_path)) == []


def test_misfiled_scope_is_a_load_error(tmp_path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(data_dir=tmp_path)
    bad = settings.catalog_dir / "reference"
    bad.mkdir(parents=True)
    # entry declares scope=derived but is filed under reference/
    (bad / "thing.yaml").write_text(
        textwrap.dedent(
            """\
            id: thing
            title: Misfiled
            scope: derived
            producer:
              kind: derived
              source: x
            refresh:
              cadence: static
            """
        ),
        encoding="utf-8",
    )
    findings = validate_entries(settings=settings)
    assert [f.kind for f in findings] == ["load-error"]


def test_unknown_owner_site_scope_is_flagged(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """#778 lint: a grammatically-valid ``site_scope`` owner must reference a real site/basin/state.
    ``site:nope`` parses (right shape) but names no registered site → an ``unknown-owner`` finding."""
    settings = Settings(data_dir=tmp_path)
    d = settings.catalog_dir / "reference"
    d.mkdir(parents=True)
    (d / "ghost.yaml").write_text(
        textwrap.dedent(
            """\
            id: ghost
            title: Ghost
            scope: reference
            site_scope: site:nope
            producer:
              kind: manual
              source: x
            refresh:
              cadence: static
            """
        ),
        encoding="utf-8",
    )
    findings = validate_entries(settings=settings)
    assert [f.kind for f in findings] == ["unknown-owner"]


def test_id_filename_mismatch_is_a_load_error(tmp_path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(data_dir=tmp_path)
    d = settings.catalog_dir / "reference"
    d.mkdir(parents=True)
    (d / "wrong-name.yaml").write_text(
        textwrap.dedent(
            """\
            id: right-name
            title: Mismatch
            scope: reference
            producer:
              kind: manual
              source: x
            refresh:
              cadence: static
            """
        ),
        encoding="utf-8",
    )
    findings = validate_entries(settings=settings)
    assert [f.kind for f in findings] == ["load-error"]


def test_duplicate_id_is_flagged(tmp_path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(data_dir=tmp_path)
    for scope in ("reference", "derived"):
        d = settings.catalog_dir / scope
        d.mkdir(parents=True)
        (d / "dupe.yaml").write_text(
            textwrap.dedent(
                f"""\
                id: dupe
                title: Duplicated across scopes
                scope: {scope}
                producer:
                  kind: manual
                  source: x
                refresh:
                  cadence: static
                """
            ),
            encoding="utf-8",
        )
    findings = validate_entries(settings=settings)
    assert [f.kind for f in findings] == ["duplicate-id"]
    assert findings[0].entry_id == "dupe"


def test_observed_snapshot_at_root_is_skipped(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """A root-level _observed.yaml (the #625 reconcile snapshot) is not a catalog entry."""
    settings = Settings(data_dir=tmp_path)
    settings.catalog_dir.mkdir(parents=True)
    (settings.catalog_dir / "_observed.yaml").write_text("reconciled_at: x\n", encoding="utf-8")
    assert load_entries(settings=settings) == []
