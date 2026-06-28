"""Corpus retrieval store: pluggable embeddings + LanceDB index (#807-#810)."""

from __future__ import annotations

from watermark.retrieval.embeddings import EmbeddingProvider, get_provider
from watermark.retrieval.store import Chunk, CorpusStore, SearchResult

__all__ = [
    "Chunk",
    "CorpusStore",
    "EmbeddingProvider",
    "SearchResult",
    "get_provider",
]
