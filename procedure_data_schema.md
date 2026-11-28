# Schema Dữ liệu Thủ tục Hành chính (Procedures Data Schema)

## 1. Mục đích

Tài liệu mô tả bản ghi thủ tục hành chính (`PROC_*.json`) và các file quan hệ được sinh từ bản ghi. Dữ liệu gốc trong dự án được thu thập từ Cổng Dịch vụ công Quốc gia.

| Đường dẫn | Vai trò |
| :--- | :--- |
| `data/procedure/records/PROC_*.json` | Bản ghi đầu vào của bước chuẩn hóa. |
| `data/procedure/normalized_records/PROC_*.json` | Bản ghi đã chuẩn hóa, dùng cho chunking, đối chiếu bằng chứng và lưu cạnh trong `relations.resolved_edges`. |
| Báo cáo JSON (khi dùng `--report <đường-dẫn>`) | Kết quả kiểm tra các cạnh, gồm cả các trường hợp cần rà soát. |

Dữ liệu phục vụ các mục đích sau.

1. **Lưu trữ chuẩn hóa**: Đảm bảo thông tin thủ tục chính xác nguyên bản, không lẫn mã rác HTML.
2. **Chunking & Vector DB (Qdrant)**: Chia nhỏ theo từng thành phần (yêu cầu điều kiện, hồ sơ giấy tờ, trình tự thực hiện, cách thức nộp phí) để Hybrid Search.
3. **Knowledge Graph (Neo4j và snapshot cục bộ)** dùng các cạnh `REQUIRES`, `NEXT_STEP`, `PART_OF` và `HAS_SUB_PROCEDURE` để tra cứu quan hệ giữa các thủ tục. Graph pháp luật và quyền lợi dùng dữ liệu liên kết riêng.
4. **Quản lý hiệu lực & Phiên bản**: Đáp ứng kiểm chứng cập nhật khi quy định pháp luật hoặc quyết định công bố TTHC thay đổi.

---

## 2. Cấu trúc bản ghi thủ tục

Ví dụ dưới đây minh họa bản ghi đầu vào. Các ID trong `relations` là tham chiếu để normalizer kiểm tra trước khi xuất cạnh.

```json
{
  "id": "PROC_1_001193",
  "national_code": "1.001193",
  "life_event": ["sinh_con"],
  "target_audience": ["Công dân Việt Nam", "Người Việt Nam định cư ở nước ngoài"],
  "domain": "Hộ tịch",
  "procedure_type": "ASSIGNED_REGULATION",

  "procedure": {
    "name": "Thủ tục đăng ký khai sinh",
    "eligibility": "Yêu cầu, điều kiện thực hiện...",
    "documents": [
      {
        "ten_giay_to": "Giấy chứng sinh do cơ sở y tế cấp",
        "so_luong": "1 Bản chính",
        "bat_buoc": true,
        "ma_giay_to": "000.00.00.G15-KQ003208"
      }
    ],
    "steps": [
      "Bước 1: Nộp hồ sơ trực tiếp tại UBND cấp xã hoặc trực tuyến trên Cổng DVCQG/VNeID...",
      "Bước 2: Cán bộ tiếp nhận kiểm tra tính hợp lệ và hẹn trả kết quả..."
    ],
    "authority": "Ủy ban nhân dân cấp xã",
    "execution_methods": [
      {
        "method": "Trực tuyến",
        "processing_time": "1 ngày làm việc",
        "fee": "Miễn phí",
        "description": "Nộp qua Cổng DVCQG hoặc ứng dụng VNeID"
      }
    ],
    "online_portal_url": "https://dichvucong.gov.vn/thu-tuc-hanh-chinh/019d2bfd-3fe0-70ac-b9d6-5e9e20d6eef7"
  },

  "relations": {
    "legal_bases": [
      {
        "name": "Nghị định số 123/2015/NĐ-CP quy định chi tiết một số điều của Luật Hộ tịch",
        "code": "123/2015/NĐ-CP"
      }
    ],
    "prerequisites": [],
    "next_steps": [
      "PROC_1_116788",
      "PROC_1_014137",
      "PROC_1_116410"
    ],
    "part_of": [
      "PROC_3_000722"
    ],
    "sub_procedures": [],
    "related_benefits": [
      {
        "law_section_id": "LAW_VBPL_0cae53bb0a99d71f/part:B/section:II",
        "scope": "subtree",
        "note": "Chế độ trợ cấp thai sản liên quan"
      }
    ]
  },

  "jurisdiction": {
    "level": "Cấp xã",
    "location": "Toàn quốc"
  },

  "source": {
    "name": "Cổng Dịch vụ công Quốc gia",
    "url": "https://dichvucong.gov.vn/thu-tuc-hanh-chinh/019d2bfd-3fe0-70ac-b9d6-5e9e20d6eef7",
    "effective_date": "2019-07-31",
    "last_updated": "2026-11-18"
  },

  "version_control": {
    "proposal_number": "QĐ/0001-BTP",
    "state": "UPDATED",
    "raw_id": "019d2bfd-3fe0-70ac-b9d6-5e9e20d6eef7"
  }
}
```

