# Schema dữ liệu văn bản pháp luật

## 1. Mục đích

File này mô tả cấu trúc của các file:

```text
data/law/records/LAW_*.json
```

Đây là dữ liệu được tạo bởi `crawl/crawl_law.py` từ `vbpl.vn` hoặc
`thuvienphapluat.vn` (TVPL). Hai nguồn cùng dùng cấu trúc JSON này.
Mỗi file JSON biểu diễn một văn bản pháp luật, gồm:

```text
Văn bản pháp luật
├── Thông tin phân loại
├── Phạm vi áp dụng
├── Nguồn dữ liệu
├── Quan hệ với thủ tục/văn bản khác
└── Nội dung văn bản
    ├── Thông tin định danh văn bản
    ├── Toàn văn
    ├── Các section pháp lý
    └── File đính kèm
```

Schema này phục vụ ba mục đích:

1. Lưu trữ dữ liệu luật gốc sau khi crawl.
2. Chia văn bản thành các chunk để đưa vào Vector DB.
3. Tạo các node và relationship trong Knowledge Graph.

## 2. Cấu trúc JSON tổng quát

```json
{
  "id": "LAW_VBPL_xxx",
  "life_event": ["sinh_con"],
  "domain": "Pháp luật",
  "jurisdiction": {
    "level": "Toàn quốc",
    "location": "Việt Nam"
  },
  "source": {
    "name": "Cơ sở dữ liệu quốc gia về văn bản pháp luật",
    "url": "https://vbpl.vn/...",
    "crawled_at": "2026-09-12T11:45:30+00:00",
    "search_matches": [
      {"query": "thai sản", "rank": 1, "issued_date": "2025-08-07"}
    ]
  },
  "relations": {
    "related_laws": [],
    "related_procedures": []
  },
  "content": {
    "title": "Tên văn bản",
    "document_type": "Thông tư",
    "document_number": "21-LB/TT",
    "issuing_authority": "Cơ quan ban hành",
    "issued_date_raw": "18/06/1994",
    "issued_date": "1994-06-18",
    "effective_date_raw": "01/01/1994",
    "effective_date": "1994-01-01",
    "expired_date_raw": "",
    "validity_raw": "Còn hiệu lực",
    "validity_checked_at": "2026-11-20T00:00:00+00:00",
    "section_validation": {
      "is_lossless": true,
      "full_text_length": 5000,
      "reconstructed_length": 4980,
      "section_count": 24
    },
    "full_text": "Toàn văn...",
    "sections": [],
    "attachments": []
  }
}
```

## 3. Các trường ở cấp gốc

| Trường | Kiểu dữ liệu | Bắt buộc | Ý nghĩa |
|---|---|---:|---|
| `id` | String | Có | ID duy nhất của văn bản trong hệ thống. Ví dụ `LAW_VBPL_ac0469d50eadc418`. |
| `life_event` | Array[String] | Có | Sự kiện đời sống liên quan. Ví dụ `sinh_con`, `thuong_tru`. Có thể là mảng rỗng. |
| `domain` | String | Có | Nhóm lĩnh vực pháp luật. Hiện crawler mặc định là `Pháp luật`. |
| `jurisdiction` | Object | Có | Phạm vi địa lý/cấp áp dụng của dữ liệu. |
| `source` | Object | Có | Nguồn và thời điểm crawl. |
| `relations` | Object | Có | Quan hệ cấp văn bản với luật hoặc thủ tục khác. |
| `content` | Object | Có | Thông tin và nội dung chính của văn bản. |

### `id`

`crawl_law.py` tạo ID theo quy tắc:

- Với VBPL, ID dựa trên `ItemID`/`id` nếu có, hoặc một phần SHA-1 của URL và tiêu đề.
- Với TVPL, ID có dạng `LAW_TVPL_<mã-văn-bản>` theo số cuối URL chi tiết.

ID này nên được dùng làm khóa chính cho Knowledge Graph và làm tiền tố của
`chunk_id` trong Vector DB.

### `life_event`

