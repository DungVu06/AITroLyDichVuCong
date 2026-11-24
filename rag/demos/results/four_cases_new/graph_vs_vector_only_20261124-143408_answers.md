# Nhật ký 8 câu trả lời — Graph-RAG vs RAG không đồ thị

- Thời điểm chạy UTC: 2026-11-24T07:34:08+00:00
- Model: `gemini-3.5-flash-lite`
- Mỗi ca được chạy độc lập; không mang hội thoại từ ca trước.
- Câu trả lời dưới đây là output nguyên văn đã được lưu từ 8 lượt chạy.

## TC01 — Khai sinh tại nhà không có Giấy chứng sinh

### Câu hỏi

Vợ tôi vừa sinh cháu tại nhà ở xã An Phú, không có Giấy chứng sinh của bệnh viện thì có làm giấy khai sinh được không? Tôi phải nộp hồ sơ ở đâu, cần giấy tờ gì thay thế và thời gian giải quyết bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_001193_c5_s0`, `PROC_1_001193_c48_s0`.
- Nội dung cần có: văn bản của người làm chứng / người làm chứng xác nhận; nếu không có người làm chứng / nếu không có người chứng kiến; cam đoan; ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã; 1 ngày / một ngày.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: Không có.
- Thứ tự bước bắt buộc: Không áp dụng.

### Trả lời — Graph-RAG

Trường hợp vợ sinh con tại nhà ở xã An Phú và không có Giấy chứng sinh của bệnh viện, anh/chị vẫn có thể thực hiện đăng ký khai sinh 【PROC_1_001193_c5_s0】【PROC_1_001193_c48_s0】.

### Thứ tự nên làm và Giấy tờ, cách thực hiện
- **Cơ quan tiếp nhận và giải quyết:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
- **Hồ sơ thay thế Giấy chứng sinh:** Theo quy định, nếu không có Giấy chứng sinh thì nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.
- **Cách thức nộp hồ sơ:** Nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp tại cơ quan 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết:** 1 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.
### Thủ tục áp dụng
- Thủ tục đăng ký khai sinh 【PROC_1_001193】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_001193_c5_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_001193_c48_s0` | ✅ Có |
| Nội dung bắt buộc | văn bản của người làm chứng / người làm chứng xác nhận | ✅ văn bản của người làm chứng |
| Nội dung bắt buộc | nếu không có người làm chứng / nếu không có người chứng kiến | ✅ nếu không có người làm chứng |
| Nội dung bắt buộc | cam đoan | ✅ cam đoan |
| Nội dung bắt buộc | ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã | ✅ ủy ban nhân dân cấp xã |
| Nội dung bắt buộc | 1 ngày / một ngày | ✅ 1 ngày |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (7/7 checks).
- Latency end-to-end: **21.993s**.
- Gemini: **2 calls**, input `6439`, output `541`, total `6980` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Trường hợp vợ sinh con tại nhà ở xã An Phú và không có Giấy chứng sinh của bệnh viện, bạn vẫn có thể thực hiện Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193)【PROC_1_001193_c5_s0】【PROC_1_001193_c48_s0】.

### Thứ tự nên làm
- Thực hiện **Thủ tục đăng ký khai sinh** tại cơ quan có thẩm quyền.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần nộp:** Trường hợp không có Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh (bản chính)【PROC_1_001193_c5_s0】.
- **Cơ quan tiếp nhận và giải quyết:** Ủy ban nhân dân cấp xã【PROC_1_001193_c48_s0】.
- **Cách thức thực hiện:** Nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết:** 1 ngày【PROC_1_001193_c48_s0】.
- **Lệ phí:** Miễn phí【PROC_1_001193_c48_s0】.

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_001193_c5_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_001193_c48_s0` | ✅ Có |
| Nội dung bắt buộc | văn bản của người làm chứng / người làm chứng xác nhận | ✅ văn bản của người làm chứng |
| Nội dung bắt buộc | nếu không có người làm chứng / nếu không có người chứng kiến | ✅ nếu không có người làm chứng |
| Nội dung bắt buộc | cam đoan | ✅ cam đoan |
| Nội dung bắt buộc | ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã | ✅ ủy ban nhân dân cấp xã |
| Nội dung bắt buộc | 1 ngày / một ngày | ✅ 1 ngày |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (7/7 checks).
- Latency end-to-end: **20.325s**.
- Gemini: **2 calls**, input `6466`, output `581`, total `7047` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.

---

## TC02 — Thường trú tại nhà thuê

### Câu hỏi

Tôi đang thuê nhà ở xã Tân Triều, có hợp đồng thuê nhà viết tay. Tôi muốn đăng ký thường trú về căn nhà thuê này thì cần điều kiện và giấy tờ gì, nộp cho Công an xã hay UBND xã?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_116788_c126_s0`, `PROC_1_116788_c127_s0`, `PROC_1_116788_c128_s0`, `PROC_1_116788_c174_s0`.
- Nội dung cần có: tờ khai thay đổi thông tin cư trú / ct01; công chứng / chứng thực; chủ sở hữu / chủ nhà; diện tích; công an xã / công an cấp xã / cơ quan đăng ký cư trú cấp xã; 7 ngày làm việc / bảy ngày làm việc.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: Không có.
- Thứ tự bước bắt buộc: Không áp dụng.

