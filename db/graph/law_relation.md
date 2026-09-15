# Cấu trúc graph pháp luật trong Neo4j

Tài liệu này chỉ mô tả phần dữ liệu **pháp luật** trong graph: văn bản pháp
luật, các section thuộc văn bản và quan hệ dẫn chiếu giữa các section.

## 1. Luồng dữ liệu

```text
data/law/records/LAW_*.json
        │
        │ graph/law_normalize.py
        ▼
data/law/normalized_records/LAW_*.json ──► Neo4j

Mọi related_laws ──► data/law/normalized_relation_report.json
Chỉ related_laws có resolved_section ──► data/law/law_relations.json ──► Neo4j
```

`law_normalize.py` chuẩn hóa ID của section, xác định văn bản/section được
dẫn chiếu và ghi trạng thái xử lý của từng tham chiếu.

Hai file quan hệ có mục đích khác nhau:

| File | Nội dung |
|---|---|
| `data/law/normalized_relation_report.json` | Toàn bộ tham chiếu: đã resolve, resolve được document nhưng thiếu vị trí section, chưa resolve hoặc ambiguous. |
| `data/law/law_relations.json` | Chỉ các quan hệ đã resolve đầy đủ tới section (`resolution_status = "resolved_section"`), dùng để import cạnh `CITES`. |

Tham chiếu chưa resolve không bị mất: chúng vẫn được lưu trong report JSON,
nhưng hiện chưa tạo node tạm hoặc relationship trong Neo4j.

## 2. Các node

Graph pháp luật có hai loại node chính.

### 2.1. `LawDocument` — văn bản pháp luật

Mỗi file `LAW_*.json` tương ứng với một node `(:LawDocument)`. Node đại diện
cho toàn bộ một văn bản, không phải một điều hoặc khoản riêng lẻ.

| Property | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | String | ID duy nhất của văn bản, lấy từ `record.id`, ví dụ `LAW_VBPL_...`. |
| `title` | String | Tên văn bản. |
| `document_type` | String | Loại văn bản, ví dụ Luật, Nghị định, Thông tư. |
| `document_number` | String | Số hiệu văn bản. |
| `issuing_authority` | String | Cơ quan ban hành. |
| `issued_date_raw` | String | Ngày ban hành theo dữ liệu nguồn. |
| `effective_date_raw` | String | Ngày có hiệu lực theo dữ liệu nguồn. |
| `validity_raw` | String | Trạng thái hiệu lực hiển thị từ nguồn. |
| `life_events` | List[String] | Các sự kiện đời sống liên quan, nếu có. |
| `domain` | String | Lĩnh vực pháp luật. |
| `jurisdiction_level` | String | Cấp/phạm vi áp dụng. |
| `location` | String | Địa phương hoặc phạm vi áp dụng. |
| `source_url` | String | URL của nguồn chính thức. |
| `crawled_at` | String | Thời điểm thu thập dữ liệu. |

`id` là khóa định danh của node. Không dùng `title` hoặc
`document_number` làm khóa duy nhất vì các trường này có thể trùng hoặc thay
đổi cách biểu diễn.

`validity_raw` chỉ phản ánh thông tin tại thời điểm crawl; không nên dùng riêng
trường này để kết luận văn bản hiện còn hiệu lực.

Ví dụ:

```cypher
(:LawDocument {
  id: "LAW_VBPL_28f00c3d57bed5dd",
  title: "Thông tư số 18/2019/TT-BLĐTBXH...",
  document_number: "18/2019/TT-BLĐTBXH",
  issuing_authority: "Bộ Lao động - Thương binh và Xã hội"
})
```

### 2.2. `LawSection` — phần nội dung của văn bản

Mỗi phần tử trong `content.sections[]` được import thành một node có label nền
`(:LawSection)`. Section có thể là chương, phần, mục, điều, khoản hoặc điểm.

| Property | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | String | ID duy nhất, có cấu trúc phân cấp và bắt đầu bằng `law_id`. |
| `law_id` | String | ID của `LawDocument` chứa section. |
| `order` | Integer | Vị trí của section trong văn bản. |
| `heading` | String | Tiêu đề hoặc heading của section. |
| `level` | String | Cấp section: `chapter`, `part`, `section`, `article`, `subsection`, `point`. |
| `marker` | String | Ký hiệu cấp, ví dụ `I`, `A`, `3`, `b`. |
| `structural_path` | String | Đường dẫn phân cấp, không gồm `law_id`. |
| `text` | String | Nội dung pháp lý của section. |

Các label chuyên biệt dưới đây được gắn thêm trên cùng node `LawSection`; đây
không phải các loại node tách biệt:

| `level` | Label thêm |
|---|---|
| `chapter` | `LawChapter` |
| `part` | `LawPart` |
| `section` | `LawSectionGroup` |
| `article` | `LawArticle` |
| `subsection` | `LawSubsection` |
| `point` | `LawPoint` |

### 2.3. Cách tạo ID và cây section

ID section được tạo từ ID văn bản và các cấp cha:

```text
LAW_VBPL_xxx/article:3/subsection:2/point:b
```

Thứ tự cấp dùng để dựng cây:

| Cấp | Ví dụ heading | Ví dụ đoạn ID |
|---|---|---|
| `chapter` | `CHƯƠNG I` | `/chapter:I` |
| `part` | `A. ĐỐI TƯỢNG ÁP DỤNG` | `/part:A` |
| `section` | `MỤC II` hoặc `II.` | `/section:II` |
| `article` | `Điều 3` | `/article:3` |
| `subsection` | `1.` hoặc `Khoản 1` | `/subsection:1` |
| `point` | `a)` hoặc `Điểm a` | `/point:a` |