Đây là nhãn phân loại để tìm kiếm nhanh, không phải nội dung pháp lý được trích
nguyên văn. Trong crawler hiện tại, nhãn `sinh_con` được gán khi toàn văn chứa
các từ khóa liên quan đến sinh con, thai sản, bảo hiểm y tế trẻ em, khai sinh...

Vì đây là kết quả phân loại bằng từ khóa, cần coi nó là dữ liệu suy luận và nên
kiểm duyệt khi dùng cho các câu trả lời quan trọng.

## 4. Object `jurisdiction`

```json
{
  "level": "Toàn quốc",
  "location": "Việt Nam"
}
```

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `level` | String | Cấp hoặc phạm vi áp dụng, ví dụ `Toàn quốc`, `Cấp tỉnh`, `Cấp xã`. |
| `location` | String | Địa phương cụ thể hoặc `Việt Nam`. |

Crawler VBPL hiện gán mặc định `Toàn quốc` và `Việt Nam`; đây là giá trị kỹ
thuật, không phải kết luận cuối cùng về phạm vi hiệu lực. Crawler TVPL ghi
`Chưa xác định` cho đến khi trích xuất được phạm vi áp dụng cụ thể.

## 5. Object `source`

```json
{
  "name": "Cơ sở dữ liệu quốc gia về văn bản pháp luật",
  "url": "https://vbpl.vn/...",
  "crawled_at": "2026-09-12T11:45:30.374333+00:00"
}
```

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `name` | String | Tên nguồn dữ liệu. |
| `url` | String | URL chính thức của văn bản để người dùng đối chiếu. |
| `crawled_at` | String | Thời điểm thu thập dữ liệu, định dạng ISO-8601 và múi giờ UTC. |
| `search_matches` | Array[Object] | Query VBPL đã chọn văn bản, thứ hạng theo từng query và ngày ban hành dùng xếp hạng. |

`crawled_at` là ngày hệ thống lấy dữ liệu, không phải ngày văn bản bắt đầu có
hiệu lực. Ngày hiệu lực nằm trong `content.effective_date_raw`.

## 6. Object `relations`

```json
{
  "related_laws": [],
  "related_procedures": []
}
```

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `related_laws` | Array | Các văn bản luật liên quan ở cấp văn bản. |
| `related_procedures` | Array | Các thủ tục hành chính liên quan. |

Hiện tại `crawl_law.py` khởi tạo hai mảng này rỗng. Các quan hệ văn bản được
phát hiện trong từng section nằm ở `content.sections[].related_laws`, không nằm
ở object này.

## 7. Object `content`

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `title` | String | Tên đầy đủ của văn bản. |
| `document_type` | String | Loại văn bản: Luật, Nghị định, Thông tư, Quyết định... Có thể rỗng nếu trang nguồn không trích xuất được. |
| `document_number` | String | Số hiệu văn bản, ví dụ `21-LB/TT`. |
| `issuing_authority` | String | Cơ quan ban hành. |
| `issued_date_raw` | String | Ngày ban hành ở dạng nguyên bản từ nguồn. |
| `issued_date` | String \| null | Ngày ban hành chuẩn `YYYY-MM-DD`, dùng để xếp hạng kết quả VBPL. |
| `effective_date_raw` | String | Ngày có hiệu lực ở dạng nguyên bản từ nguồn. |
| `effective_date` | String \| null | Ngày có hiệu lực chuẩn `YYYY-MM-DD`. |
| `expired_date_raw` | String | Ngày hết hiệu lực nếu nguồn cung cấp. |
| `validity_raw` | String | Tình trạng hiệu lực được hiển thị trên nguồn. |
| `validity_checked_at` | String | Thời điểm crawler đọc lại tình trạng hiệu lực từ VBPL. |
| `section_validation` | Object | Kết quả đối chiếu nội dung toàn văn với các section đã tách. Bản ghi VBPL không đạt kiểm tra sẽ không được lưu. |
| `full_text` | String | Nội dung đã làm sạch theo nguồn. VBPL giữ nội dung trích được; TVPL lưu phần điều khoản công khai, bỏ căn cứ, chữ ký, nơi nhận, phụ lục và biểu mẫu. |
| `sections` | Array[Object] | Các section được tách từ toàn văn. |
| `attachments` | Array[String] | URL của file PDF/DOC/DOCX hoặc file tải xuống. |

