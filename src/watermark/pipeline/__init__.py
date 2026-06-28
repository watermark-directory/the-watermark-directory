"""The BOSC research pipeline: ingest -> extract -> analyze.

Each stage is a small, independently testable module:

* :mod:`watermark.pipeline.ingest`  — discover and register source documents.
* :mod:`watermark.pipeline.extract` — turn a document into structured data.
* :mod:`watermark.pipeline.analyze` — reconcile and reason over structured data.
"""

from __future__ import annotations

from watermark.pipeline import analyze, extract, ingest

__all__ = ["analyze", "extract", "ingest"]
