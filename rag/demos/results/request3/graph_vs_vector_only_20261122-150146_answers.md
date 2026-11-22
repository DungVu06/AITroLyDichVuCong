# Nhật ký 10 câu trả lời — Graph-RAG vs RAG không đồ thị

- Thời điểm chạy UTC: 2026-11-22T08:01:46+00:00
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

Trường hợp sinh con tại nhà và không có Giấy chứng sinh, bạn vẫn hoàn toàn có thể làm thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】. 

### 1. Giấy tờ thay thế Giấy chứng sinh
- Trường hợp không có Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.

### 2. Nơi nộp hồ sơ và thời gian giải quyết
- **Cơ quan tiếp nhận và giải quyết:** Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
- **Hình thức nộp:** Có thể nộp trực tiếp, trực tuyến hoặc thông qua dịch vụ bưu chính 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết:** 1 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí:** Miễn phí 【PROC_1_001193_c48_s0】.
### Thủ tục áp dụng
- Thủ tục đăng ký khai sinh 【PROC_1_001193】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (5/5 checks).
- Latency end-to-end: **29.938s**.
- Gemini: **2 calls**, input `6310`, output `506`, total `6816` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Trường hợp vợ sinh con tại nhà ở xã An Phú và không có Giấy chứng sinh của bệnh viện, anh/chị vẫn có thể thực hiện thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】. Cụ thể hành trình và giấy tờ cần chuẩn bị như sau:

### Thứ tự nên làm
1. **Thủ tục đăng ký khai sinh 【PROC_1_001193】** (Mã: PROC_1_001193): Thực hiện tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ thay thế Giấy chứng sinh**: Trường hợp không có Giấy chứng sinh thì nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】 (1 bản chính).
- **Cách thức nộp hồ sơ**: Có thể nộp trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
- **Thời gian giải quyết**: 1 ngày 【PROC_1_001193_c48_s0】.
- **Lệ phí**: Miễn phí 【PROC_1_001193_c48_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (5/5 checks).
- Latency end-to-end: **25.164s**.
- Gemini: **2 calls**, input `6328`, output `552`, total `6880` tokens.
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

## Hướng dẫn theo thông tin đã kiểm chứng

### Thứ tự thủ tục
- Ưu tiên 1: **Đăng ký thường trú** 【PROC_1_116788】