Với TVPL, metadata không được suy diễn khi website chỉ hiển thị “Đã biết”. Phạm
vi địa lý chưa xác định được ghi là `Chưa xác định`. Các record TVPL giữ
`source.name` là `Thư Viện Pháp Luật`; `source.url` là link văn bản chuẩn hóa.

### Về các trường ngày

Tên trường có hậu tố `_raw` vì dữ liệu hiện được giữ nguyên theo cách hiển thị
của website, ví dụ:

```text
01/01/1994
18 tháng 6 năm 1994
```

Khi lọc theo ngày trong Vector DB hoặc kiểm tra hiệu lực, nên tạo thêm các
trường chuẩn hóa ở pipeline tiếp theo, ví dụ:

```json
{
  "issued_date": "1994-06-18",
  "effective_date": "1994-01-01"
}
```

Không nên xóa các trường `_raw`, vì chúng là dữ liệu gốc để đối chiếu.

## 8. Object `content.sections[]`

Mỗi phần tử trong `sections` biểu diễn một đơn vị nội dung pháp lý được parser
tách ra.

```json
{
  "heading": "A. ĐỐI TƯỢNG THI HÀNH",
  "level": "part",
  "text": "Đối tượng áp dụng thi hành...",
  "related_laws": []
}
```

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `heading` | String | Tiêu đề của section, ví dụ `Điều 1`, `CHƯƠNG I`, `A. ĐỐI TƯỢNG...`. |
| `level` | String | Loại heading được nhận diện bởi parser. |
| `text` | String | Nội dung thuộc section đó. Có thể rỗng nếu section chỉ có tiêu đề. |
| `related_laws` | Array[Object] | Các văn bản được dẫn chiếu trong section. |

Các giá trị `level` hiện có:

```text
chapter
section
article
part
subsection
point
subpoint
```

`level` giữ cấu trúc tuần tự; bước chuẩn hóa tạo `parent_section_id` và
`structural_path` để lưu quan hệ cha-con. Parser nhận diện khoản đánh số hoặc
ghi rõ `Khoản`, điểm chữ cái hoặc ghi rõ `Điểm`, cùng các heading `Phần` và
`Tiểu mục` phổ biến.

Thứ tự và quan hệ cha-con được giữ ở dữ liệu chuẩn hóa; không suy ra heading bị
thiếu trong toàn văn:

```json
{
  "parent_section_id": "LAW_VBPL_xxx/article:12/subsection:1",
  "structural_path": "article:12/subsection:1/point:a"
}
```

## 9. Object `sections[].related_laws[]`

Ví dụ:

```json
{
  "document_type": "Thông tư",
  "document_number": "21/TT-LB",
  "issued_date_raw": "18 tháng 6 năm 1994",
  "relation_type": "dẫn_chiếu"
}
```

| Trường | Kiểu dữ liệu | Ý nghĩa |
|---|---|---|
| `document_type` | String | Loại văn bản được nhắc đến. |
| `document_number` | String | Số hiệu văn bản được nhắc đến. |
| `issued_date_raw` | String | Ngày ban hành nếu section có nêu. |
| `relation_type` | String | Loại quan hệ được parser suy đoán từ ngữ cảnh. |

Các `relation_type` hiện có thể gồm:

```text
dẫn_chiếu
căn_cứ
sửa_đổi_bổ_sung
thay_thế
bãi_bỏ
```

Đây mới là tham chiếu dạng text, chưa phải liên kết đến một record cụ thể. Để
tạo Knowledge Graph, cần chuẩn hóa thành khóa văn bản, ví dụ:

```text
Thông tư + 21/TT-LB
        ↓ chuẩn hóa
thong_tu:21/tt-lb
        ↓ đối chiếu record
LAW_VBPL_xxx
```

