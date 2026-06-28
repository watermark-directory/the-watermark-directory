"""Tests for the published ``catalog`` feed (epic #631 Phase 3 / #659)."""

from __future__ import annotations

import textwrap
from pathlib import Path

from watermark.config import Settings
from watermark.site.catalog import _collection, export_catalog
from watermark.site.feeds import CatalogItem


def _settings(tmp_path: Path) -> Settings:
    (tmp_path / "data").mkdir()
    return Settings(data_dir=tmp_path / "data")


def _entry(settings: Settings, name: str, scope: str, body: str) -> None:
    path = settings.catalog_dir / scope / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


# --- collection derivation -----------------------------------------------------------------
def test_collection_drops_site_template(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(
        settings,
        "eia-consumer-energy",
        "reference",
        """\
        id: eia-consumer-energy
        title: T
        scope: reference
        site_scope: slug-scoped
        producer:
          kind: connector
          source: x
        refresh:
          cadence: static
        storage:
        - relpath: reference/eia/{site}/consumer-energy.yaml
          media_type: application/x-yaml
        """,
    )
    items = {i.id: i for i in export_catalog(settings)}
    assert items["eia-consumer-energy"].collection == "eia"  # {site} dropped


def test_collection_falls_back_to_scope_when_flat(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(
        settings,
        "data-centers",
        "extracted",
        """\
        id: data-centers
        title: T
        scope: extracted
        site_scope: slug-scoped
        producer:
          kind: extracted
          source: x
        refresh:
          cadence: static
        storage:
        - relpath: extracted/{site}/data-centers.md
          media_type: text/markdown
        """,
    )
    assert {i.id: i for i in export_catalog(settings)}["data-centers"].collection == "extracted"


# --- projection + provenance ---------------------------------------------------------------
def test_projection_carries_facts_and_citation(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(
        settings,
        "echo-x",
        "reference",
        """\
        id: echo-x
        title: Echo inventory
        scope: reference
        status: reviewed
        license: U.S. Government work
        access_tier: throttled
        producer:
          kind: connector
          command: npdes --basin maumee
          source: EPA ECHO
        refresh:
          cadence: quarterly
          ttl_days: 180
        storage:
        - relpath: reference/echo/x.yaml
          media_type: application/x-yaml
        """,
    )
    item = {i.id: i for i in export_catalog(settings)}["echo-x"]
    assert isinstance(item, CatalogItem)
    assert item.license == "U.S. Government work"
    assert item.access_tier == "throttled"
    assert item.cadence == "quarterly" and item.ttl_days == 180
    # the producer becomes the bundle's shared Citation shape
    assert item.citation.source == "EPA ECHO"
    assert item.citation.source_kind == "connector"
    assert item.citation.verified is True  # connector-sourced
    assert item.citation.note == "watermark npdes --basin maumee"
    # no _observed.yaml committed in this tmp catalog -> observed is None
    assert item.observed is None


def test_observed_snapshot_is_joined_when_present() -> None:
    """Against the real committed catalog, the reconcile snapshot is attached."""
    items = {i.id: i for i in export_catalog(Settings())}
    echo = items["echo-maumee-npdes"]
    assert echo.observed is not None
    assert echo.observed.exists is True
    assert echo.observed.file_count >= 1


def test_every_entry_is_projected() -> None:
    from watermark.catalog import load_entries

    items = export_catalog(Settings())
    assert {i.id for i in items} == {e.id for e in load_entries()}


def test_collection_helper_direct() -> None:
    from watermark.catalog import CatalogEntry

    def e(relpath: str | None) -> CatalogEntry:
        storage = [{"relpath": relpath, "media_type": "application/x-yaml"}] if relpath else []
        return CatalogEntry.model_validate(
            {
                "id": "d",
                "title": "T",
                "scope": "reference",
                "producer": {"kind": "manual", "source": "x"},
                "refresh": {"cadence": "static"},
                "storage": storage,
            }
        )

    assert _collection(e("reference/echo/maumee-wwtp.all-npdes.yaml")) == "echo"
    assert _collection(e(None)) == "reference"  # no storage -> scope
