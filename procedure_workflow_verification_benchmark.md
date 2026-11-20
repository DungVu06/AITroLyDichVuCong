# BỘ KIỂM CHỨNG TÍNH ĐÚNG ĐẮN CỦA LỘ TRÌNH THỦ TỤC HÀNH CHÍNH (PROCEDURE WORKFLOW BENCHMARK)

> **Phạm vi dữ liệu**: Bộ ca kiểm chứng này được xây dựng **BÁM SÁT 100% DUY NHẤT VÀO DỮ LIỆU LOCAL HIỆN TẠI** của dự án tại thư mục `data/procedure/records/` gồm 05 thủ tục hành chính cốt lõi và các quan hệ ràng buộc (`prerequisites`, `next_steps`, `part_of`, `sub_procedures`):
> 1. `PROC_1_001193`: Thủ tục đăng ký khai sinh (Hộ tịch - Cấp xã)
> 2. `PROC_1_116788`: Đăng ký thường trú (Cư trú - Công an xã)
> 3. `PROC_3_000722`: Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi
> 4. `PROC_1_116410`: Cấp, cấp đổi, cấp lại thẻ căn cước (Căn cước - Công an xã/Toàn quốc)
> 5. `PROC_1_014137`: Thủ tục cấp thẻ bảo hiểm y tế (BHYT - Cơ quan BHXH)
>
> **Mục tiêu**: Đánh giá độ chính xác, tính đầy đủ, thứ tự logic và căn cứ trích dẫn của các lộ trình thủ tục do AI tạo ra trên cơ sở dữ liệu nội bộ. Phát hiện các lỗi: sai bước, thiếu bước, đảo ngược thứ tự tiên quyết (prerequisite reversal), sai thẩm quyền hoặc trích dẫn căn cứ không có trong dữ liệu.

---

## MỤC LỤC BỘ CA THỬ NGHIỆM

