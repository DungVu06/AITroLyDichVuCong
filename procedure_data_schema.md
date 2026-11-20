# Schema Dữ liệu Thủ tục Hành chính (Procedures Data Schema)

## 1. Mục đích
Tài liệu này định nghĩa cấu trúc chuẩn của các bản ghi thủ tục hành chính (`PROC_*.json`) được lưu trữ tại:
```text
data/procedure/records/PROC_*.json
```
Dữ liệu được thu thập trực tiếp từ API Cổng Dịch vụ công Quốc gia (`dichvucong.gov.vn`) và phục vụ các mục đích:
1. **Lưu trữ chuẩn hóa**: Đảm bảo thông tin thủ tục chính xác nguyên bản, không lẫn mã rác HTML.
2. **Chunking & Vector DB (Qdrant)**: Chia nhỏ theo từng thành phần (yêu cầu điều kiện, hồ sơ giấy tờ, trình tự thực hiện, cách thức nộp phí) để Hybrid Search.
3. **Knowledge Graph (Neo4j)**: Xây dựng đồ thị tri thức với các quan hệ phụ thuộc giữa các thủ tục (`PREREQUISITE`, `NEXT_STEP`, `PART_OF`) và quan hệ căn cứ pháp luật / quyền lợi (`BASED_ON`, `RELATED_BENEFIT`).
4. **Quản lý hiệu lực & Phiên bản**: Đáp ứng kiểm chứng cập nhật khi quy định pháp luật hoặc quyết định công bố TTHC thay đổi.

---

## 2. Cấu trúc JSON Tổng quát

```json
{
  "id": "PROC_1_001193",
  "national_code": "1.001193",
  "life_event": ["sinh_con"],
  "target_audience": ["Công dân Việt Nam", "Người Việt Nam định cư ở nước ngoài"],
  "domain": "Hộ tịch",
  "procedure_type": "TTHC được luật giao quy định chi tiết",

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
      "PROC_1_014137"
    ],
    "part_of": [
      "PROC_3_000722"
    ],
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
| `procedure_type` | String | Không | Phân loại TTHC theo quy định (ví dụ: `TTHC được luật giao quy định chi tiết`). |

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

### 3.3. Object `relations` (Mối quan hệ Đồ thị Tri thức - Knowledge Graph)

| Tên trường con | Kiểu dữ liệu | Ý nghĩa & Mô hình hóa trong Graph |
| :--- | :--- | :--- |
| `legal_bases` | Array[Object] | **Căn cứ pháp lý hành chính**: Danh sách các văn bản luật làm cơ sở ban hành thủ tục. Mỗi item gồm `name` và `code` (VD: `{"code": "123/2015/NĐ-CP", "name": "Nghị định 123..."}`). Nối quan hệ `(Procedure)-[:BASED_ON]->(Law)`. |
| `prerequisites` | Array[String] | **Thủ tục điều kiện tiên quyết**: Danh sách `id` các thủ tục bắt buộc phải hoàn thành trước (VD: `PROC_1_001193`). Nối quan hệ `(Procedure)-[:PREREQUISITE]->(Procedure)`. |
| `next_steps` | Array[String] | **Thủ tục kế tiếp được đề xuất**: Danh sách `id` các thủ tục nên làm tiếp theo. Nối quan hệ `(Procedure)-[:NEXT_STEP]->(Procedure)`. |
| `part_of` | Array[String] | **Thủ tục liên thông cha**: `id` của thủ tục liên thông bao chứa thủ tục này (VD: trỏ về `PROC_3_000722`). Nối quan hệ `(Procedure)-[:PART_OF]->(Procedure)`. |
| `related_benefits` | Array[Object] | **Quyền lợi công dân được hưởng**: Trỏ đích danh tới từng Section của Luật quy định về chế độ trợ cấp, thai sản. Mỗi object gồm `law_section_id`, `scope` (`subtree`/`self`) và `note`. Nối quan hệ `(Procedure)-[:RELATED_BENEFIT]->(LawSection)`. |

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
| `version_control.state` | String | Trạng thái hiệu lực trên cổng: `ACTIVE` (đang có hiệu lực), `UPDATED` (đã cập nhật phiên bản mới). |
| `version_control.raw_id` | String | UUID nội bộ của thủ tục trên database Cổng DVCQG. |
