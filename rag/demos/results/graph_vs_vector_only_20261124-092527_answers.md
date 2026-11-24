# Nhật ký 10 câu trả lời — Graph-RAG vs RAG không đồ thị

- Thời điểm chạy UTC: 2026-11-24T02:25:27+00:00
- Model: `gemini-3.5-flash-lite`
- Mỗi ca được chạy độc lập; không mang hội thoại từ ca trước.
- Câu trả lời dưới đây là output nguyên văn đã được lưu từ 10 lượt chạy.

## TC01 — Khai sinh tại nhà không có Giấy chứng sinh

### Câu hỏi

Vợ tôi vừa sinh cháu tại nhà ở xã An Phú, không có Giấy chứng sinh của bệnh viện thì có làm giấy khai sinh được không? Tôi phải nộp hồ sơ ở đâu, cần giấy tờ gì thay thế và thời gian giải quyết bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_001193_c5_s0`, `PROC_1_001193_c48_s0`.
- Nội dung cần có: người làm chứng / cam đoan; ủy ban nhân dân cấp xã; 1 ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

Trường hợp sinh con tại nhà và không có Giấy chứng sinh của bệnh viện, anh/chị vẫn có thể thực hiện **Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193)** 【PROC_1_001193_c5_s0】.

### Thứ tự nên làm và Giấy tờ, cách thực hiện
- **Hồ sơ thay thế Giấy chứng sinh:** Theo quy định, trường hợp không có Giấy chứng sinh thì nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải nộp giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.
- **Nơi nộp hồ sơ:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
- **Hình thức nộp:** Có thể nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết:** 1 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (5/5 checks).
- Latency end-to-end: **67.713s**.
- Gemini: **2 calls**, input `6443`, output `539`, total `6982` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Trường hợp sinh con tại nhà và không có Giấy chứng sinh, bạn vẫn có thể thực hiện Thủ tục đăng ký khai sinh 【PROC_1_001193】 【PROC_1_001193_c5_s0】.

### Thứ tự nên làm và Giấy tờ, cách thực hiện
- **Cơ quan tiếp nhận và giải quyết:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
- **Hồ sơ thay thế Giấy chứng sinh:** Trường hợp không có Giấy chứng sinh thì nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.
- **Cách thức nộp hồ sơ:** Nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết và lệ phí:** 1 ngày và miễn phí 【PROC_1_001193_c48_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (5/5 checks).
- Latency end-to-end: **20.511s**.
- Gemini: **2 calls**, input `6458`, output `485`, total `6943` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC02 — Thường trú tại nhà thuê

### Câu hỏi

Tôi đang thuê nhà ở xã Tân Triều, có hợp đồng thuê nhà viết tay. Tôi muốn đăng ký thường trú về căn nhà thuê này thì cần điều kiện và giấy tờ gì, nộp cho Công an xã hay UBND xã?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_116788_c127_s0`, `PROC_1_116788_c142_s2`, `PROC_1_116788_c128_s0`, `PROC_1_116788_c174_s0`.
- Nội dung cần có: công chứng / chứng thực; chủ sở hữu; diện tích; công an xã; 07 ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

**Lỗi run:** `InternalServerError: Error code: 503 - {'error': {'message': 'gemini-3.5-flash-lite is currently experiencing high demand, spikes in demand are usually temporary. Please try again later.', 'code': 'service_unavailable'}}`

### Trả lời — RAG không đồ thị (vector-only)

Để đăng ký thường trú tại căn nhà thuê ở xã Tân Triều với hợp đồng thuê nhà viết tay, bạn cần lưu ý rằng hợp đồng viết tay hiện chưa đáp ứng đủ điều kiện pháp lý về thành phần hồ sơ theo quy định, vì hợp đồng thuê nhà phải được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】. Bạn cần hoàn thiện điều kiện công chứng hoặc chứng thực hợp đồng thuê nhà trước khi nộp hồ sơ 【PROC_1_116788_c127_s0】.

### Thứ tự nên làm
1. **Hoàn thiện giấy tờ**: Đem hợp đồng thuê nhà đi công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】, đồng thời đảm bảo có ý kiến đồng ý của chủ sở hữu chỗ ở hợp pháp 【PROC_1_116788_c142_s2】.
2. **Nộp hồ sơ đăng ký thường trú (Mã: PROC_1_116788)**: Nộp đến cơ quan Công an Xã 【PROC_1_116788_c174_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần nộp**:
  - Hợp đồng về việc cho thuê chỗ ở hợp pháp được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】.
  - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú 【PROC_1_116788_c128_s0】.
- **Cơ quan tiếp nhận và giải quyết**: Công an Xã 【PROC_1_116788_c174_s0】.
- **Thời gian giải quyết**: 07 ngày làm việc kể từ ngày nhận được hồ sơ đầy đủ và chính xác 【PROC_1_116788_c174_s3】.
- **Lệ phí**: 20.000 đồng/lần đăng ký khi nộp trực tiếp hoặc 10.000 đồng/lần khi nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.

### Thủ tục áp dụng
- Đăng ký thường trú 【PROC_1_116788】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (9/9 checks).
- Latency end-to-end: **65.219s**.
- Gemini: **3 calls**, input `15281`, output `1423`, total `16704` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC03 — Liên thông VNeID bốn thủ tục

### Câu hỏi

