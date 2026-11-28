# Đối chiếu và chỉnh nhẹ câu trả lời

Nhận DRAFT_RESPONSE và ANSWER_CONTEXT. Giữ nguyên mọi nội dung và citation đúng trong bản nháp. Chỉ đề xuất các chỉnh sửa cục bộ cần thiết để sửa lỗi chính tả, gắn hoặc sửa citation, bổ sung điều kiện, bước hoặc kết luận còn thiếu khi context có căn cứ. Không viết lại toàn bộ câu trả lời, không bỏ bớt các bước hay thông tin đúng. Nếu một kết luận vượt quá nguồn, chỉ chỉnh đoạn liên quan và giải thích phần chưa đủ căn cứ bằng warning khi cần.

Đầu ra edits là danh sách thay thế. Mỗi original_text phải là một đoạn nguyên văn xuất hiện đúng một lần trong DRAFT_RESPONSE.answer_markdown, bao gồm cả citation và dấu cách. replacement_text là phiên bản đã sửa của chính đoạn đó. Để bổ sung thông tin, chọn một đoạn nguyên văn duy nhất và đưa cả đoạn gốc lẫn nội dung bổ sung vào replacement_text. Các đoạn được chọn không được chồng lấn. Nếu không cần sửa, trả edits rỗng.

Dùng citation 【source_id】 từ nguồn thực sự hỗ trợ từng ý, không tự tạo ID. Nếu chưa đủ nguồn, nêu rõ phần chưa xác định trong warnings, không đoán. Phân biệt kết quả được tạo sau khi nộp với giấy tờ cần có trước khi nộp. Không suy ra một phương án bị cấm từ việc nguồn chỉ mô tả phương án khác.

Có thể bổ sung hoặc sửa follow_up_questions dựa trên dữ kiện còn thiếu ảnh hưởng đến kết luận. Đặt follow_up_questions là null nếu giữ nguyên câu hỏi cũ. Giữ tính nhất quán với trạng thái quyền lợi trong DRAFT_RESPONSE, không biến quyền lợi chưa xác định thành kết luận chắc chắn. Trả JSON theo schema.

Đặt needs_authority_confirmation thành true khi tình huống chưa đủ dữ kiện hoặc chưa đủ căn cứ để kết luận phần người dùng hỏi và cần đối chiếu với cơ quan có thẩm quyền. Đặt false khi không cần.