---

## 3. Chi tiết các trường dữ liệu

### 3.1. Metadata Root (Định danh & Lọc nhanh)

| Tên trường | Kiểu dữ liệu | Bắt buộc | Ý nghĩa & Quy ước |
| :--- | :--- | :---: | :--- |
| `id` | String | Có | Khóa chính duy nhất trong hệ thống & Knowledge Graph (`PROC_<national_code_thay_chấm_bằng_gạch_dưới>`), ví dụ: `PROC_1_001193`. |
| `national_code` | String | Có | Mã thủ tục quốc gia được cấp bởi Cổng DVCQG, ví dụ: `1.001193`, `1.116788`. |
| `life_event` | Array[String] | Có | Sự kiện đời sống kích hoạt thủ tục, ví dụ: `["sinh_con"]`, `["thuong_tru"]`. Dùng đồng bộ từ điển với schema Law. |
| `target_audience` | Array[String] | Có | Đối tượng thực hiện (ví dụ: `["Công dân Việt Nam"]`, `["Người nước ngoài"]`). |
| `domain` | String | Có | Lĩnh vực chuyên môn, ví dụ: `Hộ tịch`, `Đăng ký, quản lý cư trú`, `Bảo hiểm y tế`. |
| `procedure_type` | String | Không | Mã phân loại bản ghi lấy từ trường `formalityType` của nguồn. Trong bộ dữ liệu hiện tại, bốn bản ghi thủ tục riêng lẻ có `ASSIGNED_REGULATION`, còn gói liên thông `PROC_3_000722` có `OTHER`. Repo chưa có định nghĩa chính thức của API về các mã này. |
| `normalization_version` | String | Có trong bản chuẩn hóa | Phiên bản bộ chuẩn hóa ghi vào `normalized_records/`. Giá trị hiện tại là `procedure-normalize-v2`. |

---

### 3.2. Object `procedure` (Nội dung cốt lõi của thủ tục)

| Tên trường con | Kiểu dữ liệu | Bắt buộc | Ý nghĩa & Quy ước |
| :--- | :--- | :---: | :--- |
| `name` | String | Có | Tên chính thức của thủ tục (VD: `Thủ tục đăng ký khai sinh`). |
| `eligibility` | String | Có | Yêu cầu, điều kiện thực hiện của công dân. |
| `documents` | Array[Object] | Có | Danh sách thành phần hồ sơ giấy tờ cần chuẩn bị. |
| `steps` | Array[String] | Có | Trình tự các bước thực hiện tuần tự (Bước 1, Bước 2...). |
| `authority` | String | Có | Cơ quan giải quyết có thẩm quyền (VD: `Ủy ban nhân dân cấp xã`, `Công an Xã`, `Bảo hiểm xã hội tỉnh`). |
| `execution_methods` | Array[Object] | Có | Các hình thức nộp hồ sơ, kèm thời gian xử lý và mức phí tương ứng. |
| `online_portal_url` | String | Có | Đường dẫn trực tiếp đến cổng nộp hồ sơ. |

#### Chi tiết phần tử trong `documents`:
* `ten_giay_to` (String): Tên giấy tờ/mẫu đơn quy định.
* `so_luong` (String): Số lượng yêu cầu (VD: `1 Bản chính`, `1 Bản sao`, `Theo quy định`).
* `bat_buoc` (Boolean): `true` nếu là giấy tờ bắt buộc, `false` nếu là tùy chọn/theo trường hợp.
* `ma_giay_to` (String): Mã định danh biểu mẫu/kết quả quốc gia (VD: `000.00.00.G15-KQ003208`).

