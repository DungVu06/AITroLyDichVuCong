# Nhật ký 8 câu trả lời — Graph-RAG vs RAG không đồ thị

- Thời điểm chạy UTC: 2026-11-24T05:01:31+00:00
- Model: `gemini-3.5-flash-lite`
- Mỗi ca được chạy độc lập; không mang hội thoại từ ca trước.
- Câu trả lời dưới đây là output nguyên văn đã được lưu từ 8 lượt chạy.

## TC01 — Khai sinh tại nhà không có Giấy chứng sinh

### Câu hỏi

Vợ tôi vừa sinh cháu tại nhà ở xã An Phú, không có Giấy chứng sinh của bệnh viện thì có làm giấy khai sinh được không? Tôi phải nộp hồ sơ ở đâu, cần giấy tờ gì thay thế và thời gian giải quyết bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_001193_c5_s0`, `PROC_1_001193_c48_s0`.
- Nội dung cần có: người làm chứng / người chứng kiến; cam đoan; ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã; 1 ngày / một ngày.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: Không có.

### Trả lời — Graph-RAG

Trường hợp sinh cháu tại nhà không có Giấy chứng sinh của bệnh viện hoàn toàn có thể làm được thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】. Cụ thể thủ tục cần thực hiện như sau:

### Thứ tự nên làm và Giấy tờ, cách thực hiện
- **Thủ tục đăng ký khai sinh** 【PROC_1_001193】:
  - **Lý do cần làm:** Ghi nhận khai sinh cho trẻ em.
  - **Hồ sơ phổ biến:** Trường hợp không có Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh (số lượng: 1 bản chính) 【PROC_1_001193_c5_s0】.
  - **Cách thực hiện:** Bạn có thể nộp hồ sơ trực tuyến, qua dịch vụ bưu chính hoặc nộp trực tiếp tại **Ủy ban nhân dân cấp xã** (tại xã An Phú) 【PROC_1_001193_c48_s0】.
  - **Thời gian giải quyết:** 1 ngày 【PROC_1_001193_c48_s0】.
  - **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_001193_c5_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_001193_c48_s0` | ✅ Có |
| Nội dung bắt buộc | người làm chứng / người chứng kiến | ✅ người làm chứng |
| Nội dung bắt buộc | cam đoan | ✅ cam đoan |
| Nội dung bắt buộc | ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã | ✅ ủy ban nhân dân cấp xã |
| Nội dung bắt buộc | 1 ngày / một ngày | ✅ 1 ngày |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (6/6 checks).
- Latency end-to-end: **25.005s**.
- Gemini: **2 calls**, input `6446`, output `564`, total `7010` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Trường hợp sinh con tại nhà và không có Giấy chứng sinh của bệnh viện, anh/chị vẫn có thể thực hiện thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】.

### Thứ tự nên làm và Giấy tờ, cách thực hiện
- **Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193):**
  - **Lý do cần làm:** Đăng ký khai sinh cho trẻ mới sinh.
  - **Hồ sơ cần chuẩn bị:** 
    - Trường hợp không có Giấy chứng sinh, anh/chị cần nộp **văn bản của người làm chứng xác nhận về việc sinh**; nếu không có người làm chứng thì phải có **giấy cam đoan về việc sinh** 【PROC_1_001193_c5_s0】.
  - **Nơi nộp và cơ quan giải quyết:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
  - **Cách thức thực hiện:** Nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp 【PROC_1_001193_c48_s0】.
  - **Thời gian giải quyết:** 1 ngày 【PROC_1_001193_c48_s0】.
  - **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.

*Lưu ý về căn cứ pháp lý:* Các căn cứ pháp lý liệt kê trong dữ liệu chưa được đối chiếu đầy đủ hiệu lực hiện hành.

#### Checklist rubric

| Nhóm | Tiêu chí | Kết quả |
|---|---|---|
| Citation bắt buộc | `PROC_1_001193_c5_s0` | ✅ Có |
| Citation bắt buộc | `PROC_1_001193_c48_s0` | ✅ Có |
| Nội dung bắt buộc | người làm chứng / người chứng kiến | ✅ người làm chứng |
| Nội dung bắt buộc | cam đoan | ✅ cam đoan |
| Nội dung bắt buộc | ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã | ✅ ủy ban nhân dân cấp xã |
| Nội dung bắt buộc | 1 ngày / một ngày | ✅ 1 ngày |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (6/6 checks).
- Latency end-to-end: **22.339s**.
- Gemini: **2 calls**, input `6465`, output `619`, total `7084` tokens.
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

