# Định dạng chunk trong Qdrant

Mỗi dòng trong file `law_chunks.jsonl` hoặc `procedure_chunks.jsonl` là một chunk JSON độc lập. Chunk được embedding từ trường `page_content`; các thông tin còn lại nằm trong `metadata` và được lưu cùng vector dưới dạng payload.

## Cấu trúc chung

```json
{
  "page_content": "Nội dung văn bản dùng để embedding",
  "metadata": {
    "doc_id": "Mã tài liệu",
    "chunk_type": "Loại chunk",
    "chunk_id": "Mã chunk sau khi tách"
  }
}
```

| Trường | Kiểu | Mô tả |
|---|---|---|
| `page_content` | `string` | Nội dung văn bản được dùng để tạo vector |
| `metadata` | `object` | Metadata của tài liệu và chunk |
| `metadata.doc_id` | `string` | ID của văn bản pháp luật hoặc thủ tục |
| `metadata.chunk_id` | `string` | ID duy nhất của chunk sau khi tách |

## Chunk của Law

Mỗi `LawSection` có nội dung được dùng làm chunk gốc. Nếu quá dài, chunk được tách nhỏ hơn và có phần chồng lấn giữa các chunk.

### `page_content`

Nội dung thường gồm:

1. Tên văn bản pháp luật.
2. Loại văn bản, số hiệu và cơ quan ban hành.
3. Vị trí/tiêu đề của section.
4. Nội dung pháp lý của section.
5. Thông tin văn bản được dẫn chiếu, nếu có.

### Metadata

| Trường | Kiểu | Mô tả |
|---|---|---|
| `doc_id` | `string` | ID của `LawDocument` |
| `chunk_type` | `string` | Luôn là `section` |
| `life_event` | `string[]` | Sự kiện đời sống liên quan |
| `domain` | `string` | Lĩnh vực pháp luật |
| `section_index` | `integer` | Vị trí section trong văn bản |
| `heading` | `string` | Tiêu đề section |
| `section_level` | `string` | Cấp section, ví dụ `chapter`, `part`, `section`, `article` |
| `chunk_id` | `string` | ID chunk, dạng `{doc_id}_c{index}_s{sub_index}` |

Ví dụ:

```json
{
  "page_content": "Văn bản pháp luật: ...\n\nNội dung pháp lý:\n...",
  "metadata": {
    "doc_id": "LAW_VBPL_0cae53bb0a99d71f",
    "chunk_type": "section",
    "life_event": ["sinh_con"],
    "domain": "Pháp luật",
    "section_index": 0,
    "heading": "A. ĐỐI TƯỢNG ÁP DỤNG",
    "section_level": "part",
    "chunk_id": "LAW_VBPL_0cae53bb0a99d71f_c0_s0"
  }
}
```

## Chunk của Procedure

Một thủ tục có thể tạo ra nhiều chunk theo từng nhóm thông tin. Nội dung mỗi chunk luôn chứa tên và mã thủ tục để giữ ngữ cảnh khi tìm kiếm.

### Các loại chunk

| `chunk_type` | Nội dung |
|---|---|
| `document_item` | Một giấy tờ trong thành phần hồ sơ |
| `step_item` | Một bước trong trình tự thực hiện |
| `execution_methods` | Cách thức thực hiện, thời gian giải quyết và lệ phí |
| `note_item` | Một lưu ý khi thực hiện thủ tục |

### Metadata

| Trường | Kiểu | Mô tả |
|---|---|---|
| `doc_id` | `string` | ID của `Procedure` |
| `life_event` | `string[]` | Sự kiện đời sống liên quan |
| `domain` | `string` | Lĩnh vực thủ tục |
| `relations` | `object` | Các quan hệ với thủ tục hoặc quy định pháp luật khác |
| `chunk_type` | `string` | Loại nội dung của chunk |
| `chunk_id` | `string` | ID chunk sau khi tách |

`relations` có thể gồm các nhóm:

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `prerequisites` | `string[]` | Thủ tục điều kiện/tiền đề |
| `next_steps` | `string[]` | Các thủ tục tiếp theo |
| `part_of` | `string[]` | Thủ tục cha |
| `related_benefit` | `string[]` | Các section pháp luật liên quan |

Ví dụ:

```json
{
  "page_content": "Thành phần hồ sơ cần nộp để thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) bao gồm:\n- Văn bản ủy quyền...",
  "metadata": {
    "doc_id": "PROC_1_001193",
    "life_event": ["sinh_con"],
    "domain": "Hộ tịch",
    "relations": {
      "prerequisites": [],
      "next_steps": ["PROC_1_004222"],
      "part_of": ["PROC_3_000722"],
      "related_benefit": ["LAW_VBPL_ac0469d50eadc418/part:B/section:II"]
    },
    "chunk_type": "document_item",
    "chunk_id": "PROC_1_001193_c0_s0"
  }
}
```

## Lưu trữ trong Qdrant

Khi import, `page_content` được đổi tên thành payload `text`. Các trường trong `metadata` được đưa trực tiếp vào payload cùng với `text`.
