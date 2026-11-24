# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị

- Thời điểm UTC: 2026-11-24T02:25:27+00:00
- Model: `gemini-3.5-flash-lite`
- Dataset: 5 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.
- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.
- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.
- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.

## Bảng kết quả đối chứng

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |
|---|---:|---:|---:|---:|---|---|
| TC01 – Khai sinh tại nhà không có Giấy chứng sinh | 100.0 | 100.0 | 67.713 | 20.511 | 2 / 6982 | 2 / 6943 |
| TC02 – Thường trú tại nhà thuê | 0.0 | 100.0 | 219.618 | 65.219 | 2 / 9415 | 3 / 16704 |
| TC03 – Liên thông VNeID bốn thủ tục | 75.0 | 100.0 | 97.455 | 16.977 | 3 / 26605 | 2 / 8700 |
| TC04 – Sai ngày sinh trước khi cấp Căn cước | 81.8 | 81.8 | 60.968 | 31.398 | 3 / 43141 | 3 / 43036 |
| TC05 – BHYT khi chưa đăng ký khai sinh | 83.3 | 83.3 | 48.446 | 61.100 | 2 / 18299 | 3 / 35177 |

## Tổng hợp

| Chỉ số | Graph-RAG | Vector-only |
|---|---:|---:|
| Ca hoàn tất | 4 | 5 |
| Điểm trung bình / 100 | 85.025 | 93.02 |
| Latency trung bình (s) | 68.645 | 39.041 |
| Tổng Gemini calls | 12 | 13 |
| Input tokens | 96427 | 102093 |
| Output tokens | 8015 | 8467 |
| Total tokens | 104442 | 110560 |

## Lỗi điển hình theo rubric

### graph
- `fallback_answer`: 2 ca
- `run_error: InternalServerError: Error code: 503 - {'error': {'message': 'gemini-3.5-flash-lite is currently experiencing high demand, spikes in demand are usually temporary. Please try again later.', 'code': 'service_unavailable'}}`: 1 ca
- `missing_citation: PROC_1_116788_c127_s0`: 1 ca
- `missing_citation: PROC_1_116788_c142_s2`: 1 ca
- `missing_citation: PROC_1_116788_c128_s0`: 1 ca
- `missing_citation: PROC_1_116788_c174_s0`: 1 ca
- `missing_content: công chứng | chứng thực`: 1 ca
- `missing_content: chủ sở hữu`: 1 ca
- `missing_content: diện tích`: 1 ca
- `missing_content: công an xã`: 1 ca
- `missing_content: 07 ngày`: 1 ca
- `missing_citation: PROC_3_000722_c182_s1`: 1 ca
- `missing_content: bước 1`: 1 ca
- `missing_content: bước 3`: 1 ca
- `forbidden_citation: PROC_1_116410_c86_s0`: 1 ca
- `forbidden_citation: PROC_1_116410_c90_s0`: 1 ca
- `missing_citation: REL:PROC_1_014137:REQUIRES:PROC_1_001193`: 1 ca

### vector_only
- `forbidden_citation: PROC_1_116410_c86_s0`: 1 ca
- `forbidden_citation: PROC_1_116410_c90_s0`: 1 ca
- `fallback_answer`: 1 ca
- `missing_citation: REL:PROC_1_014137:REQUIRES:PROC_1_001193`: 1 ca

## Phạm vi và giới hạn thử

- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.
- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.
- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.
- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.
- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.
- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.
