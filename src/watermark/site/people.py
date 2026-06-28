"""Export the curated individual profiles as typed feeds.

Only profiles flagged ``expanded_research: true`` are exported; the rest stay tracked under
``data/people`` but off the bundle. Each becomes a :class:`~watermark.site.feeds.PersonItem` — its
body, identity block, and structured sources — with ``entity_key`` carried only when it
resolves into the entity graph. (The legacy markdown ``render_*`` peers were removed at the
SSG-cutover cleanup, #603.)
"""

from __future__ import annotations

from watermark.people import PersonProfile
from watermark.pipeline.entities import EntityGraph
from watermark.site.feeds import Citation, PersonItem


def export_people(
    people: list[PersonProfile], *, egraph: EntityGraph | None = None
) -> list[PersonItem]:
    """Export the published (``expanded_research``) profiles as :class:`PersonItem` items.

    Only expanded profiles are published (the ``expanded_research`` gate). ``entity_key``
    is carried only when it resolves into the graph, so the people↔entities link is clean;
    each ``sources`` string becomes a structured :class:`Citation`.
    """
    items: list[PersonItem] = []
    for profile in people:
        if not profile.expanded:
            continue
        front = profile.front
        resolved = egraph.get(profile.entity_key) if egraph is not None else None
        items.append(
            PersonItem(
                slug=profile.slug,
                name=profile.name,
                entity_key=resolved.key if resolved is not None else None,
                aliases=list(front.aliases),
                roles=list(front.roles),
                affiliations=list(front.affiliations),
                summary=front.summary,
                expanded=True,
                tags=list(front.tags),
                sources=[Citation(source=s, source_kind="document") for s in front.sources],
                body=profile.body.strip(),
            )
        )
    return items