Tôi muốn làm thủ tục liên thông trên VNeID để vừa khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho con tôi dưới 6 tuổi. Các bước hệ thống xử lý như thế nào và mất bao nhiêu ngày làm việc?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c181_s0`, `PROC_3_000722_c182_s1`, `PROC_3_000722_c183_s1`, `PROC_3_000722_c184_s0`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: bước 1; bước 2; bước 3; bước 4; bước 5; 03 / 3 ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

## Hướng dẫn theo thông tin đã kiểm chứng

### Thứ tự thủ tục
- Ưu tiên 1: **Thủ tục đăng ký khai sinh** 【PROC_1_001193】
- Ưu tiên 2: **Thủ tục cấp thẻ bảo hiểm y tế** 【PROC_1_014137】
- Ưu tiên 2: **Đăng ký thường trú** 【PROC_1_116788】
- Ưu tiên 3: **Cấp, cấp đổi, cấp lại thẻ căn cước** 【PROC_1_116410】

### Nội dung đã đối chiếu
- **Kênh nộp hồ sơ liên thông:** Người dân nộp hồ sơ liên thông trực tuyến qua VNeID hoặc Cổng Dịch vụ công quốc gia. 【PROC_3_000722_c180_s1】
- Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục đăng ký thường trú. Người dân không phải tự chuyển giấy tờ này giữa các cơ quan trong gói liên thông. (Bước 4 trong quy trình liên thông) 【REL:PROC_1_001193:NEXT_STEP:PROC_1_116788】
- Hệ thống tự chuyển Giấy khai sinh điện tử để xử lý thủ tục thủ tục cấp thẻ bảo hiểm y tế. Người dân không phải tự chuyển giấy tờ này giữa các cơ quan trong gói liên thông. (Bước 4 trong quy trình liên thông) 【REL:PROC_1_001193:NEXT_STEP:PROC_1_014137】
- Hệ thống tự chuyển Thông báo kết quả đăng ký thường trú để xử lý thủ tục cấp, cấp đổi, cấp lại thẻ căn cước. Nhánh này chỉ áp dụng khi người đại diện hợp pháp đề nghị cấp thẻ lúc nộp hồ sơ trực tuyến. (Bước 5 trong quy trình liên thông) 【REL:PROC_1_116788:NEXT_STEP:PROC_1_116410】
- **Thời gian giải quyết gói liên thông:** Cách thức nộp hồ sơ, thời gian giải quyết và lệ phí của Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722): Cơ quan tiếp nhận và giải quyết: Công an cấp Xã. - Hình thức: Trực tuyến. Thời gian giải quyết: Xem phần mô tả ngày. Lệ phí: Miễn phí (Ba (03) ngày làm việc kể từ khi các cơ quan có thẩm quyền giải quyết nhận đầy đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá năm (05) ngày làm việc. Nếu tiếp nhận hồ sơ sau 15 giờ thì thời gian được tính bắt đầu từ ngày làm việc tiếp theo. Phí, lệ phí: Theo quy định của các TTHC tương ứng). 【PROC_3_000722_c185_s0】
- Trình tự thực hiện Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722) - Bước 2: - Bước 2. Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công từ nền tảng thanh toán và tiến hành bóc tách thành phần hồ sơ, thực hiện chuyển hồ sơ (bao gồm biểu mẫu điện tử tương tác, các giấy tờ đính kèm) sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp qua Nền tảng chia sẻ và điều phối dữ liệu. Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp đồng bộ hồ sơ về Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp. Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp tiếp nhận hồ sơ và phản hồi trạng thái cho Cổng Dịch vụ công quốc gia qua Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp 【PROC_3_000722_c181_s0】
- Trường hợp cần bổ sung thành phần hồ sơ thì người yêu cầu có trách nhiệm hoàn thiện hồ sơ trong 07 ngày làm việc, nếu quá thời hạn này không bổ sung thì người thực hiện công tác hộ tịch tại Ủy ban nhân dân cấp xã thực hiện thao tác trên Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp để dừng xử lý do không bổ sung theo quy định. Thông tin về việc dừng xử lý được gửi đến Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp để thông báo cho người yêu cầu qua Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID hoặc gửi tin nhắn điện thoại tự động của Cổng Dịch vụ công quốc gia. Sau khi tiếp nhận hồ sơ đăng ký khai sinh, Chủ tịch Ủy ban nhân dân xã, phường, đặc khu đồng thời xem xét, quyết định việc hỗ trợ tài chính khi sinh con và thực hiện chi trả cho phụ nữ sinh con theo quy định pháp luật dân số 【PROC_3_000722_c182_s3】
- - Bước 4. Giải quyết hồ sơ đăng ký thường trú và cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi Sau khi Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp chuyển bản điện tử Giấy khai sinh sang Cổng Dịch vụ công quốc gia, sau đó Cổng Dịch vụ công quốc gia phân tách, chuyển hồ sơ điện tử (bao gồm biểu mẫu, tờ khai người yêu cầu đã kê khai, bản điện tử Giấy khai sinh) đến Hệ thống thông tin quản lý cư trú để thực hiện đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để thực hiện cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi theo quy định pháp luật liên quan. Thời gian giải quyết đăng ký thường trú không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử đối với trường hợp: con về với cha, mẹ và cha, mẹ là chủ hộ, đồng thời là chủ sở hữu chỗ ở hợp pháp; con về với cha, mẹ nhưng cha, mẹ không phải là chủ sở hữu chỗ ở hợp pháp 【PROC_3_000722_c183_s1】
- Trình tự thực hiện Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722) - Bước 5: - Bước 5. Giải quyết hồ sơ cấp thẻ căn cước cho trẻ em dưới 6 tuổi (khi người đại diện hợp pháp có đề nghị cấp thẻ căn cước cho trẻ tại bước nộp hồ sơ trực tuyến) Sau khi Hệ thống thông tin quản lý cư trú của Bộ Công an chuyển bản điện tử Thông báo kết quả giải quyết đăng ký thường trú sang Cổng Dịch vụ công quốc gia, sau đó Cổng Dịch vụ công quốc gia phân tách, chuyển hồ sơ điện tử (biểu mẫu, tờ khai người yêu cầu đã kê khai) đến Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước theo quy định của Luật Căn cước số 26/2023/QH15. Thời gian giải quyết cấp thẻ căn cước không quá 05 ngày làm việc kể từ ngày nhận được hồ sơ điện tử trên hệ thống 【PROC_3_000722_c184_s0】

#### Quan sát benchmark

- Điểm rubric: **75.0/100** (9/12 checks).
- Latency end-to-end: **97.455s**.
- Gemini: **3 calls**, input `24623`, output `1982`, total `26605` tokens.
- Citation bị thiếu theo rubric: `PROC_3_000722_c182_s1`.
- Citation sai/không được phép: Không có.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt. | Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Chào bạn, dưới đây là chi tiết các bước hệ thống xử lý hồ sơ và thời gian giải quyết cho nhóm thủ tục liên thông đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi trên ứng dụng VNeID (Mã: PROC_3_000722). Cơ quan tiếp nhận và giải quyết là Công an cấp Xã 【PROC_3_000722_c185_s0】.

### Thứ tự nên làm và các bước hệ thống xử lý
- **Bước 1:** Người yêu cầu truy cập vào Cổng Dịch vụ công quốc gia hoặc trên ứng dụng VNeID, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và đóng lệ phí 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách hồ sơ và chuyển sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp. Hệ thống của Bộ Tư pháp tiếp nhận và đồng bộ về Hệ thống đăng ký, quản lý hộ tịch điện tử 【PROC_3_000722_c181_s0】.
- **Bước 3:** Người thực hiện công tác hộ tịch tại Ủy ban nhân dân cấp xã thực hiện nghiệp vụ đăng ký khai sinh trong 24 giờ kể từ khi Hệ thống đăng ký, quản lý hộ tịch điện tử nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s1】.
- **Bước 4:** Sau khi chuyển bản điện tử Giấy khai sinh, hệ thống tiếp tục chuyển đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi 【PROC_3_000722_c183_s1】.
- **Bước 5:** Khi người đại diện hợp pháp có đề nghị cấp thẻ căn cước, sau khi có thông báo kết quả đăng ký thường trú, hệ thống sẽ chuyển đến Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước 【PROC_3_000722_c184_s0】.

### Thời gian giải quyết
- Thời gian giải quyết thông thường là **ba (03) ngày làm việc** kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ hợp lệ, trường hợp phải xác minh thì không quá **năm (05) ngày làm việc** 【PROC_3_000722_c185_s0】.
### Thủ tục áp dụng
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (12/12 checks).
- Latency end-to-end: **16.977s**.
- Gemini: **2 calls**, input `7859`, output `841`, total `8700` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC04 — Sai ngày sinh trước khi cấp Căn cước

### Câu hỏi

Con tôi 15 tuổi (sinh năm 2011) đi làm thẻ Căn cước, nhưng trên VNeID ngày sinh của cháu bị sai so với Giấy khai sinh gốc. Gia đình có thể đến điểm cấp căn cước đưa giấy khai sinh để cán bộ làm thẻ luôn được không, hay phải làm thế nào?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_116410_c73_s0`, `PROC_1_116410_c63_s0`, `PROC_1_116410_c76_s0`, `PROC_1_116410_c78_s0`.
- Nội dung cần có: điều chỉnh; trước; mống mắt; cc01; cc02.
- Citation không được xuất hiện: `PROC_1_116410_c86_s0`, `PROC_1_116410_c90_s0`.