### Trả lời — Graph-RAG

Trường hợp bạn thuê nhà ở xã Tân Triều và có hợp đồng thuê nhà viết tay, bạn cần hoàn thiện các điều kiện và giấy tờ theo thủ tục **Đăng ký thường trú 【PROC_1_116788】** (Mã: PROC_1_116788) như sau:

### 1. Cơ quan tiếp nhận
- Cơ quan tiếp nhận và giải quyết hồ sơ là **Công an Xã** 【PROC_1_116788_c174_s0】.

### 2. Giấy tờ cần chuẩn bị
- **Tờ khai thay đổi thông tin cư trú** (mẫu CT01), trong đó có ý kiến đồng ý cho đăng ký thường trú của chủ sở hữu chỗ ở hợp pháp (trừ trường hợp đã có văn bản đồng ý riêng) 【PROC_1_116788_c124_s0】.
- **Hợp đồng thuê chỗ ở hợp pháp**: Do bạn mới có hợp đồng viết tay, quy định yêu cầu hợp đồng thuê nhà phải được **công chứng hoặc chứng thực** theo quy định của pháp luật 【PROC_1_116788_c127_s0】. Vì vậy, bạn cần tiến hành công chứng hoặc chứng thực hợp đồng thuê nhà trước khi nộp hồ sơ.
- **Thông tin chứng minh đủ diện tích nhà ở** để đăng ký thường trú tại chỗ ở đi thuê: Được khai thác trên hệ thống điện tử hoặc xuất trình giấy tờ, tài liệu thể hiện diện tích nhà ở hoặc xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân 【PROC_1_116788_c128_s0】.

