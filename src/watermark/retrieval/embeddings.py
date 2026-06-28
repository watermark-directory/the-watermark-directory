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
            import torch
            from sentence_transformers import SentenceTransformer

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "mps"
                if torch.backends.mps.is_available()
                else "cpu"
            )
            self._model = SentenceTransformer(self._model_name, device=device)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        result: list[list[float]] = self._load().encode(texts).tolist()
        return result

    @property
    def dimension(self) -> int:
        return int(self._load().get_sentence_embedding_dimension())


_PROVIDER_CACHE: dict[str, EmbeddingProvider] = {}


def get_provider(settings: Any) -> EmbeddingProvider:
    """Resolve the :class:`EmbeddingProvider` specified in *settings*.

    Cached by (provider, model) so the sentence-transformers model is only loaded once
    per process — the MCP server calls this on every ``retrieve_corpus`` tool call.
    """
    name: str = settings.embedding_provider
    key = f"{name}:{settings.embedding_model}"
    if key not in _PROVIDER_CACHE:
        match name:
            case "sentence_transformers":
                _PROVIDER_CACHE[key] = SentenceTransformersProvider(settings.embedding_model)
            case _:
                raise ValueError(
                    f"unknown embedding provider {name!r}; known: sentence_transformers"
                )
    return _PROVIDER_CACHE[key]
