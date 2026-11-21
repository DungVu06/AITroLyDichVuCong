"""Xác định evidence bắt buộc cho các tình huống demo có rủi ro cao.

LLM không được tự chọn claim quan trọng rồi hy vọng semantic retrieval tìm đúng
chunk. Module này biến các nhánh thủ tục đã biết thành một hợp đồng kiểm chứng
được: retrieval phải đưa đúng evidence vào context và validator phải thấy
evidence đó được trích dẫn trong câu trả lời.
"""

from __future__ import annotations

from rag.core.schemas import AnswerContract, EvidenceRequirement, QueryState, UserQuery


BIRTH = "PROC_1_001193"
RESIDENCE = "PROC_1_116788"
HEALTH = "PROC_1_014137"
CARD = "PROC_1_116410"
LINKED = "PROC_3_000722"


def _requirement(
    claim_id: str,
    label: str,
    procedure_id: str,
    chunk_type: str,
    *terms: str,
) -> EvidenceRequirement:
    return EvidenceRequirement(
        claim_id=claim_id,
        label=label,
        procedure_id=procedure_id,
        chunk_type=chunk_type,
        required_terms=list(terms),
    )


def build_answer_contract(query: UserQuery, state: QueryState) -> AnswerContract:
    text = query.text.casefold()
    procedure_ids = list(dict.fromkeys(state.procedure_ids))
    requirements: list[EvidenceRequirement] = []
    questions: list[str] = []
    submission_channel: str | None = None
    processing_flow: list[str] = []

    birth_at_home = "giấy chứng sinh" in text and ("tại nhà" in text or "không có" in text)
    if birth_at_home:
        procedure_ids.append(BIRTH)
        requirements += [
            _requirement("birth_alternative_document", "Hồ sơ thay Giấy chứng sinh", BIRTH, "document_item", "người làm chứng", "giấy cam đoan"),
            _requirement("birth_authority_and_time", "Nơi nộp và thời hạn khai sinh", BIRTH, "execution_methods", "Ủy ban nhân dân cấp xã", "1 ngày"),
        ]
        questions.append("Khi sinh tại nhà, có người làm chứng có thể xác nhận việc sinh không?")

    residence_case = any(term in text for term in ("thuê", "mượn", "ở nhờ")) and any(
        term in text for term in ("thường trú", "nhập khẩu", "đăng ký cư trú")
    )
    if residence_case:
        procedure_ids.append(RESIDENCE)
        requirements += [
            _requirement("residence_contract", "Hợp đồng thuê, mượn hoặc ở nhờ", RESIDENCE, "document_item", "công chứng hoặc chứng thực"),
            _requirement("residence_owner_consent", "Văn bản đồng ý của chủ sở hữu", RESIDENCE, "document_item", "ý kiến đồng ý", "chủ sở hữu"),
            _requirement("residence_area", "Điều kiện diện tích chỗ ở", RESIDENCE, "document_item", "diện tích nhà ở"),
            _requirement("residence_authority", "Cơ quan tiếp nhận thường trú", RESIDENCE, "execution_methods", "Công an Xã"),
            _requirement("residence_time", "Thời hạn giải quyết thường trú", RESIDENCE, "execution_methods", "07 ngày làm việc"),
        ]
        questions += [
            "Hợp đồng thuê, mượn hoặc ở nhờ đã được công chứng hoặc chứng thực chưa?",
            "Chủ sở hữu chỗ ở hợp pháp đã đồng ý bằng văn bản cho đăng ký thường trú chưa?",
        ]

    linked_case = "vneid" in text and any(term in text for term in ("liên thông", "4 trong 1", "bảo hiểm y tế", "thường trú"))
    if linked_case:
        procedure_ids.append(LINKED)
        requirements += [
            _requirement("linked_submission", "Kênh nộp hồ sơ liên thông", LINKED, "step_item", "VNeID", "Cổng Dịch vụ công quốc gia"),
            _requirement("linked_birth_step", "Bước xử lý khai sinh", LINKED, "step_item", "đăng ký khai sinh", "24 giờ"),
            _requirement("linked_residence_health_step", "Bước xử lý thường trú và BHYT", LINKED, "step_item", "đăng ký thường trú", "bảo hiểm y tế"),
            _requirement("linked_card_step", "Bước xử lý cấp căn cước", LINKED, "step_item", "cấp thẻ căn cước", "05 ngày"),
            _requirement("linked_total_time", "Thời gian giải quyết gói liên thông", LINKED, "execution_methods", "Ba (03) ngày"),
        ]
        submission_channel = "Người dân nộp trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia; các cơ quan xử lý tiếp theo qua hệ thống liên thông."
        processing_flow = [
            "Cổng Dịch vụ công quốc gia chuyển hồ sơ sang hệ thống của Bộ Tư pháp.",
            "UBND cấp xã giải quyết đăng ký khai sinh khi hồ sơ hợp lệ.",
            "Sau khai sinh, hệ thống chuyển dữ liệu để giải quyết thường trú và BHYT.",
            "Hệ thống tiếp tục chuyển hồ sơ cấp thẻ căn cước nếu người đại diện đã yêu cầu.",
        ]

    mismatch_case = "vneid" in text and any(term in text for term in ("ngày sinh", "sai", "không khớp", "sai lệch"))
    if mismatch_case:
        procedure_ids.append(CARD)
        requirements += [
            _requirement("card_correct_first", "Xử lý điều chỉnh dữ liệu trước", CARD, "step_item", "điều chỉnh thông tin", "trước khi thực hiện thủ tục cấp thẻ căn cước"),
            _requirement("card_cc01", "Phiếu thu nhận thông tin căn cước", CARD, "document_item", "Mẫu CC01"),
            _requirement("card_cc02", "Phiếu thu thập thông tin dân cư", CARD, "step_item", "Mẫu CC02"),
            _requirement("card_biometrics", "Thu nhận sinh trắc học", CARD, "step_item", "mống mắt"),
        ]
        questions.append("Thông tin ngày sinh đã được điều chỉnh trong Cơ sở dữ liệu quốc gia về dân cư chưa?")

    mentions_health = "bảo hiểm y tế" in text or "bhyt" in text
    mentions_birth_registration = "khai sinh" in text or "giấy khai sinh" in text
    has_not_registered_birth = any(marker in text for marker in (
        "chưa khai sinh",
        "chưa đăng ký khai sinh",
        "chưa làm giấy khai sinh",
        "chưa có giấy khai sinh",
        "không có giấy khai sinh",
    ))
    health_without_birth = (
        mentions_health and mentions_birth_registration and has_not_registered_birth
    )
    if health_without_birth:
        procedure_ids += [BIRTH, HEALTH, LINKED]
        requirements += [
            EvidenceRequirement(
                claim_id="health_requires_birth",
                label="Khai sinh là bước tiên quyết của BHYT đơn lẻ",
                procedure_id=HEALTH,
                relation_type="REQUIRES",
            ),
            _requirement("health_form", "Tờ khai BHYT", HEALTH, "document_item", "Mẫu số 2"),
            _requirement("health_channel", "Hình thức nộp BHYT đơn lẻ", HEALTH, "execution_methods", "Hình thức: Trực tuyến"),
            _requirement("health_time", "Thời hạn cấp thẻ BHYT đơn lẻ", HEALTH, "execution_methods", "05 ngày"),
        ]

    return AnswerContract(
        procedure_ids=list(dict.fromkeys(procedure_ids)),
        requirements=requirements,
        required_follow_up_questions=list(dict.fromkeys(questions))[:3],
        submission_channel=submission_channel,
        processing_flow=processing_flow,
    )
