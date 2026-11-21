# Yorha — trợ lý thủ tục hành chính có kiểm chứng nguồn

Yorha là demo RAG tiếng Việt cho sự kiện **sinh con**. Mục tiêu không chỉ là để
LLM trả lời, mà biến tình huống người dân kể thành hành trình thủ tục có evidence,
quan hệ phụ thuộc, trích dẫn và hậu kiểm.

Ví dụ, câu “con chưa khai sinh có làm BHYT trước được không?” phải được trả lời
từ quan hệ `REQUIRES`, evidence của thủ tục khai sinh/BHYT và chunk về thời hạn;
không dùng kiến thức nền không được kiểm chứng của model.

## Phạm vi

- Dataset demo: 5 thủ tục liên quan sinh con, 4 văn bản luật và graph relation.
- Ứng dụng hướng dẫn, không nộp hồ sơ hay xác thực thay người dân.
- Nguồn pháp lý **không tự crawl**. Khi có đợt cập nhật, người quản lý sửa/import
  data; runtime so phiên bản với baseline rồi gắn review/cảnh báo.
- Citation thể hiện evidence trong dataset tại thời điểm ghi nhận, không thay thế
  xác nhận của cơ quan có thẩm quyền.

## Kiến trúc

```text
Người dùng → Streamlit → RAGEngine
                           ├─ Gemini: hiểu query, diễn đạt, repair khi cần
                           ├─ Qdrant: semantic chunks
                           ├─ Neo4j: procedure/legal relations
                           └─ Python: routing, contract, validation, fallback
```

| Thành phần | Vai trò |
| --- | --- |
| `ui/streamlit_app.py` | Chat UI, warning, nguồn, căn cứ pháp lý, phiên chat mới. |
| `rag/engine.py` | Orchestrator, local fallback, validation order và transcript. |
| Gemini | Hiểu ngôn ngữ, tạo answer draft, repair tối đa một lần. |
| Qdrant | Chunk thủ tục/văn bản cho semantic retrieval. |
| Neo4j | `REQUIRES`, `NEXT_STEP`, `PART_OF`, `HAS_SUB_PROCEDURE`, benefit relations. |
| Pydantic | Schema biên giới pipeline và JSON output của LLM. |

Embedding dùng `keepitreal/vietnamese-sbert` (768 chiều) trong process Python.
LLM không tự quyết route, thứ tự phụ thuộc, source ID hoặc validation verdict.

## Pipeline runtime

Backbone vẫn là 13 chặng; các chặng mới/củng cố giải quyết việc LLM và semantic
retrieval có thể làm rơi evidence quan trọng.

1. **Preprocess** — chuẩn hóa input thành `PreprocessedQuery`.
2. **Query understanding** — Gemini tạo `QueryState`: intent, topics, facts,
   procedure IDs, dữ kiện thiếu.
3. **Conversation merge** — hợp nhất facts và pending question từ lượt trước.
4. **Routing** — Python tạo `RetrievalPlan`, không gọi thêm LLM.
5. **Answer contract** — Python nhận diện tình huống có claim rủi ro từ facts
   rõ ràng và quy định procedure/chunk/relation/step phải có evidence.
6. **Vector retrieval** — Qdrant semantic search; lỗi network/404 collection sẽ
   chuyển sang local index từ `data/chunks/`.
7. **Graph retrieval** — Neo4j mở rộng procedure/legal relation; lỗi network/DNS
   sẽ chuyển sang snapshot graph local.
8. **Authority selection** — contract đã resolve procedure sẽ chặn procedure phụ
   do LLM đoán chỉ vì một tên giấy tờ có trong câu hỏi.
9. **Journey + detail** — tính priority và lấy document/step/execution chunks;
   contract evidence luôn được giữ trước ranking thông thường.
10. **Step sequence** — khi người dùng hỏi quy trình/trình tự, giữ tối thiểu một
    chunk cho mỗi `step_number`; validator buộc answer trích đủ các bước.
11. **Context + version metadata** — compact evidence và ghép scope, effective
    date, observed version, legal bases/review thành `AnswerContext`.
12. **Generate/validate/repair** — Gemini answer → Python validation → Python
    repair → Gemini repair một lần → fallback evidence-only nếu vẫn không đạt.
