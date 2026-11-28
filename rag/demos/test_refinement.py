"""Kiểm tra nguồn và đầu ra của bước đối chiếu."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from rag.core.config import GeminiSettings
from rag.core.schemas import AnswerContext, ProcedureEvidence, QueryState, RAGResponse, RetrievedChunk, SourceReference, UserQuery
from rag.generation.answer import filter_sources_to_citations, refine_answer


class RefinementTest(unittest.TestCase):
    def test_refinement_retains_warnings_and_maps_sources(self):
        context = AnswerContext(query=UserQuery(text="Câu hỏi"), query_state=QueryState())
        response = RAGResponse(
            answer_markdown="Bản nháp",
            sources=[SourceReference(source_type="procedure", source_id="P1", title="Thủ tục")],
            warnings=["Cảnh báo cũ"],
        )
        interaction = SimpleNamespace(output_text='{"edits":[{"original_text":"Bản nháp","replacement_text":"Thông tin 【P1】 và 【UNKNOWN】"}],"warnings":["Cần xác minh"],"follow_up_questions":["Bạn có thông tin nào?"]}')
        client = SimpleNamespace(interactions=SimpleNamespace(create=lambda **kwargs: interaction))
        with patch("google.genai.Client", return_value=client):
            result = refine_answer(response, context, GeminiSettings(api_key="test"))
        self.assertIn("【P1】", result.answer_markdown)
        self.assertNotIn("【UNKNOWN】", result.answer_markdown)
        self.assertEqual(len(result.warnings), 3)
        self.assertEqual(result.follow_up_questions, ["Bạn có thông tin nào?"])

    def test_cited_chunk_keeps_parent_metadata(self):
        chunk = RetrievedChunk(collection="procedures", point_id="point", doc_id="P1", chunk_id="C1", text="Nội dung")
        procedure = ProcedureEvidence(procedure_id="P1", name="Thủ tục", chunks=[chunk])
        context = AnswerContext(query=UserQuery(text="Câu hỏi"), query_state=QueryState(), procedure_evidence=[procedure])
        response = RAGResponse(answer_markdown="Nội dung 【C1】", sources=[
            SourceReference(source_type="procedure", source_id="P1", title="Thủ tục"),
            SourceReference(source_type="procedure_chunk", source_id="C1", title="Chi tiết"),
        ])
        result = filter_sources_to_citations(response, context)
        self.assertEqual({item.source_id for item in result.sources}, {"P1", "C1"})


if __name__ == "__main__":
    unittest.main()
