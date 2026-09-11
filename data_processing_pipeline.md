# Pipeline data
Official sources -> Crawl/Download -> Parse -> Clean -> Structured Data + Raw Documents -> Normalize -> Add Metadata -> Procedure Relations -> Chunk -> Embedding -> VectorDB + Knowledge Graph

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
| `description` | `String` | Tóm tắt mục đích của thủ tục hành chính. |
| `eligibility` | `String` | Điều kiện/tiêu chuẩn để thực hiện (VD: `Người có hộ khẩu thường trú...`). |
| `documents` | `Array of Strings` | Danh sách các loại giấy tờ cần chuẩn bị. |
| `forms` | `Array of Objects` | Chứa `name` và `url` của các biểu mẫu đi kèm (hỗ trợ tải file). |
| `steps` | `Array of Strings` | Trình tự các bước thực hiện. Giữ thứ tự 1-2-3 để tránh LLM sinh text lộn xộn. |
| `authority` | `String` | Cơ quan tiếp nhận và giải quyết (VD: `UBND cấp phường/xã`). |
| `processing_time` | `String` | Thời gian giải quyết hồ sơ (VD: `3 ngày làm việc`). |
| `fee` | `String` | Mức lệ phí phải nộp (VD: `Miễn phí` hoặc `100.000 VNĐ`). |
| `online_supported`| `Boolean` | Cờ đánh dấu thủ tục có hỗ trợ nộp trực tuyến hay không (`true`/`false`). |
| `online_portal_url`| `String` (Nullable)| Link dẫn thẳng đến trang nộp hồ sơ trực tuyến. |

## 3. Object `relations` (Mối quan hệ Knowledge Graph)
Phục vụ việc thiết lập đồ thị tri thức, giúp AI chủ động đề xuất lộ trình.

| Tên biến con | Định dạng | Ý nghĩa & Ví dụ |
| :--- | :--- | :--- |
| `prerequisites` | `Array of Strings` | Các `id` thủ tục bắt buộc phải hoàn thành trước (VD: `PROC_000_CCCD`). |
| `next_steps` | `Array of Strings` | Các `id` thủ tục nên làm tiếp theo (VD: `PROC_002_NHAP_KHAU`). |
| `related_benefits`| `Array of Strings` | Các `id` chính sách/quyền lợi liên quan (VD: `BEN_001_THAI_SAN`). |

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

## Ví dụ
```bash
{
  "id": "PROC_001",
  "life_event": ["sinh_con", "nhan_con_nuoi"],
  "target_audience": ["ca_nhan", "cong_dan_viet_nam"],
  
  "procedure": {
    "name": "Đăng ký khai sinh",
    "description": "Thủ tục cấp giấy khai sinh cho trẻ em mới sinh ra tại Việt Nam...",
    "eligibility": "Cha, mẹ, ông bà hoặc người thân thích...",
    "documents": [
      "Tờ khai đăng ký khai sinh (theo mẫu)",
      "Giấy chứng sinh do cơ sở y tế cấp"
    ],
    "forms": [
      {
        "name": "Tờ khai đăng ký khai sinh",
        "url": "https://dichvucong.gov.vn/.../to-khai-khai-sinh.docx"
      }
    ],
    "steps": [
      "Bước 1: Chuẩn bị hồ sơ...",
      "Bước 2: Nộp tại bộ phận Một cửa..."
    ],
    "authority": "UBND cấp xã/phường nơi cư trú của cha hoặc mẹ",
    "processing_time": "1 ngày làm việc (ngay trong ngày tiếp nhận)",
    "fee": "Miễn phí",
    "online_supported": true,
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