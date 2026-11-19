# Yorha – Trợ lý thủ tục hành chính

## Motivation

Khi xảy ra một sự kiện trong cuộc sống, người dân thường biết tình huống của mình nhưng chưa biết tên thủ tục cần tìm. Một câu như **“Tôi vừa sinh con”** có thể kéo theo nhiều việc: đăng ký khai sinh, các thủ tục liên quan cho trẻ và tìm hiểu quyền lợi của cha mẹ.

Dù thông tin đã được công khai trên các cổng dịch vụ công, người dân vẫn phải tự tìm kiếm, đối chiếu điều kiện và xác định việc nào cần làm trước. Điều này dễ dẫn đến bỏ sót thủ tục, chuẩn bị thiếu giấy tờ hoặc không biết tới quyền lợi có thể được hưởng.

Yorha hướng tới việc giúp người dân đi từ **tình huống thực tế đến một hành trình thủ tục có thể hiểu và thực hiện được**.

## Tổng quan dự án

Yorha là trợ lý hỏi đáp bằng tiếng Việt, kết hợp mô hình ngôn ngữ với dữ liệu thủ tục và văn bản pháp luật. Người dùng có thể đặt câu hỏi cụ thể hoặc chỉ mô tả tình huống; hệ thống sẽ:

- Nhận diện nhu cầu và dữ kiện người dùng đã cung cấp.
- Đề xuất các thủ tục liên quan và sắp xếp theo quan hệ phụ thuộc.
- Tổng hợp giấy tờ, trình tự thực hiện và thông tin hướng dẫn từ dữ liệu nguồn.
- Gợi ý quyền lợi có thể liên quan, nêu điều chưa chắc chắn và hỏi thêm khi thiếu dữ kiện.
- Trả câu trả lời kèm trích dẫn để người dùng đối chiếu.

Hệ thống sử dụng RAG (*Retrieval-Augmented Generation*): truy xuất dữ liệu trước, sau đó cung cấp dữ liệu đó cho LLM để tạo câu trả lời. Qdrant tìm nội dung gần nghĩa; Neo4j cung cấp quan hệ giữa thủ tục và căn cứ pháp luật.

## Phạm vi hiện tại

Phiên bản hiện tại tập trung vào **các thủ tục hành chính và quyền lợi liên quan đến sự kiện sinh con**, đồng hành cùng người dân từ việc xác định nhu cầu, tìm hiểu hồ sơ đến sắp xếp các bước cần thực hiện. Repository bao gồm công cụ chuẩn bị dữ liệu, RAG engine và giao diện chat Streamlit để trình diễn luồng hỗ trợ này.

- Dữ liệu được lựa chọn theo phạm vi sự kiện sinh con, bao gồm các thủ tục liên quan và văn bản pháp luật phục vụ tra cứu, hướng dẫn.
- Người dùng có thể mô tả tình huống, hỏi về giấy tờ của một thủ tục, tìm bước tiếp theo hoặc tìm hiểu quyền lợi trong phạm vi dữ liệu hiện có. Các câu hỏi trong phần hướng dẫn là ví dụ minh họa, không phải mẫu đầu vào bắt buộc.
- Qdrant và Neo4j đã được team chuẩn bị. Người chạy demo có thể kết nối trực tiếp bằng thông tin truy cập được cấp.
- UI hỗ trợ hỏi đáp nhiều lượt trong một phiên, xem nguồn, câu hỏi bổ sung và tạo cuộc trò chuyện mới; chưa có tài khoản người dùng.
- Hệ thống hướng dẫn và cung cấp thông tin; chưa nộp hồ sơ hay thực hiện thủ tục thay người dân.

Hướng phát triển là mở rộng sang những sự kiện khác như chuyển nơi ở hoặc nghỉ hưu. Schema dữ kiện `facts` được để linh hoạt nhằm hỗ trợ hướng này, nhưng việc mở rộng vẫn cần bổ sung dữ liệu, quan hệ và kiểm thử tương ứng.

## Kiến trúc tổng thể