### 3. Cách thức thực hiện và thời gian
- **Hình thức:** Trực tuyến hoặc trực tiếp 【PROC_1_116788_c174_s3】.
- **Thời gian giải quyết:** 07 ngày làm việc kể từ ngày nhận được hồ sơ đầy đủ và chính xác 【PROC_1_116788_c174_s3】.
- **Lệ phí:** 20.000 đồng/lần nếu nộp trực tiếp hoặc 10.000 đồng/lần nếu nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_116788_c126_s0` | ❌ Thiếu |
| Citation bắt buộc | `PROC_1_116788_c127_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_116788_c128_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_116788_c174_s0` | ✅ Có |
| Nội dung bắt buộc | tờ khai thay đổi thông tin cư trú / ct01 | ✅ tờ khai thay đổi thông tin cư trú |
| Nội dung bắt buộc | công chứng / chứng thực | ✅ công chứng |
| Nội dung bắt buộc | chủ sở hữu / chủ nhà | ✅ chủ sở hữu |
| Nội dung bắt buộc | diện tích | ✅ diện tích |
| Nội dung bắt buộc | công an xã / công an cấp xã / cơ quan đăng ký cư trú cấp xã | ✅ công an xã |
| Nội dung bắt buộc | 7 ngày làm việc / bảy ngày làm việc | ✅ 7 ngày làm việc |

#### Quan sát benchmark

- Điểm rubric: **90.0/100** (9/10 checks).
- Latency end-to-end: **15.807s**.
- Gemini: **2 calls**, input `8910`, output `807`, total `9717` tokens.
- Citation bị thiếu theo rubric: `PROC_1_116788_c126_s0`.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu citation `PROC_1_116788_c126_s0`
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Để đăng ký thường trú tại chỗ ở thuê ở xã Tân Triều (mã thủ tục: PROC_1_116788), cơ quan tiếp nhận hồ sơ là Công an Xã 【PROC_1_116788_c174_s0】. Do bạn sử dụng hợp đồng thuê nhà viết tay, bạn cần lưu ý quy định yêu cầu hợp đồng thuê nhà phải được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】. Bạn cần hoàn thiện điều kiện công chứng hoặc chứng thực hợp đồng thuê nhà và có văn bản đồng ý của chủ sở hữu trước khi nộp hồ sơ.

### Thứ tự nên làm
1. Hoàn thiện giấy tờ pháp lý về chỗ ở thuê (công chứng/chứng thực hợp đồng và lấy ý kiến đồng ý của chủ sở hữu).
2. Nộp hồ sơ đăng ký thường trú cho Công an Xã 【PROC_1_116788_c174_s0】.

### Giấy tờ và cách thực hiện
- **Thành phần hồ sơ**:
  - Tờ khai thay đổi thông tin cư trú (mẫu CT01), trong đó có ghi rõ ý kiến đồng ý cho đăng ký thường trú của chủ hộ hoặc chủ sở hữu chỗ ở hợp pháp 【PROC_1_116788_c124_s0】.
  - Hợp đồng cho thuê chỗ ở hợp pháp được công chứng hoặc chứng thực theo quy định của pháp luật 【PROC_1_116788_c127_s0】.
  - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú hoặc giấy tờ, tài liệu thể hiện diện tích nhà ở / xác nhận của Ủy ban nhân dân cấp xã 【PROC_1_116788_c128_s0】.
- **Cách thức thực hiện và thời gian**: Nộp trực tuyến hoặc trực tiếp tại Công an Xã 【PROC_1_116788_c174_s0】, 【PROC_1_116788_c174_s3】. Thời gian giải quyết là 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ 【PROC_1_116788_c174_s3】.
- **Lệ phí**: 20.000 đồng/lần nếu nộp trực tiếp hoặc 10.000 đồng/lần nếu nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.
### Thủ tục áp dụng
- Đăng ký thường trú 【PROC_1_116788】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_116788_c126_s0` | ❌ Thiếu |
| Citation bắt buộc | `PROC_1_116788_c127_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_116788_c128_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_116788_c174_s0` | ✅ Có |
| Nội dung bắt buộc | tờ khai thay đổi thông tin cư trú / ct01 | ✅ tờ khai thay đổi thông tin cư trú |
| Nội dung bắt buộc | công chứng / chứng thực | ✅ công chứng |
| Nội dung bắt buộc | chủ sở hữu / chủ nhà | ✅ chủ sở hữu |
| Nội dung bắt buộc | diện tích | ✅ diện tích |
| Nội dung bắt buộc | công an xã / công an cấp xã / cơ quan đăng ký cư trú cấp xã | ✅ công an xã |
| Nội dung bắt buộc | 7 ngày làm việc / bảy ngày làm việc | ✅ 7 ngày làm việc |

#### Quan sát benchmark

- Điểm rubric: **90.0/100** (9/10 checks).
- Latency end-to-end: **16.770s**.
- Gemini: **2 calls**, input `8941`, output `864`, total `9805` tokens.
- Citation bị thiếu theo rubric: `PROC_1_116788_c126_s0`.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu citation `PROC_1_116788_c126_s0`
- Fallback: Không.

---

## TC03 — Liên thông VNeID bốn thủ tục

### Câu hỏi

