# Yêu cầu cải tiến 2 — Hiệu lực, phiên bản và phạm vi nguồn

## Mục tiêu đề bài

Gắn **phiên bản**, **ngày hiệu lực**, **phạm vi địa phương** và **nguồn chính thức**; khi nguồn thay đổi thì kiểm tra lại các bước phụ thuộc hoặc cảnh báo nguồn chưa xác minh. Minh chứng yêu cầu là demo đổi phiên bản một văn bản và thấy các bước liên quan được cập nhật/cảnh báo.

## Những gì hệ thống hiện có

| Thành phần yêu cầu | Trạng thái hiện tại | Nơi dữ liệu/pipeline xử lý |
|---|---|---|
| Nguồn chính thức | Có cho từng thủ tục/law khi record gốc có `source.url`; UI/source reference có thể mở URL | `data/*/records/*.json` → `SourceMetadata.url` → `RAGResponse.sources` |
| Phiên bản | Có hash SHA-256 xác định từ snapshot record, bỏ qua timestamp crawl thuần túy | `rag/retrieval/catalog.py:revision()`; baseline `rag/retrieval/source_versions.json` |
| Ngày hiệu lực | Có nếu record nguồn cung cấp `source.effective_date` hoặc `content.effective_date_raw` | `SourceMetadata.effective_date` |
| Phạm vi địa phương | Có từ `jurisdiction.level` và `jurisdiction.location` | `SourceMetadata.scope` |
| Thời điểm ghi nhận nguồn | Có từ `source.last_updated` hoặc `source.crawled_at` | `SourceMetadata.observed_at` |
| Trạng thái hiệu lực luật | Có khi law record có `validity_raw`; thiếu thì giữ `Chưa xác minh`/review notice | `SourceMetadata.validity`, `SourceMetadata.review` |
| Phát hiện record nguồn đổi | Có: khác hash với baseline sẽ sinh review notice | `inspect_versions()` |
| Lan cảnh báo sang thủ tục bị ảnh hưởng | Có một phần: luật có trong dataset và map được từ legal-base của thủ tục sẽ lan review; relation quyền lợi cũng nhận notice | `inspect_versions()` |
| Hiển thị cảnh báo trong câu trả lời | Có điều kiện: warning được đưa vào response khi metadata/law evidence liên quan được dùng; validator ép hiển thị khi warning yêu cầu hiệu lực | `rag/generation/answer.py`, `rag/generation/validator.py` |

## Khoảng trống so với yêu cầu

| Khoảng trống | Hệ quả |
|---|---|
| Không có job tự crawl web hoặc tự xác nhận URL/status của nguồn | Hệ thống chỉ biết snapshot local đã đổi khi người quản lý cập nhật/import lại data; không thể tự kết luận luật mới hết hiệu lực. |
| Phần lớn legal base của thủ tục chưa có law record tương ứng trong 4 law documents demo | Có tên/mã căn cứ, nhưng không có URL/version/effective/validity riêng để đối chiếu. Vì vậy procedure metadata hiện cảnh báo “một số căn cứ … chưa được đối chiếu hiệu lực”. |
| `crawl/legal_bases_summary.json` là inverse mapping legal-base → procedures, không mang đủ URL/trạng thái/phiên bản | Có thể xác định thủ tục nào bị tác động bởi một mã căn cứ, nhưng không đủ metadata để xác nhận nguồn chính thức hay ngày hết hiệu lực. |
| Snapshot chỉ phát hiện khác biệt record; không có lịch sử version hoặc workflow duyệt cập nhật | Không thể trình diễn đầy đủ chuỗi “văn bản A phiên bản cũ → mới → các bước B/C cập nhật” từ một kho version độc lập. |
| Cảnh báo chỉ xuất hiện nếu source đó vào context/citation của lượt hỏi | Không phải cơ chế cảnh báo toàn cục cho tất cả thủ tục tại thời điểm data thay đổi. |

## Kết luận đánh giá hiện tại

- Đã làm được phần metadata nội bộ: URL, version hash, effective date (khi nguồn có), scope, observed date và review notice.
- Đã làm được một phần propagation bằng mapping law/benefit hiện có và đã có test `test_changed_law_marks_dependent_procedures`.
- Chưa đạt minh chứng đầy đủ của yêu cầu 2 vì chưa có nguồn/version pháp lý đầy đủ cho legal-base, không có cập nhật web tự động, và chưa demo thay thế một văn bản có version history rồi tái kiểm tất cả bước phụ thuộc.

## Phạm vi demo hiện tại

Demo chỉ gồm 5 thủ tục liên quan sự kiện sinh con và 4 law documents được import. Do đó mọi kết luận hiệu lực ngoài những record này phải được coi là **chưa xác minh**, không phải xác nhận pháp lý.
