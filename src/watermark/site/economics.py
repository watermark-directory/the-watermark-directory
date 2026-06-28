"""Export the localized economic baseline as a typed feed.

Generated from the committed ``data/reference/economics/baseline.yaml`` (BLS QCEW),
not a live pull — so the static build needs no network. (The legacy markdown
``render_economics`` peer was removed at the SSG-cutover cleanup, #603.)
"""

from __future__ import annotations

from watermark.economics.model import EconomicBaseline


def export_economics(baseline: EconomicBaseline) -> EconomicBaseline:
    """Export the localized economic baseline as a feed (it is already feed-ready).

    Every number on the baseline is a :class:`~watermark.economics.model.ProvenancedValue`
    (BLS QCEW / Census ACS), so the model already carries structured provenance per #60 —
    the feed is the model itself; this exporter gives the module a uniform surface (#59).
    """
    return baseline
