"""Bước 2-3: dùng Gemini trích xuất intent, facts và dữ kiện còn thiếu."""

from __future__ import annotations

from pathlib import Path

from rag.core.config import GeminiSettings
from rag.retrieval.catalog import procedure_catalog
from rag.core.schemas import PreprocessedQuery, QueryState


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "query_understanding.md"


def build_prompt(
    query: PreprocessedQuery,
    previous_state: QueryState | None = None,
    pending_questions: list[str] | None = None,
) -> str:
    instructions = PROMPT_PATH.read_text(encoding="utf-8").strip()
    instructions += "\nDanh mục thủ tục hiện có (ID và tên):\n" + str(procedure_catalog())
    conversation_context = ""
    if previous_state:
        conversation_context = (
            "\n\nPREVIOUS_QUERY_STATE:\n"
            f"{previous_state.model_dump_json(indent=2)}\n\n"
            "PENDING_QUESTIONS:\n"
            f"{pending_questions or []}"
        )
    return (
        f"{instructions}{conversation_context}\n\n"
        f"Câu hỏi người dùng hiện tại:\n{query.normalized_text}"
    )


def understand_query(
    query: PreprocessedQuery,
    settings: GeminiSettings | None = None,
    *,
    previous_state: QueryState | None = None,
    pending_questions: list[str] | None = None,
) -> QueryState:
    """Gọi Gemini một lần và validate kết quả bằng Pydantic."""
    try:
        from google import genai
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Thiếu google-genai. Hãy cài bằng: pip install google-genai"
        ) from exc

    active_settings = settings or GeminiSettings.from_env()
    client = genai.Client(api_key=active_settings.api_key)
    interaction = client.interactions.create(
        model=active_settings.model,
        input=build_prompt(query, previous_state, pending_questions),
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": QueryState.model_json_schema(),
        },
    )
    if not interaction.output_text:
        raise RuntimeError("Gemini không trả về nội dung phân tích câu hỏi.")
    result = QueryState.model_validate_json(interaction.output_text)
    changed_target = previous_state and previous_state.procedure_ids and result.procedure_ids and (
        set(previous_state.procedure_ids).isdisjoint(result.procedure_ids)
    )
    if previous_state and pending_questions and not changed_target:
        merged_facts = dict(previous_state.facts)
        merged_facts.update(result.facts)
        result = result.model_copy(
            update={
                "life_event": result.life_event or previous_state.life_event,
                "intent": (
                    previous_state.intent
                    if result.intent.value == "unknown"
                    else result.intent
                ),
                "topics": list(
                    dict.fromkeys([*previous_state.topics, *result.topics])
                ),
                "target": result.target or previous_state.target,
                "procedure_ids": result.procedure_ids or previous_state.procedure_ids,
                "facts": merged_facts,
                "identity_card_requested": (
                    previous_state.identity_card_requested
                    if result.identity_card_requested is None
                    else result.identity_card_requested
                ),
            }
        )
    return result