| Thành phần | Vai trò |
| --- | --- |
| Streamlit | Nhận tình huống, hiển thị hội thoại, câu hỏi bổ sung và nguồn |
| RAG engine bằng Python | Điều phối các bước, quản lý trạng thái hội thoại, kết hợp kết quả truy xuất |
| Gemini API | Hiểu tình huống, trích xuất dữ kiện, tạo câu trả lời và sửa bản nháp khi cần |
| Pydantic | Kiểm tra cấu trúc dữ liệu trao đổi và JSON do LLM sinh |
| Vietnamese SBERT | Mã hóa câu truy vấn thành vector tương thích dữ liệu đã lưu |
| Qdrant | Lưu và tìm kiếm vector của các đoạn nội dung thủ tục, pháp luật |
| Neo4j | Lưu thủ tục, văn bản, các phần nội dung luật và quan hệ giữa chúng |

LLM được gọi qua API. **Model embedding hiện chạy trong process Python của ứng dụng**, được tải về ở lần sử dụng đầu tiên và tái sử dụng trong engine.

Hai nguồn dữ liệu được nối bằng ID:

- Thủ tục: `Qdrant.doc_id` ↔ `Neo4j Procedure.id`.
- Nội dung luật: `(doc_id, section_index)` ↔ `(LawSection.law_id, LawSection.order)`.

Nhờ đó, kết quả tìm kiếm ngữ nghĩa có thể trở thành điểm bắt đầu để truy vấn quan hệ trong graph, rồi lấy lại nội dung chi tiết cho các thủ tục liên quan.

## Luồng chuẩn bị dữ liệu

```text
Nguồn dịch vụ công và văn bản pháp luật
    → Crawl, trích xuất và làm sạch
    → Bản ghi JSON
    → Chuẩn hóa ID, metadata và quan hệ
        ├─ Chia chunk → Embedding → Qdrant
        └─ Tạo node và relationship → Neo4j
```

1. **Thu thập:** các script trong `crawl/` lấy thông tin từ Cổng Dịch vụ công và cơ sở dữ liệu văn bản pháp luật.
2. **Chuẩn hóa:** các script trong `db/graph/` chuẩn hóa bản ghi, ID, phân cấp nội dung luật và tham chiếu giữa các bản ghi.
3. **Xây dựng quan hệ:** xử lý quan hệ giữa thủ tục, cũng như liên kết quyền lợi tới các phần nội dung pháp luật dựa trên dữ liệu đã gán.
4. **Chia chunk:** `chunk/` tách thủ tục theo nhóm thông tin và luật theo cấu trúc nội dung, giữ metadata để truy ngược nguồn.
5. **Lưu vector:** tạo embedding và đưa các chunk vào collection `procedures` và `laws` của Qdrant.
6. **Lưu graph:** import node và relationship vào Neo4j để phục vụ truy vấn phụ thuộc, thủ tục liên quan và căn cứ quyền lợi.

Đây là luồng chuẩn bị dữ liệu, không chạy lại ở mỗi câu hỏi của người dùng.

## Luồng hỏi đáp

```text
Tình huống / câu hỏi + trạng thái hội thoại trước
    → Chuẩn hóa → Hiểu ý định và facts → Lập kế hoạch truy xuất
    → Tìm trong Qdrant → Mở rộng / đối chiếu trong Neo4j
    → Dựng hành trình + lấy chi tiết + gom quyền lợi
    → Tạo context → Sinh câu trả lời → Kiểm tra / sửa
    → Hiển thị kết quả + lưu trạng thái cho lượt sau
```

