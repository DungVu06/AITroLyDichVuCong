# RAG engine – Trợ lý thủ tục hành chính

## 1. Module này làm gì?

`rag/` nhận một tình huống hoặc câu hỏi bằng tiếng Việt và tạo câu trả lời có
nguồn dẫn về:

- các thủ tục người dân cần làm;
- thứ tự ưu tiên và quan hệ phụ thuộc giữa các thủ tục;
- giấy tờ, bước thực hiện và cách thức thực hiện;
- quyền lợi có thể liên quan;
- căn cứ pháp luật có trong dữ liệu;
- câu hỏi bổ sung khi chưa đủ dữ kiện để kết luận.

Phạm vi dữ liệu hiện tại là bản demo cho sự kiện **sinh con**. Kiến trúc không
đóng cứng các trường dữ kiện của sự kiện này: `facts` là một JSON object linh
hoạt do LLM trích xuất, nên sau này có thể mở rộng sang sự kiện khác mà không
phải định nghĩa trước mọi trường con.

Người dùng không bắt buộc phải đặt câu hỏi đầy đủ. Ví dụ `Tôi vừa sinh con` vẫn
được hiểu là một tình huống cần chủ động gợi ý hành trình thủ tục và quyền lợi.

## 2. Thành phần chính

```text
rag/
├── engine.py           # Điều phối toàn bộ pipeline, API để UI gọi
├── core/               # Schema, cấu hình và bộ nhớ hội thoại
├── pipeline/           # Hiểu query, routing, journey, benefit và context
├── retrieval/          # Embedding, truy xuất Qdrant và Neo4j
├── generation/         # Sinh câu trả lời, kiểm tra và sửa citation
├── prompts/            # Prompt gửi cho Gemini
└── demos/              # Chạy và quan sát đầu ra ở từng chặng
```

Code ứng dụng chỉ cần gọi `RAGEngine` trong `rag.engine`. Các file `demos/` dùng
để quan sát pipeline khi phát triển và không tham gia vào runtime của engine.

## 3. Dữ liệu được sử dụng và cách liên kết

Engine chỉ đọc dữ liệu đã có, không chạy lại crawler hay script build database.

### Qdrant

- Collection `procedures`: các chunk mô tả thủ tục như giấy tờ, bước làm, cách
  thức thực hiện và lưu ý.
- Collection `laws`: các chunk nội dung văn bản pháp luật.
- Mỗi câu truy vấn được mã hóa bằng model
  `keepitreal/vietnamese-sbert` thành vector 768 chiều để tìm nội dung gần nghĩa.

### Neo4j

- Node thủ tục và quan hệ giữa các thủ tục như `REQUIRES`, `NEXT_STEP`,
  `PART_OF`, `HAS_SUB_PROCEDURE`.
- Node văn bản/điều khoản pháp luật và quan hệ tới quyền lợi.
- Graph cho biết quan hệ nghiệp vụ; Qdrant cung cấp phần nội dung chi tiết.

### Khóa nối hai nguồn

- `Qdrant procedure.doc_id` ↔ `Neo4j Procedure.id`.
- `(Qdrant law.doc_id, law.section_index)` ↔
  `(Neo4j LawSection.law_id, LawSection.order)`.

Luồng truy xuất thường dùng Qdrant để tìm **thủ tục hạt giống**, lấy ID đó mở
rộng trong Neo4j, rồi quay lại Qdrant lấy nội dung chi tiết cho toàn bộ thủ tục
đã xuất hiện trong hành trình.

## 4. Quy ước về cách xử lý

- **Prompt**: Gemini cần hiểu ngôn ngữ tự nhiên, diễn đạt câu trả lời hoặc sửa
  văn bản. Output quan trọng luôn được ép theo schema Pydantic.
- **Engineering**: Python thực hiện các phần cần tính xác định như routing,
  lọc dữ liệu, nối ID, sắp thứ tự, giới hạn context và kiểm tra citation.
- **Retrieval**: embedding và database tìm dữ liệu có sẵn; chúng không tự kết
  luận người dùng đủ điều kiện hưởng quyền lợi.

Không giao toàn bộ pipeline cho một prompt duy nhất. LLM xử lý phần ngôn ngữ;
Python giữ quyền quyết định luồng và kiểm tra kết quả.

## 5. Luồng xử lý đầy đủ

Các lệnh dưới đây chạy từ thư mục gốc dự án. Những bước có Gemini, Qdrant hoặc
Neo4j cần `.env` chứa đầy đủ khóa kết nối.

### Bước 1 – Chuẩn hóa đầu vào

