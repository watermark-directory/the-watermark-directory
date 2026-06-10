"""Render the curated place (POI) profiles as site pages.

The place peer of :mod:`bosc.site.people`. Each ``data/poi/<slug>.md`` becomes
``web/places/<slug>.md`` — its hand-written body plus an identity block (parcels,
relationships, location/tracking) and a provenance footer — linked from
``places/index.md`` and, where it resolved into the entity graph, cross-linked there.
Unlike people, every curated POI is published; ``depth`` is already the quality gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bosc.pipeline.entities import EntityGraph
from bosc.poi.model import POIProfile

_PLACE_NOTE = (
    '!!! note "What a place profile is"\n'
    "    A place collates how a parcel, facility, or feature appears across the public "
    "record and the research built on it. Geometry and ownership are read from cited "
    "county/GNIS sources; they are leads to verify, **not** accusations. Verify every "
    "claim against the cited source before quoting it."
)


@dataclass
class PlacePage:
    slug: str
    name: str
    kind: str
    depth: str
    parcels: int
    tracked: bool


def _esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _source_link(source: str) -> str:
    """Link a repo-relative citation to its mirrored copy (place pages live at web/places/)."""
    head = source.split(" ", 1)[0]  # citations may carry a trailing parenthetical
    if head.startswith("data/") and not head.endswith("/"):
        return f"[`{_esc(head)}`](../{head}) {_esc(source[len(head) :])}".strip()
    return f"`{_esc(source)}`"


def _meta_block(profile: POIProfile) -> list[str]:
    front = profile.front
    rows: list[tuple[str, str]] = [("Kind", front.kind), ("Research depth", front.depth)]
    if front.parcels:
        rows.append(("Parcels", ", ".join(f"`{p}`" for p in front.parcels)))
    if front.members:
        rows.append(("Members", ", ".join(front.members)))
    if front.aliases:
        rows.append(("Also known as", ", ".join(front.aliases)))
    if front.relationships:
        rows.append(
            ("Relationships", ", ".join(f"{r.role} → {r.entity}" for r in front.relationships))
        )
    if front.location and front.location.bbox:
        b = front.location.bbox
        method = front.location.method or "—"
        rows.append(("Location", f"bbox [{', '.join(f'{c:.4f}' for c in b)}] ({method})"))
    if profile.tracked and front.track:
        rows.append(("Tracking", f"imagery — {', '.join(front.track.collections) or '—'}"))
    if front.tags:
        rows.append(("Tags", ", ".join(f"`{t}`" for t in front.tags)))
    lines = ["| | |", "|---|---|"]
    lines += [f"| **{label}** | {_esc(value)} |" for label, value in rows]
    lines.append("")
    return lines


def render_place_page(profile: POIProfile, *, egraph: EntityGraph | None = None) -> str:
    """Render one POI profile to its markdown page."""
    front = profile.front
    lines = [f"# {front.name}", "", f"*{front.kind}, depth: {front.depth}*", ""]
    lines.append(_PLACE_NOTE)
    lines.append("")
    lines += _meta_block(profile)

    # Cross-link into the generated entity graph when this place resolved there.
    if egraph is not None and egraph.get(profile.slug) is not None:
        lines += [f"Appears in the [entity graph](../entities.md) as `{_esc(profile.slug)}`.", ""]

    body = profile.body.strip()
    if body:
        lines += [body, ""]

    if front.citations:
        lines += ["## Sources", ""]
        lines += [f"- {_source_link(c)}" for c in front.citations]
        lines.append("")
    return "\n".join(lines)


def render_place_pages(
    pois: list[POIProfile], out_dir: Path, *, egraph: EntityGraph | None = None
) -> list[PlacePage]:
    """Write a page for every curated POI; return the published set."""
    if not pois:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    pages: list[PlacePage] = []
    for poi in pois:
        (out_dir / f"{poi.slug}.md").write_text(
            render_place_page(poi, egraph=egraph), encoding="utf-8"
        )
        pages.append(
            PlacePage(
                slug=poi.slug,
                name=poi.name,
                kind=poi.kind,
                depth=poi.depth,
                parcels=len(poi.front.parcels),
                tracked=poi.tracked,
            )
        )
    return pages


def render_places_index(pages: list[PlacePage]) -> str:
    """Render ``places/index.md`` — the directory of curated places."""
    watched = sum(1 for p in pages if p.tracked)
    lines = [
        "# Places",
        "",
        f"Curated profiles of the parcels, facilities, and features in the corpus — the "
        f"place peer of the [individuals](../people/index.md). **{len(pages)}** places "
        f"are profiled; **{watched}** are tracked with satellite imagery.",
        "",
        _PLACE_NOTE,
        "",
    ]
    if not pages:
        lines += ["*No places are published yet.*", ""]
        return "\n".join(lines)
    lines += ["| Place | Kind | Depth | Parcels | Tracked |", "|---|---|---|---|---|"]
    for page in sorted(pages, key=lambda p: p.name.upper()):
        tracked = "✓" if page.tracked else ""
        lines.append(
            f"| [{_esc(page.name)}]({page.slug}.md) | {page.kind} | {page.depth} | "
            f"{page.parcels} | {tracked} |"
        )
    lines.append("")
    return "\n".join(lines)
