# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị

- Thời điểm UTC: 2026-11-24T05:01:31+00:00
- Model: `gemini-3.5-flash-lite`
- Dataset: 4 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.
- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.
- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.
- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.

## Bảng kết quả đối chứng

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |
|---|---:|---:|---:|---:|---|---|
| TC01 – Khai sinh tại nhà không có Giấy chứng sinh | 100.0 | 100.0 | 25.005 | 22.339 | 2 / 7010 | 2 / 7084 |
| TC02 – Thường trú tại nhà thuê | 90.0 | 90.0 | 16.821 | 17.317 | 2 / 9745 | 2 / 9756 |
| TC03 – Liên thông VNeID bốn thủ tục | 100.0 | 100.0 | 28.341 | 17.096 | 3 / 29796 | 2 / 10162 |
| TC05 – BHYT khi chưa đăng ký khai sinh | 93.8 | 93.8 | 26.794 | 16.952 | 3 / 35523 | 2 / 10347 |

## Tổng hợp

| Chỉ số | Graph-RAG | Vector-only |
|---|---:|---:|
| Ca hoàn tất | 4 | 4 |
| Điểm trung bình / 100 | 95.95 | 95.95 |
| Latency trung bình (s) | 24.24 | 18.426 |
| Tổng Gemini calls | 10 | 8 |
| Input tokens | 76824 | 34240 |
| Output tokens | 5250 | 3109 |
| Total tokens | 82074 | 37349 |

## Lỗi điển hình theo rubric

### graph
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_content: có thể nộp ngay | nộp hồ sơ liên thông ngay | chưa có giấy khai sinh`: 1 ca

### vector_only
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_content: giấy khai sinh điện tử | bản điện tử giấy khai sinh`: 1 ca

## Phạm vi và giới hạn thử

- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.
- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.
- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.
- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.
- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.
- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.
