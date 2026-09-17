"""Bộ nhớ hội thoại có thể thay bằng Redis/database khi nối UI."""

from __future__ import annotations

from threading import RLock

from rag.core.schemas import ConversationState


class InMemoryConversationStore:
    def __init__(self) -> None:
        self._states: dict[str, ConversationState] = {}
        self._lock = RLock()

    def get(self, conversation_id: str) -> ConversationState | None:
        with self._lock:
            state = self._states.get(conversation_id)
            return state.model_copy(deep=True) if state else None

    def put(self, state: ConversationState) -> None:
        with self._lock:
            self._states[state.conversation_id] = state.model_copy(deep=True)

    def clear(self, conversation_id: str) -> None:
        with self._lock:
            self._states.pop(conversation_id, None)