Tôi muốn làm thủ tục liên thông trên VNeID để vừa khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho con tôi dưới 6 tuổi. Các bước hệ thống xử lý như thế nào và mất bao nhiêu ngày làm việc?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c181_s0`, `PROC_3_000722_c182_s1`, `PROC_3_000722_c183_s1`, `PROC_3_000722_c184_s0`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: vneid / cổng dịch vụ công quốc gia / cổng dvcqg; 24 giờ / 24h / 24 h; giấy khai sinh điện tử / bản điện tử giấy khai sinh; kết quả đăng ký thường trú / kết quả thường trú; theo yêu cầu / có đề nghị / đã đề nghị / nếu đề nghị / đã yêu cầu; 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc; 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: Không có.
- Thứ tự bước bắt buộc: `PROC_3_000722_c180_s1` → `PROC_3_000722_c181_s0` → `PROC_3_000722_c182_s1` → `PROC_3_000722_c183_s1` → `PROC_3_000722_c184_s0`.

### Trả lời — Graph-RAG

Để thực hiện thủ tục liên thông gồm đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi, bạn cần thực hiện theo các bước hệ thống xử lý và thời gian quy định tại mã thủ tục 【PROC_3_000722】.

### Kênh nộp hồ sơ
Người dân nộp hồ sơ liên thông trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】【PROC_3_000722_c185_s0】.

### Thành phần hồ sơ
- Tờ khai điện tử Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP 【PROC_3_000722_c176_s0】.
- Dữ liệu điện tử có ký số của Giấy chứng sinh được liên thông từ cơ sở khám chữa bệnh hoặc bản điện tử/bản chụp giấy tờ thay thế do người yêu cầu đính kèm 【PROC_3_000722_c177_s0】.
- Trường hợp đăng ký thường trú cho trẻ em khác nơi thường trú của cha mẹ thì đính kèm các thành phần hồ sơ theo pháp luật về cư trú 【PROC_3_000722_c178_s0】.
- Các giấy tờ bằng giấy phải được số hóa theo quy định 【PROC_3_000722_c179_s0】.

### Quy trình các bước hệ thống xử lý (Mã: PROC_3_000722)
- **Bước 1:** Người yêu cầu truy cập Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và nộp lệ phí 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách hồ sơ và chuyển sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp để đồng bộ về Hệ thống đăng ký, quản lý hộ tịch điện tử 【PROC_3_000722_c181_s0】.
- **Bước 3:** Công chức hộ tịch tại Ủy ban nhân dân cấp xã giải quyết đăng ký khai sinh trong 24 giờ kể từ khi nhận đủ hồ sơ hợp lệ, đồng thời xem xét hỗ trợ tài chính khi sinh con (nếu có); trường hợp cần bổ sung hồ sơ, người yêu cầu hoàn thiện trong 07 ngày làm việc 【PROC_3_000722_c182_s1】【PROC_3_000722_c182_s3】.
- **Bước 4:** Sau khi bản điện tử Giấy khai sinh được chuyển lên cổng, hệ thống tiếp tục chuyển đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi 【PROC_3_000722_c183_s1】. Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục đăng ký thường trú 【REL:PROC_1_001193:NEXT_STEP:PROC_1_116788】. Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục thủ tục cấp thẻ bảo hiểm y tế 【REL:PROC_1_001193:NEXT_STEP:PROC_1_014137】.
- **Bước 5:** Khi người đại diện có đề nghị cấp thẻ căn cước, sau khi có kết quả đăng ký thường trú, hệ thống chuyển hồ sơ sang Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để cấp thẻ căn cước cho trẻ 【PROC_3_000722_c184_s0】. Hệ thống tự chuyển Thông báo kết quả đăng ký thường trú để xử lý thủ tục cấp, cấp đổi, cấp lại thẻ căn cước 【REL:PROC_1_116788:NEXT_STEP:PROC_1_116410】.

### Thời gian giải quyết
- Thời gian giải quyết chung là Ba (03) ngày làm việc kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định; trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】.
- Thời gian giải quyết cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử từ Phần mềm dịch vụ công liên thông 【PROC_3_000722_c183_s2】.

### Thủ tục áp dụng
- Thủ tục đăng ký khai sinh 【PROC_1_001193】
- Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】
- Đăng ký thường trú 【PROC_1_116788】
- Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_3_000722_c180_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c181_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c182_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c183_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c184_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c185_s0` | ✅ Có |
| Nội dung bắt buộc | vneid / cổng dịch vụ công quốc gia / cổng dvcqg | ✅ vneid |
| Nội dung bắt buộc | 24 giờ / 24h / 24 h | ✅ 24 giờ |
| Nội dung bắt buộc | giấy khai sinh điện tử / bản điện tử giấy khai sinh | ✅ giấy khai sinh điện tử |
| Nội dung bắt buộc | kết quả đăng ký thường trú / kết quả thường trú | ✅ kết quả đăng ký thường trú |
| Nội dung bắt buộc | theo yêu cầu / có đề nghị / đã đề nghị / nếu đề nghị / đã yêu cầu | ✅ có đề nghị |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ năm (05) ngày làm việc |
| Thứ tự bước | `PROC_3_000722_c180_s1` → `PROC_3_000722_c181_s0` → `PROC_3_000722_c182_s1` → `PROC_3_000722_c183_s1` → `PROC_3_000722_c184_s0` | ✅ Đúng thứ tự |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (14/14 checks).
- Latency end-to-end: **29.030s**.
- Gemini: **3 calls**, input `27717`, output `2421`, total `30138` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.
- Warning: Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Để thực hiện nhóm thủ tục hành chính liên thông (đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi), bạn có thể nộp hồ sơ trực tuyến qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】【PROC_3_000722_c185_s0】.

