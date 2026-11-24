# Request 2 — Quản lý hiệu lực và phạm vi văn bản (bản mới)

## Phần đang có trong hệ thống

| Yêu cầu | Trạng thái | Cách hiện thực hiện có |
|---|---|---|
| Phiên bản nguồn | Có | Hash version của procedure/law, bỏ qua `crawled_at` để nhận biết thay đổi nội dung thực. |
| Ngày hiệu lực | Có khi source crawl có dữ liệu | `effective_date`/`validity_raw` được đưa vào `SourceMetadata`. |
| Phạm vi áp dụng | Có | Jurisdiction level/location của procedure hiển thị trong metadata. |
| Nguồn chính thức | Có khi record có URL | URL source được gắn cho procedure, law section và citation. |
| Cảnh báo khác phiên bản/hiệu lực | Có một phần | `source_versions.json` đối chiếu snapshot; law thiếu/có trạng thái không phải “còn hiệu lực” tạo review notice. |
| Mapping legal base → thủ tục bị ảnh hưởng | Có một phần | `crawl/legal_bases_summary.json` và legal bases trong procedure record giúp truy ngược thủ tục, nhưng chưa đủ metadata cấp văn bản. |

## Giới hạn cố hữu hiện tại

- Không có job crawl/xác nhận URL tự động, nên hệ thống không tự kết luận website đã thay đổi hay văn bản mới đã thay thế văn bản cũ.
- Legal-base summary là map tham chiếu, không phải kho văn bản pháp luật đầy đủ: phần lớn mã căn cứ chưa có URL, version history, ngày hết hiệu lực riêng.
- Chưa có event store “văn bản A cũ → A mới → edge/bước B,C bị ảnh hưởng”; vì thế chưa thể demo đầy đủ propagation khi thay đổi một văn bản bằng dữ liệu thật.
- Cảnh báo chỉ đi theo source được retrieval/citation trong một lượt hỏi, không phải cảnh báo toàn cục cho toàn bộ database.

## Hành vi hiện tại khi trả lời

- Nếu evidence pháp luật có metadata review/thiếu validity, prompt cấm dùng nó để khẳng định quy định hiện hành và UI có thể hiển thị notice.
- Procedure source hiện mang version, observed date, effective date (nếu crawl được), scope và danh sách legal base.
- Hệ thống **không tự ra Internet cập nhật luật**; người quản lý phải crawl/import lại snapshot. Đây là giới hạn có chủ đích của demo.

## Verdict request 2

Đã đáp ứng phần **gắn metadata, hiển thị nguồn và cảnh báo từ snapshot**. Chưa đáp ứng minh chứng “đổi phiên bản văn bản rồi tự đánh dấu mọi bước phụ thuộc” một cách hoàn chỉnh, vì kho legal-base chưa có versioned official source cho toàn bộ căn cứ. Không nên nói request 2 đã hoàn thiện tuyệt đối.