**Loại:** Engineering.

Python chuẩn hóa Unicode, xóa ký tự vô hình, đổi khoảng trắng đặc biệt và gom
khoảng trắng liên tiếp. Nội dung và ý nghĩa câu hỏi không bị viết lại.

Đầu ra là `PreprocessedQuery`, gồm câu gốc, câu đã chuẩn hóa và
`conversation_id`. Câu chuẩn hóa được chuyển sang bước hiểu truy vấn.

```powershell
python -m rag.demos.preprocessing "  Tôi   vừa sinh con  "
```

### Bước 2 – Hiểu tình huống và ý định

**Loại:** Prompt + kiểm tra schema bằng Python.

Gemini đọc cả câu hỏi trực tiếp lẫn câu mô tả tình huống. Prompt yêu cầu model
trả về `QueryState` có:

- `life_event`: sự kiện đời sống nhận diện được;
- `intent`: cần hành trình, chi tiết thủ tục, bước tiếp theo, quyền lợi hay luật;
- `topics`: nhóm thông tin cần lấy;
- `target`: đối tượng cụ thể người dùng đang hỏi;
- `facts`: dữ kiện linh hoạt do model trích xuất;
- `missing_facts`: dữ kiện còn thiếu và câu hỏi có thể hỏi lại.

Pydantic chỉ kiểm tra hình dạng JSON; không định nghĩa trước nội dung bên trong
`facts`. Nếu là lượt hội thoại tiếp theo, prompt nhận thêm trạng thái trước và
các câu hỏi đang chờ, sau đó Python hợp nhất facts cũ với facts mới.

Đầu ra `QueryState` được chuyển nguyên vẹn sang router.

```powershell
python -m rag.demos.query_understanding "Tôi vừa sinh con"
```

Prompt: `rag/prompts/query_understanding.md`.

### Bước 3 – Xác định dữ kiện thiếu

**Loại:** Prompt ở bước 2 + Engineering.

Trong cùng lần hiểu truy vấn, Gemini chỉ ra dữ kiện nào thực sự cần để trả lời
ý định hiện tại. Python giữ danh sách này trong `QueryState` và đánh dấu kế hoạch
truy xuất có cần làm rõ hay không. Việc thiếu dữ kiện không chặn toàn bộ câu trả
lời: engine vẫn có thể đưa thủ tục đã biết, nhưng chưa kết luận chắc chắn về
quyền lợi.

Thông tin thiếu được dùng lại ở bước sinh câu trả lời để tạo câu hỏi tiếp nối.
Có thể quan sát chung bằng demo của bước 2.

### Bước 4 – Lập kế hoạch truy xuất

**Loại:** Engineering, không gọi thêm LLM.

Router đổi `intent`, `topics`, `life_event` và `target` thành `RetrievalPlan`.
Kế hoạch quyết định:

- tìm procedure hay law trong Qdrant;
- có mở rộng Neo4j hay không;
- có lấy quyền lợi và căn cứ luật hay không;
- cần những loại chunk procedure nào;
- truy vấn semantic và filter nào sẽ được dùng.

Ví dụ, `Tôi vừa sinh con` đi theo `journey_first`: tìm procedure hạt giống, mở
rộng graph, lấy quyền lợi và căn cứ liên quan. Câu `Luật quy định chế độ thai
sản thế nào?` đi theo `law_search` và bật tìm vector trong collection luật.

`RetrievalPlan` là hợp đồng để các retriever phía sau chỉ làm đúng phần được bật.

```powershell
python -m rag.demos.routing "Tôi vừa sinh con"
```

### Bước 5 – Tìm thủ tục hoặc điều luật hạt giống trong Qdrant

**Loại:** Embedding + Engineering.

Query trong `RetrievalPlan` được mã hóa bằng cùng model embedding đã dùng khi
build database. Qdrant trả các chunk gần nghĩa. Do database demo chưa có payload
index cho mọi field, retriever có thể lấy dư ứng viên rồi lọc metadata ở Python.

Đầu ra gồm các `RetrievedChunk`. `doc_id` của procedure tốt nhất trở thành ID
hạt giống để truy vấn graph. Với câu hỏi pháp luật, các chunk luật được giữ để
đối chiếu sang `LawSection`.

```powershell
python -m rag.demos.vector_retrieval "Tôi vừa sinh con" --limit 5
```

### Bước 6 – Mở rộng quan hệ trong Neo4j

**Loại:** Engineering + graph query.