### Trả lời — Graph-RAG

Để đăng ký thường trú tại chỗ ở thuê tại xã Tân Triều, bạn cần thực hiện thủ tục **Đăng ký thường trú 【PROC_1_116788】** (Mã: PROC_1_116788)【PROC_1_116788_c121_s0】.

### Thứ tự nên làm và cơ quan giải quyết
- **Cơ quan tiếp nhận và giải quyết:** Nộp hồ sơ trực tiếp hoặc trực tuyến tại **Công an Xã** 【PROC_1_116788_c174_s0】, 【PROC_1_116788_c174_s3】.
- Bạn cần hoàn thiện các điều kiện còn thiếu trước khi nộp hồ sơ, cụ thể hợp đồng thuê nhà viết tay hiện tại chưa đáp ứng quy định (yêu cầu phải được công chứng hoặc chứng thực) 【PROC_1_116788_c127_s0】.

### Giấy tờ và cách thực hiện
- **Thành phần hồ sơ:**
  - Tờ khai thay đổi thông tin cư trú (mẫu CT01), trong đó có ý kiến đồng ý cho đăng ký thường trú của chủ sở hữu chỗ ở hợp pháp 【PROC_1_116788_c124_s0】.
  - Hợp đồng hoặc văn bản về việc cho thuê chỗ ở hợp pháp được **công chứng hoặc chứng thực** theo quy định của pháp luật 【PROC_1_116788_c127_s0】.
  - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú được khai thác trên hệ thống điện tử hoặc giấy tờ/xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân 【PROC_1_116788_c128_s0】.
- **Cách thức thực hiện và thời gian:**
  - Hình thức: Trực tuyến hoặc trực tiếp 【PROC_1_116788_c174_s3】.
  - Thời gian giải quyết: 07 ngày làm việc kể từ ngày nhận được hồ sơ đầy đủ và chính xác 【PROC_1_116788_c174_s3】.
  - Lệ phí: 20.000 đồng/lần đăng ký khi nộp trực tiếp hoặc 10.000 đồng/lần khi nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.

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
- Latency end-to-end: **16.821s**.
- Gemini: **2 calls**, input `8903`, output `842`, total `9745` tokens.
- Citation bị thiếu theo rubric: `PROC_1_116788_c126_s0`.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu citation `PROC_1_116788_c126_s0`
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Để đăng ký thường trú tại nhà thuê ở xã Tân Triều, bạn cần thực hiện thủ tục đăng ký thường trú tại Công an Xã 【PROC_1_116788_c174_s0】.

### Thứ tự nên làm và Giấy tờ cần chuẩn bị
1. **Hoàn thiện điều kiện giấy tờ**: Vì bạn mới có hợp đồng thuê nhà viết tay, theo quy định, hợp đồng thuê nhà phải được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】. Bạn cần hoàn thiện việc công chứng hoặc chứng thực hợp đồng thuê nhà trước khi nộp hồ sơ.
2. **Thành phần hồ sơ đăng ký thường trú (Mã: PROC_1_116788)**:
   - Tờ khai thay đổi thông tin cư trú (mẫu CT01) có ý kiến đồng ý cho đăng ký thường trú của chủ hộ hoặc chủ sở hữu chỗ ở hợp pháp 【PROC_1_116788_c124_s0】.
   - Hợp đồng cho thuê chỗ ở hợp pháp đã được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】.
   - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú (khai thác trên ứng dụng định danh quốc gia hoặc giấy tờ, tài liệu thể hiện diện tích hoặc xác nhận của Ủy ban nhân dân cấp xã) 【PROC_1_116788_c128_s0】.

### Cách thực hiện, thời gian và lệ phí
- **Cơ quan tiếp nhận và giải quyết**: Công an Xã 【PROC_1_116788_c174_s0】.
- **Hình thức và Lệ phí**:
  - Nộp trực tuyến qua cổng dịch vụ công: 10.000 đồng/lần 【PROC_1_116788_c174_s3】.
  - Nộp trực tiếp: 20.000 đồng/lần 【PROC_1_116788_c174_s3】.
