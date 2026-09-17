"""Tạo query embedding tương thích với vector đã lưu trong Qdrant."""

from __future__ import annotations

from typing import Any

from rag.core.config import EmbeddingSettings


class QueryEmbedder:
    """Lazy-load Vietnamese SBERT và kiểm tra đúng số chiều vector."""

    def __init__(self, settings: EmbeddingSettings | None = None) -> None:
        self.settings = settings or EmbeddingSettings.from_env()
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Thiếu sentence-transformers. Hãy cài dependency trong requirements.txt."
            ) from exc

        model = SentenceTransformer(self.settings.model)
        dimension = model.get_embedding_dimension()
        if dimension != self.settings.expected_dimension:
            raise ValueError(
                f"Embedding model trả vector {dimension} chiều; "
                f"Qdrant hiện cần {self.settings.expected_dimension} chiều."
            )
        self._model = model
        return model

    def encode(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Không thể embedding câu truy vấn rỗng.")
        vector = self._load_model().encode(text)
        return vector.tolist()
