# Request 3 — Đối chứng Graph-RAG và vector-only (bản mới)

## Lượt chạy

- Thời điểm: `2026-11-24T04:31:26Z`.
- Model: `gemini-3.5-flash-lite`.
- 10 lượt độc lập: 5 Graph-RAG và 5 vector-only.
- Raw data: `_new_raw/graph_vs_vector_only_20261124-113126.json`.
- Toàn bộ câu hỏi/câu trả lời: `_new_raw/graph_vs_vector_only_20261124-113126_answers.md`.
- Bảng máy sinh: `_new_raw/graph_vs_vector_only_20261124-113126_evaluation.md`.

## Bảng kết quả

| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph token | Vector token |
|---|---:|---:|---:|---:|---:|---:|
| TC01 | 100.0 | 100.0 | 29.621 | 20.565 | 6,931 | 7,014 |
| TC02 | 90.0 | 90.0 | 26.194 | 16.215 | 17,292 | 9,750 |
| TC03 | 84.6 | 84.6 | 30.322 | 25.779 | 55,613 | 18,087 |
| TC04 | 81.2 | 100.0 | 26.132 | 16.933 | 17,168 | 9,726 |
| TC05 | 100.0 | 68.8 | 27.493 | 24.993 | 43,560 | 19,239 |
| **Trung bình** | **91.16** | **88.68** | **27.952** | **20.897** | **140,564 tổng** | **63,816 tổng** |

## Diễn giải đúng phạm vi

- Graph thắng rõ ở TC05: relation evidence buộc được thứ tự khai sinh → dữ liệu điện tử → BHYT và phân biệt được route liên thông với route cấp BHYT đơn lẻ.
- Graph chưa thắng TC03/TC04. TC03 fallback vì citation cho numbered step chưa ổn định; TC04 chất lượng nội dung tốt hơn trước nhưng model không nêu đủ các chi tiết sinh trắc học mà rubric yêu cầu.
- Vector-only vẫn dùng cùng deterministic contract và detail retrieval; đây là control arm để cô lập traversal graph, **không phải** RAG tối giản không engineering.
- Graph đắt hơn: 14 Gemini calls/140,564 token so với 12 calls/63,816 token. Điều này chủ yếu đến từ evidence workflow mở rộng và một fallback TC03.

## Lỗi điển hình và giới hạn

| Nhóm | Quan sát |
|---|---|
| Citation quá chặt | TC02 thiếu đúng `c126_s0` dù nội dung CT01 xuất hiện; rubric exact-ID cần được thay dần bằng tập citation hợp lệ cho cùng claim. |
| Fallback | Chỉ còn Graph TC03; nguyên nhân hậu kiểm `missing_step_citation`, không phải mất dữ liệu hay mất quan hệ graph. |
| Độ dao động LLM | Mỗi arm chạy một lần nên score không đủ để kết luận thống kê; cần lặp nhiều seed/lượt khi muốn công bố so sánh. |
| Phạm vi | Chỉ 5 demo cho sự kiện sinh con, không suy rộng cho thủ tục khác. |
| Manual arm | Không có arm tra cứu thủ công theo phạm vi đã chốt. |

## Kết luận request 3

Đã có minh chứng tái chạy được gồm 10 câu trả lời, score, citation mismatch, fallback, latency và token. Kết quả mới hỗ trợ nhận định hẹp: graph giúp rõ nhất ở tình huống có dependency/liên thông thật sự; nó chưa chứng minh ưu thế chung trên mọi truy vấn và vẫn cần giảm evidence expansion/fallback ở TC03.
