# Metadata
## 1. Metadata Root (Thông tin định danh & Phân loại)
Các trường nằm ở cấp cao nhất của object JSON, dùng để định danh và lọc thông tin nhanh trên VectorDB.

| Tên biến | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `id` | `String` | Mã định danh duy nhất của thủ tục (VD: `PROC_001`). Dùng làm khóa chính (primary key) trong Knowledge Graph. |
| `life_event` | `Array of Strings` | Danh sách sự kiện đời sống kích hoạt thủ tục (VD: `["sinh_con", "nhan_con_nuoi"]`). |
| `target_audience` | `Array of Strings` | Phân loại đối tượng áp dụng để AI lọc nhanh (VD: `["ca_nhan", "to_chuc"]`). |

## 2. Object `procedure` (Chi tiết thủ tục)
Chứa nội dung cốt lõi của thủ tục, là context chính để LLM sinh câu trả lời.

| Tên biến con | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `name` | `String` | Tên chính thức của thủ tục (VD: `Đăng ký khai sinh`). |
| `eligibility` | `String` | Yêu cầu, điều kiện thực hiện (VD: `Người có hộ khẩu thường trú...`). |
| `documents` | `Array of Dict` | Danh sách các loại giấy tờ cần chuẩn bị. |
| `steps` | `Array of Strings` | Trình tự các bước thực hiện. Giữ thứ tự 1-2-3 để tránh LLM sinh text lộn xộn. |
| `authority` | `String` | Cơ quan tiếp nhận và giải quyết (VD: `UBND cấp phường/xã`). |
| `execution_methods` | `Array of Dict` | Cách thức thực hiện
| `online_portal_url`| `String` (Nullable)| Link dẫn thẳng đến trang nộp hồ sơ trực tuyến. |

## 3. Object `relations` (Mối quan hệ Knowledge Graph)
Phục vụ việc thiết lập đồ thị tri thức, giúp AI chủ động đề xuất lộ trình.

| Tên biến con | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `prerequisites` | `Array of Strings` | Các `id` thủ tục bắt buộc phải hoàn thành trước (VD: `PROC_000_CCCD`). |
| `next_steps` | `Array of Strings` | Các `id` thủ tục nên làm tiếp theo (VD: `PROC_002_NHAP_KHAU`). |
| `sub_procedures`| `Array of Strings` | Các `id` thủ tục con |
| `part_of`| `Array of Strings` | Các `id` thủ tục cha |
| `related_benefits_laws`| `Array of Strings` | Các luật cho quyền lợi |

## 4. Object `jurisdiction` (Phạm vi áp dụng)
Quản lý phạm vi hiệu lực của thủ tục (phân biệt giữa các địa phương).

| Tên biến con | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `level` | `String` | Cấp độ quản lý (VD: `quoc_gia`, `tinh`, `huyen`, `xa`). |
| `location` | `String` | Tên địa phương cụ thể (VD: `Hà Nội`) hoặc `Toàn quốc`. |

## 5. Object `source` (Nguồn gốc & Độ tin cậy)
Trích dẫn nguồn và quản lý vòng đời dữ liệu để tránh thông tin hết hạn.

| Tên biến con | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `name` | `String` | Tên cổng thông tin hoặc văn bản pháp luật gốc. |
| `url` | `String` | Đường dẫn URL để người dân đối chiếu. |
| `effective_date` | `String` (Date) | Ngày thủ tục/văn bản bắt đầu có hiệu lực (Định dạng: `YYYY-MM-DD`). |
| `last_updated` | `String` (Date) | Ngày hệ thống cập nhật/crawl cuối cùng, dùng để trigger update. |

## Note
`effective_date` và `relations` lấy ở vbpl

## Ví dụ
```bash
{
  "id": "PROC_1_001193",
  "national_code": "1.001193"
  "life_event": ["Sinh con"],
  "target_audience": ["Công dân Việt Nam"],
  "domain": "Hộ tịch",
  "procedure_type": "TTHC được luật giao quy định chi tiết",
  "procedure": {
    "name": "Thủ tục đăng ký khai sinh",
    "eligibility": "Cha, mẹ, ông bà hoặc người thân thích...",
    "documents": [
      {
        "ten_giay_to": "Tờ khai đăng ký khai sinh",
        "so_luong": "01 Bản chính"
      },
      {
        "ten_giay_to": "Giấy chứng sinh do cơ sở y tế cấp",
        "so_luong": "01 Bản chính"
      }
    ],
    "steps": [
      "Bước 1: Chuẩn bị hồ sơ...",
      "Bước 2: Nộp tại bộ phận Một cửa..."
    ],
    "authority": "UBND cấp xã/phường nơi cư trú của cha hoặc mẹ",
    execution_methods: [
      {
          "method": "Trực tuyến",
          "processing_time": "1",
          "fee": "Miễn phí",
          "description": ""
      }
    ],
    "online_portal_url": "https://dichvucong.gov.vn/..."
  },

  "relations": {
    "prerequisites": [],
    "next_steps": [
      "PROC_002_NHAP_KHAU",
      "PROC_003_BHYT_TRE_EM"
    ],
    "related_benefits": [
      "BEN_001_THAI_SAN"
    ]
  },

  "jurisdiction": {
    "level": "cap_xa",
    "location": "Toàn quốc"
  },

  "source": {
    "name": "Cổng Dịch vụ công Quốc gia",
    "url": "https://dichvucong.gov.vn/...",
    "effective_date": "2020-09-01",
    "last_updated": "2024-01-15"
  }
}
```