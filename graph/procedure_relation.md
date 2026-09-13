# Cấu trúc graph thủ tục trong Neo4j

Tài liệu này mô tả phần dữ liệu **thủ tục hành chính** trong graph: các thủ tục và quan hệ dẫn chiếu giữa chúng.

## 1. Luồng dữ liệu

```text
data/procedure/records/PROC_*.json
        │
        │ graph/procedure_normalize.py
        ▼
data/procedure/normalized_records/PROC_*.json ──► Neo4j

Mọi relations ──► data/procedure/normalized_relation_report.json
Chỉ relations có resolved ──► data/procedure/procedure_relations.json ──► Neo4j
```

`procedure_normalize.py` chuẩn hóa ID của thủ tục, làm sạch văn bản và xác định các thủ tục liên quan, ghi trạng thái xử lý của từng tham chiếu.

Hai file quan hệ có mục đích khác nhau:

| File | Nội dung |
|---|---|
| `data/procedure/normalized_relation_report.json` | Toàn bộ tham chiếu: đã resolve (tồn tại trong database) hoặc chưa resolve (chưa thu thập được). |
| `data/procedure/procedure_relations.json` | Chỉ các quan hệ đã resolve đầy đủ tới thủ tục (`resolution_status = "resolved"`), dùng để import cạnh tương ứng. |

Tham chiếu chưa resolve không bị mất: chúng vẫn được lưu trong report JSON, nhưng hiện chưa tạo node tạm hoặc relationship trong Neo4j.

## 2. Các node

Graph thủ tục chủ yếu có node `Procedure`.

### 2.1. `Procedure` — Thủ tục hành chính

Mỗi file `PROC_*.json` tương ứng với một node `(:Procedure)`. Node đại diện cho toàn bộ một thủ tục hành chính.

| Property | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | String | ID duy nhất của thủ tục, ví dụ `PROC_1_001193`. |
| `national_code` | String | Mã thủ tục quốc gia. |
| `name` | String | Tên chính thức của thủ tục. |
| `procedure_type` | String | Loại thủ tục hành chính. |
| `domain` | String | Lĩnh vực thủ tục (VD: Hộ tịch). |
| `eligibility` | String | Yêu cầu, điều kiện thực hiện. |
| `authority` | String | Cơ quan tiếp nhận và giải quyết. |
| `life_events` | List[String] | Các sự kiện đời sống liên quan. |
| `target_audience` | List[String] | Đối tượng áp dụng (VD: Cá nhân, Tổ chức). |
| `jurisdiction_level` | String | Cấp quản lý giải quyết (VD: Cấp xã). |
| `location` | String | Địa phương áp dụng (VD: Toàn quốc). |
| `source_url` | String | URL tới cổng dịch vụ công quốc gia. |

Ví dụ:

```cypher
(:Procedure {
  id: "PROC_1_001193",
  name: "Thủ tục đăng ký khai sinh",
  national_code: "1.001193",
  authority: "UBND cấp xã"
})
```

(Các dữ liệu chi tiết như `steps`, `documents`, `execution_methods` thường được xử lý trong vector database thay vì node graph để tránh quá tải kích thước node, tuỳ kiến trúc lưu trữ thực tế).

## 3. Các relationship

Các thủ tục có thể dẫn chiếu, phụ thuộc hoặc bao hàm lẫn nhau thông qua các cạnh trong block `relations`. Chiều của cạnh luôn là **Thủ tục nguồn → Thủ tục đích**.

Các loại relationship có thể được tạo (tương ứng với các mảng trong `relations`):

### 3.1. `REQUIRES` (từ `prerequisites`)

```text
(:Procedure)-[:REQUIRES]->(:Procedure)
```
Thủ tục nguồn yêu cầu thủ tục đích phải được hoàn thành trước (điều kiện tiên quyết).

### 3.2. `NEXT_STEP` (từ `next_steps`)

```text
(:Procedure)-[:NEXT_STEP]->(:Procedure)
```
Thủ tục đích là bước tiếp theo logic, hoặc được khuyến nghị thực hiện sau khi hoàn thành thủ tục nguồn.

### 3.3. `PART_OF` (từ `part_of`)

```text
(:Procedure)-[:PART_OF]->(:Procedure)
```
Thủ tục nguồn là một phần con (thủ tục thành phần) thuộc thủ tục đích lớn hơn (thủ tục cha).

### 3.4. `HAS_SUB_PROCEDURE` (từ `sub_procedures`)

```text
(:Procedure)-[:HAS_SUB_PROCEDURE]->(:Procedure)
```
Thủ tục nguồn chứa thủ tục đích như một thủ tục thành phần. (Đây là chiều ngược lại của `PART_OF`).

### 3.5. `RELATES_TO_BENEFIT` (từ `related_benefits`)

```text
(:Procedure)-[:RELATES_TO_BENEFIT]->(:Benefit)
```
Thủ tục này liên quan đến việc giải quyết hoặc hưởng một chính sách trợ cấp/phúc lợi `Benefit` (VD: `BEN_001_THAI_SAN`). 

## 4. Trạng thái resolve của tham chiếu

Mỗi phần tử trong các mảng của `relations` được ghi thành một dòng trong `data/procedure/normalized_relation_report.json`. Trường `resolution_status` cho biết mức độ xác định của tham chiếu:

| Trạng thái | Ý nghĩa | Import vào graph |
|---|---|---|
| `resolved` | Xác định được ID đích tồn tại trong database (hoặc là ID `BEN_`). | Tạo cạnh tương ứng. |
| `unresolved` | ID đích chưa có trong danh sách thủ tục đã crawl. | Không tạo cạnh. |

## 5. Một số truy vấn kiểm tra

Đếm số node và relationship thủ tục:

```cypher
MATCH (n:Procedure) RETURN count(n) AS procedures;
MATCH ()-[r:REQUIRES]->() RETURN count(r) AS requires_edges;
MATCH ()-[r:NEXT_STEP]->() RETURN count(r) AS next_step_edges;
```

Tìm các bước tiếp theo sau một thủ tục:

```cypher
MATCH (p1:Procedure {id: "PROC_1_001193"})-[:NEXT_STEP]->(p2:Procedure)
RETURN p2.id, p2.name;
```

## 6. Constraint và index

Các câu lệnh cơ bản đang dùng:

```cypher
CREATE CONSTRAINT procedure_id_unique IF NOT EXISTS
FOR (n:Procedure) REQUIRE n.id IS UNIQUE;

CREATE INDEX procedure_national_code_index IF NOT EXISTS
FOR (n:Procedure) ON (n.national_code);
```
