"""``watermark.poi`` — the point-of-interest (place) research store.

Places are the third curated entity type, peer to *person* (`watermark.people`) and *org*
(`data/entities/`): markdown + frontmatter under ``data/poi/<slug>.md``, cited and
**depth-marked** (`mention → located → characterized → watched`). The place-specific
enrichment is geometry (geocoding); a POI flagged ``watched`` feeds the imagery tracking
machinery (`watermark.gis`). Design + roadmap: [`docs/poi-subsystem.md`](../../../docs/poi-subsystem.md).

P0 is the store + model. The ``discover`` (corpus → candidates) and ``resolve``
(parcel-anchored dedup funnel + merge) layers, and the geocoding connectors, land in
later increments.
"""

from __future__ import annotations

from watermark.poi.curate import CurateError, scaffold_from_group, write_profile
from watermark.poi.discover import discover_candidates
from watermark.poi.merge import MergeGroup, merge_candidates, merge_corpus, merge_resolutions
from watermark.poi.model import POICandidate, POIFrontmatter, POIProfile
from watermark.poi.resolve import Resolution, resolve_candidate, resolve_value
from watermark.poi.store import load_poi, load_pois, tracked_pois

__all__ = [
    "CurateError",
    "MergeGroup",
    "POICandidate",
    "POIFrontmatter",
    "POIProfile",
    "Resolution",
    "discover_candidates",
    "load_poi",
    "load_pois",
    "merge_candidates",
    "merge_corpus",
    "merge_resolutions",
    "resolve_candidate",
    "resolve_value",
    "scaffold_from_group",
    "tracked_pois",
    "write_profile",
]