1. [TC-PROC-01: Đăng ký khai sinh khi thiếu Giấy chứng sinh y tế (PROC_1_001193)](#tc-proc-01-đăng-ký-khai-sinh-khi-thiếu-giấy-chứng-sinh-y-tế-proc_1_001193)
2. [TC-PROC-02: Đăng ký thường trú vào chỗ ở hợp pháp do thuê, mượn, ở nhờ (PROC_1_116788)](#tc-proc-02-đăng-ký-thường-trú-vào-chỗ-ở-hợp-pháp-do-thuê-mượn-ở-nhờ-proc_1_116788)
3. [TC-PROC-03: Dịch vụ công liên thông điện tử 4 trong 1 cho trẻ em dưới 6 tuổi (PROC_3_000722)](#tc-proc-03-dịch-vụ-công-liên-thông-điện-tử-4-trong-1-cho-trẻ-em-dưới-6-tuổi-proc_3_000722)
4. [TC-PROC-04: Cấp thẻ Căn cước khi dữ liệu CSDL dân cư bị sai lệch (PROC_1_116410)](#tc-proc-04-cấp-thẻ-căn-cước-khi-dữ-liệu-csdl-dân-cư-bị-sai-lệch-proc_1_116410)
5. [TC-PROC-05: Cấp thẻ BHYT và quan hệ điều kiện tiên quyết với Khai sinh (PROC_1_014137)](#tc-proc-05-cấp-thẻ-bhyt-và-quan-hệ-điều-kiện-tiên-quyết-với-khai-sinh-proc_1_014137)

---

## TC-PROC-01: ĐĂNG KÝ KHAI SINH KHI THIẾU GIẤY CHỨNG SINH Y TẾ (PROC_1_001193)

### 1. Phân loại tình huống (Dữ liệu local `PROC_1_001193`)
* **Thủ tục đối chiếu**: `PROC_1_001193` - Thủ tục đăng ký khai sinh.
* **Thẩm quyền giải quyết**: Ủy ban nhân dân cấp xã (`jurisdiction`: Cấp xã - Toàn quốc).
* **Thời hạn giải quyết**: 01 ngày làm việc (Miễn phí).
* **Dạng thiếu giấy tờ**: Không có Giấy chứng sinh do cơ sở y tế cấp (sinh con tại nhà).
* **Mâu thuẫn / Ràng buộc**: Người dân nghĩ không có Giấy chứng sinh bệnh viện thì không làm được giấy khai sinh hoặc bị trả lại hồ sơ.

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Vợ chồng anh Nam chị Nga đang sinh sống tại xã An Phú. Chị Nga vừa sinh con tại nhà (chuyển dạ nhanh không kịp đến trạm y tế/bệnh viện). Khi làm thủ tục khai sinh cho con, gia đình không có Giấy chứng sinh của bệnh viện cấp.
* **Câu hỏi đầu vào (User Query)**:
  > *"Vợ tôi vừa sinh cháu tại nhà ở xã An Phú, không có Giấy chứng sinh của bệnh viện thì có làm giấy khai sinh được không? Tôi phải nộp hồ sơ ở đâu, cần giấy tờ gì thay thế và thời gian giải quyết bao lâu?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_1_001193`)
* **Cơ quan thẩm quyền**: Ủy ban nhân dân cấp xã nơi cư trú của cha hoặc mẹ.
* **Căn cứ pháp lý chuẩn (có trong local data)**:
  * Luật Hộ tịch (Luật 60/2014/QH13).
  * Thông tư 04/2020/TT-BTP (hướng dẫn Luật Hộ tịch và Nghị định 123/2015/NĐ-CP).
  * Thông tư 04/2024/TT-BTP sửa đổi, bổ sung Thông tư 04/2020/TT-BTP.
  * Nghị định 123/2015/NĐ-CP và Nghị định 104/2022/NĐ-CP.
* **Quy trình các bước chuẩn**:
  * **Bước 1 (Chuẩn bị hồ sơ thay thế theo quy định data local)**:
    * Giấy tờ thay thế Giấy chứng sinh: Nộp **văn bản của người làm chứng xác nhận về việc sinh**; nếu không có người làm chứng thì nộp **giấy cam đoan về việc sinh**.
    * Tờ khai đăng ký khai sinh theo mẫu (trường hợp trực tuyến kê khai trên biểu mẫu điện tử tương tác).
    * Giấy tờ tùy thân/cư trú: Được đối chiếu, khai thác qua kết nối Cơ sở dữ liệu quốc gia về dân cư.
  * **Bước 2 (Nộp hồ sơ)**:
    * Nộp trực tiếp tại Bộ phận tiếp nhận và trả kết quả (Một cửa) UBND cấp xã, HOẶC nộp trực tuyến qua Cổng Dịch vụ công quốc gia / Ứng dụng định danh quốc gia VNeID.
  * **Bước 3 (Thẩm tra & Giải quyết)**:
    * Công chức tư pháp - hộ tịch thẩm tra tính hợp lệ của giấy cam đoan/văn bản người làm chứng.
  * **Bước 4 (Nhận kết quả)**:
    * Cấp **Giấy khai sinh** (bản chính).
    * **Thời hạn giải quyết**: Trong **01 ngày làm việc** kể từ khi nhận đủ hồ sơ hợp lệ.

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
Thứ tự nên làm
1. Thủ tục đăng ký khai sinh 【PROC_1_001193】 (Mã: PROC_1_001193):
Lý do cần làm: Ghi nhận nhân thân cho trẻ sơ sinh theo quy định pháp luật 【PROC_1_001193_c5_s0】.
Hồ sơ phổ biến: Thay vì Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh 【PROC_1_001193_c5_s0】.
Cách thực hiện: Nộp hồ sơ trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
Thời gian và lệ phí: Giải quyết trong 1 ngày, miễn phí lệ phí 【PROC_1_001193_c48_s0】.

Nguồn tham khảo (5):
Thủ tục đăng ký khai sinh — PROC_1_001193
Thủ tục đăng ký khai sinh – document_item — PROC_1_001193_c5_s0
Thủ tục đăng ký khai sinh – document_item — PROC_1_001193_c15_s0
Thủ tục đăng ký khai sinh – document_item — PROC_1_001193_c17_s0
Thủ tục đăng ký khai sinh – execution_methods — PROC_1_001193_c48_s0
[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí kiểm chứng | Lộ trình chuẩn (Ground Truth từ `PROC_1_001193`) | Kết quả AI thể hiện | Đánh giá (Đạt / Không đạt) | Ghi chú của chuyên gia |
| :--- | :--- | :--- | :---: | :--- |
| **Xử lý giấy tờ thiếu (Missing Doc)** | Hướng dẫn thay thế Giấy chứng sinh bằng: **Văn bản của người làm chứng** hoặc **Giấy cam đoan về việc sinh**. | `Thay vì Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh` | `[x] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bảo thiếu giấy chứng sinh thì không giải quyết được.* |
| **Cơ quan thẩm quyền (Authority)** | **Ủy ban nhân dân cấp xã** (Bộ phận Một cửa cấp xã hoặc Cổng DVCQG/VNeID). | `Nộp hồ sơ trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp tại Ủy ban nhân dân cấp xã ` | `[x] Đạt`<br>`[ ] Không đạt` | *Trượt nếu hướng dẫn lên cấp huyện hoặc sai cơ quan.* |
| **Thời hạn giải quyết (Processing Time)** | **01 ngày làm việc** (theo `execution_methods` của bản ghi local). | `Giải quyết trong 1 ngày` | `[x] Đạt`<br>`[ ] Không đạt` | *Trượt nếu nêu thời hạn > 01 ngày làm việc đối với hồ sơ thường.* |
| **Căn cứ pháp lý (Legal Citation)** | Luật Hộ tịch (60/2014/QH13), Thông tư 04/2020/TT-BTP, Nghị định 123/2015/NĐ-CP. | `Như trên text kia` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu trích dẫn văn bản không có trong legal_bases của thủ tục.* |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Hệ thống có chủ động hỏi người dùng về người làm chứng hay giấy cam đoan không?**: `[ ] Có  |  [x] Không`
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]

```

---
---

## TC-PROC-02: ĐĂNG KÝ THƯỜNG TRÚ VÀO CHỖ Ở HỢP PHÁP DO THUÊ, MƯỢN, Ở NHỜ (PROC_1_116788)

### 1. Phân loại tình huống (Dữ liệu local `PROC_1_116788`)
* **Thủ tục đối chiếu**: `PROC_1_116788` - Đăng ký thường trú.
* **Thẩm quyền giải quyết**: Công an Xã (`jurisdiction`: Cấp xã - Toàn quốc).
* **Thời hạn giải quyết**: 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ.
* **Dạng thiếu giấy tờ**: Chưa có ý kiến đồng ý bằng văn bản của chủ sở hữu chỗ ở hợp pháp; thiếu tài liệu chứng minh diện tích nhà ở.
* **Điều kiện tiên quyết (`eligibility`)**: Người thực hiện đã được thu thập, cập nhật thông tin vào CSDLQG về dân cư, CSDL về cư trú.

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Anh Bình chuyển đến thuê một căn nhà tại xã Tân Triều. Anh muốn đăng ký thường trú (nhập hộ khẩu) vào địa chỉ nhà thuê này, nhưng anh chỉ mới ký hợp đồng viết tay với chủ nhà và chưa hỏi ý kiến chủ nhà về việc cho nhập khẩu.
* **Câu hỏi đầu vào (User Query)**:
  > *"Tôi đang thuê nhà ở xã Tân Triều, có hợp đồng thuê nhà viết tay. Tôi muốn đăng ký thường trú về căn nhà thuê này thì cần điều kiện và giấy tờ gì, nộp cho Công an xã hay UBND xã?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_1_116788`)
* **Cơ quan thẩm quyền**: Công an Xã (nộp trực tiếp tại Công an xã hoặc trực tuyến qua Cổng DVC Bộ Công an/VNeID).
* **Căn cứ pháp lý chuẩn (có trong local data)**:
  * Luật Cư trú 2020 (Luật số 68/2020/QH14).
  * Nghị định số 154/2024/NĐ-CP quy định chi tiết một số điều và biện pháp thi hành Luật Cư trú.
  * Thông tư số 116/2026/TT-BCA quy định chi tiết thi hành Luật Cư trú.
  * Thông tư số 54/2025/TT-BCA về quy trình đăng ký cư trú.
* **Quy trình các bước chuẩn**:
  * **Bước 1 (Kiểm tra điều kiện & Chuẩn bị hồ sơ theo data local)**:
    1. **Tờ khai thay đổi thông tin cư trú (mẫu CT01)** ban hành kèm Thông tư 116/2026/TT-BCA: Bắt buộc phải có **ý kiến đồng ý cho đăng ký thường trú của chủ hộ, chủ sở hữu chỗ ở hợp pháp**.
    2. **Hợp đồng cho thuê, cho mượn, cho ở nhờ**: Phải được **công chứng hoặc chứng thực** theo quy định của pháp luật (hợp đồng viết tay không công chứng/chứng thực là chưa đủ điều kiện).
    3. **Giấy tờ chứng minh đủ diện tích nhà ở**: Khai thác trong căn cước điện tử, tài khoản định danh điện tử hoặc giấy tờ theo Điều 5 Nghị định 154/2024/NĐ-CP / xác nhận của UBND cấp xã về diện tích bình quân bảo đảm quy định.
  * **Bước 2 (Nộp hồ sơ)**: Nộp đến **Công an cấp xã** (hoặc nộp trực tuyến qua Cổng dịch vụ công / ứng dụng VNeID).
  * **Bước 3 (Tiếp nhận & Đối chiếu)**: Cán bộ đăng ký đối chiếu thông tin kê khai với CSDLQG về dân cư. Nếu đủ điều kiện thì cấp Phiếu tiếp nhận và hẹn trả kết quả (mẫu CT04).
  * **Bước 4 (Nhận kết quả)**: Trong thời hạn **07 ngày làm việc**, nhận thông báo kết quả giải quyết cư trú cập nhật trên hệ thống (không cấp sổ hộ khẩu giấy).

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
Thứ tự thủ tục
Bạn có thể cung cấp thêm:
Hợp đồng thuê nhà viết tay của bạn đã có xác nhận của cơ quan, tổ chức có thẩm quyền hoặc công chứng, chứng thực chưa?
(Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt.)

-> Nếu bảo chưa: Dữ liệu hiện tại chưa có thông tin thủ tục và căn cứ pháp lý cụ thể cho trường hợp đăng ký thường trú tại chỗ ở thuê với hợp đồng viết tay tại xã Tân Triều. Vui lòng cung cấp thêm thông tin để tôi có thể hỗ trợ chi tiết hơn.
-> Nếu bảo có: Xin lỗi, hiện tại dữ liệu hệ thống chưa có sẵn thông tin chi tiết về thủ tục đăng ký thường trú tại chỗ ở hợp pháp do thuê cũng như các văn bản pháp luật liên quan trong phạm vi này. Do đó, tôi chưa thể cung cấp chính xác các điều kiện, hồ sơ và cơ quan tiếp nhận cụ thể cho trường hợp của bạn.

[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí kiểm chứng | Lộ trình chuẩn (Ground Truth từ `PROC_1_116788`) | Kết quả AI thể hiện | Đánh giá (Đạt / Không đạt) | Ghi chú của chuyên gia |
| :--- | :--- | :--- | :---: | :--- |
| **Cơ quan tiếp nhận (Authority)** | **Công an Xã** (Cơ quan đăng ký cư trú cấp xã). | `[Điền cơ quan AI chỉ dẫn]` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu bảo nộp UBND xã.* |
| **Yêu cầu sự đồng ý của chủ sở hữu** | Bắt buộc có **ý kiến đồng ý bằng văn bản của chủ sở hữu chỗ ở hợp pháp** trong mẫu CT01. | `[Điền AI có yêu cầu chủ nhà ký]` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu cho phép người thuê tự đăng ký mà không cần chủ nhà đồng ý.* |
| **Yêu cầu tính hợp pháp của hợp đồng** | Hợp đồng thuê nhà phải **được công chứng hoặc chứng thực**; Hợp đồng viết tay không đủ điều kiện. | `[Điền AI xử lý HĐ viết tay]` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu chấp nhận hợp đồng viết tay không chứng thực.* |
| **Chứng minh diện tích nhà ở** | Phải có thông tin/giấy tờ chứng minh đủ diện tích nhà ở tối thiểu (theo Điều 5 NĐ 154/2024/NĐ-CP). | `[Điền AI có nhắc diện tích nhà]` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu bỏ qua yêu cầu chứng minh diện tích.* |
| **Thời hạn & Biểu mẫu** | Thời hạn **07 ngày làm việc**; Mẫu **CT01** (theo Thông tư 116/2026/TT-BCA). | `[Điền thời hạn và mẫu AI nêu]` | `[ ] Đạt`<br>`[x] Không đạt` | *Trượt nếu sai thời hạn 7 ngày làm việc hoặc dùng mẫu sổ giấy cũ.* |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Hệ thống có hỏi làm rõ về việc chủ nhà có đồng ý hay hợp đồng đã công chứng chưa?**: `[x] Có  |  [ ] Không`
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Bạn có thể cung cấp thêm:

Hợp đồng thuê nhà viết tay của bạn đã có xác nhận của cơ quan, tổ chức có thẩm quyền hoặc công chứng, chứng thực chưa?
```

---
---

## TC-PROC-03: DỊCH VỤ CÔNG LIÊN THÔNG ĐIỆN TỬ 4 TRONG 1 CHO TRẺ EM DƯỚI 6 TUỔI (PROC_3_000722)

### 1. Phân loại tình huống (Dữ liệu local `PROC_3_000722`)
* **Thủ tục đối chiếu**: `PROC_3_000722` - Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi.
* **Cơ cấu liên thông**: Tích hợp 4 thủ tục đơn lẻ (`PROC_1_001193`, `PROC_1_116788`, `PROC_1_014137`, `PROC_1_116410`).
* **Đầu mối tiếp nhận**: Cổng Dịch vụ công quốc gia (`dichvucong.gov.vn`) hoặc ứng dụng VNeID.
* **Thời hạn giải quyết**: **Ba (03) ngày làm việc** kể từ khi nhận đủ hồ sơ hợp lệ (xác minh không quá 05 ngày làm việc).
* **Mâu thuẫn / Ràng buộc**: Phân định luân chuyển tự động giữa các cơ quan; không bắt công dân nộp hồ sơ rời rạc hoặc đảo lộn thứ tự có Giấy khai sinh điện tử trước.

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Anh Tuấn vừa đón con đầu lòng chào đời tại bệnh viện. Anh nghe nói hiện nay có thể làm cùng lúc trên VNeID cả 4 thủ tục: khai sinh, nhập khẩu thường trú, lấy thẻ BHYT và làm luôn thẻ Căn cước cho bé dưới 6 tuổi. Anh muốn biết quy trình thực hiện liên thông này như thế nào và mất bao lâu.
* **Câu hỏi đầu vào (User Query)**:
  > *"Tôi muốn làm thủ tục liên thông trên VNeID để vừa khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho con tôi dưới 6 tuổi. Các bước hệ thống xử lý như thế nào và mất bao nhiêu ngày làm việc?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_3_000722`)
* **Cơ quan thẩm quyền**:
  * Tiếp nhận: Cổng Dịch vụ công quốc gia hoặc Ứng dụng VNeID.
  * Phối hợp giải quyết: UBND cấp xã (khai sinh) -> Công an cấp xã (thường trú, căn cước) -> Cơ quan BHXH (thẻ BHYT).
* **Căn cứ pháp lý chuẩn (có trong local data)**:
  * Nghị định số 301/2026/NĐ-CP (sửa đổi, bổ sung một số điều của Nghị định số 63/2024/NĐ-CP quy định việc thực hiện liên thông điện tử 02 nhóm thủ tục hành chính).
* **Quy trình các bước chuẩn (5 bước trong `PROC_3_000722.json`)**:
  * **Bước 1**: Người yêu cầu truy cập Cổng DVCQG hoặc ứng dụng VNeID, lựa chọn dịch vụ công liên thông 4 thủ tục, kê khai biểu mẫu điện tử tương tác, đính kèm giấy tờ và nộp lệ phí trực tuyến.
  * **Bước 2**: Cổng DVCQG tiếp nhận thanh toán thành công, bóc tách thành phần hồ sơ chuyển sang Hệ thống đăng ký hộ tịch của Bộ Tư pháp.
  * **Bước 3 (Giải quyết khai sinh)**: Công chức tư pháp - hộ tịch UBND cấp xã thực hiện nghiệp vụ đăng ký khai sinh trong **24 giờ** kể từ khi nhận đủ hồ sơ hợp lệ, phát hành bản điện tử Giấy khai sinh.
  * **Bước 4 (Giải quyết thường trú & BHYT)**: Sau khi có bản điện tử Giấy khai sinh, Cổng DVCQG tự động phân tách chuyển tiếp hồ sơ sang:
    * Công an cấp xã: Giải quyết đăng ký thường trú.
    * Cơ quan Bảo hiểm xã hội: Giải quyết cấp thẻ BHYT cho trẻ dưới 6 tuổi.
  * **Bước 5 (Giải quyết thẻ Căn cước cho trẻ dưới 6 tuổi)**:
    * Sau khi có kết quả đăng ký thường trú, hệ thống chuyển hồ sơ sang cơ quan Công an giải quyết cấp thẻ căn cước cho trẻ dưới 6 tuổi *(thực hiện hoàn toàn trực tuyến, không thu nhận sinh trắc học mống mắt, vân tay đối với trẻ dưới 6 tuổi theo quy định `PROC_1_116410`)*.
* **Thời hạn giải quyết toàn trình**: **Không quá 03 ngày làm việc** kể từ khi các cơ quan nhận đầy đủ hồ sơ (trường hợp phải xác minh thì không quá 05 ngày làm việc).

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]



[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí kiểm chứng | Lộ trình chuẩn (Ground Truth từ `PROC_3_000722`) | Kết quả AI thể hiện | Đánh giá (Đạt / Không đạt) | Ghi chú của chuyên gia |
| :--- | :--- | :--- | :---: | :--- |
| **Tính liên thông 1 cửa điện tử** | Thực hiện trên **Cổng DVCQG / VNeID**, nộp 01 lần duy nhất, dữ liệu tự luân chuyển. | `[Điền cách thức AI chỉ dẫn]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bắt người dân đi nộp giấy riêng lẻ ở từng cơ quan.* |
| **Thứ tự luân chuyển hồ sơ** | UBND xã cấp Khai sinh trước (24h) -> chuyển sang Công an xã (Thường trú) và BHXH (BHYT) -> Căn cước dưới 6 tuổi. | `[Điền thứ tự các bước AI nêu]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu đảo lộn thứ tự giải quyết khi chưa có khai sinh.* |
| **Đặc thù căn cước dưới 6 tuổi** | Cấp thẻ căn cước cho trẻ dưới 6 tuổi làm **trực tuyến**, không thu nhận vân tay, mống mắt. | `[Điền AI có bắt thu nhận vân tay/mống mắt không]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bắt trẻ dưới 6 tuổi đi chụp ảnh mống mắt, lấy vân tay.* |
| **Thời hạn giải quyết toàn trình** | **Không quá 03 ngày làm việc** (xác minh không quá 05 ngày). | `[Điền tổng số ngày AI trả lời]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu cộng dồn cơ học các thủ tục đơn lẻ thành 7 - 15 ngày.* |
| **Căn cứ pháp lý (Legal Citation)** | Nghị định số 301/2026/NĐ-CP (hoặc Nghị định số 63/2024/NĐ-CP). | `[Điền văn bản AI trích dẫn]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu không trích dẫn văn bản liên thông trong data.* |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Hệ thống có hỏi rõ người dùng đã có tài khoản VNeID mức 2 và Giấy chứng sinh điện tử chưa?**: `[ ] Có  |  [ ] Không`
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]

```

---
---

## TC-PROC-04: CẤP THẺ CĂN CƯỚC KHI DỮ LIỆU CSDL DÂN CƯ BỊ SAI LỆCH (PROC_1_116410)

### 1. Phân loại tình huống (Dữ liệu local `PROC_1_116410`)
* **Thủ tục đối chiếu**: `PROC_1_116410` - Cấp, cấp đổi, cấp lại thẻ căn cước.
* **Thẩm quyền giải quyết**: Công an cấp Xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú; nộp trực tuyến một phần qua Cổng DVC / VNeID.
* **Thời hạn giải quyết**: 07 ngày làm việc.
* **Xung đột dữ liệu / Điều kiện tiên quyết (`steps - Bước 2`)**:
  > *"Trường hợp thông tin công dân có sự thay đổi, điều chỉnh thì cán bộ thu nhận hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước."*

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Em Hoàng (15 tuổi, sinh năm 2011) đến độ tuổi phải làm thẻ Căn cước. Khi phụ huynh kiểm tra thông tin của em trên ứng dụng VNeID thì thấy ngày sinh bị hiển thị sai là `01/01/2011`, trong khi Giấy khai sinh gốc ghi rõ ngày sinh là `18/05/2011`.
* **Câu hỏi đầu vào (User Query)**:
  > *"Con tôi 15 tuổi (sinh năm 2011) đi làm thẻ Căn cước, nhưng trên VNeID ngày sinh của cháu bị sai so với Giấy khai sinh gốc. Gia đình có thể đến điểm cấp căn cước đưa giấy khai sinh để cán bộ làm thẻ luôn được không, hay phải làm thế nào?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_1_116410`)
* **Cơ quan thẩm quyền**:
  * Bước 1 (Sửa dữ liệu dân cư): Công an cấp xã nơi thường trú/cư trú.
  * Bước 2 (Thu nhận Căn cước): Công an cấp Xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (hoặc Cổng DVCQG/VNeID).
* **Căn cứ pháp lý chuẩn (có trong local data)**:
  * Luật Căn cước (Luật số 26/2023/QH15).
  * Luật số 118/2025/QH15.
  * Nghị định 70/2024/NĐ-CP quy định chi tiết Luật Căn cước.
  * Thông tư số 61/2025/TT-BCA và Thông tư 118/2026/TT-BCA quy định về quy trình cấp thẻ căn cước.
* **Quy trình các bước chuẩn**:
  * **Bước 1 (Bước tiên quyết bắt buộc - Điều chỉnh thông tin dân cư)**:
    * Cán bộ thu nhận căn cước **không được làm thẻ ngay** khi thông tin dân cư chưa khớp.
    * Người đại diện/công dân phải xuất trình Giấy khai sinh bản gốc tại Công an cấp xã để thực hiện **thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư** trước.
  * **Bước 2 (Chờ đồng bộ hệ thống)**:
    * Cập nhật thông tin ngày sinh đúng `18/05/2011` vào CSDLQG về dân cư.
  * **Bước 3 (Thu nhận hồ sơ Căn cước)**:
    * Sau khi dữ liệu đã chuẩn hóa, công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã đề nghị cấp thẻ.
    * Vì công dân từ đủ 14 tuổi: Tiến hành **thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt** (theo quy định tại Bước 2 `PROC_1_116410`).
    * In Phiếu thu nhận thông tin căn cước (Mẫu CC01), kiểm tra và ký xác nhận.
  * **Bước 4 (Nhận kết quả)**:
    * Nhận Giấy hẹn trả kết quả (Mẫu CC02). Nhận thẻ Căn cước trong thời hạn **07 ngày làm việc**.

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]



[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí kiểm chứng | Lộ trình chuẩn (Ground Truth từ `PROC_1_116410`) | Kết quả AI thể hiện | Đánh giá (Đạt / Không đạt) | Ghi chú của chuyên gia |
| :--- | :--- | :--- | :---: | :--- |
| **Thứ tự tiên quyết (Prerequisite Order)** | **Bắt buộc điều chỉnh thông tin trong CSDLQG về dân cư trước**, sau đó mới thu nhận hồ sơ cấp thẻ căn cước. | `[Điền AI có bắt sửa CSDL trước không]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bảo cứ đến làm thẻ căn cước rồi đưa giấy khai sinh sửa luôn.* |
| **Thẩm quyền địa phương (Authority)** | Điểm cấp thẻ căn cước: **Công an cấp xã trong cả nước không phụ thuộc nơi cư trú**. | `[Điền cơ quan AI chỉ dẫn]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bắt buộc phải về nơi thường trú mới được làm thẻ căn cước.* |
| **Thu nhận sinh trắc học độ tuổi** | Người từ đủ 14 tuổi: Bắt buộc thu nhận **ảnh khuôn mặt, vân tay và ảnh mống mắt**. | `[Điền AI nêu các yếu tố sinh trắc nào]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bỏ quên sinh trắc học mống mắt theo Luật Căn cước.* |
| **Thời hạn & Biểu mẫu** | Thời hạn **07 ngày làm việc**; Mẫu Phiếu **CC01**, Giấy hẹn **CC02** (Thông tư 118/2026/TT-BCA). | `[Điền thời hạn và mẫu AI nêu]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu nêu sai thời hạn 7 ngày làm việc.* |
| **Căn cứ pháp lý (Legal Citation)** | Luật Căn cước (26/2023/QH15), Nghị định 70/2024/NĐ-CP, Thông tư 118/2026/TT-BCA. | `[Điền căn cứ AI trích dẫn]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu trích dẫn Luật CCCD 2014 cũ đã hết hiệu lực.* |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Hệ thống có hỏi về việc công dân đã cầm Giấy khai sinh bản gốc đến Công an xã để chỉnh sửa thông tin chưa?**: `[ ] Có  |  [ ] Không`
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]

```

---
---

## TC-PROC-05: CẤP THẺ BHYT VÀ QUAN HỆ ĐIỀU KIỆN TIÊN QUYẾT VỚI KHAI SINH (PROC_1_014137)

### 1. Phân loại tình huống (Dữ liệu local `PROC_1_014137` & Quan hệ đồ thị)
* **Thủ tục đối chiếu**: `PROC_1_014137` - Thủ tục cấp thẻ bảo hiểm y tế.
* **Quan hệ ràng buộc trong data local**:
  * `prerequisites`: `PROC_1_001193` (Thủ tục đăng ký khai sinh là điều kiện tiên quyết bắt buộc).
  * `part_of`: `PROC_3_000722` (Liên thông điện tử).
* **Thẩm quyền giải quyết**: Bảo hiểm xã hội tỉnh / cơ quan BHXH (`jurisdiction`: Cấp tỉnh - Toàn quốc).
* **Thời hạn giải quyết**: **05 ngày làm việc** kể từ ngày nhận đủ hồ sơ (Miễn phí).
* **Mâu thuẫn / Ràng buộc logic**: Trẻ em chưa đăng ký khai sinh (chưa có giấy tờ hộ tịch / mã định danh) nhưng gia đình muốn xin cấp thẻ BHYT trước để đi khám chữa bệnh.

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Chị Mai sinh con được 1 tháng tại nhà. Do bận rộn nên gia đình chưa làm thủ tục đăng ký khai sinh cho cháu. Nay cháu bị sốt cao cần nhập viện điều trị, chị Mai muốn đến thẳng cơ quan Bảo hiểm xã hội để xin cấp thẻ Bảo hiểm y tế cho cháu trước để được hưởng chế độ BHYT miễn phí cho trẻ dưới 6 tuổi.
* **Câu hỏi đầu vào (User Query)**:
  > *"Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_1_014137` & Quan hệ local)
* **Cơ quan thẩm quyền**: Bảo hiểm xã hội tỉnh / cơ quan Bảo hiểm xã hội.
* **Căn cứ pháp lý chuẩn (có trong local data)**:
  * Nghị định số 188/2025/NĐ-CP quy định chi tiết và hướng dẫn thi hành một số điều của Luật Bảo hiểm y tế.
  * Luật Bảo hiểm y tế (Luật 25/2008/QH12, sửa đổi bởi Luật 46/2014/QH13 và Luật số 51/2024/QH15).
  * Quy định liên thông tại `PROC_3_000722` (Nghị định 301/2026/NĐ-CP).
* **Quy trình các bước chuẩn**:
  * **Bước 1 (Xác định điều kiện tiên quyết - Bắt buộc phải có Khai sinh)**:
    * Cơ quan Bảo hiểm xã hội **không thể cấp thẻ BHYT cho trẻ nếu trẻ chưa có thông tin đăng ký khai sinh** (thủ tục `PROC_1_001193` là điều kiện tiên quyết - prerequisite bắt buộc của `PROC_1_014137`).
    * Hồ sơ cấp thẻ BHYT bắt buộc phải có thông tin thân nhân và số định danh cá nhân đã được xác lập qua thủ tục khai sinh.
  * **Bước 2 (Hướng dẫn 2 lộ trình hợp lệ)**:
    * **Lộ trình 1 (Tối ưu - DVC Liên thông qua VNeID)**: Nộp hồ sơ liên thông `PROC_3_000722` trên Cổng DVCQG hoặc VNeID để giải quyết đồng thời cả Khai sinh và Thẻ BHYT trong tối đa **03 ngày làm việc**.
    * **Lộ trình 2 (Làm thủ tục đơn lẻ)**:
      * Pha 1: Đến UBND cấp xã làm thủ tục Đăng ký khai sinh `PROC_1_001193` (thời hạn **01 ngày làm việc**).
      * Pha 2: Sau khi có Giấy khai sinh/Mã định danh, nộp **Tờ khai tham gia, điều chỉnh thông tin BHYT (Mẫu số 2 ban hành kèm Nghị định 188/2025/NĐ-CP)** tại cơ quan Bảo hiểm xã hội (hoặc nộp trực tuyến) để được cấp thẻ BHYT trong thời hạn **05 ngày làm việc**.
  * *(Lưu ý cấp cứu khám chữa bệnh)*: Trong thời gian chờ cấp thẻ BHYT, trẻ dưới 6 tuổi đi khám chữa bệnh có thể xuất trình Giấy chứng sinh theo quy định của pháp luật về BHYT.

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]



[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí kiểm chứng | Lộ trình chuẩn (Ground Truth từ `PROC_1_014137`) | Kết quả AI thể hiện | Đánh giá (Đạt / Không đạt) | Ghi chú của chuyên gia |
| :--- | :--- | :--- | :---: | :--- |
| **Nhận diện điều kiện tiên quyết (Prerequisite)** | Khẳng định **không thể cấp thẻ BHYT khi chưa khai sinh**; Khai sinh là thủ tục tiên quyết bắt buộc. | `[Điền AI có nhận diện tiên quyết không]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bảo công dân cứ ra cơ quan BHXH xin cấp thẻ BHYT ngay khi chưa khai sinh.* |
| **Cơ quan thẩm quyền cấp thẻ BHYT** | **Bảo hiểm xã hội tỉnh / cơ quan BHXH** (không phải UBND xã cấp thẻ BHYT). | `[Điền cơ quan AI chỉ dẫn]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu bảo UBND xã có thẩm quyền cấp thẻ BHYT.* |
| **Thời hạn giải quyết BHYT đơn lẻ** | **05 ngày làm việc** kể từ ngày nhận đủ hồ sơ (theo `execution_methods` của `PROC_1_014137`). | `[Điền thời hạn AI nêu]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu nêu sai thời hạn 5 ngày làm việc của thủ tục BHYT.* |
| **Biểu mẫu tờ khai BHYT chuẩn** | **Mẫu số 2** Phụ lục ban hành kèm theo **Nghị định số 188/2025/NĐ-CP**. | `[Điền mẫu tờ khai AI trích]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Trượt nếu trích dẫn mẫu tờ khai cũ không có trong data local.* |
| **Định hướng giải pháp liên thông** | Hướng dẫn công dân phương án tối ưu: nộp DVC liên thông trên VNeID để có cả 2 giấy tờ trong 03 ngày làm việc. | `[Điền AI có gợi ý DVC liên thông]` | `[ ] Đạt`<br>`[ ] Không đạt` | *Đánh giá tính chủ động tối ưu lộ trình của trợ lý AI.* |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Hệ thống có hỏi rõ về việc gia đình có Giấy chứng sinh hay chưa và hướng dẫn làm khai sinh trước không?**: `[ ] Có  |  [ ] Không`
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]

```

---
---

## BẢNG TỔNG HỢP KẾT QUẢ KIỂM CHỨNG TOÀN DIỆN (EXECUTIVE SCORECARD)

| Mã ca kiểm thử | Tên tình huống thủ tục (Theo mã Record Local) | Đúng bước (Step) | Đúng thứ tự (Sequence) | Đúng thẩm quyền & hồ sơ (Authority & Docs) | Đúng căn cứ (Citations) | Xử lý hỏi làm rõ (Clarification) | Kết luận chung |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TC-PROC-01** | Đăng ký khai sinh thiếu Giấy chứng sinh (`PROC_1_001193`) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ] ĐẠT / [ ] HỎNG` |
| **TC-PROC-02** | Thường trú vào chỗ ở hợp pháp do thuê (`PROC_1_116788`) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ] ĐẠT / [ ] HỎNG` |
| **TC-PROC-03** | Liên thông điện tử 4 trong 1 trẻ em (`PROC_3_000722`) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ] ĐẠT / [ ] HỎNG` |
| **TC-PROC-04** | Cấp thẻ Căn cước khi dữ liệu CSDL sai lệch (`PROC_1_116410`) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ] ĐẠT / [ ] HỎNG` |
| **TC-PROC-05** | Cấp thẻ BHYT & Quan hệ tiên quyết với Khai sinh (`PROC_1_014137`) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ] ĐẠT / [ ] HỎNG` |

### Thống kê tỷ lệ đạt chuẩn:
* **Tổng số ca kiểm thử**: 5 ca
* **Số ca Đạt tuyệt đối**: `... / 5 ca` (Chiếm `...%`)
* **Các lỗi sai phát hiện**:
  * Lỗi đảo ngược thứ tự điều kiện tiên quyết (Prerequisite reversal): `... lần`
  * Lỗi sai thẩm quyền cơ quan giải quyết (Authority hallucination): `... lần`
  * Lỗi ảo giác biểu mẫu/thời hạn giải quyết (Form & SLA hallucination): `... lần`
  * Lỗi không nhận diện giấy tờ thay thế (Missing doc handling failure): `... lần`

---
**Người kiểm duyệt / Chuyên gia thủ tục ký tên**:  
*(Ký và ghi rõ họ tên)*  
*Ngày thẩm định: .... / .... / 202...*
