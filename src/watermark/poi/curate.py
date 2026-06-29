"""Scaffold a merge group into a POI profile — the promotion step.

Promotion is a human decision; this *scaffolds* the artifact from a resolved
:class:`MergeGroup` so the human reviews and edits rather than authoring from scratch.
A scaffolded parcel POI lands at depth ``located`` (the parcel identifies it spatially);
the human promotes it to ``characterized`` / ``watched``. The tracking AOI (bbox) is
attached when promoting to ``watched`` — it is not invented here. The group's members
become the ``surface_forms`` audit trail, and every member citation is carried through
(a POI with no citation is not evidence).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from watermark.config import Settings, get_settings
from watermark.poi.merge import MergeGroup
from watermark.poi.model import (
    POIFrontmatter,
    POILocation,
    POIRelationship,
    SurfaceForm,
)


class CurateError(RuntimeError):
    """Scaffolding/writing a POI profile failed (no parcel, or refusing to overwrite)."""


def scaffold_from_group(group: MergeGroup, *, asof: str) -> tuple[POIFrontmatter, str]:
    """Build a (validated) frontmatter + body for a resolved parcel group, at ``located``."""
    if group.parcel_no is None or group.parcel is None:
        raise CurateError("cannot scaffold a POI without a resolved parcel")
    parcel = group.parcel

    # Prefer the deed-format id (as cited) for the human-facing fields; fall back to the
    # canonical normalized number when the group has no parcel-id surface form.
    deed = next((m.value for m in group.members if m.kind == "parcel-id"), group.parcel_no)
    name = parcel.situs_address or f"Parcel {deed}"
    citations = sorted({c for m in group.members for c in m.citations})
    surface_forms = [
        SurfaceForm(
            type=m.kind,  # parcel-id | address | coord — all valid SurfaceForm types
            value=m.value,
            citation="; ".join(m.citations) or None,
            resolved_parcel=group.parcel_no,
        )
        for m in group.members
    ]
    relationships = [POIRelationship(role="owner", entity=parcel.owner)] if parcel.owner else []

    front = POIFrontmatter(
        name=name,
        slug=f"parcel-{group.parcel_no}",
        kind="parcel",
        depth="located",
        parcels=[deed],
        location=POILocation(
            method="parcel-cama",
            confidence="high" if group.has_exact_id else "medium",
            asof=asof,
        ),
        surface_forms=surface_forms,
        relationships=relationships,
        citations=citations,
    )
    return front, _scaffold_body(group, deed)


def _scaffold_body(group: MergeGroup, deed: str) -> str:
    p = group.parcel
    owner = (p.owner if p else None) or "—"
    acres = p.acres if p and p.acres is not None else "—"
    return (
        f"Scaffolded parcel POI for **{deed}** (owner of record: {owner}; {acres} acres), "
        f"derived from {len(group.members)} corpus surface form(s) that resolve to county "
        f"parcel `{group.parcel_no}` ({group.status}). Values are verbatim from the Allen "
        f"County GIS; the corpus citations are in `surface_forms`.\n\n"
        f"Review before publishing. Promote `depth` to `characterized` once the owner / "
        f"relationships are confirmed, and to `watched` (adding a tracking `bbox`) to put "
        f"the parcel on the imagery timeline. A surface form is a lead to verify, not a "
        f"finding."
    )


def _clean(value: Any) -> Any:
    """Drop ``None`` and empty list/dict values, recursively — for tidy frontmatter."""
    if isinstance(value, dict):
        cleaned = {k: _clean(v) for k, v in value.items()}
        return {k: v for k, v in cleaned.items() if v not in (None, [], {})}
    return value


def render_frontmatter(front: POIFrontmatter) -> str:
    """The POI frontmatter as clean YAML (None/empty fields dropped)."""
    data = _clean(front.model_dump(mode="json"))
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()


def profile_text(front: POIFrontmatter, body: str) -> str:
    """The full ``<slug>.md`` text: frontmatter block + body."""
    return f"---\n{render_frontmatter(front)}\n---\n\n{body}\n"


def write_profile(
    front: POIFrontmatter, body: str, *, settings: Settings | None = None, force: bool = False
) -> Path:
    """Write the profile to ``data/entities/poi/<slug>.md``; refuse to overwrite unless ``force``."""
    settings = settings or get_settings()
    if not front.slug:
        raise CurateError("frontmatter has no slug")
    path = settings.poi_dir / f"{front.slug}.md"
    if path.exists() and not force:
        raise CurateError(f"{path} already exists — pass force=True to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(profile_text(front, body), encoding="utf-8")
    return path