### Nội dung đã đối chiếu
- **Hợp đồng thuê, mượn hoặc ở nhờ:** Thành phần hồ sơ cần nộp để thực hiện Đăng ký thường trú (Mã: PROC_1_116788): - Hợp đồng, văn bản về việc cho thuê, cho mượn, cho ở nhờ chỗ ở hợp pháp được công chứng hoặc chứng thực theo quy định của pháp luật - Số lượng: 1 Bản chính (Theo trường hợp / nếu có). 【PROC_1_116788_c127_s0】
- **Văn bản đồng ý của chủ sở hữu:** - Trường hợp đăng ký thường trú vào chỗ ở hợp pháp của chủ sở hữu là người bị mất năng lực hành vi dân sự, người có khó khăn trong nhận thức, làm chủ hành vi theo quy định của Bộ luật Dân sự, người dưới 18 tuổi, người bị tuyên bố mất tích, người đã chết thì chỉ cần lấy ý kiến đồng ý của một trong những người đại diện hợp pháp, người thừa kế của chủ sở hữu theo quy định của pháp luật. - Người có mối quan hệ với chủ sở hữu chỗ ở hợp pháp theo quy định tại điểm a khoản 2 Điều 20 Luật Cư trú mà chủ sở hữu không đăng ký thường trú tại chỗ ở hợp pháp đó và không thuộc trường hợp quy định tại Điều 23 Luật Cư trú hoặc người đăng ký thường trú có mối quan hệ với chủ hộ, thành viên hộ gia đình theo quy định tại điểm a khoản 2 Điều 20 Luật Cư trú mà nơi thường trú của chủ hộ, thành viên hộ gia đình đó là chỗ ở hợp pháp do thuê, mượn, ở nhờ thì hồ sơ đăng ký thường trú thực hiện theo khoản 2 Điều 21 Luật Cư trú 【PROC_1_116788_c142_s2】
- **Điều kiện diện tích chỗ ở:** Thành phần hồ sơ cần nộp để thực hiện Đăng ký thường trú (Mã: PROC_1_116788): - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú tại chỗ ở hợp pháp do thuê, mượn, ở nhờ được khai thác trong căn cước điện tử, tài khoản định danh điện tử trên hệ thống định danh và xác thực điện tử qua Ứng dụng định danh quốc gia hoặc trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu về cư trú, Hệ thống thông tin giải quyết thủ tục hành chính cấp bộ, cấp tỉnh hoặc cơ sở dữ liệu quốc gia, cơ sở dữ liệu chuyên ngành khác. Trường hợp không khai thác được thông tin thì công dân xuất trình giấy tờ, tài liệu quy định tại khoản 2 Điều 5 Nghị định số 154/2024/NĐ-CP, trong đó có thể hiện diện tích nhà ở hoặc xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân bảo đảm theo quy định của Hội đồng nhân dân tỉnh, thành phố trực thuộc trung ương theo Mẫu số 02 ban hành kèm theo Nghị định số 58/2026/NĐ-CP ngày 13/02/2026 của Chính phủ - Số lượng: 1 Bản chính (Theo trường hợp / nếu có). 【PROC_1_116788_c128_s0】
- **Cơ quan tiếp nhận thường trú:** Cách thức nộp hồ sơ, thời gian giải quyết và lệ phí của Đăng ký thường trú (Mã: PROC_1_116788): Cơ quan tiếp nhận và giải quyết: Công an Xã. 【PROC_1_116788_c174_s0】
- **Thời hạn giải quyết thường trú:** - Hình thức: Trực tuyến. Thời gian giải quyết: 7 ngày làm việc. Lệ phí: 20,000 Việt Nam Đồng (Công dân nộp hồ sơ trực tiếp thu 20.000 đồng/lần đăng ký thường trú); 10,000 Việt Nam Đồng (Công dân nộp hồ sơ qua Cổng dịch vụ công quốc gia thu 10.000 đồng/lần đăng ký thường trú); 10,000 Việt Nam Đồng (Công dân nộp hồ sơ trực tiếp thu 10.000 đồng/lần đăng ký tách hộ); 5,000 Việt Nam Đồng (Công dân nộp hồ sơ qua Cổng dịch vụ công quốc gia thu 5.000 đồng/lần đăng ký tách hộ) (- Thời hạn 07 ngày làm việc kể từ ngày nhận được hồ sơ đầy đủ và chính xác đối với trường hợp “Đăng ký thường trú”. Trường hợp công dân nộp hồ sơ đăng ký thường trú và Tờ khai đề nghị xác nhận nơi thường xuyên đậu, đỗ; sử dụng phương tiện vào mục đích để ở hoặc Tờ khai xác nhận tình trạng chỗ ở hợp pháp, diện tích nhà ở tối thiểu để đăng ký thường trú, đăng ký tạm trú đến cơ quan đăng ký cư trú thì thời gian giải quyết của Ủy ban nhân dân cấp xã không tính vào thời hạn giải quyết hồ sơ đăng ký thường trú 【PROC_1_116788_c174_s3】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (9/9 checks).
- Latency end-to-end: **36.068s**.
- Gemini: **3 calls**, input `15080`, output `1333`, total `16413` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Có.
- Warning: Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt..

### Trả lời — RAG không đồ thị (vector-only)

Để đăng ký thường trú tại căn nhà thuê ở xã Tân Triều với hợp đồng viết tay, bạn cần lưu ý rằng hồ sơ thuê nhà bắt buộc phải có hợp đồng được công chứng hoặc chứng thực theo quy định của pháp luật 【PROC_1_116788_c127_s0】. Vì bạn mới có hợp đồng viết tay chưa được công chứng/chứng thực, bạn cần hoàn thiện điều kiện này trước khi nộp hồ sơ. Cơ quan tiếp nhận và giải quyết hồ sơ là **Công an Xã** 【PROC_1_116788_c174_s0】, không phải UBND xã.

### Thứ tự nên làm
1. Công chứng hoặc chứng thực hợp đồng thuê nhà.
2. Chuẩn bị hồ sơ và nộp trực tuyến qua cổng dịch vụ công hoặc trực tiếp tại Công an Xã 【PROC_1_116788_c174_s3】.

### Giấy tờ và cách thực hiện
- **Thành phần hồ sơ:** 
  - Hợp đồng, văn bản về việc cho thuê, cho mượn, cho ở nhờ chỗ ở hợp pháp được công chứng hoặc chứng thực theo quy định của pháp luật 【PROC_1_116788_c127_s0】.
  - Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú tại chỗ ở hợp pháp do thuê, mượn, ở nhờ được khai thác trong căn cước điện tử, tài khoản định danh điện tử trên hệ thống định danh và xác thực điện tử qua Ứng dụng định danh quốc gia hoặc trong Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu về cư trú, Hệ thống thông tin giải quyết thủ tục hành chính cấp bộ, cấp tỉnh hoặc cơ sở dữ liệu quốc gia, cơ sở dữ liệu chuyên ngành khác. Trường hợp không khai thác được thông tin thì công dân xuất trình giấy tờ, tài liệu quy định tại khoản 2 Điều 5 Nghị định số 154/2024/NĐ-CP, trong đó có thể hiện diện tích nhà ở hoặc xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân bảo đảm theo quy định của Hội đồng nhân dân tỉnh, thành phố trực thuộc trung ương theo Mẫu số 02 ban hành kèm theo Nghị định số 58/2026/NĐ-CP ngày 13/02/2026 của Chính phủ 【PROC_1_116788_c128_s0】.
  - Trường hợp đăng ký thường trú vào chỗ ở hợp pháp của chủ sở hữu là người bị mất năng lực hành vi dân sự, người có khó khăn trong nhận thức, làm chủ hành vi theo quy định của Bộ luật Dân sự, người dưới 18 tuổi, người bị tuyên bố mất tích, người đã chết thì chỉ cần lấy ý kiến đồng ý của một trong những người đại diện hợp pháp, người thừa kế của chủ sở hữu theo quy định của pháp luật 【PROC_1_116788_c142_s2】.
- **Cách thức thực hiện:** Nộp trực tuyến hoặc trực tiếp tại Công an Xã 【PROC_1_116788_c174_s0】 【PROC_1_116788_c174_s3】.
- **Thời gian giải quyết:** 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ 【PROC_1_116788_c174_s3】.
- **Lệ phí:** 20.000 đồng/lần nếu nộp trực tiếp; 10.000 đồng/lần nếu nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.
### Thủ tục áp dụng
- Đăng ký thường trú 【PROC_1_116788】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (9/9 checks).
- Latency end-to-end: **30.076s**.
- Gemini: **3 calls**, input `15729`, output `1683`, total `17412` tokens.
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

Bạn có thể thực hiện gói thủ tục liên thông điện tử cho trẻ dưới 6 tuổi (gồm đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước) trực tuyến qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】【PROC_3_000722_c185_s0】.

### Thứ tự nên làm
Thực hiện nộp hồ sơ trực tuyến theo nhóm thủ tục liên thông mã `PROC_3_000722` 【PROC_3_000722】 【PROC_3_000722_c180_s1】.

### Giấy tờ và cách thực hiện
- **Cách thức thực hiện:** Nộp hồ sơ trực tuyến trên ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) 【PROC_3_000722_c180_s1】【PROC_3_000722_c185_s0】.
- **Lệ phí:** Miễn phí (phí, lệ phí theo quy định của các thủ tục hành chính tương ứng) 【PROC_3_000722_c185_s0】.
- **Thời gian giải quyết:** Tổng thời gian giải quyết thông thường là 03 ngày làm việc kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định, trường hợp phải xác minh thì không quá 05 ngày làm việc. Nếu tiếp nhận hồ sơ sau 15 giờ thì thời gian được tính bắt đầu từ ngày làm việc tiếp theo 【PROC_3_000722_c185_s0】.

