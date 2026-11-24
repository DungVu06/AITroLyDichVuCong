# Request 1 — Hậu kiểm lộ trình thủ tục (bản mới)

## Phạm vi kiểm chứng

- Bộ ca: TC01–TC05 trong `rag/demos/graph_vs_vector_only_cases.json`.
- Nguồn trả lời: snapshot thủ tục local; câu trả lời luôn phải có evidence/citation trong context.
- Lượt chạy cuối: 10 arm độc lập lúc `2026-11-24T04:31:26Z`; log nguyên văn ở `_new_raw/graph_vs_vector_only_20261124-113126_answers.md`.

## Các thay đổi pipeline đã áp dụng

1. **Routing liên thông theo fact có thể kiểm chứng.** Tình huống trẻ chưa khai sinh nhưng hỏi BHYT được nhận diện là gói liên thông, kể cả khi bước hiểu câu hỏi không trả về đúng ID `PROC_3_000722`.
2. **Contract TC02 có CT01.** Tờ khai thay đổi thông tin cư trú trở thành evidence bắt buộc, cùng hợp đồng công chứng/chứng thực, ý kiến chủ sở hữu, diện tích, cơ quan và thời hạn.
3. **Evidence workflow không chỉ lấy parent.** Khi contract cần evidence ở thủ tục thành phần, retrieval đưa bản ghi đó vào context thay vì chỉ đưa node graph.
4. **Không ép trình bày mọi nhánh thủ tục.** Chỉ truy vết đủ numbered steps khi người dùng nói rõ đang hỏi trình tự của gói liên thông; câu “phải làm thế nào” trong ca Căn cước không còn tự biến thành yêu cầu liệt kê cả các nhánh dưới 14 tuổi/cấp đổi/cấp lại.
5. **Validator bớt fallback hình thức.** `missing_requested_evidence` của topic tổng quát chỉ là warning nếu không có contract; các claim thuộc contract mới là điều kiện bắt buộc.
6. **Chunk của step bị tách.** Khi cần đủ trình tự, retriever ưu tiên fragment nội dung đầu tiên của step thay vì fragment dài nhưng là ngoại lệ ở cuối step.

## Kết quả hậu kiểm Graph-RAG

| Ca | Score | Fallback | Verdict theo dữ liệu demo |
|---|---:|---|---|
| TC01 — Sinh tại nhà, thiếu Giấy chứng sinh | 100.0 | Không | Đủ người làm chứng/cam đoan, UBND cấp xã, thời hạn. |
| TC02 — Thường trú nhà thuê | 90.0 | Không | Nội dung CT01 có xuất hiện; còn thiếu đúng citation `c126_s0` theo rubric. |
| TC03 — Liên thông 4 thủ tục | 84.6 | Có | Luồng chính đúng nhưng fallback thiếu citation fragment chứa quy định 24 giờ. |
| TC04 — Sai ngày sinh trước Căn cước | 81.2 | Không | Đúng điều chỉnh dữ liệu trước, không lẫn citation nhánh dưới 14; output không nêu đủ ba chi tiết sinh trắc học. |
| TC05 — BHYT khi chưa khai sinh | 100.0 | Không | Đúng hai phương án: nộp liên thông ngay, hoặc làm riêng sau khai sinh; phân biệt Mẫu 01/2 ngày/3–5 ngày với Mẫu 2/5 ngày. |

## Tồn tại đã được ghi nhận, chưa tuyên bố hoàn tất

- TC03 vẫn fallback vì `required_step_numbers` có thể mở rộng sang evidence của procedure thành phần qua các relation requirement. Fallback là an toàn hơn bịa nguồn, nhưng không phải output mong muốn.
- TC04 không còn lẫn nhánh tuổi, nhưng prompt chưa luôn chủ động nêu vân tay, ảnh khuôn mặt, mống mắt khi người dùng chỉ hỏi trình tự xử lý sai dữ liệu.
- Score là evidence/rubric score; không thay thế thẩm định pháp lý bởi chuyên gia.

## Quy tắc trả lời đã được giữ

- Không khẳng định route đơn lẻ là route liên thông.
- Không dùng Căn cước như nhánh bắt buộc nếu người dùng không đề nghị cấp thẻ cho trẻ trong hồ sơ liên thông.
- Một citation thiếu có thể kích hoạt sửa; fallback chỉ xảy ra sau khi bản sinh và bản sửa vẫn không qua hậu kiểm claim-level.
