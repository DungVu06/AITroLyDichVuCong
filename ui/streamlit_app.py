"""Giao diện chat Streamlit tối giản cho RAG engine."""

from __future__ import annotations

import logging
import sys
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

# Streamlit chạy file trong ui/; thêm thư mục chứa cả rag/ và db/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.engine import RAGEngine


LOGGER = logging.getLogger(__name__)
RETRIEVAL_LIMIT = 5


st.set_page_config(
    page_title="Trợ lý thủ tục hành chính",
    page_icon="📋",
    layout="centered",
)


@st.cache_resource(show_spinner=False)
def get_engine() -> RAGEngine:
    """Dùng lại embedding model và store giữa các lần Streamlit rerun."""
    return RAGEngine()


def initialize_session() -> None:
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []


def reset_conversation() -> None:
    get_engine().clear_conversation(st.session_state.conversation_id)
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []


def render_metadata(message: dict[str, Any]) -> None:
    questions = message.get("follow_up_questions", [])
    if questions:
        st.info(
            "**Bạn có thể cung cấp thêm:**\n\n"
            + "\n".join(f"- {question}" for question in questions)
        )

    for warning in message.get("warnings", []):
        st.warning(warning)

    sources = message.get("sources", [])
    if sources:
        with st.expander(f"Nguồn tham khảo ({len(sources)})"):
            for source in sources:
                title = source["title"]
                source_id = source["source_id"]
                if source.get("url"):
                    st.markdown(f"- [{title}]({source['url']}) — `{source_id}`")
                else:
                    st.markdown(f"- **{title}** — `{source_id}`")


def render_message(message: dict[str, Any]) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_metadata(message)


initialize_session()
engine = get_engine()

st.title("Trợ lý thủ tục hành chính")
st.caption("Demo hỏi đáp về các thủ tục và quyền lợi liên quan đến sinh con")

with st.sidebar:
    st.subheader("Phiên chat")
    if st.button("Cuộc trò chuyện mới", use_container_width=True):
        reset_conversation()
        st.rerun()
    st.caption("Dữ liệu hiện tại chỉ phục vụ demo sự kiện sinh con.")

if not st.session_state.messages:
    st.info(
        "Hãy mô tả tình huống của bạn, ví dụ: **Tôi vừa sinh con** hoặc "
        "**Khai sinh cần giấy tờ gì?**"
    )

for stored_message in st.session_state.messages:
    render_message(stored_message)

if user_text := st.chat_input("Nhập câu hỏi hoặc mô tả tình huống..."):
    user_message = {"role": "user", "content": user_text}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm thủ tục và căn cứ liên quan..."):
            try:
                response = engine.run(
                    user_text,
                    conversation_id=st.session_state.conversation_id,
                    limit=RETRIEVAL_LIMIT,
                )
            except Exception:
                LOGGER.exception("RAG engine failed while handling a chat message")
                error_message = {
                    "role": "assistant",
                    "content": "Không thể xử lý câu hỏi lúc này. Hãy kiểm tra kết nối dữ liệu và thử lại.",
                    "warnings": [],
                    "follow_up_questions": [],
                    "sources": [],
                }
                st.session_state.messages.append(error_message)
                st.error(error_message["content"])
            else:
                assistant_message = {
                    "role": "assistant",
                    "content": response.answer_markdown,
                    "follow_up_questions": response.follow_up_questions,
                    "warnings": response.warnings,
                    "sources": [
                        source.model_dump(mode="json") for source in response.sources
                    ],
                }
                st.session_state.messages.append(assistant_message)
                st.markdown(assistant_message["content"])
                render_metadata(assistant_message)
