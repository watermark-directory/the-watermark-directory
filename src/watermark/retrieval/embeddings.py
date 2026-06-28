"""Pluggable embedding providers for the corpus retrieval store (#807).

``EmbeddingProvider`` is the ABC; ``SentenceTransformersProvider`` is the default
(offline, no API key required). New providers implement the ABC and register in
``get_provider``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):
    """Abstract base for pluggable embedding backends."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one float vector per text (order preserved)."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Length of each embedding vector."""
        ...


class SentenceTransformersProvider(EmbeddingProvider):
    """sentence-transformers backend — offline, no API cost."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: Any = None  # lazy-loaded on first embed

    def _load(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        result: list[list[float]] = self._load().encode(texts).tolist()
        return result

    @property
    def dimension(self) -> int:
        return int(self._load().get_sentence_embedding_dimension())


def get_provider(settings: Any) -> EmbeddingProvider:
    """Resolve the :class:`EmbeddingProvider` specified in *settings*."""
    name: str = settings.embedding_provider
    match name:
        case "sentence_transformers":
            return SentenceTransformersProvider(settings.embedding_model)
        case _:
            raise ValueError(f"unknown embedding provider {name!r}; known: sentence_transformers")