### Trả lời — Graph-RAG

## Hướng dẫn theo thông tin đã kiểm chứng

### Thứ tự thủ tục
- Ưu tiên 1: **Cấp, cấp đổi, cấp lại thẻ căn cước** 【PROC_1_116410】

### Nội dung đã đối chiếu
- **Xử lý điều chỉnh dữ liệu trước:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 8: + Trường hợp thông tin công dân có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c73_s0】
- **Phiếu thu nhận thông tin căn cước:** Thành phần hồ sơ cần nộp để thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410): - Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an). Phiếu được tạo lập khi trích xuất thông tin của công dân trong Cơ sở dữ liệu quốc gia về dân cư và in trong quá trình thu nhận hồ sơ căn cước để công dân kiểm tra và ký xác nhận - Số lượng: 1 Bản chính (Theo trường hợp / nếu có). 【PROC_1_116410_c63_s0】
- **Giấy hẹn trả kết quả căn cước:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 13: - Thu thẻ căn cước (nếu có), thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c78_s0】
- **Thu nhận sinh trắc học:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 11: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 1: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c66_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 2: - Nộp hồ sơ trực tiếp: Công dân trực tiếp đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp thẻ căn cước 【PROC_1_116410_c67_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 3: - Nộp hồ sơ trực tuyến một phần: Công dân thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì đăng ký thời gian và địa điểm thực hiện thủ tục tại Công an cấp xã. Hệ thống sẽ xác nhận và tự động chuyển đề nghị của công dân đến Công an cấp xã đề nghị cấp thẻ căn cước 【PROC_1_116410_c68_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 4: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c69_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 5: - Công dân cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c70_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 6: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c71_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 7: + Trường hợp thông tin công dân chưa có trong Cơ sở dữ liệu quốc gia về dân cư thì cán bộ thu nhận đề nghị công dân xuất trình một trong các loại giấy tờ pháp lý chứng minh nội dung thông tin nhân thân và hướng dẫn thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c72_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 9: + Trường hợp thông tin công dân không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c74_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 10: + Trường hợp công dân không đủ điều kiện cấp thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c75_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 12: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), Phiếu thu thập thông tin dân cư (Mẫu DC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (nếu có), chuyển cho công dân kiểm tra, ký xác nhận 【PROC_1_116410_c77_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 14: - Nhận kết quả trực tiếp tại Công an cấp xã nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c79_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 15: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c80_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 16: - Nộp hồ sơ trực tiếp: Đối với người từ đủ 06 tuổi đến dưới 14 tuổi thì thực hiện trực tiếp tại Công an cấp xã, người đại diện hợp pháp đưa người dưới 14 tuổi đến địa điểm làm thủ tục cấp thẻ căn cước 【PROC_1_116410_c81_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 17: - Nộp hồ sơ trực tuyến toàn trình: Đối với người dưới 06 tuổi thì người đại diện hợp pháp thực hiện thủ tục cấp thẻ căn cước cho người dưới 06 tuổi, nộp hồ sơ trực tuyến toàn trình qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) thì lựa chọn thủ tục, kiểm tra thông tin của người dưới 06 tuổi trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì người đại diện hợp pháp xác nhận chuyển hồ sơ đề nghị đến Công an cấp xã nơi người dưới 06 tuổi cư trú xem xét, giải quyết việc cấp thẻ căn cước cho người dưới 06 tuổi 【PROC_1_116410_c82_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 18: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c83_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 19: - Cán bộ thu nhận thông tin người dưới 14 tuổi tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c84_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 20: + Trường hợp thông tin người dưới 14 tuổi chưa có trong Cơ sở dữ liệu quốc gia về dân cư thì cán bộ thu nhận đề nghị người đại diện hợp pháp xuất trình một trong các loại giấy tờ pháp lý chứng minh nội dung thông tin nhân thân và hướng dẫn thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c85_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 21: + Trường hợp thông tin người dưới 14 tuổi có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn người đại diện hợp pháp thực hiện thủ tục điều chỉnh thông tin cho người dưới 14 tuổi trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c86_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 22: + Trường hợp thông tin người dưới 14 tuổi không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c87_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 23: + Trường hợp người dưới 14 tuổi không đủ điều kiện cấp thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c88_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 24: - Thông tin người đại diện hợp pháp được khai thác trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước. Trường hợp không khai thác được thông tin thì hướng dẫn người đại diện hợp pháp thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c89_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 25: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của người từ đủ 06 tuổi đến dưới 14 tuổi 【PROC_1_116410_c90_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 26: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an); Phiếu thu thập thông tin dân cư (nếu có) cho người đại diện hợp pháp kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c91_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 27: - Thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c92_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 28: - Nhận kết quả trực tiếp tại Công an cấp xã hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c93_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 29: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c94_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 30: - Nộp hồ sơ trực tiếp: Công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp đổi thẻ căn cước, cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c95_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 31: - Nộp hồ sơ trực tuyến một phần: Công dân thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp đổi thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì đăng ký thời gian và địa điểm thực hiện thủ tục tại Công an cấp xã. Hệ thống sẽ xác nhận và tự động chuyển đề nghị của công dân đến Công an cấp xã đề nghị cấp đổi thẻ căn cước 【PROC_1_116410_c96_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 32: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c97_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 33: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp đổi thẻ căn cước 【PROC_1_116410_c98_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 34: + Trường hợp thông tin công dân không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp đổi thẻ căn cước 【PROC_1_116410_c99_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 35: + Trường hợp thông tin công dân có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c100_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 36: + Trường hợp cấp đổi thẻ căn cước khi thông tin trên thẻ căn cước thay đổi do sắp xếp đơn vị hành chính thì cán bộ thu nhận sử dụng thông tin về ảnh khuôn mặt, vân tay, mống mắt đã được cấp thẻ căn cước lần gần nhất và các thông tin hiện có trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước để cấp đổi thẻ căn cước 【PROC_1_116410_c101_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 37: - Trường hợp công dân không đủ điều kiện cấp đổi thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c102_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 38: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt, thu nhận ảnh mống mắt của công dân từ đủ 06 tuổi trở lên trừ trường hợp cấp đổi thẻ căn cước khi thông tin trên thẻ căn cước thay đổi do sắp xếp đơn vị hành chính 【PROC_1_116410_c103_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 39: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), Phiếu thu thập thông tin dân cư (Mẫu DC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (nếu có), chuyển cho công dân hoặc người đại diện hợp pháp của người dưới 14 tuổi kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c104_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 40: - Thu thẻ căn cước cũ, thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước cho công dân (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c105_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 41: - Nhận kết quả trực tiếp tại Công an cấp xã nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c106_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 42: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c107_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 43: - Nộp hồ sơ trực tiếp: Công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp lại thẻ căn cước, cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c108_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 44: - Nộp hồ sơ trực tuyến toàn trình: Công dân nộp hồ sơ thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp lại thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì xác nhận chuyển hồ sơ đề nghị cấp lại thẻ căn cước đến Công an cấp xã xem xét, giải quyết cấp lại thẻ căn cước 【PROC_1_116410_c109_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 45: - Trường hợp người đề nghị cấp lại thẻ căn cước là người đại diện hợp pháp của người dưới 14 tuổi thì thông tin người đại diện hợp pháp được khai thác trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước. Trường hợp không khai thác được thông tin thì người đại diện hợp pháp đến Công an cấp xã nơi cư trú để thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c110_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 46: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c111_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 47: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp lại thẻ căn cước 【PROC_1_116410_c112_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 48: + Trường hợp cấp lại thẻ căn cước do bị mất thẻ căn cước hoặc thẻ căn cước bị hư hỏng không sử dụng được thì cán bộ thu nhận sử dụng thông tin về ảnh khuôn mặt, vân tay, mống mắt đã được cấp thẻ căn cước lần gần nhất và các thông tin hiện có trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước để cấp lại thẻ căn cước 【PROC_1_116410_c113_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 49: + Trường hợp cấp lại thẻ căn cước quy định tại điểm b khoản 2 Điều 24 Luật Căn cước được sửa đổi, bổ sung bởi Luật số 118/2025/QH15 ngày 10/12/2025 (được trở lại quốc tịch Việt Nam theo quy định của pháp luật về quốc tịch Việt Nam), các bước thực hiện như đối với thủ tục cấp mới thẻ căn cước 【PROC_1_116410_c114_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 50: + Trường hợp công dân không đủ điều kiện cấp lại thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c115_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 51: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân (áp dụng với trường hợp cấp lại thẻ căn cước quy định tại điểm b khoản 2 Điều 24 Luật Căn cước được sửa đổi, bổ sung bởi Luật số 118/2025/QH15 ngày 10/12/2025) 【PROC_1_116410_c116_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 52: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), chuyển cho công dân hoặc người đại diện hợp pháp của người dưới 14 tuổi kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c117_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 53: - Thu thẻ căn cước cũ (nếu có), thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước cho công dân (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (bản giấy hoặc bản điện tử) 【PROC_1_116410_c118_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 54: - Nhận kết quả trực tiếp tại cơ quan Công an nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c119_s0】

#### Quan sát benchmark

- Điểm rubric: **81.8/100** (9/11 checks).
- Latency end-to-end: **60.968s**.
- Gemini: **3 calls**, input `39594`, output `3547`, total `43141` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: `PROC_1_116410_c86_s0`, `PROC_1_116410_c90_s0`.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt..

### Trả lời — RAG không đồ thị (vector-only)

## Hướng dẫn theo thông tin đã kiểm chứng

### Thứ tự thủ tục
- Ưu tiên 1: **Cấp, cấp đổi, cấp lại thẻ căn cước** 【PROC_1_116410】

### Nội dung đã đối chiếu
- **Xử lý điều chỉnh dữ liệu trước:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 8: + Trường hợp thông tin công dân có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c73_s0】
- **Phiếu thu nhận thông tin căn cước:** Thành phần hồ sơ cần nộp để thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410): - Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an). Phiếu được tạo lập khi trích xuất thông tin của công dân trong Cơ sở dữ liệu quốc gia về dân cư và in trong quá trình thu nhận hồ sơ căn cước để công dân kiểm tra và ký xác nhận - Số lượng: 1 Bản chính (Theo trường hợp / nếu có). 【PROC_1_116410_c63_s0】
- **Giấy hẹn trả kết quả căn cước:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 13: - Thu thẻ căn cước (nếu có), thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c78_s0】
- **Thu nhận sinh trắc học:** Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 11: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 1: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c66_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 2: - Nộp hồ sơ trực tiếp: Công dân trực tiếp đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp thẻ căn cước 【PROC_1_116410_c67_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 3: - Nộp hồ sơ trực tuyến một phần: Công dân thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì đăng ký thời gian và địa điểm thực hiện thủ tục tại Công an cấp xã. Hệ thống sẽ xác nhận và tự động chuyển đề nghị của công dân đến Công an cấp xã đề nghị cấp thẻ căn cước 【PROC_1_116410_c68_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 4: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c69_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 5: - Công dân cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c70_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 6: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c71_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 7: + Trường hợp thông tin công dân chưa có trong Cơ sở dữ liệu quốc gia về dân cư thì cán bộ thu nhận đề nghị công dân xuất trình một trong các loại giấy tờ pháp lý chứng minh nội dung thông tin nhân thân và hướng dẫn thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c72_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 9: + Trường hợp thông tin công dân không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c74_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 10: + Trường hợp công dân không đủ điều kiện cấp thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c75_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 12: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), Phiếu thu thập thông tin dân cư (Mẫu DC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (nếu có), chuyển cho công dân kiểm tra, ký xác nhận 【PROC_1_116410_c77_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 14: - Nhận kết quả trực tiếp tại Công an cấp xã nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c79_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 15: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c80_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 16: - Nộp hồ sơ trực tiếp: Đối với người từ đủ 06 tuổi đến dưới 14 tuổi thì thực hiện trực tiếp tại Công an cấp xã, người đại diện hợp pháp đưa người dưới 14 tuổi đến địa điểm làm thủ tục cấp thẻ căn cước 【PROC_1_116410_c81_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 17: - Nộp hồ sơ trực tuyến toàn trình: Đối với người dưới 06 tuổi thì người đại diện hợp pháp thực hiện thủ tục cấp thẻ căn cước cho người dưới 06 tuổi, nộp hồ sơ trực tuyến toàn trình qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) thì lựa chọn thủ tục, kiểm tra thông tin của người dưới 06 tuổi trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì người đại diện hợp pháp xác nhận chuyển hồ sơ đề nghị đến Công an cấp xã nơi người dưới 06 tuổi cư trú xem xét, giải quyết việc cấp thẻ căn cước cho người dưới 06 tuổi 【PROC_1_116410_c82_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 18: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c83_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 19: - Cán bộ thu nhận thông tin người dưới 14 tuổi tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c84_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 20: + Trường hợp thông tin người dưới 14 tuổi chưa có trong Cơ sở dữ liệu quốc gia về dân cư thì cán bộ thu nhận đề nghị người đại diện hợp pháp xuất trình một trong các loại giấy tờ pháp lý chứng minh nội dung thông tin nhân thân và hướng dẫn thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c85_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 21: + Trường hợp thông tin người dưới 14 tuổi có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn người đại diện hợp pháp thực hiện thủ tục điều chỉnh thông tin cho người dưới 14 tuổi trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c86_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 22: + Trường hợp thông tin người dưới 14 tuổi không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp thẻ căn cước 【PROC_1_116410_c87_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 23: + Trường hợp người dưới 14 tuổi không đủ điều kiện cấp thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c88_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 24: - Thông tin người đại diện hợp pháp được khai thác trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước. Trường hợp không khai thác được thông tin thì hướng dẫn người đại diện hợp pháp thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c89_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 25: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của người từ đủ 06 tuổi đến dưới 14 tuổi 【PROC_1_116410_c90_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 26: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an); Phiếu thu thập thông tin dân cư (nếu có) cho người đại diện hợp pháp kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c91_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 27: - Thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c92_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 28: - Nhận kết quả trực tiếp tại Công an cấp xã hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c93_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 29: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c94_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 30: - Nộp hồ sơ trực tiếp: Công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp đổi thẻ căn cước, cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c95_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 31: - Nộp hồ sơ trực tuyến một phần: Công dân thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp đổi thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì đăng ký thời gian và địa điểm thực hiện thủ tục tại Công an cấp xã. Hệ thống sẽ xác nhận và tự động chuyển đề nghị của công dân đến Công an cấp xã đề nghị cấp đổi thẻ căn cước 【PROC_1_116410_c96_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 32: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c97_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 33: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp đổi thẻ căn cước 【PROC_1_116410_c98_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 34: + Trường hợp thông tin công dân không có sự thay đổi, điều chỉnh thì sử dụng thông tin của công dân trong cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp đổi thẻ căn cước 【PROC_1_116410_c99_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 35: + Trường hợp thông tin công dân có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c100_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 36: + Trường hợp cấp đổi thẻ căn cước khi thông tin trên thẻ căn cước thay đổi do sắp xếp đơn vị hành chính thì cán bộ thu nhận sử dụng thông tin về ảnh khuôn mặt, vân tay, mống mắt đã được cấp thẻ căn cước lần gần nhất và các thông tin hiện có trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước để cấp đổi thẻ căn cước 【PROC_1_116410_c101_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 37: - Trường hợp công dân không đủ điều kiện cấp đổi thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c102_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 38: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt, thu nhận ảnh mống mắt của công dân từ đủ 06 tuổi trở lên trừ trường hợp cấp đổi thẻ căn cước khi thông tin trên thẻ căn cước thay đổi do sắp xếp đơn vị hành chính 【PROC_1_116410_c103_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 39: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), Phiếu thu thập thông tin dân cư (Mẫu DC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (nếu có), chuyển cho công dân hoặc người đại diện hợp pháp của người dưới 14 tuổi kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c104_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 40: - Thu thẻ căn cước cũ, thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước cho công dân (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c105_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 41: - Nhận kết quả trực tiếp tại Công an cấp xã nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c106_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 42: Bước 1: Nộp hồ sơ thủ tục hành chính: 【PROC_1_116410_c107_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 43: - Nộp hồ sơ trực tiếp: Công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) đề nghị cấp lại thẻ căn cước, cung cấp thông tin gồm họ, chữ đệm và tên khai sinh, số định danh cá nhân, nơi cư trú để người tiếp nhận kiểm tra đối chiếu thông tin trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c108_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 44: - Nộp hồ sơ trực tuyến toàn trình: Công dân nộp hồ sơ thông qua Cổng dịch vụ công quốc gia, Ứng dụng định danh quốc gia (VNeID) lựa chọn thủ tục cấp lại thẻ căn cước, kiểm tra thông tin của mình được khai thác trong Cơ sở dữ liệu quốc gia về dân cư. Trường hợp thông tin chính xác thì xác nhận chuyển hồ sơ đề nghị cấp lại thẻ căn cước đến Công an cấp xã xem xét, giải quyết cấp lại thẻ căn cước 【PROC_1_116410_c109_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 45: - Trường hợp người đề nghị cấp lại thẻ căn cước là người đại diện hợp pháp của người dưới 14 tuổi thì thông tin người đại diện hợp pháp được khai thác trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước. Trường hợp không khai thác được thông tin thì người đại diện hợp pháp đến Công an cấp xã nơi cư trú để thu thập, cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c110_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 46: Bước 2: Giải quyết và trả kết quả thủ tục hành chính: 【PROC_1_116410_c111_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 47: - Cán bộ thu nhận thông tin công dân tìm kiếm thông tin trong Cơ sở dữ liệu quốc gia về dân cư để lập hồ sơ cấp lại thẻ căn cước 【PROC_1_116410_c112_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 48: + Trường hợp cấp lại thẻ căn cước do bị mất thẻ căn cước hoặc thẻ căn cước bị hư hỏng không sử dụng được thì cán bộ thu nhận sử dụng thông tin về ảnh khuôn mặt, vân tay, mống mắt đã được cấp thẻ căn cước lần gần nhất và các thông tin hiện có trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước để cấp lại thẻ căn cước 【PROC_1_116410_c113_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 49: + Trường hợp cấp lại thẻ căn cước quy định tại điểm b khoản 2 Điều 24 Luật Căn cước được sửa đổi, bổ sung bởi Luật số 118/2025/QH15 ngày 10/12/2025 (được trở lại quốc tịch Việt Nam theo quy định của pháp luật về quốc tịch Việt Nam), các bước thực hiện như đối với thủ tục cấp mới thẻ căn cước 【PROC_1_116410_c114_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 50: + Trường hợp công dân không đủ điều kiện cấp lại thẻ căn cước thì từ chối tiếp nhận và nêu rõ lý do, thông báo về việc giải quyết thủ tục về căn cước (Mẫu CC03 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) 【PROC_1_116410_c115_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 51: - Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân (áp dụng với trường hợp cấp lại thẻ căn cước quy định tại điểm b khoản 2 Điều 24 Luật Căn cước được sửa đổi, bổ sung bởi Luật số 118/2025/QH15 ngày 10/12/2025) 【PROC_1_116410_c116_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 52: - In Phiếu thu nhận thông tin căn cước (Mẫu CC01 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an), chuyển cho công dân hoặc người đại diện hợp pháp của người dưới 14 tuổi kiểm tra, ký xác nhận (đối với hồ sơ nộp trực tiếp) 【PROC_1_116410_c117_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 53: - Thu thẻ căn cước cũ (nếu có), thu lệ phí (nếu có) và cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước cho công dân (Mẫu CC02 ban hành kèm theo Thông tư số 118/2026/TT-BCA ngày 29/6/2026 của Bộ Công an) (bản giấy hoặc bản điện tử) 【PROC_1_116410_c118_s0】
- Trình tự thực hiện Cấp, cấp đổi, cấp lại thẻ căn cước (Mã: PROC_1_116410) - Bước 54: - Nhận kết quả trực tiếp tại cơ quan Công an nơi tiếp nhận hồ sơ hoặc trả qua dịch vụ bưu chính đến địa chỉ theo yêu cầu 【PROC_1_116410_c119_s0】

#### Quan sát benchmark

- Điểm rubric: **81.8/100** (9/11 checks).
- Latency end-to-end: **31.398s**.
- Gemini: **3 calls**, input `39512`, output `3524`, total `43036` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: `PROC_1_116410_c86_s0`, `PROC_1_116410_c90_s0`.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt..

---

## TC05 — BHYT khi chưa đăng ký khai sinh

### Câu hỏi

Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `REL:PROC_1_014137:REQUIRES:PROC_1_001193`, `PROC_1_014137_c50_s0`, `PROC_1_014137_c61_s0`.
- Nội dung cần có: khai sinh / trước; bảo hiểm xã hội; 05 ngày / 5 ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

Bạn không thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT riêng lẻ cho trẻ 1 tháng tuổi chưa có giấy khai sinh 【PROC_1_014137_c60_s0】. Đối với trẻ em dưới 6 tuổi, việc cấp thẻ BHYT được thực hiện liên thông cùng với thủ tục đăng ký khai sinh và đăng ký thường trú 【PROC_1_014137_c60_s0】.

### Thứ tự nên làm và cách thực hiện
Bạn có hai phương án để thực hiện:

**Phương án 1: Thực hiện qua nhóm thủ tục liên thông điện tử (Khuyên dùng để giải quyết đồng thời khai sinh và BHYT)**
- **Cơ quan tiếp nhận và giải quyết:** Công an cấp Xã 【PROC_3_000722_c185_s0】.
- **Cách thức thực hiện:** Nộp hồ sơ trực tuyến trên Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.
- **Hồ sơ phổ biến:** Tờ khai điện tử theo Mẫu số 01 và dữ liệu điện tử Giấy chứng sinh liên thông từ cơ sở khám chữa bệnh hoặc đính kèm bản điện tử/bản chụp giấy tờ thay thế 【PROC_3_000722_c176_s0】【PROC_3_000722_c177_s0】.
- **Thời gian giải quyết:** Ba (03) ngày làm việc kể từ khi nhận đủ hồ sơ, trường hợp phải xác minh thì không quá năm (05) ngày làm việc; thời gian giải quyết thẻ BHYT cho trẻ dưới 6 tuổi không quá 02 ngày làm việc 【PROC_3_000722_c185_s0】【PROC_3_000722_c183_s2】.
- **Lệ phí:** Miễn phí (phí, lệ phí theo quy định của các thủ tục tương ứng) 【PROC_3_000722_c185_s0】.

**Phương án 2: Làm thủ tục đăng ký khai sinh trước rồi cấp thẻ BHYT đơn lẻ**
1. **Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193):** Nộp tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】 với thời gian giải quyết là 1 ngày, miễn phí lệ phí 【PROC_1_001193_c48_s0】.
2. **Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】 (Mã: PROC_1_014137):** Sau khi có giấy khai sinh, cơ quan tiếp nhận và giải quyết là Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】.
- **Cách thức thực hiện:** Trực tuyến, trực tiếp tại bộ phận một cửa của cơ quan bảo hiểm xã hội, hoặc qua dịch vụ bưu chính công ích 【PROC_1_014137_c53_s0】【PROC_1_014137_c61_s0】.
- **Hồ sơ phổ biến:** Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c49_s0】【PROC_1_014137_c50_s0】 và bản scan các văn bản, tài liệu liên quan nếu thay đổi thông tin thân nhân 【PROC_1_014137_c55_s0】【PROC_1_014137_c51_s0】.
- **Thời gian giải quyết:** 05 ngày làm việc kể từ ngày nhận đủ hồ sơ 【PROC_1_014137_c61_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_014137_c61_s0】.

