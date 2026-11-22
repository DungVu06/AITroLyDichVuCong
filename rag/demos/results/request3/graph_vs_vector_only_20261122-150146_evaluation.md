# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị

- Thời điểm UTC: 2026-11-22T08:01:46+00:00
- Model: `gemini-3.5-flash-lite`
- Dataset: 5 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.
- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.
- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.
- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.

## Bảng kết quả đối chứng

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |
|---|---:|---:|---:|---:|---|---|
| TC01 – Khai sinh tại nhà không có Giấy chứng sinh | 100.0 | 100.0 | 29.938 | 25.164 | 2 / 6816 | 2 / 6880 |
| TC02 – Thường trú tại nhà thuê | 100.0 | 100.0 | 36.068 | 30.076 | 3 / 16413 | 3 / 17412 |
| TC03 – Liên thông VNeID bốn thủ tục | 100.0 | 100.0 | 26.242 | 18.670 | 2 / 9006 | 2 / 8637 |
| TC04 – Sai ngày sinh trước khi cấp Căn cước | 100.0 | 100.0 | 61.446 | 27.866 | 3 / 16703 | 3 / 16472 |
| TC05 – BHYT khi chưa đăng ký khai sinh | 100.0 | 83.3 | 95.348 | 54.568 | 3 / 34296 | 2 / 17724 |

## Tổng hợp

| Chỉ số | Graph-RAG | Vector-only |
|---|---:|---:|
| Ca hoàn tất | 5 | 5 |
| Điểm trung bình / 100 | 100.0 | 96.66 |
| Latency trung bình (s) | 49.808 | 31.269 |
| Tổng Gemini calls | 13 | 12 |
| Input tokens | 76914 | 61614 |
| Output tokens | 6320 | 5511 |
| Total tokens | 83234 | 67125 |

## Lỗi điển hình theo rubric

### graph
- `fallback_answer`: 1 ca

### vector_only
- `missing_citation: REL:PROC_1_014137:REQUIRES:PROC_1_001193`: 1 ca

## Phạm vi và giới hạn thử

- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.
- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.
- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.
- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.
- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.
- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.