### Các bước hệ thống xử lý (Mã thủ tục: PROC_3_000722)
- **Bước 1:** Người yêu cầu truy cập Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và đóng lệ phí. Thông tin trên tờ khai điện tử được điền tự động từ cơ sở dữ liệu quốc gia 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thông tin thanh toán thành công, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp để đồng bộ về Hệ thống đăng ký, quản lý hộ tịch điện tử 【PROC_3_000722_c181_s0】.
- **Bước 3:** Người thực hiện công tác hộ tịch tại UBND cấp xã giải quyết đăng ký khai sinh trong 24 giờ kể từ khi nhận đủ hồ sơ hợp lệ. Trường hợp hồ sơ chưa đầy đủ, thông báo bổ sung sẽ được gửi qua Cổng Dịch vụ công hoặc VNeID trong vòng 24 giờ. Nếu cần bổ sung, người yêu cầu hoàn thiện hồ sơ trong 07 ngày làm việc. Chủ tịch UBND cấp xã đồng thời xem xét hỗ trợ tài chính khi sinh con (nếu có) 【PROC_3_000722_c182_s1】【PROC_3_000722_c182_s2】【PROC_3_000722_c182_s3】.
- **Bước 4:** Sau khi chuyển bản điện tử Giấy khai sinh, hệ thống tiếp tục chuyển dữ liệu đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế. Thời gian giải quyết thường trú không quá 02 ngày làm việc (hoặc không quá 05 ngày làm việc nếu cần xác minh theo Luật Cư trú). Thời gian cấp thẻ bảo hiểm y tế không quá 02 ngày làm việc 【PROC_3_000722_c183_s1】【PROC_3_000722_c183_s2】.
- **Bước 5:** Giải quyết hồ sơ cấp thẻ căn cước cho trẻ em dưới 6 tuổi (khi người đại diện có đề nghị tại bước nộp hồ sơ). Hệ thống quản lý cư trú chuyển thông báo kết quả thường trú để Hệ thống sản xuất, cấp và quản lý căn cước thực hiện cấp thẻ. Thời gian giải quyết không quá 05 ngày làm việc kể từ ngày nhận được hồ sơ điện tử 【PROC_3_000722_c184_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (12/12 checks).
- Latency end-to-end: **26.242s**.
- Gemini: **2 calls**, input `7747`, output `1259`, total `9006` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Để thực hiện gói thủ tục liên thông điện tử cho trẻ dưới 6 tuổi (gồm đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước), bạn có thể nộp hồ sơ trực tuyến qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】【PROC_3_000722_c185_s0】.