| Bước | Cách xử lý và kết quả chuyển tiếp |
| --- | --- |
| 1. Chuẩn hóa | Python làm sạch khoảng trắng, Unicode và ký tự vô hình để tạo câu truy vấn chuẩn hóa. |
| 2. Hiểu tình huống | Prompt Gemini trích xuất sự kiện, ý định, chủ đề, đối tượng và `facts`; Pydantic kiểm tra JSON. |
| 3. Nhận diện dữ kiện thiếu | Cùng bước hiểu truy vấn, LLM chỉ ra thông tin cần làm rõ; Python giữ lại để phục vụ hỏi tiếp. |
| 4. Routing | Python chọn tìm thủ tục hay luật, có mở rộng graph/lấy quyền lợi không và cần loại chunk nào. |
| 5. Tìm ứng viên | Embedding + Qdrant tìm các đoạn gần nghĩa; ID thủ tục trở thành điểm bắt đầu cho graph. |
| 6. Truy vấn graph | Neo4j cung cấp các thủ tục liên quan, quan hệ phụ thuộc và căn cứ luật theo kế hoạch. |
| 7. Dựng hành trình | Python tính thứ tự từ quan hệ phụ thuộc; các thủ tục cùng mức có thể có cùng độ ưu tiên. |
| 8. Lấy chi tiết | Truy vấn lại Qdrant theo ID của các thủ tục trong hành trình để lấy giấy tờ, bước làm và thông tin thực hiện. |
| 9. Gom quyền lợi | Python nhóm và khử trùng lặp căn cứ luật; chưa mặc định người dùng đủ điều kiện hưởng. |
| 10. Tạo context | Python ghép câu hỏi, facts, hành trình và evidence; giới hạn nội dung trước khi gửi LLM. |
| 11. Sinh câu trả lời | Prompt Gemini tạo Markdown, trích dẫn, đánh giá quyền lợi và câu hỏi bổ sung. |
| 12. Hậu kiểm | Python kiểm tra citation và các quy tắc; sửa bằng Python, gọi Gemini repair khi cần, cuối cùng dùng câu trả lời dự phòng nếu bản chi tiết không đạt. |
| 13. Trả kết quả | Engine trả response cho UI và lưu trạng thái cùng câu hỏi đang chờ để hiểu lượt tiếp theo. |

Các bước truy xuất được bật theo ý định. Ví dụ, câu hỏi trực tiếp về luật có thể tìm trong collection `laws` mà không cần dựng hành trình thủ tục.

Xem [README của RAG engine](rag/README.md) để đọc phương pháp từng bước, schema trao đổi và lệnh demo tương ứng.

## Cấu trúc thư mục

```text
Yorha/
├── crawl/                  # Thu thập và kiểm tra dữ liệu nguồn
├── data/                   # Bản ghi, dữ liệu chuẩn hóa và quan hệ của demo
├── chunk/                  # Chia nội dung thành chunk cho vector search
├── db/
│   ├── graph/              # Chuẩn hóa, tạo quan hệ và import Neo4j
│   ├── vector/             # Embedding và import Qdrant
│   ├── neo4j_client.py     # Client kết nối graph
│   └── qdrant_client.py    # Client kết nối vector database
├── rag/
│   ├── core/               # Config, schema, bộ nhớ hội thoại
│   ├── pipeline/           # Xử lý query, routing, journey, benefit, context
│   ├── retrieval/          # Embedding và truy xuất hai database
│   ├── generation/         # Sinh, kiểm tra và sửa câu trả lời
│   ├── prompts/            # Chỉ dẫn cho Gemini
│   ├── demos/              # Quan sát kết quả từng chặng
│   └── engine.py           # API điều phối để CLI và UI sử dụng
├── ui/streamlit_app.py      # Giao diện chat demo
├── .env.example            # Mẫu biến môi trường
└── requirements.txt        # Dependency Python
```

## Cài đặt và chạy demo

### Chuẩn bị môi trường

Các lệnh dưới đây dùng PowerShell, chạy tại thư mục gốc repository. Dự án đang dùng Python 3.11; danh sách dependency hiện có gói dành riêng cho Windows (`pywin32`).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Nếu đã có `.venv`, chỉ cần kích hoạt môi trường đang dùng.

### Cấu hình kết nối

Nếu chưa có `.env`, sao chép `.env.example` thành `.env`, rồi điền thông tin:

| Biến | Mục đích |
| --- | --- |
| `GEMINI_API_KEY` | Khóa gọi Gemini API |
| `GEMINI_QUERY_MODEL` | Model Gemini dùng trong engine; tên biến hiện được dùng chung cho các bước gọi LLM |
| `QDRANT_URL`, `QDRANT_API_KEY` | Kết nối Qdrant đã chứa dữ liệu demo |
| `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` | Kết nối Neo4j đã chứa graph demo |
| `EMBEDDING_MODEL` | Model phải trùng với model đã dùng để build vector: `keepitreal/vietnamese-sbert`, 768 chiều |

Không cần crawl hay build database lại khi dùng dữ liệu team đã chuẩn bị. Có thể kiểm tra kết nối và cấu trúc nguồn bằng lệnh chỉ đọc:

```powershell
python -m rag.demos.inspect_data_sources
```

### Chạy giao diện chat

```powershell
python -m streamlit run ui/streamlit_app.py
```

Mở địa chỉ Streamlit in ra trong terminal và đặt câu hỏi trong phạm vi các thủ tục liên quan đến sự kiện sinh con. Chẳng hạn, có thể bắt đầu bằng `Tôi vừa sinh con` để tìm hiểu hành trình tổng thể, hoặc `Khai sinh cần giấy tờ gì?` để hỏi một nội dung cụ thể, rồi tiếp tục trả lời câu hỏi bổ sung trong cùng phiên chat. Nút **Cuộc trò chuyện mới** xóa lịch sử hiển thị và trạng thái hội thoại của phiên hiện tại.

### Chạy bằng terminal

```powershell
# Một câu hỏi
python -m rag "Tôi vừa sinh con"

# Hội thoại nhiều lượt
python -m rag "Tôi vừa sinh con" --interactive

# Xem response có cấu trúc
python -m rag "Khai sinh cần giấy tờ gì?" --json
```

### Khi cần tự xây dựng dữ liệu

Thực hiện theo luồng chuẩn bị dữ liệu ở trên, dùng các script trong `crawl/`, `chunk/`, `db/graph/` và `db/vector/`. Cần đối chiếu đường dẫn đầu vào/đầu ra trước khi import:

- Các script chunk và script import Qdrant dùng chung đầu vào tại `data/chunks/` (`procedure_chunks.jsonl` và `law_chunks.jsonl`).
- Script import Qdrant đọc biến môi trường của process; không tự nạp `.env` như các client runtime.
- File quan hệ quyền lợi có sẵn nằm trong `data/benefit_relation/`; Neo4j importer có tham số `--related-benefit-relations` để chỉ định đúng file.
- Các tùy chọn `--reset` của importer xóa dữ liệu hiện có; không cần dùng khi chỉ chạy ứng dụng demo.

#### Crawl văn bản pháp luật theo từ khóa

Crawler hỗ trợ cả VBPL và Thư Viện Pháp Luật (TVPL). Giới hạn `--limit` là số
văn bản hợp lệ tối đa cho **mỗi từ khóa**; mặc định là 50. Khi chạy lại, bản ghi
hợp lệ đã có sẽ được bỏ qua. Dùng `--refresh` để cập nhật lại bản ghi hoặc
`--discover-only` để chỉ liệt kê URL tìm thấy.

```powershell
# Tìm và crawl tối đa 100 văn bản công khai từ TVPL
python crawl/crawl_law.py --source tvpl --query "thuế thu nhập cá nhân" --limit 100

# Nhiều từ khóa, mỗi từ khóa tối đa 30 văn bản
python crawl/crawl_law.py --source tvpl --query "thai sản" --query "khai sinh" --limit 30

# Xem trước URL mà không tải nội dung
python crawl/crawl_law.py --source tvpl --query "thuế thu nhập cá nhân" --limit 20 --discover-only

# Làm mới các bản ghi TVPL đã có
python crawl/crawl_law.py --source tvpl --query "thuế thu nhập cá nhân" --limit 50 --refresh
```