Nếu không tìm được record tương ứng, nên tạo node `UnresolvedLawReference`
hoặc đánh dấu quan hệ là `unresolved`, không tự động coi nó là một node luật
đã xác minh.

## 10. Dùng schema này cho Vector DB

Không nên embedding toàn bộ `full_text` thành một vector duy nhất. Mỗi phần tử
`content.sections[]` nên trở thành một hoặc nhiều chunk.

Ví dụ `chunk` từ section đang chọn:

```json
{
  "chunk_id": "LAW_VBPL_ac0469d50eadc418:section:000",
  "source_type": "law",
  "source_id": "LAW_VBPL_ac0469d50eadc418",
  "chunk_type": "section",
  "text": "Văn bản: ...\nMục: A. ĐỐI TƯỢNG THI HÀNH\nĐối tượng áp dụng thi hành...",
  "metadata": {
    "title": "...",
    "document_number": "...",
    "heading": "A. ĐỐI TƯỢNG THI HÀNH",
    "section_level": "part",
    "life_event": ["sinh_con"],
    "validity_raw": "Còn hiệu lực",
    "source_url": "https://vbpl.vn/..."
  }
}
```

Các metadata tối thiểu nên giữ:

```text
source_type
source_id
title
document_type
document_number
heading
section_level
life_event
domain
validity_raw
source_url
crawled_at
```

## 11. Dùng schema này cho Knowledge Graph

Có thể ánh xạ như sau:

| JSON | Knowledge Graph |
|---|---|
| Văn bản JSON | Node `LawDocument` |
| `content.sections[]` | Node `LawSection` |
| `content.sections[].related_laws[]` | Relationship `CITES`, `AMENDS`, `REPEALS` hoặc `RELATED_TO` |
| `life_event[]` | Relationship đến node `LifeEvent` |
| `jurisdiction` | Node/thuộc tính `Location` |
| `content.issuing_authority` | Node `Authority` |
| `relations.related_procedures[]` | Relationship đến node `Procedure` |
| `source.url` | Provenance của node hoặc relationship |

Ví dụ:

```text
(:LawDocument {id: "LAW_VBPL_ac0469d50eadc418"})
      -[:HAS_SECTION]->
(:LawSection {
  id: "LAW_VBPL_ac0469d50eadc418:section:000",
  heading: "A. ĐỐI TƯỢNG THI HÀNH"
})
```

Một quan hệ được tự động phát hiện nên có thêm thông tin kiểm soát:

```json
{
  "relation_type": "dẫn_chiếu",
  "confidence": 0.8,
  "created_by": "rule_parser",
  "review_status": "needs_review",
  "source_section": "LAW_VBPL_ac0469d50eadc418:section:000"
}
```

## 12. Quy tắc dữ liệu cần giữ

1. Không xóa `full_text`; đây là nội dung đã thu thập theo quy tắc của nguồn, dùng để kiểm tra lại chunk.
2. Không coi `validity_raw` là kết luận pháp lý tuyệt đối nếu chưa kiểm tra nguồn.
3. Không coi `related_laws` là quan hệ đã xác minh cho đến khi resolve được văn bản.
4. Giữ `source.url` trong mọi chunk để sinh citation.
5. Khi văn bản thay đổi, tạo lại các chunk có nội dung thay đổi và giữ hash phiên bản.
6. Không dùng `heading` làm ID duy nhất; hai section ở các văn bản khác nhau có thể trùng heading.

## 13. Phân biệt với dữ liệu thủ tục

`LAW_*.json` và `PROC_*.json` là hai schema khác nhau:

```text
PROC_*.json
  = người dân cần làm thủ tục gì và làm như thế nào

LAW_*.json
  = căn cứ pháp lý, điều kiện và quy định được dẫn chiếu
```

Hai schema có thể dùng chung Vector DB nhưng phải có `source_type` để phân biệt.
Trong Knowledge Graph, `Procedure` và `LawDocument` là hai loại node riêng,
được nối với nhau bằng quan hệ như `GROUNDED_IN` hoặc `CITES`.