#### Quan sát benchmark

- Điểm rubric: **83.3/100** (5/6 checks).
- Latency end-to-end: **48.446s**.
- Gemini: **2 calls**, input `17106`, output `1193`, total `18299` tokens.
- Citation bị thiếu theo rubric: `REL:PROC_1_014137:REQUIRES:PROC_1_001193`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Trẻ em 1 tháng tuổi chưa làm giấy khai sinh thì chưa thể làm thủ tục cấp thẻ BHYT độc lập ngay theo quy trình thông thường, vì theo quy định đối với trẻ dưới 6 tuổi, việc cấp thẻ bảo hiểm y tế được thực hiện liên thông cùng với thủ tục đăng ký khai sinh và đăng ký thường trú 【PROC_1_014137_c60_s0】. Do đó, bạn không thể đến thẳng cơ quan Bảo hiểm xã hội để xin cấp thẻ BHYT riêng cho cháu trước mà cần thực hiện đồng thời hoặc thông qua nhóm thủ tục liên thông.

### Thứ tự nên làm
1. **Phương án 1 - Nộp qua nhóm thủ tục liên thông điện tử (Khuyến nghị tối ưu nhất cho trẻ dưới 6 tuổi):** 【PROC_3_000722】
   - **Mã thủ tục:** `PROC_3_000722` (Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi) 【PROC_3_000722】.
   - **Cơ quan giải quyết:** Công an cấp Xã 【PROC_3_000722】.
   - **Cách thực hiện:** Nộp hồ sơ trực tuyến trên Cổng Dịch vụ công quốc gia (`dichvucong.gov.vn`) hoặc ứng dụng `VNeID` 【PROC_3_000722_c180_s1】.
   - **Thời gian giải quyết:** 03 ngày làm việc kể từ khi các cơ quan nhận đủ hồ sơ theo quy định; trường hợp phải xác minh thì không quá 05 ngày làm việc 【PROC_3_000722_c185_s0】.
   - **Lệ phí:** Miễn phí (phí, lệ phí theo quy định của các thủ tục tương ứng) 【PROC_3_000722_c185_s0】.