- **Thời gian giải quyết**: 07 ngày làm việc kể từ ngày nhận được hồ sơ đầy đủ và chính xác 【PROC_1_116788_c174_s3】.
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
- Latency end-to-end: **17.317s**.
- Gemini: **2 calls**, input `8941`, output `815`, total `9756` tokens.
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

### Trả lời — Graph-RAG

Để thực hiện gói liên thông điện tử bao gồm đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi, bạn có thể thực hiện theo các bước xử lý của hệ thống và thông tin chi tiết như sau 【PROC_3_000722_c180_s1】.

### Kênh nộp hồ sơ
- Người dân nộp hồ sơ liên thông trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】.

### Thành phần hồ sơ phổ biến
- Tờ khai điện tử (Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP) 【PROC_3_000722_c176_s0】.
- Dữ liệu điện tử có ký số của Giấy chứng sinh được liên thông từ cơ sở khám bệnh, chữa bệnh hoặc bản điện tử Giấy chứng sinh do người yêu cầu đính kèm 【PROC_3_000722_c177_s0】.
- Trường hợp đăng ký thường trú cho trẻ em khác nơi thường trú của cha, mẹ thì đính kèm các thành phần hồ sơ theo quy định pháp luật về cư trú 【PROC_3_000722_c178_s0】.

### Các bước hệ thống xử lý
- Bước 1: Người yêu cầu truy cập vào Cổng Dịch vụ công quốc gia hoặc trên ứng dụng VNeID, lựa chọn dịch vụ công liên thông để thực hiện nộp hồ sơ trực tuyến và lệ phí theo quy định 【PROC_3_000722_c180_s1】.
- Bước 2: Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp, sau đó đồng bộ về Hệ thống đăng ký, quản lý hộ tịch điện tử 【PROC_3_000722_c181_s0】.
- Bước 3: Người thực hiện công tác hộ tịch tại Ủy ban nhân dân cấp xã thực hiện nghiệp vụ đăng ký khai sinh trong 24 giờ kể từ khi nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s1】.
- Bước 4: Sau khi chuyển bản điện tử Giấy khai sinh, hệ thống tiếp tục chuyển dữ liệu đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để thực hiện cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi 【PROC_3_000722_c183_s1】.
- Bước 5: Sau khi có kết quả đăng ký thường trú, hệ thống chuyển hồ sơ đến Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước (khi người đại diện hợp pháp có đề nghị) 【PROC_3_000722_c184_s0】.
- Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục đăng ký thường trú. Người dân không phải tự chuyển giấy tờ này giữa các cơ quan trong gói liên thông 【REL:PROC_1_001193:NEXT_STEP:PROC_1_116788】.
- Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục thủ tục cấp thẻ bảo hiểm y tế. Người dân không phải tự chuyển giấy tờ này giữa các cơ quan trong gói liên thông 【REL:PROC_1_001193:NEXT_STEP:PROC_1_014137】.
- Hệ thống tự chuyển Thông báo kết quả đăng ký thường trú để xử lý thủ tục cấp, cấp đổi, cấp lại thẻ căn cước. Nhánh này chỉ áp dụng khi người đại diện hợp pháp đề nghị cấp thẻ lúc nộp hồ sơ trực tuyến 【REL:PROC_1_116788:NEXT_STEP:PROC_1_116410】.

### Thời gian và lệ phí giải quyết
- Thời gian giải quyết: Ba (03) ngày làm việc kể từ khi các cơ quan có thẩm quyền giải quyết nhận đầy đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】.
- Lệ phí: Miễn phí (phí, lệ phí theo quy định của các thủ tục hành chính tương ứng) 【PROC_3_000722_c185_s0】.

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

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (13/13 checks).
- Latency end-to-end: **28.341s**.
- Gemini: **3 calls**, input `27468`, output `2328`, total `29796` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.
- Warning: Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Để thực hiện nhóm thủ tục hành chính liên thông (đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi), bạn có thể tiến hành trực tuyến qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia theo mã thủ tục 【PROC_3_000722_c180_s1】.

