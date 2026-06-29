"""LanceDB-backed corpus retrieval store (#808).

The store lives under ``data/cache/lancedb/`` (git-ignored, regenerable via
``watermark index``). Each row is a corpus chunk with its embedding vector and
provenance metadata. The store is append/rebuild only — no partial-row edits.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from watermark.retrieval.embeddings import EmbeddingProvider

_TABLE = "corpus"
_BATCH = 256  # rows per embedding call (memory/latency trade-off)


@dataclass
class Chunk:
    """A corpus fragment ready for indexing."""

    chunk_id: str
    text: str
    site: str  # site slug or "" for corpus-global content
    collection: str  # first-level dir under source root (e.g. "aedg", "oepa")
    doc_kind: str  # "document" | "reference" | "extracted"
    source_path: str  # path relative to its root dir (documents_dir / reference_dir / etc.)
    page: int  # 0-based PDF page, or -1 for non-paged sources
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """One ranked hit from a corpus query."""

    chunk_id: str
    text: str
    score: float  # cosine similarity (higher = more relevant)
    site: str
    collection: str
    doc_kind: str
    source_path: str
    page: int
    provenance: dict[str, Any]


class CorpusStore:
    """Thin wrapper over a LanceDB table storing corpus chunks + their embeddings."""

    def __init__(self, db_path: Path, provider: EmbeddingProvider) -> None:
        self._db_path = db_path
        self._provider = provider
        self._db: Any = None

    def _connect(self) -> Any:
        if self._db is None:
            import lancedb

            self._db_path.mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(str(self._db_path))
        return self._db

    def _table_names(self) -> list[str]:
        resp = self._connect().list_tables()
        # LanceDB 0.17+ returns a ListTablesResponse with a .tables attr; older
        # versions returned a plain list. Handle both.
        return list(resp.tables) if hasattr(resp, "tables") else list(resp)

    @property
    def exists(self) -> bool:
        """True when the index has been built (the LanceDB table is present)."""
        try:
            return _TABLE in self._table_names()
        except Exception:
            return False

    def _embed_batched(self, chunks: list[Chunk]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(chunks), _BATCH):
            batch = chunks[i : i + _BATCH]
            vectors.extend(self._provider.embed([c.text for c in batch]))
        return vectors

    def _to_records(self, chunks: list[Chunk], vectors: list[list[float]]) -> list[dict[str, Any]]:
        return [
            {
                "chunk_id": c.chunk_id,
                "text": c.text,
                "vector": v,
                "site": c.site,
                "collection": c.collection,
                "doc_kind": c.doc_kind,
                "source_path": c.source_path,
                "page": c.page,
                "provenance": json.dumps(c.provenance),
            }
            for c, v in zip(chunks, vectors, strict=True)
        ]

    def rebuild(self, chunks: list[Chunk]) -> None:
        """Full rebuild: drop and recreate the table from *chunks*."""
        if not chunks:
            return
        db = self._connect()
        vectors = self._embed_batched(chunks)
        records = self._to_records(chunks, vectors)
        db.create_table(_TABLE, records, mode="overwrite")

    def update_site(self, site: str, chunks: list[Chunk]) -> None:
        """Replace all rows for *site* with the new *chunks* (other sites untouched)."""
        db = self._connect()
        if _TABLE not in self._table_names():
            self.rebuild(chunks)
            return
        table = db.open_table(_TABLE)
        table.delete(f"site = '{site}'")
        if chunks:
            vectors = self._embed_batched(chunks)
            table.add(self._to_records(chunks, vectors))

    def query(
        self,
        query_text: str,
        *,
        site: str | None = None,
        collection: str | None = None,
        doc_kind: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Semantic search over the store; returns *limit* ranked results."""
        if not self.exists:
            return []
        db = self._connect()
        table = db.open_table(_TABLE)
        vector = self._provider.embed([query_text])[0]
        q = table.search(vector).metric("cosine").limit(limit)

        filters: list[str] = []
        if site is not None:
            escaped = site.replace("'", "''")
            filters.append(f"site = '{escaped}'")
        if collection is not None:
            escaped = collection.replace("'", "''")
            filters.append(f"collection = '{escaped}'")
        if doc_kind is not None:
            escaped = doc_kind.replace("'", "''")
            filters.append(f"doc_kind = '{escaped}'")
        if filters:
            q = q.where(" AND ".join(filters))

        rows: list[dict[str, Any]] = q.to_list()
        return [
            SearchResult(
                chunk_id=str(r["chunk_id"]),
                text=str(r["text"]),
                score=min(1.0, max(0.0, 1.0 - float(r.get("_distance", 0.0)))),
                site=str(r["site"]),
                collection=str(r["collection"]),
                doc_kind=str(r["doc_kind"]),
                source_path=str(r["source_path"]),
                page=int(r["page"]),
                provenance=json.loads(str(r["provenance"])) if r.get("provenance") else {},
            )
            for r in rows
        ]
