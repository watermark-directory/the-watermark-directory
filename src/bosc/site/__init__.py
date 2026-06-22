"""Typed content-bundle export — turn the committed corpus into the frontend's JSON bundle.

:func:`bosc.site.export.export_bundle` emits the versioned, schema-validated JSON content
bundle under ``data/site/bundle/`` (feeds + a manifest carrying a ``CONTRACT_VERSION``)
that the Astro frontend reads at build time (``bosc export``). The per-section data
builders (``candidates``, ``economics``, ``gismap``, ``records``, …) produce the typed
feeds defined in :mod:`bosc.site.feeds`.
"""

from __future__ import annotations

from bosc.site.export import BundleResult, export_bundle

__all__ = [
    "BundleResult",
    "export_bundle",
]
