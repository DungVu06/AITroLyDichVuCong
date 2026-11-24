# Nhật ký 10 câu trả lời — Graph-RAG vs RAG không đồ thị

- Thời điểm chạy UTC: 2026-11-24T03:17:49+00:00
- Model: `gemini-3.5-flash-lite`
- Mỗi ca được chạy độc lập; không mang hội thoại từ ca trước.
- Câu trả lời dưới đây là output nguyên văn đã được lưu từ 10 lượt chạy.

## TC01 — Khai sinh tại nhà không có Giấy chứng sinh

### Câu hỏi

Vợ tôi vừa sinh cháu tại nhà ở xã An Phú, không có Giấy chứng sinh của bệnh viện thì có làm giấy khai sinh được không? Tôi phải nộp hồ sơ ở đâu, cần giấy tờ gì thay thế và thời gian giải quyết bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_001193_c5_s0`, `PROC_1_001193_c48_s0`.
- Nội dung cần có: người làm chứng / người chứng kiến; cam đoan; ủy ban nhân dân cấp xã / ubnd cấp xã / ubnd xã; 1 ngày / một ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

Trường hợp vợ sinh con tại nhà ở xã An Phú và không có Giấy chứng sinh, bạn vẫn có thể làm thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】 tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.

### Thứ tự nên làm
- Nộp hồ sơ đăng ký khai sinh tại Ủy ban nhân dân cấp xã An Phú 【PROC_1_001193_c48_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ thay thế Giấy chứng sinh:** Trường hợp không có Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh (01 bản chính) 【PROC_1_001193_c5_s0】.
- **Cách thức nộp hồ sơ:** Nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết:** 01 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.

*Lưu ý:* Căn cứ pháp lý được cung cấp từ cơ sở dữ liệu chưa có thông tin đầy đủ về hiệu lực hiện hành.
### Thủ tục áp dụng
- Thủ tục đăng ký khai sinh 【PROC_1_001193】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (6/6 checks).
- Latency end-to-end: **80.723s**.
- Gemini: **2 calls**, input `6445`, output `590`, total `7035` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.
- Warning: Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Trường hợp sinh con tại nhà ở xã An Phú và không có Giấy chứng sinh của bệnh viện, anh/chị vẫn có thể thực hiện Thủ tục đăng ký khai sinh 【PROC_1_001193】 【PROC_1_001193_c5_s0】.

### Thứ tự nên làm
- **Thủ tục đăng ký khai sinh** (Mã: PROC_1_001193): Thực hiện tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ cần nộp**: Thay vì Giấy chứng sinh, anh/chị cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.
- **Cách thức nộp hồ sơ**: Có thể thực hiện bằng hình thức trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp tại cơ quan có thẩm quyền 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết**: 1 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí**: Miễn phí 【PROC_1_001193_c48_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (6/6 checks).
- Latency end-to-end: **25.765s**.
- Gemini: **2 calls**, input `6466`, output `560`, total `7026` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC02 — Thường trú tại nhà thuê

### Câu hỏi

Tôi đang thuê nhà ở xã Tân Triều, có hợp đồng thuê nhà viết tay. Tôi muốn đăng ký thường trú về căn nhà thuê này thì cần điều kiện và giấy tờ gì, nộp cho Công an xã hay UBND xã?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_116788_c126_s0`, `PROC_1_116788_c127_s0`, `PROC_1_116788_c128_s0`, `PROC_1_116788_c174_s0`.
- Nội dung cần có: tờ khai thay đổi thông tin cư trú / ct01; công chứng / chứng thực; chủ sở hữu / chủ nhà; diện tích; công an xã / công an cấp xã / cơ quan đăng ký cư trú cấp xã; 7 ngày làm việc / bảy ngày làm việc.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

Để đăng ký thường trú tại chỗ ở thuê tại xã Tân Triều, cơ quan tiếp nhận và giải quyết hồ sơ là **Công an Xã** (không phải UBND xã) 【PROC_1_116788_c174_s0】.

Do bạn sử dụng hợp đồng thuê nhà viết tay, pháp luật yêu cầu hợp đồng thuê nhà phải được công chứng hoặc chứng thực 【PROC_1_116788_c127_s0】.

### Thứ tự nên làm và Giấy tờ cần chuẩn bị (Mã: PROC_1_116788)

1. **Hoàn thiện điều kiện về giấy tờ:** Vì hợp đồng thuê nhà của bạn là viết tay, bạn cần tiến hành công chứng hoặc chứng thực hợp đồng thuê nhà này trước khi nộp hồ sơ 【PROC_1_116788_c127_s0】.
2. **Thành phần hồ sơ:**
   - Hợp đồng cho thuê chỗ ở hợp pháp đã được công chứng hoặc chứng thực (1 bản chính) 【PROC_1_116788_c127_s0】.
   - Thông tin hoặc giấy tờ chứng minh đủ diện tích nhà ở tối thiểu để đăng ký thường trú 【PROC_1_116788_c128_s0】.
   - Ý kiến đồng ý của chủ sở hữu chỗ ở hợp pháp cho đăng ký thường trú 【PROC_1_116788_c142_s2】.
