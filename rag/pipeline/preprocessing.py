"""Bước 1: làm sạch và chuẩn hóa câu hỏi người dùng."""

from __future__ import annotations

import re
import unicodedata

from rag.core.schemas import PreprocessedQuery, UserQuery


INVISIBLE_CHARACTERS = str.maketrans(
    {
        "\ufeff": None,
        "\u200b": None,
        "\u200c": None,
        "\u200d": None,
        "\u200e": None,
        "\u200f": None,
    }
)


def normalize_query_text(text: str) -> str:
    """Chuẩn hóa kỹ thuật mà không thay đổi ý nghĩa câu hỏi."""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.translate(INVISIBLE_CHARACTERS)
    normalized = normalized.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", normalized).strip()


def preprocess_query(query: UserQuery) -> PreprocessedQuery:
    """Tạo đầu vào sạch cho bước hiểu câu hỏi."""
    normalized_text = normalize_query_text(query.text)
    if not normalized_text:
        raise ValueError("Câu hỏi không được để trống sau khi chuẩn hóa.")

    return PreprocessedQuery(
        raw_text=query.text,
        normalized_text=normalized_text,
        conversation_id=query.conversation_id,
    )


