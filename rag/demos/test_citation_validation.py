"""Kiểm tra phân loại citation của validator."""
import unittest

from rag.core.schemas import RAGResponse, SourceReference
from rag.generation.validator import validate_answer


class CitationValidationTest(unittest.TestCase):
    def test_missing_citation_is_warning(self):
        response = RAGResponse(
            answer_markdown="Thời gian giải quyết là 1 ngày.",
            sources=[SourceReference(source_type="procedure", source_id="P1", title="Thủ tục")],
        )
        result = validate_answer(response)
        self.assertTrue(result.is_valid)
        self.assertIn("uncited_claim", {issue.code for issue in result.issues})

    def test_unknown_citation_is_error(self):
        response = RAGResponse(answer_markdown="Nội dung 【UNKNOWN】")
        result = validate_answer(response)
        self.assertFalse(result.is_valid)
        self.assertIn("unknown_citation", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