3. **Cách thực hiện và Lệ phí:**
   - Nộp hồ sơ trực tuyến qua cổng dịch vụ công hoặc trực tiếp tại Công an Xã 【PROC_1_116788_c174_s3】.
   - Thời hạn giải quyết: 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ 【PROC_1_116788_c174_s3】.
   - Lệ phí: 10.000 đồng/lần nếu nộp trực tuyến hoặc 20.000 đồng/lần nếu nộp trực tiếp 【PROC_1_116788_c174_s3】.
### Thủ tục áp dụng
- Đăng ký thường trú 【PROC_1_116788】

#### Quan sát benchmark

- Điểm rubric: **80.0/100** (8/10 checks).
- Latency end-to-end: **48.036s**.
- Gemini: **2 calls**, input `8661`, output `782`, total `9443` tokens.
- Citation bị thiếu theo rubric: `PROC_1_116788_c126_s0`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Để đăng ký thường trú tại nhà thuê ở xã Tân Triều, bạn thực hiện thủ tục theo mã PROC_1_116788【PROC_1_116788_c121_s0】 tại cơ quan tiếp nhận là Công an xã【PROC_1_116788_c174_s0】.

### Điều kiện và Giấy tờ cần chuẩn bị
- **Hợp đồng thuê nhà:** Theo quy định, hợp đồng, văn bản về việc cho thuê chỗ ở hợp pháp phải được công chứng hoặc chứng thực theo quy định của pháp luật 【PROC_1_116788_c127_s0】.
- **Văn bản đồng ý của chủ sở hữu:** Hồ sơ cần có ý kiến đồng ý của chủ sở hữu chỗ ở hợp pháp【PROC_1_116788_c142_s2】.
- **Diện tích nhà ở:** Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú được khai thác trực tiếp trên hệ thống định danh điện tử hoặc qua cơ sở dữ liệu về cư trú. Trường hợp không khai thác được, bạn cần xuất trình giấy tờ thể hiện diện tích nhà ở hoặc xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân【PROC_1_116788_c128_s0】.

### Cách thức thực hiện, thời gian và lệ phí
- **Cách nộp:** Nộp trực tiếp tại Công an Xã hoặc nộp trực tuyến qua Cổng dịch vụ công【PROC_1_116788_c174_s3】【PROC_1_116788_c174_s0】.
- **Thời gian giải quyết:** 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ (không tính thời gian xác nhận diện tích của UBND cấp xã nếu có)【PROC_1_116788_c174_s3】【PROC_1_116788_c174_s2】.
- **Lệ phí:** 20.000 đồng/lần nếu nộp trực tiếp hoặc 10.000 đồng/lần nếu nộp qua Cổng dịch vụ công quốc gia【PROC_1_116788_c174_s3】.
### Thủ tục áp dụng
- Đăng ký thường trú 【PROC_1_116788】

#### Quan sát benchmark

- Điểm rubric: **80.0/100** (8/10 checks).
- Latency end-to-end: **94.478s**.
- Gemini: **3 calls**, input `15252`, output `1366`, total `16618` tokens.
- Citation bị thiếu theo rubric: `PROC_1_116788_c126_s0`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC03 — Liên thông VNeID bốn thủ tục

### Câu hỏi