#### Chi tiết phần tử trong `execution_methods`:
* `method` (String): `Trực tuyến`, `Trực tiếp`, hoặc `Dịch vụ bưu chính`.
* `processing_time` (String): Thời hạn giải quyết (VD: `1 ngày làm việc`, `05 ngày làm việc`).
* `fee` (String): Phí/lệ phí phải nộp (VD: `Miễn phí` hoặc `115,000 VNĐ`).
* `description` (String): Hướng dẫn bổ sung về cách thức nộp hoặc điều kiện thời gian.

---

### 3.3. Object `relations` (Tham chiếu trong bản ghi)

Bốn mảng ID dưới đây chứa các tham chiếu đầu vào. Cạnh xuất ra có thể bổ sung quan hệ được xác nhận từ nội dung thủ tục hoặc đưa tham chiếu thiếu bằng chứng vào báo cáo. Xem [schema đầu ra](#4-schema-cạnh-đồ-thị-và-báo-cáo-rà-soát).

| Tên trường con | Kiểu dữ liệu | Ý nghĩa |
| :--- | :--- | :--- |
| `legal_bases` | Array[Object] | Căn cứ pháp lý được ghi trong bản thủ tục. Mỗi phần tử gồm `name` và `code`. |
| `prerequisites` | Array[String] | Mã thủ tục dự kiến làm trước. Cạnh `REQUIRES` đi từ thủ tục hiện tại đến thủ tục tiên quyết. |
| `next_steps` | Array[String] | Mã thủ tục dự kiến làm sau. Cạnh `NEXT_STEP` đi từ thủ tục hiện tại đến thủ tục tiếp theo. |
| `part_of` | Array[String] | Mã gói liên thông chứa thủ tục hiện tại. Cạnh `PART_OF` đi từ thủ tục thành phần đến gói. |
| `sub_procedures` | Array[String] | Mã thủ tục thành phần của gói. Cạnh `HAS_SUB_PROCEDURE` đi từ gói đến thủ tục thành phần. |
| `related_benefits` | Array[Object] | Tham chiếu quyền lợi đến mục văn bản pháp luật. Mỗi phần tử gồm `law_section_id`, `scope` (`subtree` hoặc `self`) và `note`. Importer đọc các cạnh `RELATED_TO_BENEFIT` từ file quan hệ quyền lợi riêng. |

---

### 3.4. Object `jurisdiction` (Phạm vi áp dụng)

| Tên trường con | Kiểu dữ liệu | Ý nghĩa |
| :--- | :--- | :--- |
| `level` | String | Cấp quản lý hành chính: `Cấp xã`, `Cấp huyện`, `Cấp tỉnh`, `Cấp Bộ` hoặc `Toàn quốc`. |
| `location` | String | Địa phương áp dụng: Tên tỉnh/thành phố cụ thể hoặc `Toàn quốc` (đối với thủ tục khung quốc gia). |

---

### 3.5. Object `source` & `version_control` (Nguồn gốc & Quản lý hiệu lực)

Phục vụ trực tiếp việc kiểm soát phiên bản và cảnh báo khi có cập nhật (Yêu cầu 2 của BTC):

| Tên trường con | Kiểu dữ liệu | Ý nghĩa |
| :--- | :--- | :--- |
| `source.name` | String | Tên cổng thông tin (`Cổng Dịch vụ công Quốc gia`). |
| `source.url` | String | URL nguồn để đối chiếu. |
| `source.effective_date`| String (Date) | Ngày văn bản/quyết định công bố bắt đầu có hiệu lực (`YYYY-MM-DD`). |
| `source.last_updated` | String (Date) | Ngày hệ thống crawler quét và cập nhật bản ghi (`YYYY-MM-DD`). |
| `version_control.proposal_number` | String | Số quyết định công bố TTHC của Bộ/Ngành (VD: `5860/QĐ-BCA-C06`, `QĐ/0001-BTP`). |
| `version_control.state` | String | Trạng thái bản ghi theo trường `state` của nguồn, ví dụ `ACTIVE` hoặc `UPDATED`. Crawler dùng `ACTIVE` làm mặc định khi phản hồi thiếu trường này. |
| `version_control.raw_id` | String | UUID nội bộ của thủ tục trên database Cổng DVCQG. |

Repo chưa có định nghĩa chính thức của API cho các giá trị này. Dữ liệu hiện có chưa đủ căn cứ để dùng riêng `state` kết luận hiệu lực pháp lý. Knowledge graph không dùng `state` để tạo cạnh hay xếp thứ tự thủ tục. RAG hiện dùng trường này làm giá trị dự phòng cho `source_metadata.validity` khi thiếu `validity_raw`. Trường này cũng nằm trong dữ liệu tính mã băm đối chiếu phiên bản.

---

## 4. Schema cạnh đồ thị và báo cáo rà soát

[Normalizer](db/graph/procedure_normalize.py) ghi các cạnh đã xác nhận vào `relations.resolved_edges` của bản ghi nguồn trong `normalized_records/`. Neo4j và snapshot cục bộ lấy `source_id` từ `id` của bản ghi chứa cạnh.

### 4.1. Cạnh trong `relations.resolved_edges`

| Trường | Kiểu dữ liệu | Khi có | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| `target_id` | String | Luôn có | ID thủ tục ở đích cạnh. |
| `relation_type` | String | Luôn có | Một trong `prerequisites`, `next_steps`, `part_of`, `sub_procedures`. Tên cạnh tương ứng trong Neo4j được liệt kê ở mục 3.3. |
| `resolution_status` | String | Luôn có | Mảng cạnh chỉ chứa giá trị `resolved`. |
| `workflow_id` | String | Cạnh đã xác nhận trong gói liên thông | ID của gói mà quan hệ áp dụng. |
| `evidence_record_id` | String | Cạnh đã xác nhận trong gói liên thông | ID bản ghi chứa bước làm bằng chứng. |
| `evidence_step` | Integer | Cạnh đã xác nhận trong gói liên thông | Vị trí đếm từ 1 trong mảng `procedure.steps` của bản ghi bằng chứng. Ví dụ, `5` trỏ đến `procedure.steps[4]`. |
| `condition` | String | Quan hệ có điều kiện | `identity_card_requested` nghĩa là người đại diện hợp pháp đề nghị cấp căn cước khi nộp hồ sơ liên thông trực tuyến. |
| `transferred_result` | String | Cạnh mô tả việc chuyển kết quả | Tên giấy tờ hoặc kết quả được hệ thống chuyển sang thủ tục tiếp theo. |

Ví dụ về cạnh **Thường trú → Căn cước** trong [bản chuẩn hóa của thủ tục thường trú](data/procedure/normalized_records/PROC_1_116788.json). Bằng chứng nằm ở Bước 5 của [bản chuẩn hóa gói liên thông](data/procedure/normalized_records/PROC_3_000722.json).

```json
{
  "target_id": "PROC_1_116410",
  "relation_type": "next_steps",
  "resolution_status": "resolved",
  "workflow_id": "PROC_3_000722",
  "evidence_record_id": "PROC_3_000722",
  "evidence_step": 5,
  "condition": "identity_card_requested",
  "transferred_result": "Thông báo kết quả đăng ký thường trú"
}
```

Trong ca Sinh con, Bước 4 mô tả việc hệ thống chuyển Giấy khai sinh điện tử sang hai nhánh thường trú và BHYT. Bước 5 mô tả việc hệ thống chuyển kết quả thường trú để xử lý nhánh căn cước khi có đề nghị. Phạm vi của các cạnh này là gói `PROC_3_000722`.

### 4.2. Báo cáo rà soát tùy chọn

Báo cáo dùng cùng các trường của cạnh và ghi thêm `source_id`. Mục cần rà soát có thêm `reason`. Xuất báo cáo bằng lệnh sau.

```powershell
python db/graph/procedure_normalize.py --report data/procedure/normalized_relation_report.json
```

| `resolution_status` | Ý nghĩa |
| :--- | :--- |
| `resolved` | Cạnh được ghi vào `relations.resolved_edges` của bản ghi nguồn. |
| `unresolved` | Thiếu bản ghi cho ID ở đầu hoặc đích của cạnh. |
| `unverified` | Bản ghi chưa đủ bằng chứng cho quan hệ hoặc phạm vi áp dụng. |
| `duplicate` | Trùng tổ hợp `source_id`, `target_id` và `relation_type`. |

Ví dụ về tham chiếu **Khai sinh → Căn cước** khi xuất báo cáo.

```json
{
  "source_id": "PROC_1_001193",
  "target_id": "PROC_1_116410",
  "relation_type": "next_steps",
  "resolution_status": "unverified",
  "reason": "Bản ghi chưa xác nhận quan hệ này trong phạm vi áp dụng."
}
```
