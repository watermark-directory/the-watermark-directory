"""Export the cross-document layer (timeline + entity graph) as typed bundle feeds.

Reuses the structured returns of :func:`watermark.pipeline.timeline.build_timeline` and
:func:`watermark.pipeline.entities.build_entity_graph` and emits the :mod:`watermark.site.feeds`
models the Astro frontend reads. (The legacy markdown ``render_*`` peers were removed at
the SSG-cutover cleanup, #603 — ``export.py`` was already the only live path.)
"""

from __future__ import annotations

from watermark.pipeline.entities import EntityGraph
from watermark.pipeline.timeline import TimelineEvent
from watermark.site.feeds import Citation, EntityNode, RelationshipEdge, TimelineEntry


def export_timeline(events: list[TimelineEvent]) -> list[TimelineEntry]:
    """Export the assembled chronology as :class:`TimelineEntry` items (data peer of render)."""
    return [
        TimelineEntry(
            date=e.date,
            category=e.category,
            title=e.title,
            ref=e.ref,
            parties=list(e.parties),
            detail=e.detail,
            source=e.source,
            also_sources=list(e.also_sources),
            citation=Citation(source=e.source, source_kind="document"),
        )
        for e in events
    ]


def export_entities(graph: EntityGraph) -> list[EntityNode]:
    """Export resolved entities as :class:`EntityNode` items (sets → sorted lists)."""
    return [
        EntityNode(
            key=ent.key,
            display=ent.display,
            kind=ent.kind,
            classification=ent.classification,
            relation_class=ent.relation_class,
            relation_basis=ent.relation_basis,
            variants=sorted(ent.variants),
            signals=sorted(ent.signals),
            roles=dict(ent.roles.most_common()),
            parcels=sorted(ent.parcels),
            addresses=sorted(ent.addresses),
            sources=sorted(ent.sources),
            lei=ent.lei,
            uei=ent.uei,
            federal_obligations=ent.federal_obligations,
        )
        for ent in sorted(graph.entities.values(), key=lambda e: (e.kind, e.key))
    ]


def export_relationships(graph: EntityGraph) -> list[RelationshipEdge]:
    """Export graph edges as :class:`RelationshipEdge` items (``""`` overlay → ``None``)."""
    return [
        RelationshipEdge(
            src=r.src,
            rel=r.rel,
            dst=r.dst,
            date=r.date,
            ref=r.ref,
            source=r.source,
            relation_class=r.relation_class or None,
            relation_basis=r.relation_basis or None,
        )
        for r in graph.relationships
    ]