Các lệnh cũ tiếp tục dùng VBPL mặc định; có thể ghi rõ `--source vbpl`. Bản ghi
TVPL dùng cùng cấu trúc `data/law/records/LAW_*.json`, có ID dạng
`LAW_TVPL_<mã-văn-bản>` và chỉ lưu phần điều khoản công khai. Phần căn cứ, chữ ký,
nơi nhận, phụ lục và biểu mẫu được bỏ qua. Các giá trị hiệu lực mà TVPL chỉ hiển
thị là “Đã biết” được giữ nguyên, không được diễn giải thành ngày hoặc trạng thái
cụ thể. Mỗi văn bản và mỗi lượt tìm kiếm được ghi vào
`data/law/crawl_report.jsonl`. Nếu trang yêu cầu xác minh hoặc chặn truy cập,
crawler ghi lỗi và không lưu trang chặn như một văn bản.
Trang TVPL có thông báo quyền tác giả đối với bản dịch; hãy kiểm tra quyền sử
dụng trước khi công bố hoặc phân phối lại dữ liệu thu thập.

#### Tự động khám phá quyền lợi

Sau khi có JSON luật/thủ tục đã chuẩn hóa và collection `laws` trong Qdrant, có thể tạo hàng chờ duyệt:

```powershell
python -m db.graph.discover_benefits --top-k 30
```

Kiểm tra `data/benefit_relation/discovery_review.jsonl`, rồi đổi `status` thành `approved` hoặc `rejected`. Import graph với các liên kết đã duyệt:

```powershell
python -m db.graph.neo4j_import --reviewed-benefits data/benefit_relation/discovery_review.jsonl
```

Pipeline dùng Gemini Flash qua `GEMINI_BENEFIT_MODEL`, Vietnamese SBERT/Qdrant để tìm ứng viên và không tự ghi graph trước khi duyệt. Xem [hướng dẫn benefit discovery](db/graph/benefit_discovery.md) để biết schema review, cache và chi tiết các bước.

## Giới hạn hiện tại

- Câu trả lời phụ thuộc vào phạm vi và chất lượng dữ liệu demo; một số văn bản thiếu thông tin hiệu lực. Có trích dẫn không đồng nghĩa với đã xác minh quy định còn áp dụng.
- Hậu kiểm dùng các quy tắc Python để phát hiện lỗi citation và cách diễn đạt; chưa chứng minh được mọi kết luận đều được nguồn hỗ trợ về mặt ngữ nghĩa.
- Thứ tự thủ tục được suy ra từ quan hệ đã lưu; mức độ đầy đủ và chính xác phụ thuộc vào graph.
- Bộ nhớ hội thoại nằm trong RAM của process. Khởi động lại ứng dụng sẽ mất trạng thái; chưa có lưu trữ hội thoại bền vững hay đồng bộ nhiều process.
- Lần truy vấn đầu có thể chậm hơn do tải model embedding. Các bước gọi Gemini và database cần kết nối mạng.

## Tài liệu chi tiết

| Tài liệu | Nội dung |
| --- | --- |
| [RAG engine](rag/README.md) | Pipeline 13 bước, prompt/engineering, demo và cách tích hợp |
| [Pipeline dữ liệu](data_processing_pipeline.md) | Sơ lược luồng chuẩn bị dữ liệu |
| [Benefit discovery](db/graph/benefit_discovery.md) | Tạo ứng viên quyền lợi, duyệt JSONL và import các liên kết đã duyệt |
| [Schema thủ tục](procedure_data_schema.md) | Cấu trúc bản ghi thủ tục |
| [Schema pháp luật](law_data_schema.md) | Cấu trúc bản ghi pháp luật |
| [Dữ liệu Qdrant](db/qdrant_data_format.md) | Chunk, metadata và định dạng lưu vector |
| [Dữ liệu Neo4j](db/neo4j_data_format.md) | Node và relationship |
| [Quan hệ thủ tục](db/graph/procedure_relation.md) | Mô hình graph thủ tục |
| [Quan hệ pháp luật](db/graph/law_relation.md) | Phân cấp và tham chiếu nội dung luật |
