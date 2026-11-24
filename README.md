# Yorha

Yorha là trợ lý hỏi đáp thủ tục hành chính tiếng Việt cho nhóm tình huống xoay quanh sự kiện sinh con. Hệ thống kết hợp LLM với dữ liệu thủ tục có cấu trúc để trả lời kèm nguồn, điều kiện, trình tự thực hiện và các quan hệ phụ thuộc giữa thủ tục.

## Chức năng

- Tra cứu thủ tục, hồ sơ, cơ quan tiếp nhận, cách nộp, thời hạn và lệ phí.
- Hướng dẫn các hành trình nhiều thủ tục, ví dụ khai sinh → thường trú → BHYT → Căn cước.
- Trích dẫn chunk dữ liệu đã dùng trong câu trả lời.
- Hiển thị căn cứ pháp lý, phạm vi áp dụng và trạng thái cần rà soát khi metadata nguồn có thông tin đó.
- Lưu transcript Markdown riêng theo từng phiên chat.
- Hỏi bổ sung khi chưa đủ dữ kiện hoặc trả lời dựa trên evidence khi không thể xác minh một claim cần thiết.

## Kiến trúc

```text
Streamlit UI
    │
    ▼
RAG engine
    ├── LLM: hiểu câu hỏi, tạo và sửa câu trả lời
    ├── Qdrant: tìm chunk thủ tục và văn bản theo ngữ nghĩa
    ├── Neo4j: truy vấn quan hệ giữa thủ tục, luật và quyền lợi
    └── Python: route, kiểm evidence, kiểm thứ tự, fallback và hiển thị nguồn
```

LLM xử lý phần ngôn ngữ. Việc chọn bằng chứng bắt buộc, kiểm citation, thứ tự workflow và quyết định fallback được thực hiện bằng schema và code Python.

## Luồng một lượt hỏi đáp

1. Chuẩn hóa câu hỏi và nhận diện ý định, thủ tục, dữ kiện đã có và dữ kiện còn thiếu.
2. Lập kế hoạch truy xuất và xác định evidence bắt buộc cho những tình huống có rủi ro sai lộ trình.
3. Lấy chunk liên quan từ Qdrant; mở rộng quan hệ từ Neo4j khi câu hỏi liên quan dependency hoặc workflow.
4. Ghép context gồm thủ tục, các bước, điều kiện, nguồn pháp lý và metadata nguồn.
5. Tạo câu trả lời, hậu kiểm citation/nội dung/thứ tự, sửa có kiểm soát khi cần, rồi trả fallback dựa trên evidence nếu vẫn không đạt.

Khi Qdrant hoặc Neo4j không kết nối được, engine có thể sử dụng chỉ mục vector cục bộ hoặc snapshot graph từ dữ liệu dự án và gắn cảnh báo vào lượt trả lời.

## Cài đặt

Yêu cầu: Python và quyền truy cập Gemini, Qdrant Cloud, Neo4j Aura (hoặc cấu hình tương đương).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Cấu hình `.env`:

| Biến | Mô tả |
| --- | --- |
| `GEMINI_API_KEY` | Khóa gọi Gemini. |
| `GEMINI_QUERY_MODEL` | Model Gemini dùng cho hệ thống. |
| `QDRANT_URL`, `QDRANT_API_KEY` | Kết nối Qdrant. |
| `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` | Kết nối Neo4j. |
| `EMBEDDING_MODEL` | Embedding model, phải trùng model khi tạo vector database. |

## Chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py
```

Chạy từ dòng lệnh:

```powershell
.\.venv\Scripts\python.exe -m rag "Khai sinh cần giấy tờ gì?"
.\.venv\Scripts\python.exe -m rag "Tôi vừa sinh con" --interactive
.\.venv\Scripts\python.exe -m rag "Khai sinh cần giấy tờ gì?" --json
```

## Khởi tạo dữ liệu truy xuất

Sau khi cấu hình các biến kết nối, import graph và vector database:

```powershell
.\.venv\Scripts\python.exe db/graph/neo4j_import.py --related-benefit-relations data/benefit_relation/related_benefit_relations.json
.\.venv\Scripts\python.exe db/vector/setup_qdrant_db.py
```

Graph import tạo các node thủ tục, luật, section và relationship. Vector import tạo các collection Qdrant cần thiết cho retrieval. Cần chạy cả hai lệnh khi dựng database mới.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/rag -v
```

## Cấu trúc thư mục

```text
data/       Dữ liệu thủ tục, luật, chunk và mapping relation
db/         Client và script import Neo4j/Qdrant
rag/        Engine, retrieval, pipeline, generation, schema và prompt
tests/      Unit test và regression test
ui/         Ứng dụng Streamlit
```