### Thứ tự nên làm và các bước hệ thống xử lý (Mã: 【PROC_3_000722】)
- **Bước 1:** Người yêu cầu truy cập vào Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) hoặc trên ứng dụng VNeID, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và đóng lệ phí theo quy định 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp 【PROC_3_000722_c181_s0】.
- **Bước 3:** Cán bộ hộ tịch tại Ủy ban nhân dân cấp xã giải quyết hồ sơ đăng ký khai sinh trong 24 giờ kể từ khi Hệ thống đăng ký, quản lý hộ tịch điện tử nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s1】.
- **Bước 4:** Sau khi chuyển bản điện tử Giấy khai sinh, hệ thống tiếp tục chuyển hồ sơ điện tử đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi 【PROC_3_000722_c183_s1】.
- **Bước 5:** Sau khi có thông báo kết quả đăng ký thường trú, hệ thống chuyển hồ sơ đến hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để cấp thẻ căn cước theo yêu cầu 【PROC_3_000722_c184_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần chuẩn bị:** Tờ khai điện tử (Mẫu số 01 theo Nghị định số 301/2026/NĐ-CP) 【PROC_3_000722_c176_s0】 và dữ liệu điện tử có ký số của Giấy chứng sinh (hoặc bản điện tử/bản chụp giấy tờ thay thế) 【PROC_3_000722_c177_s0】.
- **Cách thức thực hiện:** Nộp hồ sơ trực tuyến tại cơ quan tiếp nhận và giải quyết là Công an cấp Xã 【PROC_3_000722_c185_s0】.
- **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định; trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】.
- **Lệ phí:** Miễn phí thủ tục (phí, lệ phí theo quy định của các thủ tục hành chính tương ứng) 【PROC_3_000722_c185_s0】.

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
| Nội dung bắt buộc | kết quả đăng ký thường trú / kết quả thường trú | ✅ kết quả đăng ký thường trú |
| Nội dung bắt buộc | theo yêu cầu / có đề nghị / đã đề nghị / nếu đề nghị / đã yêu cầu | ✅ theo yêu cầu |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ năm (05) ngày làm việc |

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (13/13 checks).
- Latency end-to-end: **17.096s**.
- Gemini: **2 calls**, input `9181`, output `981`, total `10162` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: Không có.
- Fallback: Không.

---

## TC05 — BHYT khi chưa đăng ký khai sinh