Tôi muốn làm thủ tục liên thông trên VNeID để vừa khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho con tôi dưới 6 tuổi. Các bước hệ thống xử lý như thế nào và mất bao nhiêu ngày làm việc?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c181_s0`, `PROC_3_000722_c182_s1`, `PROC_3_000722_c183_s1`, `PROC_3_000722_c184_s0`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: vneid / cổng dịch vụ công quốc gia / cổng dvcqg; 24 giờ / 24h / 24 h; giấy khai sinh điện tử / bản điện tử giấy khai sinh; kết quả đăng ký thường trú / kết quả thường trú; theo yêu cầu / có đề nghị / đã đề nghị / nếu đề nghị / đã yêu cầu; 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc; 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc.
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

- Điểm rubric: **84.6/100** (11/13 checks).
- Latency end-to-end: **55.624s**.
- Gemini: **3 calls**, input `24500`, output `1491`, total `25991` tokens.
- Citation bị thiếu theo rubric: `PROC_3_000722_c182_s1`.
- Citation sai/không được phép: Không có.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt. | Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án. | Không kết nối được Qdrant Cloud. Lượt này dùng chỉ mục Qdrant từ dữ liệu local của dự án..

### Trả lời — RAG không đồ thị (vector-only)

Chào bạn, để thực hiện nhóm thủ tục liên thông (đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi) qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】, bạn cần tuân theo trình tự các bước xử lý của hệ thống và thời gian giải quyết như sau:

### Thứ tự nên làm và cách hệ thống xử lý hồ sơ
- **Bước 1:** Người yêu cầu truy cập vào ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và đóng lệ phí theo quy định 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp qua Nền tảng chia sẻ và điều phối dữ liệu để đồng bộ về Hệ thống đăng ký, quản lý hộ tịch điện tử 【PROC_3_000722_c181_s0】.
- **Bước 3:** Người thực hiện công tác hộ tịch tại Ủy ban nhân dân cấp xã thực hiện nghiệp vụ đăng ký khai sinh trong 24 giờ kể từ khi Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s1】. Trường hợp hồ sơ chưa đầy đủ hoặc cần bổ sung, cơ quan có thẩm quyền sẽ thông báo qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia trong thời gian không quá 24 giờ 【PROC_3_000722_c182_s2】【PROC_3_000722_c182_s3】.
- **Bước 4:** Sau khi bản điện tử Giấy khai sinh được chuyển sang Cổng Dịch vụ công quốc gia, hệ thống sẽ phân tách và chuyển dữ liệu đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế cho trẻ 【PROC_3_000722_c183_s1】.
- **Bước 5:** Khi người đại diện có đề nghị cấp thẻ căn cước, sau khi có thông báo kết quả đăng ký thường trú, hệ thống sẽ chuyển hồ sơ đến Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722_c184_s0】.

### Thời gian giải quyết
- Thời gian giải quyết thông thường là **ba (03) ngày làm việc** kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định 【PROC_3_000722_c185_s0】.
- Trường hợp phải xác minh thì thời gian giải quyết không quá **năm (05) ngày làm việc** 【PROC_3_000722_c185_s0】.
- Nếu tiếp nhận hồ sơ sau 15 giờ, thời gian được tính bắt đầu từ ngày làm việc tiếp theo 【PROC_3_000722_c185_s0】.
### Thủ tục áp dụng
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (13/13 checks).
- Latency end-to-end: **24.968s**.
- Gemini: **3 calls**, input `14124`, output `1826`, total `15950` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC04 — Sai ngày sinh trước khi cấp Căn cước

### Câu hỏi

Con tôi 15 tuổi (sinh năm 2011) đi làm thẻ Căn cước, nhưng trên VNeID ngày sinh của cháu bị sai so với Giấy khai sinh gốc. Gia đình có thể đến điểm cấp căn cước đưa giấy khai sinh để cán bộ làm thẻ luôn được không, hay phải làm thế nào?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_1_116410_c73_s0`, `PROC_1_116410_c63_s0`, `PROC_1_116410_c76_s0`, `PROC_1_116410_c78_s0`.
- Nội dung cần có: điều chỉnh / sửa / đính chính; cơ sở dữ liệu quốc gia về dân cư / csdl quốc gia về dân cư / cơ sở dữ liệu dân cư / csdl dân cư; trước khi cấp / trước khi làm / trước khi thực hiện thủ tục cấp / sau khi điều chỉnh / sau khi thông tin đã được cập nhật; công an cấp xã / công an xã / bộ phận một cửa cấp xã; vân tay; ảnh khuôn mặt / chụp ảnh mặt; mống mắt; cc01; cc02; 7 ngày làm việc / bảy ngày làm việc.
- Citation không được xuất hiện: `PROC_1_116410_c86_s0`, `PROC_1_116410_c90_s0`.

### Trả lời — Graph-RAG

Trường hợp thông tin ngày sinh trên VNeID của con bạn bị sai lệch so với Giấy khai sinh gốc, theo quy định thủ tục Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】 (Mã: PROC_1_116410), nếu thông tin có sự thay đổi hoặc điều chỉnh, cán bộ thu nhận sẽ hướng dẫn thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c73_s0】【PROC_1_116410_c66_s0】【PROC_1_116410_c67_s0】【PROC_1_116410_c68_s0】【PROC_1_116410_c69_s0】【PROC_1_116410_c70_s0】【PROC_1_116410_c71_s0】【PROC_1_116410_c72_s0】【PROC_1_116410_c74_s0】【PROC_1_116410_c75_s0】【PROC_1_116410_c76_s0】【PROC_1_116410_c77_s0】【PROC_1_116410_c78_s0】【PROC_1_116410_c79_s0】【PROC_1_116410_c80_s0】【PROC_1_116410_c81_s0】【PROC_1_116410_c82_s0】【PROC_1_116410_c83_s0】【PROC_1_116410_c84_s0】【PROC_1_116410_c85_s0】【PROC_1_116410_c86_s0】【PROC_1_116410_c87_s0】【PROC_1_116410_c88_s0】【PROC_1_116410_c89_s0】【PROC_1_116410_c90_s0】【PROC_1_116410_c91_s0】【PROC_1_116410_c92_s0】【PROC_1_116410_c93_s0】【PROC_1_116410_c94_s0】【PROC_1_116410_c95_s0】【PROC_1_116410_c96_s0】【PROC_1_116410_c97_s0】【PROC_1_116410_c98_s0】【PROC_1_116410_c99_s0】【PROC_1_116410_c100_s0】【PROC_1_116410_c101_s0】【PROC_1_116410_c102_s0】【PROC_1_116410_c103_s0】【PROC_1_116410_c104_s0】【PROC_1_116410_c105_s0】【PROC_1_116410_c106_s0】【PROC_1_116410_c107_s0】【PROC_1_116410_c108_s0】【PROC_1_116410_c109_s0】【PROC_1_116410_c110_s0】【PROC_1_116410_c111_s0】【PROC_1_116410_c112_s0】【PROC_1_116410_c113_s0】【PROC_1_116410_c114_s0】【PROC_1_116410_c115_s0】【PROC_1_116410_c116_s0】【PROC_1_116410_c117_s0】【PROC_1_116410_c118_s0】【PROC_1_116410_c119_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ phổ biến:** Phiếu thu nhận thông tin căn cước (Mẫu CC01) được in trong quá trình thu nhận để kiểm tra và ký xác nhận 【PROC_1_116410_c63_s0】.
- **Giấy hẹn trả kết quả:** Cơ quan Công an cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước theo Mẫu CC02 【PROC_1_116410_c78_s0】.
- **Thu nhận sinh trắc học:** Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】.
- **Cách thực hiện:** Người đại diện hợp pháp đưa người dưới 14 tuổi đến trực tiếp tại Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú 【PROC_1_116410_c67_s0】【PROC_1_116410_c81_s0】.
- **Thời gian giải quyết:** 7 ngày làm việc 【PROC_1_116410_c120_s1】.
- **Lệ phí:** Miễn phí hoặc theo quy định pháp luật 【PROC_1_116410_c120_s1】.

