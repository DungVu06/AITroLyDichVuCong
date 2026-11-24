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
Chào bạn, trường hợp sinh con tại nhà và không có Giấy chứng sinh vẫn có thể thực hiện thủ tục đăng ký khai sinh 【PROC_1_001193_c5_s0】.

Thủ tục đăng ký khai sinh 【PROC_1_001193】
Lý do cần làm: Ghi nhận khai sinh cho trẻ em mới sinh theo quy định pháp luật. 【PROC_1_001193】
Hồ sơ phổ biến:
Trường hợp không có Giấy chứng sinh, bạn cần nộp văn bản của người làm chứng xác nhận về việc sinh; nếu không có người làm chứng thì phải có giấy cam đoan về việc sinh (1 bản chính) 【PROC_1_001193_c5_s0】.
Cách thức thực hiện: Nộp hồ sơ trực tuyến, qua dịch vụ bưu chính hoặc trực tiếp 【PROC_1_001193_c48_s0】 tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】.
Thời gian giải quyết: 1 ngày 【PROC_1_001193_c48_s0】.
Lệ phí: Miễn phí 【PROC_1_001193_c48_s0】.
Bạn có thể cung cấp thêm:

Khi sinh tại nhà, có người làm chứng có thể xác nhận việc sinh không?
Nguồn tham khảo (3)

Thủ tục đăng ký khai sinh — PROC_1_001193
Thủ tục đăng ký khai sinh – document_item — PROC_1_001193_c5_s0
Thủ tục đăng ký khai sinh – execution_methods — PROC_1_001193_c48_s0

Thủ tục đăng ký khai sinh · 15 văn bản

Căn cứ pháp lý của thủ tục
Cấp xã · Toàn quốc · Hiệu lực từ 2019-07-31 · Ghi nhận 2026-11-18 · Phiên bản 178839f9e166