### Các bước hệ thống xử lý (Mã: PROC_3_000722)
- **Bước 1:** Người yêu cầu truy cập Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID, lựa chọn dịch vụ công liên thông để nộp hồ sơ trực tuyến và đóng lệ phí 【PROC_3_000722_c180_s1】.
- **Bước 2:** Cổng Dịch vụ công quốc gia nhận thanh toán, bóc tách hồ sơ và chuyển sang Hệ thống thông tin giải quyết thủ tục hành chính của Bộ Tư pháp 【PROC_3_000722_c181_s0】.
- **Bước 3:** UBND cấp xã giải quyết hồ sơ đăng ký khai sinh trong 24 giờ kể từ khi nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s1】. Trường hợp cần bổ sung hồ sơ, người yêu cầu hoàn thiện trong 07 ngày làm việc 【PROC_3_000722_c182_s3】.
- **Bước 4:** Hệ thống chuyển bản điện tử Giấy khai sinh để thực hiện đăng ký thường trú (thời gian không quá 02 ngày làm việc hoặc 05 ngày làm việc nếu phải xác minh) và cấp thẻ bảo hiểm y tế (không quá 02 ngày làm việc) 【PROC_3_000722_c183_s1】【PROC_3_000722_c183_s2】.
- **Bước 5:** Giải quyết hồ sơ cấp thẻ căn cước cho trẻ em dưới 6 tuổi (nếu có đề nghị từ bước nộp hồ sơ) với thời gian không quá 05 ngày làm việc kể từ khi nhận hồ sơ điện tử 【PROC_3_000722_c184_s0】.

