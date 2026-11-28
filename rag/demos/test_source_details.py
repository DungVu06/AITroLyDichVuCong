"""Kiểm tra thông tin nguồn và gợi ý cơ quan khi thiếu dữ kiện."""
import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from rag.core.schemas import AnswerContext, BenefitEvidence, EligibilityStatus, Intent, ProcedureEvidence, QueryState, RAGResponse, RetrievedChunk, SourceMetadata, UserQuery
from rag.engine import RAGEngine
from rag.generation.answer import _collect_sources
from rag.retrieval.catalog import inspect_versions


class SourceDetailsTest(unittest.TestCase):
    def test_matching_legal_basis_has_own_metadata(self):
        law = {
            "id": "LAW1", "source": {"url": "https://example.org/law", "effective_date": "2020-01-01"},
            "content": {"document_number": "12/2020/TT", "validity_raw": "Còn hiệu lực"},
            "jurisdiction": {"level": "Toàn quốc"},
        }
        procedure = {
            "id": "PROC1", "source": {"url": "https://example.org/procedure"},
            "jurisdiction": {"level": "Cấp xã"},
            "relations": {"legal_bases": [{"code": "12/2020/TT", "name": "Văn bản"}, {"code": "13/2020/TT", "name": "Khác"}]},
        }
        metadata = inspect_versions([law], [procedure], {})["PROC1"]
        self.assertEqual(metadata.legal_basis_metadata["12/2020/TT — Văn bản"].effective_date, "2020-01-01")
        self.assertEqual(metadata.legal_basis_metadata["12/2020/TT — Văn bản"].url, "https://example.org/law")
        self.assertNotIn("13/2020/TT — Khác", metadata.legal_basis_metadata)

    def test_chunk_carries_procedure_metadata(self):
        chunk = RetrievedChunk(collection="procedures", point_id="p", doc_id="PROC1", chunk_id="C1", text="Nội dung")
        context = AnswerContext(query=UserQuery(text="Hỏi"), query_state=QueryState(),
            procedure_evidence=[ProcedureEvidence(procedure_id="PROC1", name="Thủ tục", chunks=[chunk])],
            source_metadata={"PROC1": SourceMetadata(version="v1", effective_date="2020-01-01")})
        sources = _collect_sources(context)
        self.assertEqual(next(s for s in sources if s.source_id == "C1").metadata.effective_date, "2020-01-01")

    def test_follow_up_suggests_matching_procedure_authority(self):
        context = AnswerContext(query=UserQuery(text="Hỏi"), query_state=QueryState(procedure_ids=["PROC1"]),
            procedure_evidence=[ProcedureEvidence(procedure_id="PROC1", name="Thủ tục", authority="Cơ quan A")])
        response = RAGResponse(answer_markdown="Thông tin", follow_up_questions=["Bạn có giấy tờ chưa?"])
        with patch("rag.engine.build_context", return_value=context), patch("rag.engine._generate_validated_response", return_value=response):
            result = RAGEngine().run("Hỏi")
        self.assertTrue(any("Thủ tục: Cơ quan A" in warning for warning in result.warnings))

    def test_missing_authority_is_explicit(self):
        context = AnswerContext(query=UserQuery(text="Hỏi"), query_state=QueryState(procedure_ids=["PROC1"]),
            procedure_evidence=[ProcedureEvidence(procedure_id="PROC1", name="Thủ tục")])
        response = RAGResponse(answer_markdown="Thông tin", follow_up_questions=["Cần thêm thông tin?"])
        with patch("rag.engine.build_context", return_value=context), patch("rag.engine._generate_validated_response", return_value=response):
            result = RAGEngine().run("Hỏi")
        self.assertTrue(any("chưa xác định được cơ quan" in warning for warning in result.warnings))

    def test_benefit_question_does_not_use_unrelated_procedure_authority(self):
        context = AnswerContext(query=UserQuery(text="Hỏi quyền lợi"),
            query_state=QueryState(intent=Intent.BENEFIT_CHECK, procedure_ids=["PROC1"]),
            procedure_evidence=[ProcedureEvidence(procedure_id="PROC1", name="Thủ tục", authority="Công an xã")])
        benefit = BenefitEvidence(related_procedure_id="PROC1", title="Quyền lợi", eligibility_status=EligibilityStatus.UNKNOWN)
        response = RAGResponse(answer_markdown="Thông tin", benefits=[benefit])
        with patch("rag.engine.build_context", return_value=context), patch("rag.engine._generate_validated_response", return_value=response):
            result = RAGEngine().run("Hỏi quyền lợi")
        self.assertTrue(any("chưa xác định được cơ quan" in warning for warning in result.warnings))
        self.assertFalse(any("Công an xã" in warning for warning in result.warnings))

    def test_ui_lists_each_basis_and_its_own_availability(self):
        code = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        tree = ast.parse(code)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "render_metadata")
        fake = FakeStreamlit()
        namespace = {"st": fake, "Any": object}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), "ui/streamlit_app.py", "exec"), namespace)
        namespace["render_metadata"]({"sources": [{"source_type": "procedure", "source_id": "P", "title": "Thủ tục", "url": "https://example.org/p", "metadata": {"version": "abc", "effective_date": "2020-01-01", "legal_bases": ["A", "B"], "legal_basis_metadata": {"A": {"effective_date": "2021-01-01", "url": "https://example.org/a", "validity": "Còn hiệu lực"}}}}]})
        captions = "\n".join(fake.captions)
        self.assertIn("Hiệu lực từ: 2021-01-01", captions)
        self.assertIn("Hiệu lực từ: chưa có thông tin", captions)
        self.assertIn("Chưa có đường dẫn văn bản", captions)


class FakeStreamlit:
    def __init__(self):
        self.captions = []
    def expander(self, *_args, **_kwargs):
        return self
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        pass
    def markdown(self, *_args, **_kwargs):
        pass
    def caption(self, value):
        self.captions.append(value)
    def info(self, *_args, **_kwargs):
        pass
    def warning(self, *_args, **_kwargs):
        pass


if __name__ == "__main__":
    unittest.main()