Từ các procedure ID hạt giống, Neo4j lấy node thủ tục và duyệt các quan hệ nghiệp
vụ. Việc mở rộng lặp lại cho đến khi không tìm thấy thủ tục mới trong giới hạn
của demo, nhờ đó có thể lấy quan hệ nhiều tầng thay vì chỉ hàng xóm trực tiếp.

Nếu kế hoạch yêu cầu quyền lợi, graph đồng thời trả quan hệ tới điều khoản luật.
Nếu Qdrant đã tìm chunk luật, cặp khóa luật/section được dùng để lấy node
`LawSection` tương ứng.

Đầu ra là `GraphRetrievalResult`, gồm thủ tục, quan hệ thủ tục và quan hệ quyền
lợi. Kết quả này được chuyển sang journey builder và benefit resolver.

```powershell
python -m rag.demos.graph_retrieval "Tôi vừa sinh con" --limit 5
```

### Bước 7 – Dựng hành trình và thứ tự ưu tiên

**Loại:** Engineering, không để LLM tự sắp xếp.

Python diễn giải chiều quan hệ graph để tính phụ thuộc:

- `A REQUIRES B`: A phụ thuộc B;
- `A NEXT_STEP B`: B là bước sau A;
- các thủ tục cùng mức phụ thuộc có thể có cùng độ ưu tiên.

Mỗi `JourneyItem` có ID, tên, priority, nhóm required/recommended/optional,
trạng thái và danh sách `depends_on`. Với intent hỏi “bước tiếp theo”, thủ tục
hạt giống được đánh dấu hoàn thành trước khi tính các bước sau.

Danh sách hành trình cung cấp cả thứ tự trả lời lẫn tập procedure ID cần lấy chi
tiết ở bước 8.

```powershell
python -m rag.demos.journey "Tôi vừa sinh con" --limit 5
```

### Bước 8 – Lấy chi tiết cho từng thủ tục

**Loại:** Retrieval + Engineering.

Engine quay lại Qdrant với từng procedure ID trong hành trình. Mỗi loại chunk
được truy xuất và xếp hạng riêng:

- `document_item`: hồ sơ, giấy tờ;
- `step_item`: các bước thực hiện;
- `execution_methods`: hình thức, thời gian, lệ phí;
- `note_item`: lưu ý.

Router có thể giới hạn loại chunk theo chủ đề người dùng hỏi. Retriever cũng ưu
tiên nội dung phổ biến trước các nhánh trường hợp đặc biệt để context không bị
lệch bởi một kết quả semantic đơn lẻ.

Đầu ra là `ProcedureEvidence` cho từng item trong journey.

```powershell
python -m rag.demos.procedure_details "Tôi vừa sinh con" --limit 5
```

### Bước 9 – Tổng hợp quyền lợi và căn cứ pháp luật

**Loại:** Engineering.

Benefit resolver gom các quan hệ graph có cùng quyền lợi, làm sạch tiêu đề và
khử trùng lặp điều khoản theo `(law_id, section_id)`. Trạng thái ban đầu luôn là
`unknown`: sự tồn tại của một điều luật liên quan không có nghĩa người dùng chắc
chắn đủ điều kiện.

Mỗi `BenefitEvidence` giữ quyền lợi, procedure liên quan và danh sách căn cứ
pháp luật. Nếu dữ liệu không có trạng thái hiệu lực văn bản, thông tin này tiếp
tục được giữ là chưa chắc chắn và phải xuất hiện trong cảnh báo cuối.

```powershell
python -m rag.demos.benefits "Tôi vừa sinh con" --limit 5
```

### Bước 10 – Đóng gói và rút gọn context

**Loại:** Engineering.

Context builder ghép câu hỏi, `QueryState`, journey, chi tiết procedure, quyền
lợi, căn cứ luật và các quy tắc trả lời thành một `AnswerContext` duy nhất.

Trước khi gửi Gemini, Python:

- sắp procedure theo journey;
- giới hạn số chunk của từng loại;
- cắt nội dung quá dài;
- bỏ điều khoản rỗng và giới hạn số section trên mỗi văn bản;
- giữ ID nguồn để bước sinh câu trả lời có thể citation chính xác.

Đây là điểm hợp nhất toàn bộ kết quả từ Qdrant và Neo4j. Gemini ở bước sau chỉ
được nhìn thấy context đã kiểm soát này.

```powershell
python -m rag.demos.context "Tôi vừa sinh con" --limit 5
python -m rag.demos.context "Tôi vừa sinh con" --limit 5 --full
```

### Bước 11 – Sinh câu trả lời và đánh giá quyền lợi

**Loại:** Prompt + schema Pydantic.

Gemini diễn đạt `AnswerContext` thành câu trả lời Markdown. Prompt yêu cầu:

