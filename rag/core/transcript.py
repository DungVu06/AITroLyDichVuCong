"""Persistent, human-readable transcripts for RAG conversations."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from rag.core.config import PROJECT_ROOT
from rag.core.schemas import RAGResponse


class ConversationTranscriptStore:
    """Append each completed response to one Markdown file per conversation."""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or PROJECT_ROOT / "rag" / "conversation_logs"
        self.lock = Lock()

    def path_for(self, conversation_id: str) -> Path:
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", conversation_id)
        return self.directory / f"{safe_id}.md"

    def append(self, conversation_id: str, question: str, response: RAGResponse) -> Path:
        path = self.path_for(conversation_id)
        timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        lines = [f"## Lượt hỏi · {timestamp}", "", "### Người dùng", "", question.strip(), "", "### Trợ lý", "", response.answer_markdown.strip()]

        if response.follow_up_questions:
            lines.extend(["", "### Cần làm rõ", ""])
            lines.extend(f"- {question}" for question in response.follow_up_questions)
        if response.warnings:
            lines.extend(["", "### Cảnh báo", ""])
            lines.extend(f"- {warning}" for warning in response.warnings)
        if response.sources:
            lines.extend(["", "### Nguồn đã trích", ""])
            for source in response.sources:
                link = f" ([mở nguồn]({source.url}))" if source.url else ""
                lines.append(f"- {source.title} — `{source.source_id}`{link}")
                metadata = source.metadata
                if metadata:
                    details = [
                        metadata.scope,
                        f"Hiệu lực từ {metadata.effective_date}" if metadata.effective_date else None,
                        f"Ghi nhận {metadata.observed_at}" if metadata.observed_at else None,
                        f"Phiên bản {metadata.version[:12]}",
                    ]
                    lines.append(f"  - {' · '.join(item for item in details if item)}")
                    lines.extend(f"  - Căn cứ: {basis}" for basis in metadata.legal_bases)
                    lines.extend(f"  - {notice}" for notice in metadata.review)

        block = "\n".join(lines) + "\n\n"
        with self.lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(f"# Hội thoại {conversation_id}\n\n", encoding="utf-8")
            with path.open("a", encoding="utf-8") as stream:
                stream.write(block)
        return path