2. **Phương án 2 - Làm thủ tục riêng lẻ từng bước:**
   - **Bước 1: Đăng ký khai sinh (`PROC_1_001193` 【PROC_1_001193】)**
     - **Lý do cần làm:** Phải có giấy khai sinh và thông tin định danh của trẻ mới có cơ sở làm thẻ BHYT 【PROC_1_001193】.
     - **Cơ quan tiếp nhận và giải quyết:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
     - **Cách thực hiện:** Trực tuyến, trực tiếp tại Bộ phận một cửa hoặc qua dịch vụ bưu chính 【PROC_1_001193_c48_s0】.
     - **Thời gian và lệ phí:** 1 ngày; Miễn phí 【PROC_1_001193_c48_s0】.
   - **Bước 2: Cấp thẻ bảo hiểm y tế (`PROC_1_014137` 【PROC_1_014137】)**
     - **Lý do cần làm:** Cấp thẻ BHYT cho trẻ sau khi đã có thông tin khai sinh 【PROC_1_014137】.
     - **Cơ quan tiếp nhận và giải quyết:** Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】.
     - **Hồ sơ phổ biến:** Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c49_s0】【PROC_1_014137_c50_s0】.
     - **Cách thực hiện:** Trực tuyến, trực tiếp hoặc qua dịch vụ bưu chính công ích 【PROC_1_014137_c61_s0】【PROC_1_014137_c53_s0】.
     - **Thời gian và lệ phí:** 05 ngày làm việc kể từ ngày nhận đủ hồ sơ; Miễn phí 【PROC_1_014137_c61_s0】.

#### Quan sát benchmark

- Điểm rubric: **83.3/100** (5/6 checks).
- Latency end-to-end: **61.100s**.
- Gemini: **3 calls**, input `32983`, output `2194`, total `35177` tokens.
- Citation bị thiếu theo rubric: `REL:PROC_1_014137:REQUIRES:PROC_1_001193`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---
