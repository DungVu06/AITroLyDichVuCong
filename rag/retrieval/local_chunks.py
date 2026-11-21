"""Read-only search over the same JSONL payloads used to populate Qdrant Cloud."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING

from qdrant_client import QdrantClient, models

from rag.core.config import PROJECT_ROOT

if TYPE_CHECKING:
    from rag.retrieval.embedding import QueryEmbedder


class LocalChunkIndex:
    def __init__(self, directory: Path = PROJECT_ROOT / "data" / "chunks"):
        self.directory = directory
        self.lock = Lock()
        self.collections = {}

    def search(self, collection: str, vector: list[float], limit: int, embedder: QueryEmbedder):
        filename = {"procedures": "procedure_chunks.jsonl", "laws": "law_chunks.jsonl"}[collection]
        path = self.directory / filename
        with self.lock:
            stamp = path.stat().st_mtime_ns
            cached = self.collections.get(collection)
            if cached is None or stamp != cached[0]:
                client = QdrantClient(":memory:")
                try:
                    client.create_collection(collection, vectors_config=models.VectorParams(
                        size=len(vector), distance=models.Distance.COSINE))
                    with path.open(encoding="utf-8-sig") as stream:
                        rows = [json.loads(line) for line in stream if line.strip()]
                    for offset in range(0, len(rows), 32):
                        batch = rows[offset:offset + 32]
                        texts = [r["page_content"] for r in batch]
                        vectors = embedder.encode_documents(texts)
                        client.upsert(collection, points=models.Batch(
                            ids=list(range(offset, offset + len(batch))),
                            vectors=vectors,
                            payloads=[{"text": r["page_content"], **r["metadata"]} for r in batch],
                        ))
                except Exception:
                    client.close()
                    raise
                self.collections[collection] = stamp, client
                if cached:
                    cached[1].close()
            client = self.collections[collection][1]
            return client.query_points(collection, query=vector, limit=limit, with_payload=True).points
