"""Reusable Qdrant client for application code and ad-hoc vector queries.

Example::

    from db.qdrant_client import QdrantVectorClient

    with QdrantVectorClient.from_env() as client:
        client.ensure_collection("documents", vector_size=768)
        results = client.search("documents", query_vector, limit=5)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class QdrantVectorClient:
    """Small reusable wrapper around the official Qdrant client."""

    def __init__(self, client: QdrantClient) -> None:
        self.client = client

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "QdrantVectorClient":
        load_dotenv(env_file or PROJECT_ROOT / ".env")
        url = os.getenv("QDRANT_URL", "").strip()
        api_key = os.getenv("QDRANT_API_KEY", "").strip()
        missing = [name for name, value in (("QDRANT_URL", url), ("QDRANT_API_KEY", api_key)) if not value]
        if missing:
            raise ValueError(f"Thiếu cấu hình Qdrant: {', '.join(missing)}")
        return cls(QdrantClient(url=url, api_key=api_key))

    def verify_connectivity(self) -> Any:
        """Check connectivity and return the server response."""
        return self.client.get_collections()

    def collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
    ) -> None:
        if not self.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

    def delete_collection(self, collection_name: str) -> bool:
        return self.client.delete_collection(collection_name)

    def upsert(
        self,
        collection_name: str,
        points: Iterable[PointStruct | Mapping[str, Any]],
    ) -> Any:
        """Upsert PointStruct objects or point dictionaries."""
        normalized = [PointStruct(**point) if isinstance(point, Mapping) else point for point in points]
        return self.client.upsert(collection_name=collection_name, points=normalized)

    def search(
        self,
        collection_name: str,
        query_vector: Sequence[float],
        limit: int = 10,
        query_filter: Any = None,
    ) -> list[Any]:
        """Search nearest vectors; returns Qdrant scored points."""
        result = self.client.query_points(
            collection_name=collection_name,
            query=list(query_vector),
            query_filter=query_filter,
            limit=limit,
        )
        return list(result.points)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "QdrantVectorClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
