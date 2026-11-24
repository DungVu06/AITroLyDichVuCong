# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị

- Thời điểm UTC: 2026-11-24T03:17:49+00:00
- Model: `gemini-3.5-flash-lite`
- Dataset: 5 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.
- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.
- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.
- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.

## Bảng kết quả đối chứng

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |
|---|---:|---:|---:|---:|---|---|
| TC01 – Khai sinh tại nhà không có Giấy chứng sinh | 100.0 | 100.0 | 80.723 | 25.765 | 2 / 7035 | 2 / 7026 |
| TC02 – Thường trú tại nhà thuê | 80.0 | 80.0 | 48.036 | 94.478 | 2 / 9443 | 3 / 16618 |
| TC03 – Liên thông VNeID bốn thủ tục | 84.6 | 100.0 | 55.624 | 24.968 | 3 / 25991 | 3 / 15950 |
| TC04 – Sai ngày sinh trước khi cấp Căn cước | 87.5 | 93.8 | 125.484 | 24.775 | 3 / 41795 | 3 / 16931 |
| TC05 – BHYT khi chưa đăng ký khai sinh | 60.0 | 53.3 | 31.384 | 55.970 | 3 / 38470 | 2 / 18425 |

## Tổng hợp

| Chỉ số | Graph-RAG | Vector-only |
|---|---:|---:|
| Ca hoàn tất | 5 | 5 |
| Điểm trung bình / 100 | 82.42 | 85.42 |
| Latency trung bình (s) | 68.25 | 45.191 |
| Tổng Gemini calls | 13 | 13 |
| Input tokens | 114767 | 68625 |
| Output tokens | 7967 | 6325 |
| Total tokens | 122734 | 74950 |

## Lỗi điển hình theo rubric

### graph
- `fallback_answer`: 2 ca
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_content: tờ khai thay đổi thông tin cư trú | ct01`: 1 ca
- `missing_citation: PROC_3_000722_c182_s1`: 1 ca
- `missing_content: 24 giờ | 24h | 24 h`: 1 ca
- `forbidden_citation: PROC_1_116410_c86_s0`: 1 ca
- `forbidden_citation: PROC_1_116410_c90_s0`: 1 ca
- `missing_citation: PROC_3_000722_c176_s0`: 1 ca
- `missing_citation: PROC_3_000722_c183_s2`: 1 ca
- `missing_citation: PROC_3_000722_c185_s0`: 1 ca
- `missing_content: khai sinh trước | sau khi đăng ký khai sinh | sau khi có giấy khai sinh | sau khi có bản điện tử giấy khai sinh | khi đã có giấy khai sinh | sau khi hoàn tất khai sinh | sau khi có kết quả khai sinh`: 1 ca
- `missing_content: mẫu số 01 | mẫu số 1 | mẫu 01`: 1 ca
- `missing_content: 3 ngày làm việc | ba ngày làm việc | ba (03) ngày làm việc`: 1 ca

### vector_only
- `missing_citation: PROC_1_116788_c126_s0`: 1 ca
- `missing_content: tờ khai thay đổi thông tin cư trú | ct01`: 1 ca
- `missing_content: trước khi cấp | trước khi làm | trước khi thực hiện thủ tục cấp | sau khi điều chỉnh | sau khi thông tin đã được cập nhật`: 1 ca
- `missing_citation: PROC_3_000722_c176_s0`: 1 ca
- `missing_citation: PROC_3_000722_c183_s2`: 1 ca
- `missing_citation: PROC_3_000722_c185_s0`: 1 ca
- `missing_content: giấy khai sinh điện tử | bản điện tử giấy khai sinh`: 1 ca
- `missing_content: mẫu số 01 | mẫu số 1 | mẫu 01`: 1 ca
- `missing_content: 2 ngày làm việc | hai ngày làm việc | hai (02) ngày làm việc`: 1 ca
- `missing_content: nhận hồ sơ điện tử | nhận được hồ sơ điện tử | tiếp nhận hồ sơ điện tử`: 1 ca

## Phạm vi và giới hạn thử

- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.
- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.
- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.
- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.
- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.
- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.
