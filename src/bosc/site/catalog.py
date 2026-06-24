"""Build the published ``catalog`` feed (epic #631 Phase 3 / #659).

Projects the data catalog (:mod:`bosc.catalog`) into the content bundle: each
:class:`bosc.catalog.CatalogEntry` becomes a :class:`bosc.site.feeds.CatalogItem`, joined to
the reconcile observed snapshot (``data/catalog/_observed.yaml``) where one is committed. This
is what lets the Astro ``/about/data`` page read the catalog at build time — the data tier's
view of *what datasets exist, where each came from, its license/access tier, and whether it's
fresh*, the legible successor to the manual corpus-completeness audit.
"""

from __future__ import annotations

from bosc.catalog import CatalogEntry, ProducerKind, load_entries
from bosc.catalog_reconcile import load_observed
from bosc.config import Settings, get_settings
from bosc.site.feeds import (
    CatalogItem,
    CatalogObserved,
    CatalogStorageFile,
    Citation,
    SourceKind,
)

# Producer kind → the bundle's shared provenance vocabulary (mirrors catalog_backfill).
_SOURCE_KIND: dict[ProducerKind, SourceKind] = {
    "connector": "connector",
    "extracted": "document",
    "derived": "derived",
    "vendored": "reference",
    "manual": "reference",
}


def _collection(entry: CatalogEntry) -> str:
    """The dataset's collection — the first dir under its scope, ``{site}`` dropped."""
    if not entry.storage:
        return entry.scope
    parts = [p for p in entry.storage[0].relpath.split("/")[1:-1] if p != "{site}"]
    return parts[0] if parts else entry.scope


def export_catalog(settings: Settings | None = None) -> list[CatalogItem]:
    """Project every catalog entry to a :class:`CatalogItem`, joined to the observed snapshot."""
    settings = settings or get_settings()
    snapshot = load_observed(settings=settings)
    items: list[CatalogItem] = []
    for entry in load_entries(settings=settings):
        obs = snapshot.entries.get(entry.id) if snapshot else None
        observed = (
            CatalogObserved(
                exists=obs.exists,
                sha256=obs.sha256,
                size_bytes=obs.size_bytes,
                lfs_materialized=obs.lfs_materialized,
                file_count=obs.file_count,
                stale=obs.stale,
                asof=obs.asof,
            )
            if obs is not None
            else None
        )
        items.append(
            CatalogItem(
                id=entry.id,
                title=entry.title,
                scope=entry.scope,
                collection=_collection(entry),
                status=entry.status,
                producer_kind=entry.producer.kind,
                command=entry.producer.command,
                connector_ref=entry.producer.connector_ref,
                source=entry.producer.source,
                external_url=entry.producer.external_url,
                license=entry.license,
                access_tier=entry.access_tier,
                site_scope=entry.site_scope,
                cadence=entry.refresh.cadence,
                ttl_days=entry.refresh.ttl_days,
                last_refreshed=entry.refresh.last_refreshed,
                tags=list(entry.tags),
                storage=[
                    CatalogStorageFile(relpath=s.relpath, media_type=s.media_type, lfs=s.lfs)
                    for s in entry.storage
                ],
                observed=observed,
                citation=Citation(
                    source=entry.producer.source,
                    source_kind=_SOURCE_KIND[entry.producer.kind],
                    note=f"bosc {entry.producer.command}" if entry.producer.command else None,
                ),
            )
        )
    return sorted(items, key=lambda i: (i.scope, i.id))
