"""Xác định evidence bắt buộc cho các tình huống demo có rủi ro cao.

LLM không được tự chọn claim quan trọng rồi hy vọng semantic retrieval tìm đúng
chunk. Module này biến các nhánh thủ tục đã biết thành một hợp đồng kiểm chứng
được: retrieval phải đưa đúng evidence vào context và validator phải thấy
evidence đó được trích dẫn trong câu trả lời.
"""

from __future__ import annotations

import re

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
    step_number: int | None = None,
    excluded_terms: tuple[str, ...] = (),
) -> EvidenceRequirement:
    return EvidenceRequirement(
        claim_id=claim_id,
        label=label,
        procedure_id=procedure_id,
        chunk_type=chunk_type,
        required_terms=list(terms),
        step_number=step_number,
        excluded_terms=list(excluded_terms),
    )


def build_answer_contract(query: UserQuery, state: QueryState) -> AnswerContract:
    text = query.text.casefold()
    procedure_ids = list(dict.fromkeys(state.procedure_ids))
    requirements: list[EvidenceRequirement] = []
    questions: list[str] = []
    submission_channel: str | None = None
    sequence_markers = (
        "các bước", "trình tự", "quy trình", "hệ thống xử lý",
        "thứ tự", "thực hiện như thế nào",
    )
    enforce_step_sequence = "steps" in state.topics or any(
        marker in text for marker in sequence_markers
    )

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

    separate_filing = any(term in text for term in (
        "tôi làm riêng", "tôi nộp riêng", "muốn làm riêng", "muốn nộp riêng",
        "không làm liên thông", "không nộp liên thông",
    ))
    asks_for_linked = any(term in text for term in ("liên thông", "4 trong 1", "4-trong-1"))
    related_to_birth = state.life_event == "sinh_con" or any(term in text for term in (
        "khai sinh", "thường trú", "bảo hiểm y tế", "bhyt", "căn cước",
    ))
    linked_case = not separate_filing and (
        LINKED in state.procedure_ids or (asks_for_linked and related_to_birth)
    )
    if linked_case:
        procedure_ids.append(LINKED)
        requirements.append(
            _requirement("linked_submission", "Kênh nộp hồ sơ liên thông", LINKED, "step_item",
                         "VNeID", "Cổng Dịch vụ công quốc gia", step_number=1)
        )
        transfers = [
            (BIRTH, RESIDENCE, "Kết quả khai sinh chuyển sang thường trú"),
            (BIRTH, HEALTH, "Kết quả khai sinh chuyển sang BHYT"),
        ]
        if state.identity_card_requested is not False:
            transfers.append((RESIDENCE, CARD, "Điều kiện và thứ tự xử lý căn cước"))
        requirements.extend(
            EvidenceRequirement(
                claim_id=f"linked_transfer_{target}",
                label=label,
                procedure_id=source,
                target_procedure_id=target,
                relation_type="NEXT_STEP",
            )
            for source, target, label in transfers
        )
        if "processing_time" in state.topics or "bao lâu" in text or "bao nhiêu ngày" in text:
            requirements.append(
                _requirement("linked_total_time", "Thời gian giải quyết gói liên thông",
                             LINKED, "execution_methods", "Ba (03) ngày")
            )
        submission_channel = "Người dân nộp hồ sơ liên thông trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia."

    mismatch_case = "vneid" in text and any(term in text for term in ("ngày sinh", "sai", "không khớp", "sai lệch"))
    if mismatch_case:
        procedure_ids.append(CARD)
        age_match = re.search(r"\b(\d{1,2})\s*tuổi\b", text)
        age = int(age_match.group(1)) if age_match else None
        # The source contains separate numbered branches for under-14 and for
        # general/from-14 cases. Select from the stated age instead of mixing
        # semantic matches from incompatible branches.
        initial_card_steps = (21, 25, 27) if age is not None and age < 14 else (8, 11, 13)
        requirements += [
            _requirement("card_correct_first", "Xử lý điều chỉnh dữ liệu trước", CARD, "step_item", "điều chỉnh thông tin", "trước khi thực hiện thủ tục cấp thẻ căn cước", step_number=initial_card_steps[0]),
            _requirement("card_cc01", "Phiếu thu nhận thông tin căn cước", CARD, "document_item", "Mẫu CC01"),
            _requirement("card_cc02", "Giấy hẹn trả kết quả căn cước", CARD, "step_item", "Mẫu CC02", step_number=initial_card_steps[2]),
            _requirement("card_biometrics", "Thu nhận sinh trắc học", CARD, "step_item", "mống mắt", step_number=initial_card_steps[1]),
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
    if health_without_birth and not linked_case:
        procedure_ids += [BIRTH, HEALTH, LINKED]
        requirements += [
            _requirement("health_under_six_filing", "Cấp thẻ BHYT cho trẻ dưới 6 tuổi",
                         HEALTH, "step_item", "trẻ em dưới 6 tuổi", "thực hiện liên thông"),
            _requirement("health_form", "Tờ khai BHYT", HEALTH, "document_item", "Mẫu số 2"),
            _requirement("health_channel", "Hình thức nộp BHYT đơn lẻ", HEALTH, "execution_methods", "Hình thức: Trực tuyến"),
            _requirement("health_time", "Thời hạn cấp thẻ BHYT đơn lẻ", HEALTH, "execution_methods", "05 ngày"),
        ]

    return AnswerContract(
        procedure_ids=list(dict.fromkeys(procedure_ids)),
        requirements=requirements,
        required_follow_up_questions=list(dict.fromkeys(questions))[:3],
        workflow_id=LINKED if linked_case else None,
        submission_channel=submission_channel,
        enforce_step_sequence=enforce_step_sequence,
    )
