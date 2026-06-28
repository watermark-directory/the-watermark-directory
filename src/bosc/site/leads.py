"""Export the per-site open-leads board (#796).

A site's leads are a committed, hand-curated YAML store (`data/site/leads.yaml`, slug-scoped via
`site_scoped_path` so a sibling reads its own `site/<slug>/leads.yaml`, never Lima's). Each lead
traces to a real source — the corpus-completeness audit's owed/withheld/`[open]` items and the
boom-origin hypotheses' open threads — and is *unverified inference until a source corroborates
it*. The data peer of the (now-retired) frontend `leads.ts` constant: the source of truth moves
here so a peer carries its own leads and the frontend reads one feed.

Absent store → an empty leads feed (the frontend falls back to the readiness-derived needs board),
never Lima's leads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from bosc.logging import get_logger
from bosc.site.feeds import LeadItem

log = get_logger(__name__)


def export_leads(store_path: Path) -> list[LeadItem]:
    """Load a site's curated leads store into validated :class:`LeadItem`s (empty if absent)."""
    if not store_path.exists():
        log.info("site.leads.no_store", path=str(store_path))
        return []
    raw = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
    entries: list[dict[str, Any]] = raw.get("leads") or []
    items = [LeadItem.model_validate(entry) for entry in entries]
    log.info("site.leads.built", total=len(items), path=str(store_path))
    return items