Nếu cùng một đường dẫn xuất hiện nhiều lần, normalizer thêm hậu tố như `~2`,
`~3` để không ghi đè section.

Quan hệ cha-con được lưu bằng `PARENT_SECTION`; `parent_section_id` là dữ liệu
trung gian dùng khi import và không phải property được ghi vào node
`LawSection`.

## 3. Các relationship

### 3.1. `HAS_SECTION`: văn bản chứa section

```text
(:LawDocument)-[:HAS_SECTION {order: 3}]->(:LawSection)
```

Một `LawDocument` có thể có nhiều section. `order` trên relationship là vị
trí của section trong văn bản.

### 3.2. `PARENT_SECTION`: section con thuộc section cha

```text
(:LawSection)-[:PARENT_SECTION]->(:LawSection)
```

Chiều của cạnh là **section con → section cha**.

Ví dụ:

```text
Điểm a ──PARENT_SECTION──► Khoản 1
Khoản 1 ──PARENT_SECTION──► Điều 3
```

Quan hệ này tạo cây cấu trúc nội bộ của từng văn bản. Các section cùng cấp
không trỏ vào nhau.

### 3.3. `CITES`: section dẫn chiếu section khác

```text
(:LawSection)-[:CITES]->(:LawSection)
```

Chiều của cạnh là **section nguồn → section được dẫn chiếu**. Cạnh chỉ được
import khi cả hai đầu mút đều là section đã xác định, tức là relation có:

```text
resolution_status = "resolved_section"
```

Các property hiện được lưu trên `CITES`:

| Property | Ý nghĩa |
|---|---|
| `relation_type` | Loại quan hệ lấy từ dữ liệu nguồn, thường là `dẫn_chiếu`. |
| `referenced_location` | Vị trí được nhắc tới trong văn bản nguồn, ví dụ `Điều 3` hoặc `điểm b Khoản 2 Điều 3`. |
| `source` | Nguồn tạo cạnh, hiện là `parsed_section`. |

Ví dụ:

```cypher
(:LawSection {id: "LAW_VBPL_a/article:1"})
-[:CITES {
  relation_type: "dẫn_chiếu",
  referenced_location: "Điều 3",
  source: "parsed_section"
}]->
(:LawSection {id: "LAW_VBPL_b/article:3"})
```

Hiện tại graph chỉ có relationship type `CITES` cho quan hệ dẫn chiếu. Các
loại `BASED_ON`, `AMENDS`, `REPLACES` chưa được tạo thành relationship type
riêng trong importer; nếu dữ liệu nguồn có loại khác, loại đó vẫn được giữ ở
property `relation_type` của cạnh `CITES` khi relation đã resolve tới section.

## 4. Trạng thái resolve của tham chiếu

Mỗi phần tử trong `related_laws[]` được ghi thành một dòng trong
`data/law/normalized_relation_report.json`. Trường `resolution_status` cho
biết mức độ xác định của tham chiếu:

| Trạng thái | Ý nghĩa | Import vào graph |
|---|---|---|
| `resolved_section` | Xác định được văn bản đích và một hoặc nhiều section đích. | Tạo một hoặc nhiều cạnh `CITES`. |
| `document_resolved_location_missing` | Xác định được văn bản đích nhưng thiếu hoặc chưa khớp vị trí section. | Không tạo cạnh. |
| `unresolved_document` | Chưa xác định được văn bản đích. | Không tạo cạnh. |
| `ambiguous_document` | Có nhiều văn bản có thể là văn bản đích, chưa chọn được một văn bản. | Không tạo cạnh. |

Một tham chiếu có nhiều section đích được tách thành nhiều cạnh `CITES`, mỗi
cạnh có một `target_section_id` trong `law_relations.json`.

Tóm lại:

```text
resolved_section
    └── law_relations.json ──► Neo4j (:LawSection)-[:CITES]->(:LawSection)

mọi trạng thái
    └── normalized_relation_report.json
```

## 5. Một số truy vấn kiểm tra

Đếm số node và relationship pháp luật:

```cypher
MATCH (n:LawDocument) RETURN count(n) AS law_documents;
MATCH (n:LawSection) RETURN count(n) AS law_sections;
MATCH ()-[r:HAS_SECTION]->() RETURN count(r) AS has_section_edges;
MATCH ()-[r:PARENT_SECTION]->() RETURN count(r) AS parent_section_edges;
MATCH ()-[r:CITES]->() RETURN count(r) AS cites_edges;
```

Xem các section của một văn bản:

```cypher
MATCH (law:LawDocument {id: "LAW_VBPL_xxx"})
      -[r:HAS_SECTION]->(section:LawSection)
RETURN section.id, section.order, section.heading, section.level, section.text
ORDER BY r.order;
```

Xem các section mà một section dẫn chiếu:

```cypher
MATCH (source:LawSection {id: "LAW_VBPL_xxx/article:1"})
      -[r:CITES]->(target:LawSection)
RETURN target.id, target.heading, r.referenced_location, r.relation_type;
```

## 6. Constraint và index

Các câu lệnh cơ bản đang dùng:

```cypher
CREATE CONSTRAINT law_document_id_unique IF NOT EXISTS
FOR (n:LawDocument) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT law_section_id_unique IF NOT EXISTS
FOR (n:LawSection) REQUIRE n.id IS UNIQUE;

CREATE INDEX law_document_number_index IF NOT EXISTS
FOR (n:LawDocument) ON (n.document_number);
```

Các node và relationship được import bằng `MERGE`, vì vậy có thể chạy lại
quy trình import mà không tạo bản sao theo cùng ID.