#### Quan sát benchmark

- Điểm rubric: **87.5/100** (14/16 checks).
- Latency end-to-end: **125.484s**.
- Gemini: **3 calls**, input `39539`, output `2256`, total `41795` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: `PROC_1_116410_c86_s0`, `PROC_1_116410_c90_s0`.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Khi thông tin ngày sinh trên VNeID hoặc Cơ sở dữ liệu quốc gia về dân cư bị sai so với Giấy khai sinh gốc, bạn cần thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi tiến hành thủ tục cấp thẻ Căn cước 【PROC_1_116410_c73_s0】. Do đó, bạn không thể chỉ mang Giấy khai sinh ra điểm cấp căn cước để làm thẻ ngay nếu dữ liệu trên hệ thống chưa khớp 【PROC_1_116410_c73_s0】.

### Thứ tự nên làm
1. **Điều chỉnh thông tin:** Liên hệ cơ quan có thẩm quyền để cập nhật lại ngày sinh cho chính xác với Giấy khai sinh gốc trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c73_s0】.
2. **Thủ tục cấp thẻ Căn cước:** Sau khi thông tin đã được điều chỉnh, tiến hành thủ tục cấp thẻ Căn cước theo quy định 【PROC_1_116410_c73_s0】.

### Giấy tờ và cách thực hiện cấp thẻ Căn cước
- **Hồ sơ phổ biến:** Phiếu thu nhận thông tin căn cước (Mẫu CC01) 【PROC_1_116410_c63_s0】.
- **Cách thức thực hiện:**
  - **Trực tiếp:** Đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước 【PROC_1_116410_c120_s1】.
  - **Trực tuyến:** Thực hiện qua cổng dịch vụ công 【PROC_1_116410_c120_s2】.
- **Thời gian giải quyết:** 7 ngày làm việc 【PROC_1_116410_c120_s1】.
- **Lệ phí:** Miễn phí cho độ tuổi cấp thẻ lần đầu (hoặc theo quy định cụ thể tùy trường hợp) 【PROC_1_116410_c120_s1】.
- **Giấy hẹn trả kết quả:** Cơ quan sẽ cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02) 【PROC_1_116410_c78_s0】.
- **Thu nhận sinh trắc học:** Tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】.

### Thủ tục áp dụng
- Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】

#### Quan sát benchmark

- Điểm rubric: **93.8/100** (15/16 checks).
- Latency end-to-end: **24.775s**.
- Gemini: **3 calls**, input `15537`, output `1394`, total `16931` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC05 — BHYT khi chưa đăng ký khai sinh

### Câu hỏi

Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `PROC_3_000722_c180_s1`, `PROC_3_000722_c176_s0`, `PROC_3_000722_c183_s2`, `PROC_3_000722_c185_s0`.
- Nội dung cần có: liên thông; vneid / cổng dịch vụ công quốc gia / cổng dvcqg; khai sinh trước / sau khi đăng ký khai sinh / sau khi có giấy khai sinh / sau khi có bản điện tử giấy khai sinh / khi đã có giấy khai sinh / sau khi hoàn tất khai sinh / sau khi có kết quả khai sinh; giấy khai sinh điện tử / bản điện tử giấy khai sinh; bảo hiểm xã hội / bhxh; mẫu số 01 / mẫu số 1 / mẫu 01; 2 ngày làm việc / hai ngày làm việc / hai (02) ngày làm việc; 3 ngày làm việc / ba ngày làm việc / ba (03) ngày làm việc; 5 ngày làm việc / năm ngày làm việc / năm (05) ngày làm việc; xác minh; nhận hồ sơ điện tử / nhận được hồ sơ điện tử / tiếp nhận hồ sơ điện tử.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

## Hướng dẫn theo thông tin đã kiểm chứng

### Thứ tự thủ tục
- Ưu tiên 1: **Thủ tục đăng ký khai sinh** 【PROC_1_001193】
- Ưu tiên 1: **Thủ tục cấp thẻ bảo hiểm y tế** 【PROC_1_014137】

