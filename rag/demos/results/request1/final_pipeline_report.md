# Yêu cầu cải tiến 1 — Trạng thái pipeline hoàn chỉnh cuối cùng

## Mục tiêu đã xử lý

Kiểm chứng lộ trình thủ tục để tránh **sai bước, thiếu bước, đảo thứ tự, dùng sai nhánh điều kiện hoặc thiếu căn cứ trích dẫn**. Báo cáo này chỉ mô tả trạng thái hoàn chỉnh hiện tại, không bao gồm lịch sử các lượt sửa trước đó.

## Pipeline hiện tại

| Bước | Thành phần | Vai trò kiểm soát |
|---:|---|---|
| 1 | Preprocess | Chuẩn hóa câu hỏi và giữ conversation ID. |
| 2 | Gemini query understanding | Trích xuất intent, thủ tục mục tiêu, facts, dependency, topics và facts còn thiếu theo schema `QueryState`. |
| 3 | Python routing | Chọn retrieval strategy và loại chunk cần lấy; LLM không trực tiếp quyết định truy vấn DB. |
| 4 | Answer contract | Python phát hiện các tình huống rủi ro của demo và biến thành requirement có thể kiểm chứng: procedure, loại evidence, terms, step number, exclusion hoặc quan hệ graph. |
| 5 | Qdrant retrieval | Lấy semantic seed và chi tiết theo đúng procedure/chunk type; required evidence không bị semantic rank đẩy ra ngoài. |
| 6 | Graph retrieval | Neo4j mở rộng dependency/next step/part-of/benefit; lỗi kết nối sẽ dùng `SnapshotGraph` local và gắn warning. |
| 7 | Journey builder | Tính priority từ `REQUIRES`/`NEXT_STEP`; không để LLM tự đảo thứ tự phụ thuộc. |
| 8 | Context builder | Nén evidence theo giới hạn nhưng giữ chunk bắt buộc và đủ numbered step khi người dùng hỏi quy trình. |
| 9 | Gemini answer generation | Chỉ nhận `AnswerContext` có cấu trúc; prompt bắt citation theo procedure/chunk/relation, phân biệt kênh nộp với luồng xử lý nội bộ. |
| 10 | Deterministic citation repair | Bổ sung citation procedure còn thiếu khi Python xác định được vị trí chắc chắn. |
| 11 | Validation | Kiểm tra citation lạ, claim/số liệu không citation, evidence theo topic, evidence theo contract, step sequence, benefit uncertainty và cảnh báo hiệu lực. |
| 12 | Gemini repair | Chỉ chạy khi deterministic repair không làm câu trả lời đạt validator. |
| 13 | Evidence fallback | Nếu vẫn không đạt, dựng câu trả lời từ evidence/contract đã retrieve, không bịa thông tin; warning nêu rõ fallback. |
| 14 | Source filtering + transcript | Chỉ trả source thực sự được citation; lưu câu hỏi/đáp khi có conversation ID. |

## Guardrail cho 5 use case

