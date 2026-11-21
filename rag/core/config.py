"""Cấu hình dùng chung cho RAG engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def configure_tls_certificates() -> None:
    """Use certifi's CA bundle when the terminal has not configured one.

    Some Windows installations expose a TLS root store that cannot validate
    the public certificate chain used by Aura and Qdrant Cloud.  certifi is
    installed with the project dependencies and gives Python clients a stable
    CA bundle without requiring each user to configure SSL_CERT_FILE manually.
    """
    if os.getenv("SSL_CERT_FILE"):
        return
    try:
        import certifi
    except ModuleNotFoundError:
        return
    os.environ["SSL_CERT_FILE"] = certifi.where()


def load_env_file(path: Path = PROJECT_ROOT / ".env") -> None:
    """Đọc KEY=VALUE từ `.env` mà không ghi đè biến môi trường hiện có."""
    configure_tls_certificates()
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str
    model: str = "gemini-3.5-flash-lite"

    @classmethod
    def from_env(cls) -> "GeminiSettings":
        load_env_file()
        api_key = (
            os.getenv("GEMINI_API_KEY", "").strip()
            or os.getenv("GOOGLE_API_KEY", "").strip()
        )
        if not api_key:
            raise ValueError("Thiếu GEMINI_API_KEY hoặc GOOGLE_API_KEY trong .env")

        model = os.getenv("GEMINI_QUERY_MODEL", cls.model).strip() or cls.model
        return cls(api_key=api_key, model=model)


@dataclass(frozen=True)
class EmbeddingSettings:
    model: str = "keepitreal/vietnamese-sbert"
    expected_dimension: int = 768

    @classmethod
    def from_env(cls) -> "EmbeddingSettings":
        load_env_file()
        model = os.getenv("EMBEDDING_MODEL", cls.model).strip() or cls.model
        return cls(model=model)