### Nội dung đã đối chiếu
- **Cấp thẻ BHYT cho trẻ dưới 6 tuổi:** Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 8: - Đối với trẻ em dưới 6 tuổi, việc cấp thẻ bảo hiểm y tế thực hiện liên thông cùng với thủ tục đăng ký khai sinh, đăng ký thường trú theo quy định tại Nghị định số 63/2024/NĐ-CP ngày 10 tháng 6 năm 2024 của Chính phủ quy định việc thực hiện liên thông điện tử 02 nhóm thủ tục hành chính: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi; đăng ký khai tử, xóa đăng ký thường trú, giải quyết mai táng phí, tử tuất 【PROC_1_014137_c60_s0】
- **Tờ khai BHYT:** Thành phần hồ sơ cần nộp để thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137): - Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP - Số lượng: 1 Bản chính (Theo trường hợp / nếu có). 【PROC_1_014137_c50_s0】
- **Hình thức nộp BHYT đơn lẻ:** Cách thức nộp hồ sơ, thời gian giải quyết và lệ phí của Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137): Cơ quan tiếp nhận và giải quyết: Bảo hiểm xã hội tỉnh. - Hình thức: Trực tuyến. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). - Hình thức: Dịch vụ bưu chính. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). - Hình thức: Trực tiếp. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). 【PROC_1_014137_c61_s0】
- **Thời hạn cấp thẻ BHYT đơn lẻ:** Cách thức nộp hồ sơ, thời gian giải quyết và lệ phí của Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137): Cơ quan tiếp nhận và giải quyết: Bảo hiểm xã hội tỉnh. - Hình thức: Trực tuyến. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). - Hình thức: Dịch vụ bưu chính. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). - Hình thức: Trực tiếp. Thời gian giải quyết: 5 ngày làm việc. Lệ phí: Miễn phí (05 ngày làm việc kể từ ngày nhận đủ hồ sơ). 【PROC_1_014137_c61_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 1: - Nếu lựa chọn hình thức nộp hồ sơ trực tiếp, người yêu cầu đăng ký khai sinh nộp hồ sơ đăng ký khai tâm Phục vụ hành chính công có thẩm quyền; nộp lệ phí nếu thuộc trường hợp phải nộp lệ phí đăng ký khai sinh; nộp phí cấp bản sao Giấy khai sinh nếu có yêu cầu cấp bản sao Giấy khai sinh 【PROC_1_001193_c34_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 2: - Nếu lựa chọn hình thức nộp hồ sơ trực tuyến, người yêu cầu đăng ký khai sinh truy cập Cổng dịch vụ công quốc gia hoặc Ứng dụng định danh quốc gia. Người yêu cầu đăng ký khai sinh trực tuyến cung cấp thông tin theo mẫu hộ tịch điện tử tương tác đăng ký khai sinh, đính kèm bản chụp hoặc bản sao điện tử các giấy tờ, tài liệu theo quy định; nộp phí, lệ phí thông qua chức năng thanh toán trực tuyến hoặc bằng cách thức khác theo quy định pháp luật, hoàn tất việc sinh tại Trung nộp hồ sơ 【PROC_1_001193_c35_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 3: 【PROC_1_001193_c36_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 4: - Công chức tư pháp - hộ tịch thẩm tra hồ sơ (thẩm tra tính thống nhất, hợp lệ của các thông tin trong hồ sơ, giấy tờ, tài liệu do người yêu cầu nộp, xuất trình hoặc đính kèm) 【PROC_1_001193_c37_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 5: + Trường hợp hồ sơ cần bổ sung, hoàn thiện hoặc không đủ điều kiện giải quyết, phải từ chối thì công chức tư pháp - hộ tịch gửi thông báo về tình trạng hồ sơ tới Trung tâm Phục vụ hành chính công để thông báo cho người nộp hồ sơ – thực hiện lại bước (ii) hoặc (iii) 【PROC_1_001193_c38_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 6: + Trường hợp cần phải kiểm tra, xác minh làm rõ hoặc do nguyên nhân khác mà không thể trả kết quả đúng thời gian đã hẹn thì công chức tư pháp - hộ tịch lập Phiếu xin lỗi và hẹn lại ngày trả kết quả, trong đó nêu rõ lý do chậm trả kết quả và thời gian hẹn trả kết quả, chuyển Trung tâm Phục vụ hành chính công để trả cho người yêu cầu (nếu người yêu cầu nộp hồ sơ trực tiếp), hoặc gửi Phiếu xin lỗi và hẹn lại ngày trả kết quả qua thư điện tử hoặc gửi tin nhắn qua điện thoại di động cho người yêu cầu (nếu người yêu cầu nộp hồ sơ trực tuyến) 【PROC_1_001193_c39_s0】
- + Nếu thấy hồ sơ đầy đủ, hợp lệ, đúng quy định, trường hợp tiếp nhận hồ sơ đăng ký khai sinh theo hình thức trực tiếp, thì công chức tư pháp - hộ tịch thực hiện ghi vào Sổ đăng ký khai sinh, cập nhật thông tin đăng ký khai sinh trên Phần mềm đăng ký, quản lý hộ tịch điện tử dùng chung và chuyển thông tin đến Cơ sở dữ liệu quốc gia về dân cư để lấy Số định danh cá nhân. Trường hợp tiếp nhận hồ sơ đăng ký khai sinh theo hình thức trực tuyến, công chức tư pháp - hộ tịch gửi lại biểu mẫu Giấy khai sinh điện tử với thông tin đầy đủ cho người yêu cầu qua thư điện tử hoặc thiết bị số. Người yêu cầu có trách nhiệm kiểm tra tính chính xác, đầy đủ của các thông tin trên biểu mẫu Giấy khai sinh điện tử và xác nhận (tối đa một ngày) 【PROC_1_001193_c40_s1】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 8: - Sau khi Cơ sở dữ liệu quốc gia về dân cư trả về Số định danh cá nhân, công chức tư pháp - hộ tịch in Giấy khai sinh, bản sao Giấy khai sinh, bản điện tử Giấy khai sinh trình Lãnh đạo Ủy ban nhân dân cấp xã ký, chuyển tới Trung tâm Phục vụ hành chính công để trả kết quả cho người yêu cầu. * Lưu ý: 【PROC_1_001193_c41_s0】
- - Trường hợp cha, mẹ trẻ đã đăng ký kết hôn, trên cơ sở thông tin về Giấy chứng nhận kết hôn cung cấp trong hồ sơ đăng ký khai sinh, cơ quan đăng ký hộ tịch có trách nhiệm tra cứu, xác thực thông tin trên Hệ thống thông tin giải quyết thủ tục hành chính cấp tỉnh thông qua kết nối với Cơ sở dữ liệu hộ tịch điện tử, Cơ sở dữ liệu quốc gia về dân cư. Kết quả tra cứu được lưu trữ dưới dạng điện tử hoặc bản giấy, phản ánh đầy đủ, chính xác thông tin tại thời điểm tra cứu và đính kèm trong hồ sơ của người đăng ký. Trường hợp không tra cứu được tình trạng hôn nhân do chưa có thông tin trong Cơ sở dữ liệu hộ tịch điện tử, Cơ sở dữ liệu quốc gia về dân cư, thì cơ quan đăng ký hộ tịch đề nghị Ủy ban nhân dân cấp xã nơi người yêu cầu thường trú/nơi đã đăng ký kết hôn xác minh, cung cấp thông tin 【PROC_1_001193_c42_s1】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 10: - Trong thời hạn 60 ngày kể từ ngày sinh con, cha hoặc mẹ có trách nhiệm đăng ký khai sinh cho con; trường hợp cha, mẹ không thể đăng ký khai sinh cho con thì ông hoặc bà hoặc người thân thích khác hoặc cá nhân, tổ chức đang nuôi dưỡng trẻ em có trách nhiệm đăng ký khai sinh cho trẻ em 【PROC_1_001193_c43_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 11: - Trường hợp đăng ký khai sinh cho trẻ bị bỏ rơi thì sau khi nhận được thông báo, Lãnh đạo Ủy ban nhân dân hoặc Trưởng công an cấp xã có trách nhiệm tổ chức lập biên bản về việc trẻ bị bỏ rơi. Sau khi lập biên bản, Ủy ban nhân dân cấp xã tiến hành niêm yết tại trụ sở Ủy ban nhân dân trong 07 ngày liên tục về việc trẻ bị bỏ rơi. Hết thời hạn niêm yết, nếu không có thông tin về cha, mẹ đẻ của trẻ, Ủy ban nhân dân cấp xã thông báo cho cá nhân hoặc tổ chức đang tạm thời nuôi dưỡng trẻ để tiến hành đăng ký khai sinh cho trẻ 【PROC_1_001193_c44_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 12: - Trường hợp trẻ chưa xác định được cha thì họ, dân tộc, quê quán, quốc tịch của con được xác định theo họ, dân tộc, quê quán, quốc tịch của mẹ; phần ghi về cha của trẻ để trống. Nếu vào thời điểm đăng ký khai sinh người cha yêu cầu làm thủ tục nhận con thì kết hợp giải quyết việc nhận con và đăng ký khai sinh 【PROC_1_001193_c45_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 13: - Trường hợp trẻ chưa xác định được mẹ mà khi đăng ký khai sinh cha yêu cầu làm thủ tục nhận con thì kết hợp giải quyết việc nhận con và đăng ký khai sinh; phần khai về mẹ của trẻ để trống 【PROC_1_001193_c46_s0】
- Trình tự thực hiện Thủ tục đăng ký khai sinh (Mã: PROC_1_001193) - Bước 14: - Trường hợp trẻ chưa xác định được cả cha và mẹ nhưng không thuộc diện bị bỏ rơi, thì thực hiện tương tự như đăng ký khai sinh cho trẻ bị bỏ rơi, trong Sổ hộ tịch ghi rõ “Trẻ chưa xác định được cha, mẹ” 【PROC_1_001193_c47_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 1: - Bước 1: Người tham gia bảo hiểm y tế kê khai đầy đủ thông tin theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP hoặc cơ quan, tổ chức quản lý đối tượng kê khai đầy đủ thông tin theo Mẫu số 3 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP trên Cổng dịch vụ công quốc gia hoặc qua ứng dụng của cơ quan bảo hiểm xã hội hoặc nộp trực tiếp tại bộ phận một cửa của cơ quan bảo hiểm xã hội hoặc gửi qua dịch vụ bưu chính công ích đến cơ quan bảo hiểm xã hội được giao nhiệm vụ tiếp nhận 【PROC_1_014137_c53_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 2: + Người tham gia bảo hiểm y tế hoặc cơ quan, tổ chức quản lý đối tượng tích chọn cấp thẻ bảo hiểm y tế bản điện tử hoặc cấp thẻ bảo hiểm y tế bản giấy trên Tờ khai tham gia hoặc danh sách đối tượng tham gia 【PROC_1_014137_c54_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 3: + Trường hợp thay đổi thông tin thân nhân hoặc thay đổi thông tin quyền lợi được hưởng thì người tham gia bảo hiểm y tế phải cung cấp bản chụp (scan) các văn bản, tài liệu liên quan để nộp cùng Tờ khai trên 【PROC_1_014137_c55_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 4: - Bước 2: Cổng dịch vụ công quốc gia hoặc ứng dụng của cơ quan bảo hiểm xã hội hoặc cán bộ tiếp nhận hồ sơ trả Giấy tiếp nhận hồ sơ và hẹn trả kết quả cấp thẻ bảo hiểm y tế cho người tham gia bảo hiểm y tế hoặc cho cơ quan, tổ chức quản lý đối tượng 【PROC_1_014137_c56_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 5: - Bước 3: Trong thời hạn 05 ngày làm việc, kể từ ngày nhận đủ hồ sơ theo quy định, cơ quan bảo hiểm xã hội trả thẻ bảo hiểm y tế, cụ thể như sau: 【PROC_1_014137_c57_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 6: + Trường hợp cấp thẻ bảo hiểm y tế bản điện tử, cơ quan bảo hiểm xã hội trả kết quả thẻ bảo hiểm y tế bản điện tử vào ứng dụng bảo hiểm xã hội số (VssID), hòm thư điện tử cá nhân (email), liên kết với tài khoản định danh điện tử (VNeID) mức độ 2 【PROC_1_014137_c58_s0】
- Trình tự thực hiện Thủ tục cấp thẻ bảo hiểm y tế (Mã: PROC_1_014137) - Bước 7: + Trường hợp cấp thẻ bảo hiểm y tế bản giấy, cơ quan bảo hiểm xã hội chuyển thẻ bảo hiểm y tế bản giấy cho người tham gia bảo hiểm y tế hoặc tổ chức quản lý đối tượng 【PROC_1_014137_c59_s0】
- - Bước 1: Người yêu cầu truy cập vào Cổng Dịch vụ công quốc gia (tại địa chỉ dichvucong.gov.vn) hoặc trên ứng dụng VNeID, lựa chọn dịch vụ công liên thông Đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi để thực hiện nộp hồ sơ trực tuyến và lệ phí theo quy định. Các thông tin trong tờ khai điện tử được điền tự động đối với các thông tin đã có trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu hộ tịch, Cơ sở dữ liệu quốc gia về Bảo hiểm và cơ sở dữ liệu, hệ thống thông tin có liên quan khác. Cá nhân đăng nhập Cổng Dịch vụ công quốc gia hoặc Ứng dụng định danh quốc gia (VNeID) đề nghị giải quyết thủ tục hành chính thì không phải thực hiện ký số biểu mẫu điện tử tương tác. Thông báo hẹn trả kết quả giải quyết từng thủ tục hành chính trong quy trình liên thông được gửi cho người yêu cầu qua Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID hoặc gửi tin nhắn điện thoại tự động của Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】
- Trình tự thực hiện Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722) - Bước 2: - Bước 2. Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công từ nền tảng thanh toán và tiến hành bóc tách thành phần hồ sơ, thực hiện chuyển hồ sơ (bao gồm biểu mẫu điện tử tương tác, các giấy tờ đính kèm) sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp qua Nền tảng chia sẻ và điều phối dữ liệu. Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp đồng bộ hồ sơ về Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp. Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp tiếp nhận hồ sơ và phản hồi trạng thái cho Cổng Dịch vụ công quốc gia qua Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp 【PROC_3_000722_c181_s0】
- Trường hợp cần bổ sung thành phần hồ sơ thì người yêu cầu có trách nhiệm hoàn thiện hồ sơ trong 07 ngày làm việc, nếu quá thời hạn này không bổ sung thì người thực hiện công tác hộ tịch tại Ủy ban nhân dân cấp xã thực hiện thao tác trên Hệ thống đăng ký, quản lý hộ tịch điện tử của Bộ Tư pháp để dừng xử lý do không bổ sung theo quy định. Thông tin về việc dừng xử lý được gửi đến Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp để thông báo cho người yêu cầu qua Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID hoặc gửi tin nhắn điện thoại tự động của Cổng Dịch vụ công quốc gia. Sau khi tiếp nhận hồ sơ đăng ký khai sinh, Chủ tịch Ủy ban nhân dân xã, phường, đặc khu đồng thời xem xét, quyết định việc hỗ trợ tài chính khi sinh con và thực hiện chi trả cho phụ nữ sinh con theo quy định pháp luật dân số 【PROC_3_000722_c182_s3】
- - Bước 4. Giải quyết hồ sơ đăng ký thường trú và cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi Sau khi Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp chuyển bản điện tử Giấy khai sinh sang Cổng Dịch vụ công quốc gia, sau đó Cổng Dịch vụ công quốc gia phân tách, chuyển hồ sơ điện tử (bao gồm biểu mẫu, tờ khai người yêu cầu đã kê khai, bản điện tử Giấy khai sinh) đến Hệ thống thông tin quản lý cư trú để thực hiện đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để thực hiện cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi theo quy định pháp luật liên quan. Thời gian giải quyết đăng ký thường trú không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử đối với trường hợp: con về với cha, mẹ và cha, mẹ là chủ hộ, đồng thời là chủ sở hữu chỗ ở hợp pháp; con về với cha, mẹ nhưng cha, mẹ không phải là chủ sở hữu chỗ ở hợp pháp 【PROC_3_000722_c183_s1】
- Trình tự thực hiện Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722) - Bước 5: - Bước 5. Giải quyết hồ sơ cấp thẻ căn cước cho trẻ em dưới 6 tuổi (khi người đại diện hợp pháp có đề nghị cấp thẻ căn cước cho trẻ tại bước nộp hồ sơ trực tuyến) Sau khi Hệ thống thông tin quản lý cư trú của Bộ Công an chuyển bản điện tử Thông báo kết quả giải quyết đăng ký thường trú sang Cổng Dịch vụ công quốc gia, sau đó Cổng Dịch vụ công quốc gia phân tách, chuyển hồ sơ điện tử (biểu mẫu, tờ khai người yêu cầu đã kê khai) đến Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước theo quy định của Luật Căn cước số 26/2023/QH15. Thời gian giải quyết cấp thẻ căn cước không quá 05 ngày làm việc kể từ ngày nhận được hồ sơ điện tử trên hệ thống 【PROC_3_000722_c184_s0】