- trình bày thủ tục theo đúng journey;
- không tạo thêm thủ tục ngoài context;
- gắn citation dạng `【source_id】` cho claim;
- đánh dấu rõ quyền lợi chưa chắc chắn;
- tạo tối đa ba câu hỏi tiếp theo khi thiếu facts;
- trả assessment có cấu trúc cho từng quyền lợi.

Python ghép assessment vào `BenefitEvidence`. Nếu Gemini kết luận `eligible`
nhưng dữ liệu chưa có trạng thái hiệu lực luật, kết quả bị hạ xuống
`possibly_eligible`; kết luận loại trừ không đủ căn cứ bị hạ về `unknown`.

```powershell
python -m rag.demos.answer "Tôi vừa sinh con" --limit 5
```

Prompt: `rag/prompts/answer_generation.md`.

### Bước 12 – Hậu kiểm và sửa câu trả lời

**Loại:** Engineering trước, Prompt khi cần.

Validator kiểm tra:

- citation có tồn tại trong danh sách nguồn hay không;
- mỗi procedure trong journey đã được dẫn nguồn chưa;
- claim định lượng hoặc pháp lý đã có citation chưa;
- quyền lợi chưa chắc chắn có bị diễn đạt thành chắc chắn không;
- cảnh báo thiếu trạng thái hiệu lực luật có được hiển thị không;
- câu trả lời có lộ thuật ngữ nội bộ như vector, graph, chunk hoặc RAG không.

Thứ tự sửa là:

1. Python sửa citation procedure có thể xác định chắc chắn từ heading hiện tại.
2. Nếu vẫn lỗi, Gemini sửa một lần theo danh sách lỗi và context gốc.
3. Nếu vẫn không đạt, engine tạo câu trả lời dự phòng an toàn.

Engine chỉ trả kết quả khi hậu kiểm cuối cùng hợp lệ.

```powershell
python -m rag.demos.validation "Tôi vừa sinh con" --limit 5
```

Prompt sửa: `rag/prompts/answer_repair.md`.

### Bước 13 – Trả response và duy trì hội thoại

**Loại:** Engineering.

`RAGResponse` trả cho CLI hoặc UI gồm:

- `answer_markdown`;
- journey đã sắp thứ tự;
- quyền lợi và trạng thái đánh giá;
- câu hỏi bổ sung;
- danh sách nguồn;
- cảnh báo.

Khi có `conversation_id`, engine lưu `QueryState`, facts và câu hỏi đang chờ
trong `InMemoryConversationStore`. Lượt sau dùng lại trạng thái đó ở bước 2. Bộ
nhớ này phù hợp cho demo một process; khi triển khai nhiều process có thể thay
bằng Redis hoặc database mà không đổi các bước còn lại.

Chạy toàn bộ pipeline:

```powershell
python -m rag "Tôi vừa sinh con"
python -m rag "Tôi vừa sinh con" --json
python -m rag "Tôi vừa sinh con" --interactive
```

## 6. Dùng engine từ Python

```python
from rag.engine import RAGEngine

engine = RAGEngine()

first = engine.run(
    "Tôi vừa sinh con",
    conversation_id="demo-session",
)

second = engine.run(
    "Tôi đang làm ở công ty và đã đóng BHXH liên tục 12 tháng trước khi sinh",
    conversation_id="demo-session",
)
```

Nên giữ một instance `RAGEngine` sống xuyên suốt các request để tái sử dụng model
embedding và bộ nhớ hội thoại.

## 7. Giao diện Streamlit

Giao diện demo không có đăng nhập. Mỗi tab trình duyệt là một phiên chat riêng;
nút **Cuộc trò chuyện mới** xóa trạng thái RAG và lịch sử đang hiển thị.

```powershell
python -m streamlit run ui/streamlit_app.py
```

Chạy lệnh từ thư mục gốc dự án với môi trường `.venv` đã kích hoạt.
Entry point UI tự thêm thư mục gốc theo vị trí file vào đường dẫn import để
Python tìm được cả `rag` và `db`, kể cả khi chạy Streamlit từ thư mục khác
bằng đường dẫn tuyệt đối tới file UI.

UI dùng chính `RAGEngine`, hiển thị câu trả lời Markdown, câu hỏi bổ sung, cảnh
báo và danh sách nguồn. Không có một pipeline riêng cho giao diện.

## 8. Kiểm tra nguồn dữ liệu

Script sau chỉ đọc và tóm tắt cấu trúc Qdrant/Neo4j:

```powershell
python -m rag.demos.inspect_data_sources
```