04/2024/TT-BTP — Sửa đổi, bổ sung một số điều của Thông tư số 02/2020/TT-BTP ngày 08/4/2020 của Bộ trưởng Bộ Tư pháp ban hành, hướng dẫn sử dụng, quản lý mẫu sổ quốc tịch và mẫu giấy tờ về quốc tịch và Thông tư số 04/2020/TT-BTP ngày 28/5/2020 của Bộ trưởng Bộ Tư pháp quy định chi tiết thi hành một số điều của Luật Hộ tịch và Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
Thông tư số 03/2023/TT-BTP — Thông tư số 03/2023/TT-BTP ngày 02/8/2023 của Bộ trưởng Bộ Tư pháp
106/2021/TT-BTC — Thông tư sửa đổi, bổ sung một số điều của Thông tư số 85/2019/TT-BTC ngày 29/11/2019 của Bộ Tài chính hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương.
04/2020/TT-BTP — Hướng dẫn Luật hộ tịch và Nghị định 123/2015/NĐ-CP hướng dẫn Luật hộ tịch do Bộ trưởng Bộ Tư pháp ban hành
07/2025/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định trong lĩnh vực hộ tịch, quốc tịch, chứng thực.
120/2025/NĐ-CP — Nghị định số 120/2025/NĐ-CP ngày 11/6/2025 của Chính phủ quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp.
66.7/2025/NQ-CP — Nghị quyết số 66.7/2025/NQ-CP của Chính phủ: Quy định cắt giảm, đơn giản hóa thủ tục hành chính dựa trên dữ liệu
60/2014/QH13 — Luật 60/2014/QH13
01/2022/TT-BTP — Thông tư quy định chi tiết một số điều và biện pháp thi hành Nghị định số 87/2020/NĐ-CP ngày 28 tháng 7 năm 2020 của Chính phủ quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
85/2019/TT-BTC — Thông tư Hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương
104/2022/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định liên quan đến việc nộp xuất trình sổ hộ khẩu, sổ tạm trú giấy khi thực hiện thủ tục hành chính, cung cấp dịch vụ công
123/2015/NĐ-CP — Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
08/2025/TT-BTP — Thông tư số 08/2025/TT-BTP ngày 12/6/2025 của Bộ trưởng Bộ Tư pháp quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp và phân cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp
18/2026/NĐ-CP — Nghị định sửa đổi, bổ sung một số nghị định để cắt giảm, đơn giản hóa thủ tục hành chính, điều kiện kinh doanh thuộc phạm vi quản lý của Bộ Tư pháp
87/2020/NĐ-CP — Nghị định quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
Một số căn cứ do thủ tục liệt kê chưa được đối chiếu hiệu lực.
[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí | Lộ trình chuẩn | Kết quả AI thể hiện | Đánh giá | Ghi chú theo JSON |
| --- | --- | --- | --- | --- |
| Xử lý giấy tờ thiếu (Missing Doc) | Hướng dẫn thay thế Giấy chứng sinh bằng: Văn bản của người làm chứng hoặc Giấy cam đoan về việc sinh. | Có văn bản xác nhận của người làm chứng hoặc giấy cam đoan nếu không có người làm chứng. | Đạt | Trượt nếu bảo thiếu giấy chứng sinh thì không giải quyết được. |
| Cơ quan thẩm quyền (Authority) | Ủy ban nhân dân cấp xã (Bộ phận Một cửa cấp xã hoặc Cổng DVCQG/VNeID). | Nêu UBND cấp xã và các kênh nộp. | Đạt | Trượt nếu hướng dẫn lên cấp huyện hoặc sai cơ quan. |
| Thời hạn giải quyết (Processing Time) | 01 ngày làm việc (theo execution_methods của bản ghi local). | Nêu “1 ngày” và dẫn đúng mục thời hạn. Cách diễn đạt thiếu chữ “làm việc”. | Đạt | Trượt nếu nêu thời hạn > 01 ngày làm việc đối với hồ sơ thường. |
| Căn cứ pháp lý (Legal Citation) | Luật Hộ tịch (60/2014/QH13), Thông tư 04/2020/TT-BTP, Nghị định 123/2015/NĐ-CP. | Phần căn cứ của câu trả lời có đủ 60/2014/QH13, 04/2020/TT-BTP và 123/2015/NĐ-CP. Danh mục khớp bản ghi local. | Đạt | Trượt nếu trích dẫn văn bản không có trong legal_bases của thủ tục. |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Nhận xét**. Hỏi về người làm chứng sau khi đã hướng dẫn cả hai phương án giấy tờ.
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Khi sinh tại nhà, có người làm chứng có thể xác nhận việc sinh không?
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
Để đăng ký thường trú tại nhà thuê ở xã Tân Triều (mã thủ tục PROC_1_116788), cơ quan tiếp nhận và giải quyết là Công an Xã 【PROC_1_116788_c174_s0】. Do bạn mới có hợp đồng thuê nhà viết tay, điều kiện và giấy tờ hiện chưa đáp ứng đầy đủ quy định và bạn cần hoàn thiện các điều kiện sau trước khi nộp hồ sơ:

Thứ tự nên làm
Hoàn thiện giấy tờ nhà thuê: Hợp đồng thuê nhà phải được công chứng hoặc chứng thực theo quy định pháp luật 【PROC_1_116788_c127_s0】.
Cần có văn bản đồng ý của chủ sở hữu chỗ ở hợp pháp cho đăng ký thường trú 【PROC_1_116788_c142_s2】.
Nộp hồ sơ đăng ký thường trú tại Công an Xã 【PROC_1_116788_c174_s0】.
Giấy tờ và cách thực hiện (PROC_1_116788)
Thành phần hồ sơ:
Hợp đồng, văn bản về việc cho thuê chỗ ở hợp pháp được công chứng hoặc chứng thực (1 bản chính) 【PROC_1_116788_c127_s0】.
Văn bản đồng ý của chủ sở hữu chỗ ở hợp pháp đối với trường hợp thuê chỗ ở 【PROC_1_116788_c142_s2】.
Thông tin chứng minh đủ diện tích nhà ở để đăng ký thường trú (hoặc giấy tờ, tài liệu thể hiện diện tích nhà ở / xác nhận của Ủy ban nhân dân cấp xã về điều kiện diện tích bình quân) 【PROC_1_116788_c128_s0】.
Cách thức thực hiện & Lệ phí:
Nộp trực tuyến hoặc trực tiếp tại Công an Xã 【PROC_1_116788_c174_s3】【PROC_1_116788_c174_s0】.
Thời hạn giải quyết: 07 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ 【PROC_1_116788_c174_s3】.
Lệ phí: 20.000 đồng/lần nếu nộp trực tiếp; 10.000 đồng/lần nếu nộp qua Cổng dịch vụ công quốc gia 【PROC_1_116788_c174_s3】.
Thủ tục áp dụng
Đăng ký thường trú 【PROC_1_116788】
Bạn có thể cung cấp thêm:

Hợp đồng thuê, mượn hoặc ở nhờ đã được công chứng hoặc chứng thực chưa?
Chủ sở hữu chỗ ở hợp pháp đã đồng ý bằng văn bản cho đăng ký thường trú chưa?
Nguồn tham khảo (6)

Đăng ký thường trú — PROC_1_116788
Đăng ký thường trú – document_item — PROC_1_116788_c127_s0
Đăng ký thường trú – document_item — PROC_1_116788_c142_s2
Đăng ký thường trú – document_item — PROC_1_116788_c128_s0
Đăng ký thường trú – execution_methods — PROC_1_116788_c174_s0
Đăng ký thường trú – execution_methods — PROC_1_116788_c174_s3

Căn cứ pháp lý của thủ tục

Đăng ký thường trú · 8 văn bản

Cấp xã · Toàn quốc · Hiệu lực từ 2026-09-15 · Ghi nhận 2026-11-18 · Phiên bản 68b8db2264f6

154/2024/NĐ-CP — Nghị định quy định chi tiết một số điều và biện pháp thi hành Luật Cư trú
54/2025/TT-BCA — Thông tư số 54/2025/TT-BCA ngày 01/7/2025 của Bộ trưởng Bộ Công an quy định về quy trình đăng ký cư trú.
66.7/2025/NQ-CP — Nghị quyết số 66.7/2025/NQ-CP của Chính phủ: Quy định cắt giảm, đơn giản hóa thủ tục hành chính dựa trên dữ liệu
68/2020/QH14 — Luật Cư trú 2020
116/2026/TT-BCA — Thông tư số 116/2026/TT-BCA ngày 29/6/2026 của Bộ trưởng Bộ Công an quy định chi tiết một số điều và biện pháp thi hành Luật Cư trú
190/2021/TT-BQP — Thông tư số 190/2021/TT-BQP ngày 31/12/2021 của Bộ trưởng Bộ Quốc phòng quy định điều kiện, hồ sơ, thủ tục đăng ký thường trú, đăng ký tạm trú trong Bộ Quốc phòng.
75/2022/TT-BTC — Thông tư số 75/2022/TT-BTC của Bộ Tài chính: Quy định mức thu, chế độ thu, nộp và quản lý lệ phí đăng ký cư trú
29/2026/TT-BTC — QUY ĐỊNH MỨC THU, MIỄN MỘT SỐ KHOẢN PHÍ, LỆ PHÍ ĐỂ HỖ TRỢ VIỆC KẾT NỐI, KHAI THÁC, SỬ DỤNG DỮ LIỆU VÀ KHUYẾN KHÍCH THỰC HIỆN DỊCH VỤ CÔNG TRÊN ỨNG DỤNG VNEID

Căn cứ pháp lý của thủ tục

Thủ tục đăng ký khai sinh · 15 văn bản

Cấp xã · Toàn quốc · Hiệu lực từ 2019-07-31 · Ghi nhận 2026-11-18 · Phiên bản 178839f9e166

04/2024/TT-BTP — Sửa đổi, bổ sung một số điều của Thông tư số 02/2020/TT-BTP ngày 08/4/2020 của Bộ trưởng Bộ Tư pháp ban hành, hướng dẫn sử dụng, quản lý mẫu sổ quốc tịch và mẫu giấy tờ về quốc tịch và Thông tư số 04/2020/TT-BTP ngày 28/5/2020 của Bộ trưởng Bộ Tư pháp quy định chi tiết thi hành một số điều của Luật Hộ tịch và Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
Thông tư số 03/2023/TT-BTP — Thông tư số 03/2023/TT-BTP ngày 02/8/2023 của Bộ trưởng Bộ Tư pháp
106/2021/TT-BTC — Thông tư sửa đổi, bổ sung một số điều của Thông tư số 85/2019/TT-BTC ngày 29/11/2019 của Bộ Tài chính hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương.
04/2020/TT-BTP — Hướng dẫn Luật hộ tịch và Nghị định 123/2015/NĐ-CP hướng dẫn Luật hộ tịch do Bộ trưởng Bộ Tư pháp ban hành
07/2025/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định trong lĩnh vực hộ tịch, quốc tịch, chứng thực.
120/2025/NĐ-CP — Nghị định số 120/2025/NĐ-CP ngày 11/6/2025 của Chính phủ quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp.
66.7/2025/NQ-CP — Nghị quyết số 66.7/2025/NQ-CP của Chính phủ: Quy định cắt giảm, đơn giản hóa thủ tục hành chính dựa trên dữ liệu
60/2014/QH13 — Luật 60/2014/QH13
01/2022/TT-BTP — Thông tư quy định chi tiết một số điều và biện pháp thi hành Nghị định số 87/2020/NĐ-CP ngày 28 tháng 7 năm 2020 của Chính phủ quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
85/2019/TT-BTC — Thông tư Hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương
104/2022/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định liên quan đến việc nộp xuất trình sổ hộ khẩu, sổ tạm trú giấy khi thực hiện thủ tục hành chính, cung cấp dịch vụ công
123/2015/NĐ-CP — Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
08/2025/TT-BTP — Thông tư số 08/2025/TT-BTP ngày 12/6/2025 của Bộ trưởng Bộ Tư pháp quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp và phân cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp
18/2026/NĐ-CP — Nghị định sửa đổi, bổ sung một số nghị định để cắt giảm, đơn giản hóa thủ tục hành chính, điều kiện kinh doanh thuộc phạm vi quản lý của Bộ Tư pháp
87/2020/NĐ-CP — Nghị định quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
Một số căn cứ do thủ tục liệt kê chưa được đối chiếu hiệu lực.

Thủ tục cấp thẻ bảo hiểm y tế · 4 văn bản

Cấp tỉnh · Toàn quốc · Hiệu lực từ 2025-07-11 · Ghi nhận 2026-11-18 · Phiên bản 7ee3b4668fb0

188/2025/NĐ-CP — Nghị định quy định chi tiết và hướng dẫn thi hành một số điều của Luật Bảo hiểm y tế (188/2025/NĐ-CP ngày 01/7/2025)
25/2008/QH12 — Luật 25/2008/QH12 - Bảo hiểm y tế
51/2024/QH15 — Luật số 51/2024/QH15 ngày 27/11/2024 của Quốc hội sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế
Luật 46/2014/QH13 — 46/2014/QH13 Sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế

[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí | Lộ trình chuẩn | Kết quả AI thể hiện | Đánh giá | Ghi chú theo JSON |
| --- | --- | --- | --- | --- |
| Cơ quan tiếp nhận (Authority) | Công an Xã (Cơ quan đăng ký cư trú cấp xã). | Nêu Công an xã tiếp nhận. | Đạt | Trượt nếu bảo nộp UBND xã. |
| Yêu cầu sự đồng ý của chủ sở hữu | Bắt buộc có ý kiến đồng ý bằng văn bản của chủ sở hữu chỗ ở hợp pháp | Có yêu cầu chủ nhà đồng ý bằng văn bản | đạt | Trượt nếu cho phép người thuê tự đăng ký mà không cần chủ nhà đồng ý. |
| Yêu cầu tính hợp pháp của hợp đồng | Hợp đồng thuê nhà phải được công chứng hoặc chứng thực; Hợp đồng viết tay không đủ điều kiện. | Nêu hợp đồng viết tay chưa đủ và yêu cầu công chứng hoặc chứng thực. | Đạt | Trượt nếu chấp nhận hợp đồng viết tay không chứng thực. |
| Chứng minh diện tích nhà ở | Phải có thông tin/giấy tờ chứng minh đủ diện tích nhà ở tối thiểu (theo Điều 5 NĐ 154/2024/NĐ-CP). | Nêu giấy tờ về diện tích hoặc xác nhận của UBND xã. | Đạt | Trượt nếu bỏ qua yêu cầu chứng minh diện tích. |
| Thời hạn & Biểu mẫu | Thời hạn 07 ngày làm việc; Mẫu CT01 (theo Thông tư 116/2026/TT-BCA). | Đúng 07 ngày làm việc nhưng thiếu CT01. | Không đạt | Trượt nếu sai thời hạn 7 ngày làm việc hoặc dùng mẫu sổ giấy cũ. |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Nhận xét**. Hỏi về sự đồng ý của chủ nhà là phù hợp. Câu hỏi về công chứng lặp lại phần đã xử lý từ thông tin hợp đồng viết tay.
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Hợp đồng thuê, mượn hoặc ở nhờ đã được công chứng hoặc chứng thực chưa?
Chủ sở hữu chỗ ở hợp pháp đã đồng ý bằng văn bản cho đăng ký thường trú chưa?
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
Thủ tục liên thông điện tử đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế và cấp thẻ căn cước cho trẻ em dưới 6 tuổi (Mã: PROC_3_000722) được thực hiện hoàn toàn trực tuyến qua ứng dụng VNeID hoặc Cổng Dịch vụ công quốc gia 【PROC_3_000722_c180_s1】.

Thứ tự nên làm và các bước hệ thống xử lý
Quy trình xử lý nội bộ của các cơ quan trên hệ thống liên thông diễn ra qua các bước sau:

Bước 1: Người yêu cầu truy cập Cổng Dịch vụ công quốc gia hoặc ứng dụng VNeID, lựa chọn dịch vụ công liên thông và nộp hồ sơ trực tuyến【PROC_3_000722_c180_s1】.
Bước 2: Cổng Dịch vụ công quốc gia nhận thanh toán thành công, bóc tách thành phần hồ sơ và chuyển sang Hệ thống thông tin giải quyết TTHC của Bộ Tư pháp【PROC_3_000722_c181_s0】.
Bước 3: Công chức tư pháp - hộ tịch tại Ủy ban nhân dân cấp xã giải quyết đăng ký khai sinh trong 24 giờ kể từ khi Hệ thống đăng ký, quản lý hộ tịch điện tử nhận đủ hồ sơ hợp lệ【PROC_3_000722_c182_s1】.
Bước 4: Hệ thống tiếp tục chuyển bản điện tử Giấy khai sinh và dữ liệu đến Hệ thống thông tin quản lý cư trú để đăng ký thường trú và Hệ thống thông tin ngành Bảo hiểm xã hội để cấp thẻ bảo hiểm y tế【PROC_3_000722_c183_s1】.
Bước 5: Sau khi có thông báo kết quả đăng ký thường trú, hệ thống chuyển hồ sơ sang Hệ thống sản xuất, cấp và quản lý căn cước của Bộ Công an để thực hiện cấp thẻ căn cước theo yêu cầu【PROC_3_000722_c184_s0】.
Thời gian và lệ phí
Thời gian giải quyết: Tổng thời gian giải quyết là 03 ngày làm việc kể từ khi các cơ quan có thẩm quyền nhận đầy đủ hồ sơ theo quy định; trường hợp phải xác minh thì thời gian không quá 05 ngày làm việc【PROC_3_000722_c185_s0】.
Lệ phí: Miễn phí (phí, lệ phí khác theo quy định của các thủ tục tương ứng)【PROC_3_000722_c185_s0】.
Thủ tục áp dụng
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi 【PROC_3_000722】
Nguồn tham khảo (7)

Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi — PROC_3_000722
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c180_s1
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c181_s0
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c183_s1
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c184_s0
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c182_s1
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – execution_methods — PROC_3_000722_c185_s0

Căn cứ pháp lý của thủ tục

Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi · 1 văn bản

Cấp xã · Toàn quốc · Hiệu lực từ 2026-08-09 · Ghi nhận 2026-11-18 · Phiên bản 7f6120790947

Nghị định số 301/2026/NĐ-CP — Nghị định số 301/2026/NĐ-CP ngày 30 tháng 7 năm 2026 của Chính phủ sửa đổi, bổ sung một số điều của Nghị định số 63/2024/NĐ-CP ngày 10 tháng 6 năm 2024 của Chính phủ quy định việc thực hiện liên thông điện tử 02 nhóm thủ tục hành chính: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế cho trẻ em dưới 6 tuổi; đăng ký khai tử, xóa đăng ký thường trú, giải quyết mai táng phí, tử tuất.

[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí | Lộ trình chuẩn | Kết quả AI thể hiện | Đánh giá | Ghi chú theo JSON |
| --- | --- | --- | --- | --- |
| Tính liên thông 1 cửa điện tử | Thực hiện trên Cổng DVCQG / VNeID, nộp 01 lần duy nhất, dữ liệu tự luân chuyển. | Nộp trực tuyến qua VNeID hoặc Cổng DVCQG, hệ thống tự chuyển dữ liệu. | Đạt | Trượt nếu bắt người dân đi nộp giấy riêng lẻ ở từng cơ quan. |
| Thứ tự luân chuyển hồ sơ | UBND xã cấp Khai sinh trước (24h) -> chuyển sang Công an xã (Thường trú) và BHXH (BHYT) -> Căn cước dưới 6 tuổi. | Nêu khai sinh trong 24 giờ, chuyển hồ sơ cư trú và BHXH, sau đó xử lý căn cước theo yêu cầu khi có kết quả thường trú. | Đạt | Trượt nếu đảo lộn thứ tự giải quyết khi chưa có khai sinh. |
| Đặc thù căn cước dưới 6 tuổi | Cấp thẻ căn cước cho trẻ dưới 6 tuổi làm trực tuyến, không thu nhận vân tay, mống mắt. | Có nêu làm trực tuyến | Đạt | Trượt nếu bắt trẻ dưới 6 tuổi đi chụp ảnh mống mắt, lấy vân tay. |
| Thời hạn giải quyết toàn trình | Không quá 03 ngày làm việc (xác minh không quá 05 ngày). | Nêu đúng 03 ngày làm việc, tối đa 05 ngày nếu xác minh. | Đạt | Trượt nếu cộng dồn cơ học các thủ tục đơn lẻ |
| Căn cứ pháp lý (Legal Citation) | Nghị định số 301/2026/NĐ-CP (hoặc Nghị định số 63/2024/NĐ-CP). | Đầy đủ | Đạt | Trượt nếu không trích dẫn văn bản liên thông trong data. |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Nhận xét**. Không hỏi thêm. Tình huống đã đủ thông tin để trả lời về trình tự và thời hạn.
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Không có
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

* **Cơ quan thẩm quyền**
  * Điểm thu nhận: Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước nếu đã triển khai, không phụ thuộc nơi cư trú. Có thể đăng ký thời gian và địa điểm trên Cổng DVCQG/VNeID khi thông tin chính xác.
* **Căn cứ pháp lý**
  * Luật Căn cước (Luật số 26/2023/QH15).
  * Luật số 118/2025/QH15.
  * Nghị định 70/2024/NĐ-CP quy định chi tiết Luật Căn cước.
  * Thông tư số 61/2025/TT-BCA và Thông tư 118/2026/TT-BCA quy định về quy trình cấp thẻ căn cước.
* **Quy trình**
  * **Bước 1 (Bước tiên quyết bắt buộc - Điều chỉnh thông tin dân cư)**
    * Đối chiếu ngày sinh trong CSDL quốc gia về dân cư. Nếu dữ liệu cần sửa, cán bộ hướng dẫn điều chỉnh trước khi cấp thẻ.
    * Nếu chưa có dữ liệu nhân thân, cán bộ đề nghị xuất trình một trong các giấy tờ pháp lý chứng minh thông tin nhân thân và hướng dẫn cập nhật dữ liệu.
  * **Kiểm tra dữ liệu sau khi điều chỉnh**
    * Dùng ngày sinh đã điều chỉnh trong cơ sở dữ liệu để lập hồ sơ cấp thẻ.
  * **Bước 3 (Thu nhận hồ sơ Căn cước)**
    * Sau khi dữ liệu đã chuẩn hóa, công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã đề nghị cấp thẻ.
    * Thu nhận vân tay, ảnh khuôn mặt và ảnh mống mắt khi cấp thẻ cho công dân từ đủ 06 tuổi, bao gồm người 15 tuổi trong ca kiểm thử.
    * In Phiếu thu nhận thông tin căn cước (Mẫu CC01), kiểm tra và ký xác nhận.
  * **Bước 4 (Nhận kết quả)**
    * Nhận Giấy hẹn trả kết quả (Mẫu CC02). Nhận thẻ Căn cước trong thời hạn 07 ngày làm việc.
* **Thông tin bổ sung**
  * Ngoại lệ theo bản ghi: Khi cấp đổi do sắp xếp đơn vị hành chính làm thay đổi thông tin trên thẻ, cán bộ dùng lại sinh trắc lần cấp gần nhất.

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
Theo quy định, khi thông tin công dân có sự thay đổi hoặc sai lệch, cán bộ thu nhận sẽ hướng dẫn công dân thực hiện thủ tục điều chỉnh thông tin trong Cơ sở dữ liệu quốc gia về dân cư trước khi thực hiện thủ tục cấp thẻ căn cước 【PROC_1_116410_c73_s0】. Do đó, bạn không thể đưa giấy khai sinh để làm thẻ căn cước ngay khi dữ liệu chưa khớp, mà cần hoàn thiện việc điều chỉnh ngày sinh cho cháu khớp với Giấy khai sinh gốc trong cơ sở dữ liệu quốc gia về dân cư trước.

Thứ tự nên làm
Điều chỉnh thông tin ngày sinh: Liên hệ cơ quan công an để cập nhật, điều chỉnh lại thông tin ngày sinh của cháu trong Cơ sở dữ liệu quốc gia về dân cư dựa trên Giấy khai sinh gốc 【PROC_1_116410_c73_s0】.
Thực hiện cấp thẻ căn cước: Sau khi thông tin đã được cập nhật chính xác, tiến hành làm thủ tục cấp thẻ căn cước tại cơ quan công an 【PROC_1_116410_c73_s0】.
Giấy tờ và cách thực hiện
Hồ sơ phổ biến:
Phiếu thu nhận thông tin căn cước (Mẫu CC01) được tạo lập khi trích xuất thông tin trong Cơ sở dữ liệu quốc gia về dân cư để kiểm tra và ký xác nhận 【PROC_1_116410_c63_s0】.
Giấy tờ pháp lý chứa thông tin nhân thân (Giấy khai sinh gốc của cháu) 【PROC_1_116410_c65_s0】.
Khi thực hiện thủ tục, tiến hành thu nhận vân tay, chụp ảnh khuôn mặt và thu nhận ảnh mống mắt của công dân 【PROC_1_116410_c76_s0】.
Cấp giấy hẹn trả kết quả giải quyết thủ tục về căn cước (Mẫu CC02) 【PROC_1_116410_c78_s0】.
Cách thực hiện:
Trực tiếp: Công dân đến Công an cấp xã hoặc Bộ phận một cửa cấp xã trong cả nước không phụ thuộc vào nơi cư trú (nếu đã triển khai) 【PROC_1_116410_c120_s1】.
Trực tuyến: Thực hiện trực tuyến một phần đối với công dân từ đủ 06 tuổi trở lên 【PROC_1_116410_c120_s2】.
Thời gian giải quyết: 7 ngày làm việc 【PROC_1_116410_c120_s1】.
Lệ phí: Miễn phí hoặc theo mức quy định pháp luật 【PROC_1_116410_c120_s1】.
Thủ tục áp dụng
Cấp, cấp đổi, cấp lại thẻ căn cước 【PROC_1_116410】
Bạn có thể cung cấp thêm:

Thông tin ngày sinh đã được điều chỉnh trong Cơ sở dữ liệu quốc gia về dân cư chưa?

Nguồn tham khảo (9)

Cấp, cấp đổi, cấp lại thẻ căn cước — PROC_1_116410
Cấp, cấp đổi, cấp lại thẻ căn cước – document_item — PROC_1_116410_c63_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – document_item — PROC_1_116410_c65_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – execution_methods — PROC_1_116410_c120_s1
Cấp, cấp đổi, cấp lại thẻ căn cước – step_item — PROC_1_116410_c73_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – step_item — PROC_1_116410_c76_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – step_item — PROC_1_116410_c78_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – step_item — PROC_1_116410_c81_s0
Cấp, cấp đổi, cấp lại thẻ căn cước – step_item — PROC_1_116410_c85_s0
Căn cứ pháp lý của thủ tục

Cấp, cấp đổi, cấp lại thẻ căn cước · 8 văn bản

Cấp xã · Toàn quốc · Hiệu lực từ 2026-08-17 · Ghi nhận 2026-11-18 · Phiên bản 3ffe219db3db

118/2025/QH15 — Sửa đổi, bổ sung một số điều của 10 Luật có liên quan đến an ninh, trật tự
26/2023/QH15 — Luật Căn cước
70/2024/NĐ-CP — Nghị định của Chính phủ: Quy định chi tiết một số điều và biện pháp thi hành Luật Căn cước
64/2025/TT-BTC — Thông tư quy định mức thu, miễn một số khoản phí, lệ phí nhằm hỗ trợ cho doanh nghiệp, người dân.
16/2024/TT-BCA — Thông tư 16/2024/TT-BCA quy định về mẫu thẻ căn cước, mẫu giấy chứng nhận căn cước
17/2024/TT-BCA — Thông tư quy định chi tiết một số điều và biện pháp thi hành Luật Căn cước
73/2024/TT-BTC — Thông tư số 73/2024/TT-BTC ngày 21/10/2024 của Bộ Tài chính quy định mức thu, miễn, chế độ thu, nộp lệ phí cấp đổi, cấp lại thẻ căn cước
61/2025/TT-BCA — Thông tư số 61/2025/TT-BCA ngày 10/7/2025 của Bộ Công an quy định về quy trình cấp, cấp đổi, cấp lại thẻ căn cước, giấy chứng nhận căn cước được sửa đổi, bổ sung bởi Thông tư số 120/2026/TT-BCA ngày 29/6/2026 của Bộ Công an sửa đổi, bổ sung một số điều của Thông tư số 61/2025/TT-BCA
Một số căn cứ do thủ tục liệt kê chưa được đối chiếu hiệu lực.

[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí | Lộ trình chuẩn | Kết quả AI thể hiện | Đánh giá | Ghi chú theo JSON |
| --- | --- | --- | --- | --- |
| Thứ tự tiên quyết (Prerequisite Order) | Đối chiếu ngày sinh và hướng dẫn điều chỉnh dữ liệu dân cư nếu cần trước khi cấp thẻ. | Hướng dẫn điều chỉnh ngày sinh trong CSDL dân cư trước khi cấp thẻ. Liệt kê Giấy khai sinh gốc trong hồ sơ phổ biến, nhưng chưa nói rõ khi nào phải xuất trình. | Đạt | Trượt nếu hứa cấp thẻ ngay khi dữ liệu cần sửa hoặc mặc định phải nộp Giấy khai sinh bản gốc khi điều chỉnh. |
| Thẩm quyền địa phương (Authority) | Điểm cấp thẻ căn cước: Công an cấp xã trong cả nước không phụ thuộc nơi cư trú. | Nêu Công an cấp xã hoặc Bộ phận một cửa cấp xã nơi đã triển khai, không phụ thuộc nơi cư trú. | Đạt | Trượt nếu bắt buộc phải về nơi thường trú mới được làm thẻ căn cước. |
| Thu nhận sinh trắc học độ tuổi | Khi cấp thẻ cho người từ đủ 06 tuổi, thu nhận ảnh khuôn mặt, vân tay và ảnh mống mắt. | Nêu đủ vân tay, ảnh khuôn mặt và mống mắt cho người 15 tuổi trong ca này. | Đạt | Trượt nếu bỏ quên sinh trắc học mống mắt theo Luật Căn cước. |
| Thời hạn & Biểu mẫu | Thời hạn 07 ngày làm việc; Mẫu Phiếu CC01, Giấy hẹn CC02 (Thông tư 118/2026/TT-BCA). | Có 07 ngày làm việc, CC01 và CC02. | Đạt | Trượt nếu nêu sai thời hạn 7 ngày làm việc. |
| Căn cứ pháp lý (Legal Citation) | Luật Căn cước (26/2023/QH15), Nghị định 70/2024/NĐ-CP, Thông tư 118/2026/TT-BCA. | Đầy đủ | Đạt | Trượt nếu trích dẫn Luật CCCD 2014 cũ đã hết hiệu lực. |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Nhận xét**. Hỏi đúng về tình trạng điều chỉnh ngày sinh trong CSDL dân cư.
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Thông tin ngày sinh đã được điều chỉnh trong Cơ sở dữ liệu quốc gia về dân cư chưa?
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
* **Thời hạn giải quyết**: Liên thông 03 ngày làm việc từ khi nhận đủ hồ sơ, tối đa 05 ngày nếu phải xác minh. Khâu BHYT không quá 02 ngày làm việc kể từ khi BHXH nhận hồ sơ điện tử liên thông. Thủ tục riêng lẻ có thời hạn 05 ngày làm việc.
* **Mâu thuẫn / Ràng buộc logic**: Trẻ em chưa đăng ký khai sinh (chưa có giấy tờ hộ tịch / mã định danh) nhưng gia đình muốn xin cấp thẻ BHYT trước để đi khám chữa bệnh.

### 2. Thông tin ca kiểm thử
* **Bối cảnh người dùng**: Chị Mai sinh con được 1 tháng tại nhà. Do bận rộn nên gia đình chưa làm thủ tục đăng ký khai sinh cho cháu. Nay cháu bị sốt cao cần nhập viện điều trị, chị Mai muốn đến thẳng cơ quan Bảo hiểm xã hội để xin cấp thẻ Bảo hiểm y tế cho cháu trước để được hưởng chế độ BHYT miễn phí cho trẻ dưới 6 tuổi.
* **Câu hỏi đầu vào (User Query)**:
  > *"Con tôi 1 tháng tuổi chưa làm giấy khai sinh, giờ cháu đang bị ốm cần đi viện. Tôi có thể đến cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT trước cho cháu được không? Cơ quan nào cấp và thời gian giải quyết là bao lâu?"*

### 3. Lộ trình chuẩn của Chuyên gia (Ground Truth từ `PROC_1_014137` & Quan hệ local)

* **Cơ quan thẩm quyền**
  * UBND cấp xã đăng ký khai sinh.
  * Cơ quan BHXH nhận hồ sơ liên thông và cấp thẻ BHYT.
* **Căn cứ pháp lý**
  * Nghị định số 188/2025/NĐ-CP quy định chi tiết và hướng dẫn thi hành một số điều của Luật Bảo hiểm y tế.
  * Luật Bảo hiểm y tế (Luật 25/2008/QH12, sửa đổi bởi Luật 46/2014/QH13 và Luật số 51/2024/QH15).
  * Quy định liên thông tại PROC_3_000722 (Nghị định 301/2026/NĐ-CP).
* **Quy trình**
  * **Bước 1 (Nộp hồ sơ liên thông)**
    * Nộp hồ sơ liên thông cho trẻ dưới 6 tuổi trên Cổng DVCQG hoặc VNeID ngay khi trẻ chưa có Giấy khai sinh.
    * Tờ khai điện tử Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP.
  * **Bước 2 (Đăng ký khai sinh rồi chuyển hồ sơ sang BHXH)**
    * UBND cấp xã đăng ký khai sinh trước. Cổng DVCQG chuyển hồ sơ kèm bản điện tử Giấy khai sinh sang hệ thống BHXH để cấp thẻ.
    * Toàn trình 03 ngày làm việc từ khi cơ quan có thẩm quyền nhận đủ hồ sơ, tối đa 05 ngày nếu phải xác minh.
    * Khâu cấp thẻ BHYT không quá 02 ngày làm việc kể từ khi BHXH nhận được hồ sơ điện tử liên thông.
* **Thông tin bổ sung**
  * (Lưu ý cấp cứu khám chữa bệnh): Trong thời gian chờ cấp thẻ BHYT, trẻ dưới 6 tuổi đi khám chữa bệnh có thể xuất trình Giấy chứng sinh theo quy định của pháp luật về BHYT.
  * Thủ tục cấp thẻ BHYT riêng lẻ PROC_1_014137 ghi thời hạn 05 ngày làm việc kể từ khi nhận đủ hồ sơ và dùng Mẫu số 2 kèm theo Nghị định số 188/2025/NĐ-CP.

---

### 4. Kết quả thực nghiệm của hệ thống AI
*(Sao chép nguyên văn phản hồi của AI vào khung bên dưới)*

```text
[=== BẮT ĐẦU ĐIỀN KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
Con bạn 1 tháng tuổi chưa làm giấy khai sinh và đang bị ốm cần đi viện, bạn không thể đến thẳng cơ quan Bảo hiểm xã hội xin cấp thẻ BHYT riêng lẻ cho trẻ trước khi có khai sinh theo cách thông thường, vì đối với trẻ dưới 6 tuổi, việc cấp thẻ BHYT được thực hiện liên thông cùng với thủ tục đăng ký khai sinh, đăng ký thường trú theo quy định 【PROC_1_014137_c60_s0】.

Cơ quan tiếp nhận và giải quyết cấp thẻ BHYT đơn lẻ là Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】 với thời gian giải quyết là 05 ngày làm việc kể từ ngày nhận đủ hồ sơ 【PROC_1_014137_c61_s0】, nhưng bạn có thể lựa chọn phương án thực hiện nhanh chóng qua gói liên thông điện tử.

Thứ tự nên làm
Bạn có hai phương án thực hiện:

Phương án 1: Thực hiện gói liên thông điện tử (Khuyên dùng)

Lý do: Giúp giải quyết đồng thời đăng ký khai sinh, đăng ký thường trú và cấp thẻ BHYT cho trẻ dưới 6 tuổi 【PROC_3_000722_c183_s1】.
Cơ quan tiếp nhận: Công an cấp xã (hoặc nộp trực tuyến qua Cổng Dịch vụ công quốc gia / ứng dụng VNeID) 【PROC_3_000722_c185_s0】【PROC_3_000722_c180_s1】.
Hồ sơ cần nộp: Tờ khai điện tử (Mẫu số 01) và dữ liệu điện tử/bản điện tử Giấy chứng sinh 【PROC_3_000722_c176_s0】【PROC_3_000722_c177_s0】.
Phương án 2: Làm thủ tục đăng ký khai sinh trước tại Ủy ban nhân dân cấp xã 【PROC_1_001193_c48_s0】

Lý do: Hoàn thành khai sinh (trong thời hạn 60 ngày kể từ ngày sinh con) 【PROC_1_001193_c43_s0】 để làm cơ sở cấp thẻ BHYT.
Thời gian giải quyết: 01 ngày (Miễn phí) 【PROC_1_001193_c48_s0】.
Sau khi có giấy khai sinh: Bạn có thể tiến hành nộp hồ sơ xin cấp thẻ BHYT theo hình thức trực tuyến, qua bưu chính hoặc trực tiếp tại Bảo hiểm xã hội tỉnh 【PROC_1_014137_c61_s0】 với Tờ khai tham gia, điều chỉnh thông tin bảo hiểm y tế theo Mẫu số 2 【PROC_1_014137_c50_s0】.
Thủ tục áp dụng
Thủ tục đăng ký khai sinh 【PROC_1_001193】
Thủ tục cấp thẻ bảo hiểm y tế 【PROC_1_014137】
Nguồn tham khảo (12)

Thủ tục đăng ký khai sinh — PROC_1_001193
Thủ tục đăng ký khai sinh – execution_methods — PROC_1_001193_c48_s0
Thủ tục đăng ký khai sinh – step_item — PROC_1_001193_c43_s0
Thủ tục cấp thẻ bảo hiểm y tế — PROC_1_014137
Thủ tục cấp thẻ bảo hiểm y tế – execution_methods — PROC_1_014137_c61_s0
Thủ tục cấp thẻ bảo hiểm y tế – step_item — PROC_1_014137_c60_s0
Thủ tục cấp thẻ bảo hiểm y tế – document_item — PROC_1_014137_c50_s0
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – execution_methods — PROC_3_000722_c185_s0
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c180_s1
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – step_item — PROC_3_000722_c183_s1
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – document_item — PROC_3_000722_c177_s0
Liên thông điện tử: đăng ký khai sinh, đăng ký thường trú, cấp thẻ bảo hiểm y tế, cấp thẻ căn cước cho trẻ em dưới 6 tuổi – document_item — PROC_3_000722_c176_s0
Căn cứ pháp lý của thủ tục

Thủ tục đăng ký khai sinh · 15 văn bản

Cấp xã · Toàn quốc · Hiệu lực từ 2019-07-31 · Ghi nhận 2026-11-18 · Phiên bản 178839f9e166

04/2024/TT-BTP — Sửa đổi, bổ sung một số điều của Thông tư số 02/2020/TT-BTP ngày 08/4/2020 của Bộ trưởng Bộ Tư pháp ban hành, hướng dẫn sử dụng, quản lý mẫu sổ quốc tịch và mẫu giấy tờ về quốc tịch và Thông tư số 04/2020/TT-BTP ngày 28/5/2020 của Bộ trưởng Bộ Tư pháp quy định chi tiết thi hành một số điều của Luật Hộ tịch và Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
Thông tư số 03/2023/TT-BTP — Thông tư số 03/2023/TT-BTP ngày 02/8/2023 của Bộ trưởng Bộ Tư pháp
106/2021/TT-BTC — Thông tư sửa đổi, bổ sung một số điều của Thông tư số 85/2019/TT-BTC ngày 29/11/2019 của Bộ Tài chính hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương.
04/2020/TT-BTP — Hướng dẫn Luật hộ tịch và Nghị định 123/2015/NĐ-CP hướng dẫn Luật hộ tịch do Bộ trưởng Bộ Tư pháp ban hành
07/2025/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định trong lĩnh vực hộ tịch, quốc tịch, chứng thực.
120/2025/NĐ-CP — Nghị định số 120/2025/NĐ-CP ngày 11/6/2025 của Chính phủ quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp.
66.7/2025/NQ-CP — Nghị quyết số 66.7/2025/NQ-CP của Chính phủ: Quy định cắt giảm, đơn giản hóa thủ tục hành chính dựa trên dữ liệu
60/2014/QH13 — Luật 60/2014/QH13
01/2022/TT-BTP — Thông tư quy định chi tiết một số điều và biện pháp thi hành Nghị định số 87/2020/NĐ-CP ngày 28 tháng 7 năm 2020 của Chính phủ quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
85/2019/TT-BTC — Thông tư Hướng dẫn về phí và lệ phí thuộc thẩm quyền quyết định của Hội đồng nhân dân tỉnh, thành phố trực thuộc Trung ương
104/2022/NĐ-CP — Nghị định sửa đổi, bổ sung một số điều của các Nghị định liên quan đến việc nộp xuất trình sổ hộ khẩu, sổ tạm trú giấy khi thực hiện thủ tục hành chính, cung cấp dịch vụ công
123/2015/NĐ-CP — Nghị định số 123/2015/NĐ-CP ngày 15/11/2015 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Hộ tịch
08/2025/TT-BTP — Thông tư số 08/2025/TT-BTP ngày 12/6/2025 của Bộ trưởng Bộ Tư pháp quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp và phân cấp trong lĩnh vực quản lý nhà nước của Bộ Tư pháp
18/2026/NĐ-CP — Nghị định sửa đổi, bổ sung một số nghị định để cắt giảm, đơn giản hóa thủ tục hành chính, điều kiện kinh doanh thuộc phạm vi quản lý của Bộ Tư pháp
87/2020/NĐ-CP — Nghị định quy định về Cơ sở dữ liệu hộ tịch điện tử, đăng ký hộ tịch trực tuyến
Một số căn cứ do thủ tục liệt kê chưa được đối chiếu hiệu lực.

Thủ tục cấp thẻ bảo hiểm y tế · 4 văn bản

Cấp tỉnh · Toàn quốc · Hiệu lực từ 2025-07-11 · Ghi nhận 2026-11-18 · Phiên bản 7ee3b4668fb0

188/2025/NĐ-CP — Nghị định quy định chi tiết và hướng dẫn thi hành một số điều của Luật Bảo hiểm y tế (188/2025/NĐ-CP ngày 01/7/2025)
25/2008/QH12 — Luật 25/2008/QH12 - Bảo hiểm y tế
51/2024/QH15 — Luật số 51/2024/QH15 ngày 27/11/2024 của Quốc hội sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế
Luật 46/2014/QH13 — 46/2014/QH13 Sửa đổi, bổ sung một số điều của Luật Bảo hiểm y tế
[=== KẾT THÚC KẾT QUẢ AI TẠO RA TẠI ĐÂY ===]
```

---

### 5. Bảng thẩm định Đúng / Sai & Đánh giá chất lượng

| Tiêu chí | Lộ trình chuẩn | Kết quả AI thể hiện | Đánh giá | Ghi chú theo JSON |
| --- | --- | --- | --- | --- |
| Nhận diện điều kiện tiên quyết (Prerequisite) | Đăng ký khai sinh hoàn tất trước khi chuyển hồ sơ sang BHXH để cấp thẻ. Gia đình có thể nộp hồ sơ liên thông ngay. | Nêu khai sinh đi trước cấp thẻ và đưa ra phương án liên thông khi trẻ chưa có Giấy khai sinh. Chưa mô tả rõ việc chuyển hồ sơ sang BHXH. | Đạt | Trượt nếu hướng dẫn xin thẻ trước khi đăng ký khai sinh hoặc yêu cầu phải có sẵn Giấy khai sinh mới được nộp hồ sơ liên thông. |
| Cơ quan thẩm quyền cấp thẻ BHYT | Bảo hiểm xã hội tỉnh / cơ quan BHXH (không phải UBND xã cấp thẻ BHYT). | Nêu BHXH tỉnh cấp thẻ và UBND cấp xã đăng ký khai sinh. | Đạt | Trượt nếu bảo UBND xã có thẩm quyền cấp thẻ BHYT. |
| Thời hạn liên thông và khâu cấp thẻ BHYT | Toàn trình 03 ngày làm việc từ khi cơ quan có thẩm quyền nhận đủ hồ sơ, tối đa 05 ngày nếu phải xác minh. Khâu cấp thẻ BHYT không quá 02 ngày làm việc kể từ khi BHXH nhận được hồ sơ điện tử liên thông. | Chỉ nêu 05 ngày của thủ tục đơn lẻ. Thiếu 03 ngày toàn trình, tối đa 05 ngày nếu xác minh, và không quá 02 ngày cho khâu BHYT. | Không đạt | Trượt nếu nhầm thời hạn cấp riêng hoặc thời hạn của riêng khâu BHYT với thời hạn toàn trình. |
| Biểu mẫu tờ khai liên thông | Tờ khai điện tử Mẫu số 01 kèm theo Nghị định số 301/2026/NĐ-CP. | Nêu 2 mẫu cho 2 trường hợp | Đạt | Trượt nếu dùng Mẫu số 2 của thủ tục cấp thẻ BHYT riêng lẻ cho hồ sơ liên thông. |
| Định hướng giải pháp liên thông | Nộp hồ sơ liên thông cho trẻ dưới 6 tuổi trên Cổng DVCQG hoặc VNeID ngay khi trẻ chưa có Giấy khai sinh. | Đề xuất nộp liên thông qua Cổng DVCQG hoặc VNeID. | Đạt | Trượt nếu chỉ hướng dẫn thực hiện các thủ tục riêng lẻ. |

#### Đánh giá tương tác yêu cầu bổ sung thông tin:
* **Nhận xét**. Hỏi về Giấy chứng sinh là phù hợp, nhưng cách hỏi giả định trẻ sinh tại cơ sở y tế.
* **Nội dung phản hồi làm rõ của AI**:
```text
[=== ĐIỀN CÂU HỎI LÀM RÕ CỦA AI NẾU CÓ ===]
Bạn đã có Giấy chứng sinh của cháu tại cơ sở y tế nơi sinh chưa?
```

---
---

## BẢNG TỔNG HỢP KẾT QUẢ KIỂM CHỨNG TOÀN DIỆN (EXECUTIVE SCORECARD)

Mỗi tiêu chí được chấm theo nội dung kỳ vọng trong JSON và bằng chứng trong câu trả lời đã lưu. Dẫn mã chunk giúp truy vết dữ liệu. Tiêu chí yêu cầu văn bản cụ thể cần nêu số hiệu văn bản. Phần hỏi làm rõ được nhận xét định tính.

| Mã ca | Tiêu chí đạt | Kết luận |
| --- | ---: | --- |
| TC-PROC-01 | 4/4 | Đạt |
| TC-PROC-02 | 4/5 | Không đạt |
| TC-PROC-03 | 5/5 | Đạt |
| TC-PROC-04 | 5/5 | Đạt |
| TC-PROC-05 | 4/5 | Không đạt |

- **Tiêu chí đạt** 22/24 (91.7%).
- **Ca đạt toàn bộ tiêu chí** 3/5.


---
**Người kiểm duyệt / Chuyên gia thủ tục ký tên**:  
*(Ký và ghi rõ họ tên)*  
*Ngày thẩm định: .... / .... / 202...*