#### Quan sát benchmark

- Điểm rubric: **60.0/100** (9/15 checks).
- Latency end-to-end: **31.384s**.
- Gemini: **3 calls**, input `35622`, output `2848`, total `38470` tokens.
- Citation bị thiếu theo rubric: `PROC_3_000722_c176_s0`, `PROC_3_000722_c183_s2`, `PROC_3_000722_c185_s0`.
- Citation sai/không được phép: Không có.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt..

### Trả lời — RAG không đồ thị (vector-only)

Con bạn 1 tháng tuổi chưa làm giấy khai sinh và đang ốm cần đi viện, bạn **không thể** tự ý đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT riêng lẻ trước cho cháu mà bỏ qua khai sinh, vì đối với trẻ dưới 6 tuổi, việc cấp thẻ BHYT được thực hiện liên thông cùng với thủ tục đăng ký khai sinh và đăng ký thường trú 【PROC_1_014137_c60_s0】. Tình trạng của bạn cần hoàn thiện điều kiện đăng ký khai sinh trước khi nộp hồ sơ. 

Dưới đây là các phương án và thông tin thủ tục cần thực hiện:

### Thứ tự nên làm
1. **Thủ tục đăng ký khai sinh 【PROC_1_001193】** (Mã: PROC_1_001193): Cần thực hiện tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】 trong thời hạn 60 ngày kể từ ngày sinh con 【PROC_1_001193_c43_s0】.
2. **Liên thông điện tử đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi** (Mã: PROC_3_000722): Hoặc bạn có thể thực hiện nhóm thủ tục liên thông này trực tuyến để giải quyết đồng thời khai sinh và cấp thẻ BHYT cho trẻ 【PROC_3_000722_c183_s1】.