### Thời gian và lệ phí
- **Thời gian giải quyết:** 03 ngày làm việc kể từ khi các cơ quan nhận đầy đủ hồ sơ; trường hợp phải xác minh thì không quá 05 ngày làm việc. Nếu nộp hồ sơ sau 15 giờ, thời gian được tính bắt đầu từ ngày làm việc tiếp theo 【PROC_3_000722_c185_s0】.
- **Lệ phí:** Miễn phí (phí, lệ phí khác theo quy định của các thủ tục tương ứng) 【PROC_3_000722_c185_s0】.
### Thủ tục áp dụng
- Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (12/12 checks).
- Latency end-to-end: **18.670s**.
- Gemini: **2 calls**, input `7745`, output `892`, total `8637` tokens.
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

Khi thông tin ngày sinh trên VNeID hoặc Cơ sở dữ liệu quốc gia về dân cư có sai sót so với Giấy khai sinh, trường hợp thông tin công dân có sự thay đổi hoặc điều chỉnh thì cán bộ thu nhận sẽ hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c73_s0】. Cán bộ thu nhận sẽ tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】. Đồng thời, cơ quan công an sẽ cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02) khi hoàn tất quy trình 【PROC_1_116410_c78_s0】. Do đó, bạn cần hoàn thiện việc điều chỉnh thông tin ngày sinh cho cháu trước khi làm thẻ căn cước.

### Thứ tự nên làm
1. **Điều chỉnh thông tin:** Mang Giấy khai sinh gốc đến cơ quan có thẩm quyền để cập nhật, điều chỉnh lại ngày sinh cho chính xác trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c73_s0】.
2. **Thực hiện cấp thẻ căn cước:** Sau khi thông tin đã được đồng bộ chính xác, tiến hành làm thủ tục cấp thẻ căn cước tại cơ quan công an.

### Giấy tờ và cách thực hiện (Mã thủ tục: PROC_1_116410)
- **Hồ sơ phổ biến:** 
  - Phiếu thu nhận thông tin căn cước (Mẫu CC01) được in trong quá trình thu nhận để kiểm tra và ký xác nhận 【PROC_1_116410_c63_s0】.
  - Giấy khai sinh hoặc giấy tờ pháp lý chứa thông tin hợp lệ của công dân.
- **Cách thực hiện:** 
  - **Trực tiếp:** Công dân từ đủ 14 tuổi (tính đến hiện tại cháu 15 tuổi) có thể đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc nơi cư trú để làm thủ tục 【PROC_1_116410_c120_s1】.
  - **Trực tuyến:** Nộp hồ sơ trực tuyến một phần đối với công dân từ đủ 06 tuổi trở lên 【PROC_1_116410_c120_s2】.
- **Thời gian và lệ phí:** 7 ngày làm việc 【PROC_1_116410_c120_s1】.

### Thủ tục áp dụng
- Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (11/11 checks).
- Latency end-to-end: **61.446s**.
- Gemini: **3 calls**, input `15261`, output `1442`, total `16703` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Khi thông tin ngày sinh của con trên VNeID và Cơ sở dữ liệu quốc gia về dân cư bị sai lệch so với Giấy khai sinh gốc, gia đình cần thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi tiến hành làm thẻ Căn cước 【PROC_1_116410_c73_s0】.

### Thứ tự nên làm
1. **Bước 1:** Đến Công an cấp xã để yêu cầu cập nhật, điều chỉnh lại ngày sinh cho khớp với Giấy khai sinh gốc trong Cơ sở dữ liệu quốc gia về dân cư 【PROC_1_116410_c73_s0】.
2. **Bước 2:** Sau khi thông tin đã được điều chỉnh chính xác, thực hiện thủ tục cấp thẻ Căn cước cho cháu 【PROC_1_116410_c73_s0】.

