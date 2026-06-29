"""Export the curated place (POI) profiles as typed feeds.

The place peer of :mod:`watermark.site.people`. Each ``data/entities/poi/<slug>.md`` becomes a
:class:`~watermark.site.feeds.PlaceItem` — its body, identity (parcels, relationships,
location/tracking), and a structured provenance footer. Every curated POI is exported;
``depth`` is already the quality gate. (The legacy markdown ``render_place_*`` peers were
removed at the SSG-cutover cleanup, #603.)
"""

from __future__ import annotations

from watermark.poi.model import POIProfile
from watermark.site.feeds import (
    Citation,
    PlaceItem,
    PlaceLocation,
    PlaceRelationship,
    PlaceTrack,
)


def _place_citation(raw: str) -> Citation:
    """A POI citation string (a ``data/`` path + an optional trailing parenthetical)."""
    head = raw.split(" ", 1)[0]
    rest = raw[len(head) :].strip()
    return Citation(source=head, source_kind="document", note=rest or None)


def export_places(pois: list[POIProfile]) -> list[PlaceItem]:
    """Export every curated POI as a :class:`PlaceItem` (the data peer of render).

    Each POI's ``slug`` is its cross-feed key — the same key the entity graph resolves it
    by — and ``relationships[].entity`` references entity keys. Geometry stays WGS84
    verbatim (bbox only; the drawn geometry lives in the geo feeds, issue #61).
    """
    items: list[PlaceItem] = []
    for poi in pois:
        front = poi.front
        loc = front.location
        location = (
            PlaceLocation(
                method=loc.method,
                confidence=loc.confidence,
                asof=loc.asof,
                bbox=[float(c) for c in loc.bbox] if loc.bbox else None,
            )
            if loc is not None
            else None
        )
        track = (
            PlaceTrack(
                enabled=front.track.enabled,
                collections=list(front.track.collections),
                since=front.track.since,
            )
            if poi.tracked and front.track is not None
            else None
        )
        items.append(
            PlaceItem(
                slug=poi.slug,
                name=poi.name,
                kind=poi.kind,
                depth=poi.depth,
                parcels=list(front.parcels),
                members=list(front.members),
                aliases=list(front.aliases),
                tags=list(front.tags),
                location=location,
                track=track,
                relationships=[
                    PlaceRelationship(role=r.role, entity=r.entity) for r in front.relationships
                ],
                citations=[_place_citation(c) for c in front.citations],
                body=poi.body.strip(),
            )
        )
    return items