### Giấy tờ và cách thực hiện cho từng phương án

#### Phương án 1: Thực hiện gói Liên thông điện tử (Khuyên dùng để giải quyết nhanh BHYT cho trẻ)
- **Hồ sơ cần nộp:**
  - Tờ khai điện tử theo mẫu 【PROC_3_000722_c175_s0】.
  - Dữ liệu điện tử có ký số của Giấy chứng sinh được liên thông từ cơ sở khám chữa bệnh hoặc bản điện tử Giấy chứng sinh do người yêu cầu đính kèm 【PROC_3_000722_c177_s0】.
- **Cách thức thực hiện:** Nộp trực tuyến trên Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.
- **Cơ quan tiếp nhận và giải quyết:** Công an cấp xã 【PROC_3_000722_c184_s0】.
- **Thời gian giải quyết:** 3 ngày làm việc kể từ khi các cơ quan nhận đủ hồ sơ, trường hợp phải xác minh thì không quá 5 ngày làm việc 【PROC_3_000722_c184_s0】.

#### Phương án 2: Nộp thủ tục cấp thẻ BHYT đơn lẻ (Sau khi đã có giấy khai sinh)
- **Hồ sơ cần nộp:** Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c50_s0】.
- **Cách thức thực hiện:** Trực tuyến, dịch vụ bưu chính công ích, hoặc trực tiếp tại bộ phận một cửa của cơ quan bảo hiểm xã hội 【PROC_1_014137_c53_s0】.
- **Cơ quan tiếp nhận và giải quyết:** Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】.
- **Thời gian giải quyết:** 05 ngày làm việc kể từ ngày nhận đủ hồ sơ 【PROC_1_014137_c61_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_014137_c61_s0】.
### Thủ tục áp dụng
- Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Quan sát benchmark

- Điểm rubric: **53.3/100** (8/15 checks).
- Latency end-to-end: **55.970s**.
- Gemini: **2 calls**, input `17246`, output `1179`, total `18425` tokens.
- Citation bị thiếu theo rubric: `PROC_3_000722_c176_s0`, `PROC_3_000722_c183_s2`, `PROC_3_000722_c185_s0`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---