### Thứ tự nên làm (Các bước xử lý của hệ thống)
- **Bước 1:** Người yêu cầu truy cập Cổng Dịch vụ công quốc gia hoặc VNeID để nộp hồ sơ trực tuyến và đóng lệ phí 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp 【PROC_3_000722_c181_s0】.
- **Bước 3:** Ủy ban nhân dân cấp xã giải quyết hồ sơ đăng ký khai sinh trong 24 giờ kể từ khi Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp nhận đủ hồ sơ hợp lệ và xem xét hỗ trợ kinh phí khi sinh con (nếu có) 【PROC_3_000722_c182_s1】.
- **Bước 4:** Chuyển bản điện tử Giấy khai sinh sang Cổng Dịch vụ công quốc gia, sau đó Cổng Dịch vụ công quốc gia phân tách, chuyển hồ sơ điện tử đến Hệ thống thông tin quản lý cư trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế 【PROC_3_000722_c183_s1】; thời hạn giải quyết cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi không quá 02 ngày làm việc, kể từ ngày nhận được hồ sơ điện tử từ Phần mềm dịch vụ công liên thông 【PROC_3_000722_c183_s2】.
- **Bước 5:** Hệ thống sản xuất, cấp và quản lý căn cước thực hiện cấp thẻ căn cước khi có đề nghị 【PROC_3_000722_c184_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần chuẩn bị:** Tờ khai điện tử Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP 【PROC_3_000722_c176_s0】, dữ liệu điện tử hoặc bản điện tử Giấy chứng sinh (hoặc giấy tờ thay thế) 【PROC_3_000722_c177_s0】, và các giấy tờ cư trú liên quan nếu đăng ký thường trú khác nơi cư trú của cha mẹ 【PROC_3_000722_c178_s0】.
- **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi cơ quan có thẩm quyền nhận đầy đủ hồ sơ, trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】.
- **Lệ phí:** Miễn phí thủ tục liên thông (phí, lệ phí khác theo quy định của các thủ tục tương ứng nếu có) 【PROC_3_000722_c185_s0】.

### Thủ tục áp dụng
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_3_000722_c180_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c181_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c182_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c183_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c184_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c185_s0` | ✅ Có |
| Nội dung bắt buộc | vneid / cổng dịch vụ công quốc gia / cổng dvcqg | ✅ vneid |
| Nội dung bắt buộc | 24 giờ / 24h / 24 h | ✅ 24 giờ |
| Nội dung bắt buộc | giấy khai sinh điện tử / bản điện tử giấy khai sinh | ✅ bản điện tử giấy khai sinh |
| Nội dung bắt buộc | kết quả đăng ký thường trú / kết quả thường trú | ❌ Thiếu toàn bộ nhóm |
| Nội dung bắt buộc | theo yêu cầu / có đề nghị / đã đề nghị / nếu đề nghị / đã yêu cầu | ✅ có đề nghị |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ năm (05) ngày làm việc |
| Thứ tự bước | `PROC_3_000722_c180_s1` → `PROC_3_000722_c181_s0` → `PROC_3_000722_c182_s1` → `PROC_3_000722_c183_s1` → `PROC_3_000722_c184_s0` | ✅ Đúng thứ tự |

#### Quan sát benchmark

- Điểm rubric: **92.9/100** (13/14 checks).
- Latency end-to-end: **24.937s**.
- Gemini: **3 calls**, input `16792`, output `1806`, total `18598` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu nội dung `kết quả đăng ký thường trú / kết quả thường trú`
- Fallback: Không.

---

## TC05 — BHYT khi chưa đăng ký khai sinh

### Câu hỏi

Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c176_s0`, `PROC_3_000722_c183_s2`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: liên thông; vneid / cổng dịch vụ công quốc gia / cổng dvcqg; có thể nộp hồ sơ liên thông ngay / có thể nộp ngay qua vneid / có thể nộp ngay qua cổng dịch vụ công quốc gia; giấy khai sinh điện tử / bản điện tử giấy khai sinh; bảo hiểm xã hội / bhxh; mẫu số 01 / mẫu số 1 / mẫu 01; 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc; 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc; 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc; xác minh; nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: phải hoàn tất khai sinh rồi mới được nộp liên thông / phải có giấy khai sinh trước khi nộp hồ sơ liên thông.
- Thứ tự bước bắt buộc: Không áp dụng.