13. **Delivery** — UI chỉ hiện cited source; transcript tự lưu theo conversation.

Xem [debug_request1.md](debug_request1.md) để đọc audit năm use case và kiến
trúc kiểm chứng chi tiết.

## Version, hiệu lực và căn cứ pháp lý

`rag/retrieval/catalog.py` tạo `SourceMetadata` từ normalized records và mốc
`rag/retrieval/source_versions.json`.

- Metadata: URL, phạm vi, ngày hiệu lực, ngày ghi nhận, hash phiên bản, validity
  và legal bases.
- Record khác baseline, law hết hiệu lực/chưa xác minh sẽ gắn `review`.
- Review law lan tới procedure tham chiếu law đó; UI hiển thị trong **Căn cứ pháp
  lý của thủ tục**. Answer đưa warning khi review nói nguồn đổi phiên bản/hết
  hiệu lực.
- Đây là kiểm soát sau khi quản trị viên cập nhật data, không là tự động update
  qua internet.

## Cài đặt

Chạy trong PowerShell tại root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền `.env`:

| Biến | Mục đích |
| --- | --- |
| `GEMINI_API_KEY` | Gemini cho query understanding, answer và repair. |
| `GEMINI_QUERY_MODEL` | Model Gemini; mặc định `gemini-3.5-flash-lite`. |
| `QDRANT_URL`, `QDRANT_API_KEY` | Qdrant Cloud có collections `procedures`, `laws`. |
| `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` | Neo4j Aura/graph. |
| `EMBEDDING_MODEL` | Phải trùng embedding model dùng lúc import Qdrant. |

Runtime tự dùng CA bundle của `certifi` nếu `SSL_CERT_FILE` chưa được đặt. Không
cần thêm biến đó vào `.env` chỉ để chạy trên Windows.

### Chạy UI

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py
```

### Chạy CLI

```powershell
.\.venv\Scripts\python.exe -m rag "Khai sinh cần giấy tờ gì?"
.\.venv\Scripts\python.exe -m rag "Tôi vừa sinh con" --interactive
.\.venv\Scripts\python.exe -m rag "Khai sinh cần giấy tờ gì?" --json
```

Một lượt thông thường có 2 Gemini API calls: query understanding và answer.
Nếu validation cần repair, có thêm tối đa 1 Gemini call.

### Chạy test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/rag -v
```

Test không gọi Gemini; kiểm tra contract của 5 tình huống, validator, transcript,
version impact, conversation state và local graph/vector fallback.

## Rebuild database

Người dùng demo chỉ cần `.env` hợp lệ rồi chạy UI. Khi dựng database mới, import
cả graph và vector trước:

```powershell
.\.venv\Scripts\python.exe db/graph/neo4j_import.py --related-benefit-relations data/benefit_relation/related_benefit_relations.json
.\.venv\Scripts\python.exe db/vector/setup_qdrant_db.py
```

Thiếu Qdrant import sẽ tạo lỗi `Collection procedures doesn't exist`. Runtime có
local fallback để không chết phiên demo, nhưng không thay thế việc import DB đầy
đủ trước khi bàn giao.

## Cấu trúc runtime

```text
rag/
├── engine.py                 # Orchestrator
├── core/                     # config, schema, conversation, transcript
├── pipeline/                 # understanding, routing, contract, journey, context
├── retrieval/                # Qdrant/Neo4j + fallback + version catalog
├── generation/               # answer, validator, repair
├── prompts/                  # Gemini prompts
└── conversation_logs/        # Markdown transcript runtime
tests/rag/                    # Unit/regression test, không gọi Gemini
ui/streamlit_app.py           # Streamlit frontend
```

## Tài liệu

| File | Nội dung |
| --- | --- |
| [rag/README.md](rag/README.md) | Mô tả module RAG chi tiết. |
| [debug_request1.md](debug_request1.md) | Cải tổ pipeline, evidence contract và audit 5 use case. |
| [procedure_workflow_verification_benchmark.md](procedure_workflow_verification_benchmark.md) | Benchmark gốc. |
| [data_processing_pipeline.md](data_processing_pipeline.md) | Chuẩn bị dữ liệu. |
