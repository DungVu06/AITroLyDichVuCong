# Nhiệm vụ sửa câu trả lời

Sửa `ORIGINAL_ANSWER` theo đúng các lỗi trong `VALIDATION_ISSUES`.

Quy tắc:

1. Chỉ sử dụng dữ liệu và source ID có trong `ANSWER_CONTEXT`.
2. Giữ nguyên nội dung đúng; chỉ sửa hoặc loại bỏ phần gây lỗi.
3. Mỗi citation phải chứa đúng một source ID: `【source_id】`.
4. Không tự tạo procedure ID, chunk ID hoặc section ID.
5. Claim về thủ tục, số liệu, thời hạn và lệ phí phải có citation cùng dòng.
6. Quyền lợi có trạng thái `unknown` phải được diễn đạt là chưa chắc chắn.
7. Chỉ trả về Markdown đã sửa theo JSON schema do API cung cấp.