### Trả lời — Graph-RAG

Bạn có thể nộp hồ sơ liên thông ngay qua VNeID hoặc Cổng Dịch vụ công quốc gia; không cần có sẵn Giấy khai sinh điện tử. Sau khi tiếp nhận hồ sơ, hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục đích. 【PROC_3_000722_c180_s1】 【REL:PROC_1_001193:NEXT_STEP:PROC_1_014137】

Bạn không thể đến cơ quan Bảo hiểm xã hội để xin cấp thẻ bảo hiểm y tế trước một cách độc lập cho trẻ 1 tháng tuổi chưa có giấy khai sinh, vì đối với trẻ em dưới 6 tuổi, việc cấp thẻ bảo hiểm y tế phải được thực hiện liên thông cùng với thủ tục đăng ký khai sinh và đăng ký thường trú 【PROC_1_014137_c60_s0】.

### Thứ tự nên làm và Phương án thực hiện
Bạn có hai phương án để thực hiện:

1. **Phương án sử dụng gói Liên thông điện tử (Khuyên dùng):**
   - **Lý do cần làm:** Giải quyết đồng thời đăng ký khai sinh, đăng ký thường trú và cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi mà không cần nộp hồ sơ riêng lẻ từng thủ tục 【PROC_1_014137_c60_s0】.
   - **Cách thực hiện:** Nộp hồ sơ trực tuyến qua Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.
   - **Hồ sơ cần nộp:** Tờ khai điện tử Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP 【PROC_3_000722_c176_s0】 và dữ liệu điện tử hoặc bản điện tử Giấy chứng sinh 【PROC_3_000722_c177_s0】.
   - **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi nhận đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá năm (05) ngày làm việc. Thời gian cấp thẻ bảo hiểm y tế không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử 【PROC_3_000722_c185_s0】【PROC_3_000722_c183_s2】.
   - **Lệ phí:** Miễn phí (phí, lệ phí theo quy định của các thủ tục tương ứng) 【PROC_3_000722_c185_s0】.
   - Kết quả khai sinh được hệ thống tự chuyển sang thường trú 【REL:PROC_1_001193:NEXT_STEP:PROC_1_116788】.
   - Sau khi có bản điện tử Giấy khai sinh, hệ thống sẽ chuyển hồ sơ BHYT sang cơ quan Bảo hiểm xã hội để giải quyết 【PROC_3_000722_c183_s1】.

2. **Phương án thủ tục cấp thẻ bảo hiểm y tế đơn lẻ:**
   - **Lý do cần làm:** Cấp thẻ bảo hiểm y tế cho người tham gia theo hình thức thông thường 【PROC_1_014137_c61_s0】.
   - **Cách thực hiện:** Nộp hồ sơ trực tuyến, qua dịch vụ bưu chính công ích hoặc trực tiếp tại bộ phận một cửa của cơ quan bảo hiểm xã hội 【PROC_1_014137_c53_s0】【PROC_1_014137_c61_s0】.
   - **Hồ sơ cần nộp:** Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c50_s0】.
   - **Thời gian giải quyết:** 05 ngày làm việc kể từ ngày nhận đủ hồ sơ 【PROC_1_014137_c61_s0】.
   - **Lệ phí:** Miễn phí 【PROC_1_014137_c61_s0】.
