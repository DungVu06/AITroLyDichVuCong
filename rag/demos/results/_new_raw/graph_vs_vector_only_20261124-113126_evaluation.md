# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị

- Thời điểm UTC: 2026-11-24T04:31:26+00:00
- Model: `gemini-3.5-flash-lite`
- Dataset: 5 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.
- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.
- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.
- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.

## Bảng kết quả đối chứng

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |
|---|---:|---:|---:|---:|---|---|
| TC01 – Khai sinh tại nhà không có Giấy chứng sinh | 100.0 | 100.0 | 29.621 | 20.565 | 2 / 6931 | 2 / 7014 |
| TC02 – Thường trú tại nhà thuê | 90.0 | 90.0 | 26.194 | 16.215 | 3 / 17292 | 2 / 9750 |
| TC03 – Liên thông VNeID bốn thủ tục | 84.6 | 84.6 | 30.322 | 25.779 | 3 / 55613 | 3 / 18087 |
| TC04 – Sai ngày sinh trước khi cấp Căn cước | 81.2 | 100.0 | 26.132 | 16.933 | 3 / 17168 | 2 / 9726 |
| TC05 – BHYT khi chưa đăng ký khai sinh | 100.0 | 68.8 | 27.493 | 24.993 | 3 / 43560 | 3 / 19239 |

## Tổng hợp

| Chỉ số | Graph-RAG | Vector-only |
|---|---:|---:|
| Ca hoàn tất | 5 | 5 |
| Điểm trung bình / 100 | 91.16 | 88.68 |
| Latency trung bình (s) | 27.952 | 20.897 |
| Tổng Gemini calls | 14 | 12 |
| Input tokens | 130672 | 58617 |
| Output tokens | 9892 | 5199 |
| Total tokens | 140564 | 63816 |

## Lỗi điển hình theo rubric

### graph
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_citation: PROC_3_000722_c182_s1`: 1 ca
- `missing_content: 24 giờ | 24h | 24 h`: 1 ca
- `fallback_answer`: 1 ca
- `missing_content: vân tay`: 1 ca
- `missing_content: ảnh khuôn mặt | chụp ảnh mặt`: 1 ca
- `missing_content: mống mắt`: 1 ca

### vector_only
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_content: kết quả đăng ký thường trú | kết quả thường trú`: 1 ca
- `missing_content: theo yêu cầu | có đề nghị | đã đề nghị | nếu đề nghị | đã yêu cầu`: 1 ca
- `missing_citation: PROC_3_000722_c183_s2`: 1 ca
- `missing_content: có thể nộp ngay | nộp hồ sơ liên thông ngay | chưa có giấy khai sinh`: 1 ca
- `missing_content: giấy khai sinh điện tử | bản điện tử giấy khai sinh`: 1 ca
- `missing_content: 2 ngày làm việc | hai ngày làm việc | hai (02) ngày làm việc`: 1 ca
- `missing_content: nhận hồ sơ điện tử | nhận được hồ sơ điện tử | tiếp nhận hồ sơ điện tử`: 1 ca

## Phạm vi và giới hạn thử

- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.
- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.
- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.
- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.
- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.
- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.
