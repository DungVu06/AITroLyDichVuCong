# Định dạng dữ liệu Neo4j

Tài liệu này mô tả các loại node, thuộc tính của node và các relation được sử dụng trong graph. Các giá trị bên dưới chỉ là ví dụ minh họa; đây không phải là các câu lệnh truy vấn Neo4j.

## Quy ước kiểu dữ liệu

| Ký hiệu | Ý nghĩa |
|---|---|
| `string` | Chuỗi ký tự |
| `integer` | Số nguyên |
| `datetime` | Thời điểm theo ISO 8601 |
| `date` | Ngày theo định dạng `YYYY-MM-DD` |
| `string[]` | Danh sách chuỗi |

## Các loại node

### `LawDocument`

Đại diện cho một văn bản pháp luật.

| Thuộc tính | Kiểu | Mô tả |
|---|---|---|
| `id` | `string` | Mã định danh duy nhất |
| `title` | `string` | Tên văn bản |
| `document_type` | `string` | Loại văn bản |
| `document_number` | `string` | Số/ký hiệu văn bản |
| `issuing_authority` | `string` | Cơ quan ban hành |
| `issued_date_raw` | `string` | Ngày ban hành dạng gốc |
| `effective_date_raw` | `string` | Ngày có hiệu lực dạng gốc |
| `validity_raw` | `string` | Trạng thái hiệu lực dạng gốc |
| `life_events` | `string[]` | Các sự kiện đời sống liên quan |
| `domain` | `string` | Lĩnh vực |
| `jurisdiction_level` | `string` | Phạm vi/cấp áp dụng |
| `location` | `string` | Địa bàn áp dụng |
| `source_url` | `string` | URL nguồn |
| `crawled_at` | `datetime` | Thời điểm thu thập |

### `LawSection`

Node nội dung thuộc văn bản pháp luật: `LawSection`

| Thuộc tính | Kiểu | Mô tả |
|---|---|---|
| `id` | `string` | Mã định danh duy nhất |
| `law_id` | `string` | `id` của `LawDocument` chứa section |
| `order` | `integer` | Thứ tự trong văn bản |
| `heading` | `string` | Tiêu đề section |
| `level` | `string` | Cấp cấu trúc, ví dụ `article` |
| `text` | `string` | Nội dung văn bản |
| `marker` | `string` | Ký hiệu hiển thị, ví dụ `Điều 1` |
| `structural_path` | `string` | Đường dẫn cấu trúc |
| `section_label` | `string` | Loại section |

### `Procedure`

Đại diện cho một thủ tục hành chính/dịch vụ công.

| Thuộc tính | Kiểu | Mô tả |
|---|---|---|
| `id` | `string` | Mã định danh duy nhất |
| `national_code` | `string` | Mã thủ tục quốc gia |
| `name` | `string` | Tên thủ tục |
| `eligibility` | `string` | Đối tượng/điều kiện thực hiện |
| `domain` | `string` | Lĩnh vực |
| `procedure_type` | `string` | Loại thủ tục |
| `life_events` | `string[]` | Các sự kiện đời sống liên quan |
| `target_audience` | `string[]` | Đối tượng phục vụ |
| `authority` | `string` | Cơ quan có thẩm quyền |
| `jurisdiction_level` | `string` | Cấp thực hiện |
| `location` | `string` | Địa bàn áp dụng |
| `source_url` | `string` | URL nguồn |
| `source_name` | `string` | Tên nguồn |
| `effective_date` | `date` | Ngày có hiệu lực |
| `last_updated` | `date` | Ngày cập nhật gần nhất |

## Các loại relation

| Relation | Hướng | Node nguồn → node đích | Thuộc tính relation |
|---|---|---|---|
| `HAS_SECTION` | Văn bản → section (1 văn bản tới toàn bộ section) | `LawDocument → LawSection` | `order: integer` |
| `PARENT_SECTION` | Section con → section cha | `LawSection → LawSection` | Không có |
| `CITES` | Section dẫn chiếu → section được dẫn chiếu | `LawSection → LawSection` | `relation_type: string`, `referenced_location: string`, `source: string` |
| `REQUIRES` | Thủ tục → thủ tục được yêu cầu | `Procedure → Procedure` | Không có |
| `NEXT_STEP` | Thủ tục → thủ tục kế tiếp | `Procedure → Procedure` | Không có |
| `PART_OF` | Thủ tục con → thủ tục cha | `Procedure → Procedure` | Không có |
| `HAS_SUB_PROCEDURE` | Thủ tục cha → thủ tục con | `Procedure → Procedure` | Không có |
| `RELATED_TO_BENEFIT` | Thủ tục → quy định liên quan | `Procedure → LawSection` | `scope: string`, `source: string`, `note: string`, `benefit_id: string` |

## Ví dụ cấu trúc relation

```json
{
  "type": "CITES",
  "from": "LAW_VBPL_10089:section:0001",
  "to": "LAW_VBPL_10090:section:0003",
  "properties": {
    "relation_type": "dẫn_chiếu",
    "referenced_location": "Điều 3",
    "source": "parsed_section"
  }
}
```

```json
{
  "type": "RELATED_TO_BENEFIT",
  "from": "PROC_3_000722",
  "to": "LAW_VBPL_10089:section:0001",
  "properties": {
    "scope": "subtree",
    "source": "manual",
    "note": "Căn cứ quyền lợi đăng ký khai sinh",
    "benefit_id": "birth-registration"
  }
}
```