### Thủ tục áp dụng
- Thủ tục đăng ký khai sinh 【PROC_1_001193】
- Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】
- Đăng ký thường trú 【PROC_1_116788】
- Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_3_000722_c180_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c176_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c183_s2` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c185_s0` | ✅ Có |
| Nội dung bắt buộc | liên thông | ✅ liên thông |
| Nội dung bắt buộc | vneid / cổng dịch vụ công quốc gia / cổng dvcqg | ✅ vneid |
| Nội dung bắt buộc | có thể nộp hồ sơ liên thông ngay / có thể nộp ngay qua vneid / có thể nộp ngay qua cổng dịch vụ công quốc gia | ✅ có thể nộp hồ sơ liên thông ngay |
| Nội dung bắt buộc | giấy khai sinh điện tử / bản điện tử giấy khai sinh | ✅ giấy khai sinh điện tử |
| Nội dung bắt buộc | bảo hiểm xã hội / bhxh | ✅ bảo hiểm xã hội |
| Nội dung bắt buộc | mẫu số 01 / mẫu số 1 / mẫu 01 | ✅ mẫu số 01 |
| Nội dung bắt buộc | 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc | ✅ 2 ngày làm việc |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ 5 ngày làm việc |
| Nội dung bắt buộc | xác minh | ✅ xác minh |
| Nội dung bắt buộc | nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử | ✅ nhận được hồ sơ điện tử |
| Nội dung cấm | phải hoàn tất khai sinh rồi mới được nộp liên thông / phải có giấy khai sinh trước khi nộp hồ sơ liên thông | ✅ Không khẳng định |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (16/16 checks).
- Latency end-to-end: **27.531s**.
- Gemini: **3 calls**, input `34491`, output `2185`, total `36676` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.
- Warning: Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Bạn không thể đến trực tiếp cơ quan Bảo hiểm xã hội để xin cấp thẻ BHYT riêng cho cháu trước khi làm giấy khai sinh. Đối với trẻ em dưới 6 tuổi, việc cấp thẻ BHYT được thực hiện thông qua gói thủ tục liên thông điện tử bao gồm đăng ký khai sinh, đăng ký thường trú và cấp thẻ bảo hiểm y tế 【PROC_3_000722_c183_s1】.

### Hành trình và cách thực hiện:
- **Lý do cần làm:** Thực hiện đồng thời đăng ký khai sinh, thường trú và cấp thẻ BHYT cho trẻ dưới 6 tuổi 【PROC_3_000722_c185_s0】.
- **Hồ sơ phổ biến:** Tờ khai điện tử Mẫu số 01 【PROC_3_000722_c176_s0】 và dữ liệu điện tử Giấy chứng sinh từ cơ sở khám chữa bệnh hoặc bản điện tử/bản chụp giấy tờ thay thế 【PROC_3_000722_c177_s0】.
- **Cách thực hiện:** Nộp hồ sơ trực tuyến qua Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.
- **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi cơ quan có thẩm quyền nhận đủ hồ sơ, trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】; riêng khâu cấp thẻ BHYT không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử từ phần mềm dịch vụ công liên thông 【PROC_3_000722_c183_s2】.
- **Lệ phí:** Miễn phí 【PROC_3_000722_c185_s0】.
### Thủ tục áp dụng
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_3_000722_c180_s1` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c176_s0` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c183_s2` | ✅ Có |
| Citation bắt buộc | `PROC_3_000722_c185_s0` | ✅ Có |
| Nội dung bắt buộc | liên thông | ✅ liên thông |
| Nội dung bắt buộc | vneid / cổng dịch vụ công quốc gia / cổng dvcqg | ✅ vneid |
| Nội dung bắt buộc | có thể nộp hồ sơ liên thông ngay / có thể nộp ngay qua vneid / có thể nộp ngay qua cổng dịch vụ công quốc gia | ❌ Thiếu toàn bộ nhóm |
| Nội dung bắt buộc | giấy khai sinh điện tử / bản điện tử giấy khai sinh | ❌ Thiếu toàn bộ nhóm |
| Nội dung bắt buộc | bảo hiểm xã hội / bhxh | ✅ bảo hiểm xã hội |
| Nội dung bắt buộc | mẫu số 01 / mẫu số 1 / mẫu 01 | ✅ mẫu số 01 |
| Nội dung bắt buộc | 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc | ✅ 2 ngày làm việc |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ năm (05) ngày làm việc |
| Nội dung bắt buộc | xác minh | ✅ xác minh |
| Nội dung bắt buộc | nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử | ✅ nhận được hồ sơ điện tử |
| Nội dung cấm | phải hoàn tất khai sinh rồi mới được nộp liên thông / phải có giấy khai sinh trước khi nộp hồ sơ liên thông | ✅ Không khẳng định |

#### Quan sát benchmark

- Điểm rubric: **87.5/100** (14/16 checks).
- Latency end-to-end: **15.464s**.
- Gemini: **2 calls**, input `9625`, output `661`, total `10286` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu nội dung `có thể nộp hồ sơ liên thông ngay / có thể nộp ngay qua vneid / có thể nộp ngay qua cổng dịch vụ công quốc gia`; thiếu nội dung `giấy khai sinh điện tử / bản điện tử giấy khai sinh`
- Fallback: Không.

---