| Case | Rủi ro cần chặn | Guardrail cuối cùng | Kết quả mục tiêu |
|---|---|---|---|
| TC01 — Sinh tại nhà, thiếu Giấy chứng sinh | Bỏ qua nhánh chứng minh việc sinh; sai nơi nộp hoặc thời hạn | Contract bắt `document_item` có **người làm chứng + giấy cam đoan** và `execution_methods` có **UBND cấp xã + 1 ngày**; hỏi thêm về người làm chứng | Hướng dẫn văn bản người làm chứng hoặc cam đoan, UBND cấp xã, 1 ngày, citation đúng chunk |
| TC02 — Thường trú nhà thuê | Xem hợp đồng viết tay là đủ; thiếu đồng ý chủ sở hữu/diện tích; nhầm UBND với Công an | Contract buộc evidence hợp đồng công chứng/chứng thực, đồng ý chủ sở hữu, diện tích, Công an xã, 07 ngày; prompt buộc kết luận cần hoàn thiện điều kiện đang thiếu; follow-up hỏi đúng hai fact quyết định | Nói rõ phải hoàn thiện công chứng/chứng thực trước khi nộp, nêu các điều kiện còn lại và cơ quan đúng |
| TC03 — Liên thông VNeID | Thiếu/đảo 5 bước xử lý hoặc gọi luồng nội bộ là nơi nộp | `enforce_step_sequence`; retrieval giữ một chunk substantive cho từng step; validator yêu cầu citation từng step; contract tách `submission_channel` khỏi `processing_flow` | Đủ Bước 1→5 theo thứ tự, đúng VNeID/Cổng DVC là kênh nộp và có thời gian gói liên thông |
| TC04 — Sai ngày sinh VNeID, 15 tuổi | Lấy nhầm nhánh dưới 14; hướng dẫn làm thẻ trước khi sửa dữ liệu | Contract đọc tuổi; chọn step 8/11/13 cho từ 14 tuổi thay vì 21/25/27; requirement có exclusion; bắt evidence điều chỉnh trước, CC01, sinh trắc và CC02 | Điều chỉnh dữ liệu dân cư trước, rồi mới cấp Căn cước; không dùng evidence nhánh dưới 14 |
| TC05 — BHYT khi chưa khai sinh | Cho phép cấp BHYT đơn lẻ trước hoặc chỉ nêu từng thủ tục rời rạc | Graph `REQUIRES` tạo `RelationEvidence` có citation; contract bắt relation, Mẫu 2, kênh nộp và 05 ngày; journey sắp khai sinh là bước tiên quyết | Nêu rõ khai sinh trước BHYT đơn lẻ, trích dependency relation, đồng thời nêu phương án liên thông nếu evidence có |

## Những thay đổi hệ thống giữ vai trò quyết định

- **Schema:** `EvidenceRequirement` có procedure/chunk/terms/step/relation/exclusion; `AnswerContract` có step sequence; `RetrievedChunk` mang `step_number`; context mang `relation_evidence` và source metadata.
- **Engineering thay vì chỉ prompt:** contract, retrieval pinning, dependency priority, numbered-step preservation, validator và fallback đều là logic Python có thể kiểm tra, không đặt niềm tin vào một lần sinh của LLM.
- **Prompt:** chỉ diễn đạt evidence đã cấp; bắt citation đúng cấp; không bịa thủ tục; nêu điều kiện thiếu như bước cần hoàn thiện; tách nơi nộp và luồng nội bộ.
- **Fallback có chủ đích:** khi câu trả lời LLM không qua hậu kiểm, hệ thống ghép evidence bắt buộc đã retrieve. Fallback tồn tại để trả lời có căn cứ thay vì trả lời “không tìm thấy thông tin” trong khi context thực tế đã có bằng chứng.

## Kiểm chứng ở trạng thái cuối

- Unit tests RAG: **18/18 pass**.
- Bộ câu trả lời hiện tại và đo lường Graph-RAG/RAG không đồ thị: `rag/demos/results/graph_vs_vector_only_20261122-150146_answers.md` và `..._evaluation.md`.
- Trong lượt chạy được lưu, Graph-RAG đạt đủ rubric evidence ở 5/5 case. TC02 có một lần fallback sau hậu kiểm, nhưng fallback vẫn trả đủ evidence bắt buộc và report đánh dấu cờ này thay vì che đi.

## Giới hạn phạm vi

- Contract hiện được thiết kế cho 5 tình huống demo, không phải rule engine tổng quát cho mọi thủ tục hành chính.
- LLM vẫn được dùng ở bước hiểu câu hỏi, diễn đạt và repair; validator chỉ kiểm tra được những ràng buộc đã model hóa.
- Data demo và trạng thái hiệu lực nguồn là giới hạn riêng của yêu cầu cải tiến 2; không được suy diễn thành xác nhận pháp lý toàn diện.