### Câu hỏi

Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c176_s0`, `PROC_3_000722_c183_s2`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: liên thông; vneid / cổng dịch vụ công quốc gia / cổng dvcqg; có thể nộp ngay / nộp hồ sơ liên thông ngay / chưa có giấy khai sinh; giấy khai sinh điện tử / bản điện tử giấy khai sinh; bảo hiểm xã hội / bhxh; mẫu số 01 / mẫu số 1 / mẫu 01; 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc; 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc; 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc; xác minh; nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử.
- Citation không được xuất hiện: Không có.
- Nội dung không được khẳng định: phải hoàn tất khai sinh rồi mới được nộp liên thông / phải có giấy khai sinh trước khi nộp hồ sơ liên thông.

### Trả lời — Graph-RAG

Bạn không thể tự ý đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT riêng lẻ cho trẻ 1 tháng tuổi chưa làm giấy khai sinh. Theo quy định, đối với trẻ em dưới 6 tuổi, việc cấp thẻ BHYT được thực hiện liên thông cùng với thủ tục đăng ký khai sinh và đăng ký thường trú 【PROC_1_014137_c60_s0】.

### Thứ tự nên làm
Bạn nên thực hiện gói thủ tục hành chính liên thông điện tử bao gồm đăng ký khai sinh, đăng ký thường trú và cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi 【PROC_3_000722】.

### Giấy tờ và cách thực hiện
1. **Kênh nộp hồ sơ:** Người dân nộp hồ sơ liên thông trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】.
2. **Hồ sơ cần chuẩn bị:**
   - Tờ khai điện tử theo Mẫu số 01 【PROC_3_000722_c176_s0】.
   - Dữ liệu điện tử có ký số của Giấy chứng sinh hoặc bản điện tử/bản chụp giấy tờ thay thế theo quy định 【PROC_3_000722_c177_s0】.
3. **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】.
4. **Lệ phí:** Miễn phí 【PROC_3_000722_c185_s0】.

### Các bước chuyển đổi hồ sơ liên thông
- Kết quả khai sinh chuyển sang thường trú 【REL:PROC_1_001193:NEXT_STEP:PROC_1_116788】.
- Kết quả khai sinh chuyển sang BHYT 【REL:PROC_1_001193:NEXT_STEP:PROC_1_014137】.
- Chuyển hồ sơ BHYT sau khai sinh qua hệ thống điện tử chứa bản điện tử Giấy khai sinh tới Bảo hiểm xã hội 【PROC_3_000722_c183_s1】.
- Thời hạn khâu BHYT liên thông là không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử 【PROC_3_000722_c183_s2】.

### Phương án đơn lẻ (tham khảo)
- Tờ khai BHYT của phương án đơn lẻ sử dụng Mẫu số 2 【PROC_1_014137_c50_s0】.
- Cách nộp BHYT của phương án đơn lẻ áp dụng hình thức trực tuyến 【PROC_1_014137_c61_s0】.
- Thời hạn cấp thẻ BHYT của phương án đơn lẻ là 05 ngày làm việc 【PROC_1_014137_c61_s0】.

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
| Nội dung bắt buộc | có thể nộp ngay / nộp hồ sơ liên thông ngay / chưa có giấy khai sinh | ❌ Thiếu toàn bộ nhóm |
| Nội dung bắt buộc | giấy khai sinh điện tử / bản điện tử giấy khai sinh | ✅ bản điện tử giấy khai sinh |
| Nội dung bắt buộc | bảo hiểm xã hội / bhxh | ✅ bảo hiểm xã hội |
| Nội dung bắt buộc | mẫu số 01 / mẫu số 1 / mẫu 01 | ✅ mẫu số 01 |
| Nội dung bắt buộc | 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc | ✅ 2 ngày làm việc |
| Nội dung bắt buộc | 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc | ✅ ba (03) ngày làm việc |
| Nội dung bắt buộc | 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc | ✅ 5 ngày làm việc |
| Nội dung bắt buộc | xác minh | ✅ xác minh |
| Nội dung bắt buộc | nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử | ✅ nhận được hồ sơ điện tử |
| Nội dung cấm | phải hoàn tất khai sinh rồi mới được nộp liên thông / phải có giấy khai sinh trước khi nộp hồ sơ liên thông | ✅ Không khẳng định |

#### Quan sát benchmark

- Điểm rubric: **93.8/100** (15/16 checks).
- Latency end-to-end: **26.794s**.
- Gemini: **3 calls**, input `34007`, output `1516`, total `35523` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu nội dung `có thể nộp ngay / nộp hồ sơ liên thông ngay / chưa có giấy khai sinh`
- Fallback: Không.
- Warning: Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Theo quy định, bạn không thể đến trực tiếp cơ quan Bảo hiểm xã hội để xin cấp thẻ BHYT riêng lẻ trước cho trẻ chưa có giấy khai sinh 【PROC_3_000722_c183_s1】 mà cần thực hiện đồng thời qua nhóm thủ tục hành chính liên thông điện tử (đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi) 【PROC_3_000722_c185_s0】.

### Thứ tự nên làm
- Nộp hồ sơ trực tuyến qua Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần chuẩn bị:** Tờ khai điện tử Mẫu số 01 và dữ liệu điện tử/bản điện tử Giấy chứng sinh 【PROC_3_000722_c176_s0】【PROC_3_000722_c177_s0】.
- **Cách thực hiện:** Nộp hồ sơ trực tuyến 【PROC_3_000722_c185_s0】.
- **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi các cơ quan có thẩm quyền giải quyết nhận đầy đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá năm (05) ngày làm việc 【PROC_3_000722_c185_s0】; trong đó thời gian cấp thẻ BHYT cho trẻ em dưới 6 tuổi không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử từ Phần mềm dịch vụ công liên thông 【PROC_3_000722_c183_s2】.
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
| Nội dung bắt buộc | có thể nộp ngay / nộp hồ sơ liên thông ngay / chưa có giấy khai sinh | ✅ chưa có giấy khai sinh |
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

- Điểm rubric: **93.8/100** (15/16 checks).
- Latency end-to-end: **16.952s**.
- Gemini: **2 calls**, input `9653`, output `694`, total `10347` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Mục không đạt: thiếu nội dung `giấy khai sinh điện tử / bản điện tử giấy khai sinh`
- Fallback: Không.

---