### Giấy tờ và cách thực hiện
- **Hồ sơ phổ biến gồm:** Phiếu thu nhận thông tin căn cước (Mẫu CC01) 【PROC_1_116410_c63_s0】.
- **Quy trình tiếp nhận:** Quá trình làm thủ tục bao gồm việc thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】, sau đó cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02) 【PROC_1_116410_c78_s0】.
- **Cách thức thực hiện:** Trực tiếp tại Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú 【PROC_1_116410_c120_s1】, hoặc nộp trực tuyến một phần qua cổng dịch vụ công đối với công dân từ đủ 06 tuổi trở lên 【PROC_1_116410_c120_s2】.
- **Thời gian giải quyết:** 7 ngày làm việc 【PROC_1_116410_c120_s1】.

### Thủ tục áp dụng
- Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (11/11 checks).
- Latency end-to-end: **27.866s**.
- Gemini: **3 calls**, input `15292`, output `1180`, total `16472` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---

## TC05 — BHYT khi chưa đăng ký khai sinh

### Câu hỏi

Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?

### Rubric đối chiếu

- Citation bắt buộc: `REL:PROC_1_014137:REQUIRES:PROC_1_001193`, `PROC_1_014137_c50_s0`, `PROC_1_014137_c61_s0`.
- Nội dung cần có: khai sinh / trước; bảo hiểm xã hội; 05 ngày / 5 ngày.
- Citation không được xuất hiện: Không có.

### Trả lời — Graph-RAG

Theo quy định, bạn chưa thể làm ngay thủ tục cấp thẻ bảo hiểm y tế đơn lẻ tại cơ quan Bảo hiểm xã hội cho bé 1 tháng tuổi khi chưa có giấy khai sinh do thủ tục đăng ký khai sinh là điều kiện tiên quyết【REL:PROC_1_014137:REQUIRES:PROC_1_001193】【PROC_1_014137_c60_s0】.

Để giải quyết nhanh chóng cho con đi viện, bạn nên thực hiện qua phương án nhóm thủ tục liên thông điện tử (Đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi) để các cơ quan phối hợp giải quyết đồng thời【PROC_3_000722_c180_s1】.

### Thứ tự nên làm
1. **Phương án ưu tiên (Liên thông điện tử):** 
   - Thực hiện **Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722)**【PROC_3_000722_c180_s1】.
   - Cơ quan tiếp nhận và giải quyết: Công an cấp Xã 【PROC_3_000722_c185_s0】.
   - Cách thực hiện: Trực tuyến qua Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) hoặc ứng dụng VNeID 【PROC_3_000722_c180_s1】.
   - Thời gian giải quyết: 03 ngày làm việc kể từ khi các cơ quan nhận đủ hồ sơ hợp lệ (trường hợp phải xác minh không quá 05 ngày làm việc). Lệ phí: Miễn phí 【PROC_3_000722_c185_s0】.

2. **Phương án làm từng bước riêng lẻ (nếu không chọn liên thông):**
   - **Bước 1:** Thực hiện **Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193)** tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】. Thời gian giải quyết: 1 ngày. Lệ phí: Miễn phí 【PROC_1_001193_c48_s0】.
   - **Bước 2:** Sau khi có giấy khai sinh, thực hiện **Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】 (Mã: PROC_1_014137)** tại Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】.
     - Hồ sơ gồm: Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c50_s0】.
     - Hình thức nộp: Trực tuyến, dịch vụ bưu chính hoặc trực tiếp 【PROC_1_014137_c61_s0】.
     - Thời gian giải quyết: 05 ngày làm việc kể từ ngày nhận đủ hồ sơ. Lệ phí: Miễn phí 【PROC_1_014137_c61_s0】.

#### Quan sát benchmark

- Điểm rubric: **100.0/100** (6/6 checks).
- Latency end-to-end: **95.348s**.
- Gemini: **3 calls**, input `32516`, output `1780`, total `34296` tokens.
- Citation bị thiếu theo rubric: Không có.
- Citation sai/không được phép: Không có.
- Fallback: Không.

### Trả lời — RAG không đồ thị (vector-only)

Theo quy định, bạn **không thể** đến cơ quan Bảo hiểm xã hội để xin cấp thẻ bảo hiểm y tế (BHYT) đơn lẻ cho trẻ khi chưa có giấy khai sinh, vì đăng ký khai sinh là thủ tục tiên quyết 【PROC_1_014137_c60_s0】.

Tuy nhiên, để giải quyết nhanh chóng cho việc đi viện của cháu, bạn nên thực hiện nhóm thủ tục **liên thông điện tử** cho trẻ em dưới 6 tuổi (bao gồm: đăng ký khai sinh, đăng ký thường trú và cấp thẻ BHYT) 【PROC_3_000722_c184_s0】.

### Thứ tự nên làm
1. **Cách 1: Thực hiện qua cổng dịch vụ công liên thông (Khuyên dùng)**
   - **Lý do cần làm:** Giải quyết đồng thời khai sinh, thường trú và cấp thẻ BHYT nhanh chóng trên một hệ thống.
   - **Cách thực hiện:** Truy cập Cổng Dịch vụ công quốc gia (`dichvucong.gov.vn`) hoặc ứng dụng VNeID, chọn nhóm thủ tục **Đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi** (Mã: `PROC_3_000722` 【PROC_3_000722】) và nộp hồ sơ trực tuyến 【PROC_3_000722_c180_s1】.
   - **Thời gian giải quyết:** 
     - Đăng ký khai sinh: Trong 24 giờ kể từ khi hệ thống nhận đủ hồ sơ hợp lệ 【PROC_3_000722_c182_s2】.
     - Cấp thẻ BHYT cho trẻ dưới 6 tuổi: Không quá 02 ngày làm việc kể từ ngày nhận được hồ sơ điện tử từ phần mềm dịch vụ công liên thông 【PROC_3_000722_c183_s2】.
     - Đăng ký thường trú: Không quá 02 đến 05 ngày làm việc tùy theo trường hợp cụ thể 【PROC_3_000722_c183_s1】【PROC_3_000722_c183_s2】.
   - **Lệ phí:** Miễn phí (phí, lệ phí theo quy định của các thủ tục tương ứng) 【PROC_3_000722_c185_s0】.

2. **Cách 2: Thực hiện thủ tục đơn lẻ (Lần lượt từng bước)**
   - **Bước 1:** Thực hiện **Thủ tục đăng ký khai sinh** (Mã: `PROC_1_001193` 【PROC_1_001193】) tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
     - *Thời gian giải quyết:* 01 ngày 【PROC_1_001193_c48_s0】.
     - *Lệ phí:* Miễn phí 【PROC_1_001193_c48_s0】.
   - **Bước 2:** Sau khi có giấy khai sinh, thực hiện **Thủ tục cấp thẻ bảo hiểm y tế** (Mã: `PROC_1_014137` 【PROC_1_014137】) tại Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】.
     - *Hồ sơ phổ biến:* Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 Phụ lục ban hành kèm theo Nghị định số 188/2025/NĐ-CP 【PROC_1_014137_c50_s0】.
     - *Cách thực hiện:* Trực tuyến, dịch vụ bưu chính công ích, hoặc trực tiếp tại bộ phận một cửa của cơ quan bảo hiểm xã hội 【PROC_1_014137_c61_s0】.
     - *Thời gian giải quyết:* 05 ngày làm việc kể từ ngày nhận đủ hồ sơ 【PROC_1_014137_c61_s0】.
     - *Lệ phí:* Miễn phí 【PROC_1_014137_c61_s0】.

#### Quan sát benchmark

- Điểm rubric: **83.3/100** (5/6 checks).
- Latency end-to-end: **54.568s**.
- Gemini: **2 calls**, input `16520`, output `1204`, total `17724` tokens.
- Citation bị thiếu theo rubric: `REL:PROC_1_014137:REQUIRES:PROC_1_001193`.
- Citation sai/không được phép: Không có.
- Fallback: Không.

---
