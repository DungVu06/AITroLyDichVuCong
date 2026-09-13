import json
import os
def chunk_procedure_json(filepath):
    """
    Hàm đọc file JSON thủ tục và cắt thành các chunk theo chủ đề (Hồ sơ, Các bước, Lưu ý).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # --- 1. Lấy thông tin chung (Metadata) ---
    proc_id = data.get("id", "")
    life_event = data.get("life_event", [])
    domain = data.get("domain", "")
    
    procedure_info = data.get("procedure", {})
    proc_name = procedure_info.get("name", "Không rõ tên thủ tục")
    
    chunks = []
    
    # --- 2. Tạo Chunk 1: Hồ sơ cần nộp (Documents) ---
    documents = procedure_info.get("documents", [])
    if documents:
        doc_texts = []
        for i, doc in enumerate(documents, 1):
            ten_giay_to = doc.get('ten_giay_to', '').strip()
            so_luong = doc.get('so_luong', '').strip()
            doc_texts.append(f"{i}. {ten_giay_to} (Số lượng: {so_luong})")
        
        doc_content = f"Để thực hiện {proc_name} (Mã: {proc_id}), công dân cần chuẩn bị thành phần hồ sơ giấy tờ sau:\n" + "\n".join(doc_texts)
        
        chunks.append({
            "page_content": doc_content,
            "metadata": {
                "doc_id": proc_id,
                "chunk_type": "documents",
                "life_event": life_event,
                "domain": domain
            }
        })
    # --- 3. Tạo Chunk 2: Trình tự thực hiện (Steps) ---
    steps = procedure_info.get("steps", [])
    if steps:
        step_texts = []
        for i, step in enumerate(steps, 1):
            step_texts.append(f"Bước {i}: {step}")
        
        step_content = f"Trình tự các bước thực hiện {proc_name} (Mã: {proc_id}):\n" + "\n".join(step_texts)
        
        chunks.append({
            "page_content": step_content,
            "metadata": {
                "doc_id": proc_id,
                "chunk_type": "steps",
                "life_event": life_event,
                "domain": domain
            }
        })
    # --- 4. Tạo Chunk 3: Thông tin chung & Lưu ý (Notes & Execution Methods) ---
    notes = procedure_info.get("notes", [])
    exec_methods = procedure_info.get("execution_methods", [])
    
    info_parts = [f"Thông tin chung và lưu ý của {proc_name} (Mã: {proc_id}):\n"]
    
    if exec_methods:
        info_parts.append("Cách thức thực hiện, thời gian giải quyết và lệ phí:")
        for method in exec_methods:
            hinh_thuc = method.get('method', '')
            thoi_gian = method.get('processing_time', '')
            phi = method.get('fee', '')
            info_parts.append(f"- Hình thức: {hinh_thuc}. Thời gian: {thoi_gian}. Lệ phí: {phi}.")
            
    if notes:
        info_parts.append("\nCác lưu ý quan trọng cần biết:")
        for note in notes:
            info_parts.append(f"- {note}")
            
    if len(info_parts) > 1:
        chunks.append({
            "page_content": "\n".join(info_parts),
            "metadata": {
                "doc_id": proc_id,
                "chunk_type": "notes_and_methods",
                "life_event": life_event,
                "domain": domain
            }
        })
        
    return chunks

if __name__ == "__main__":
    procedure_dir = r"d:\Study\ML-DL\DL\MiniProject\AITroLyDichVuCong\data\procedure"
    all_chunks = []
    if os.path.exists(procedure_dir):
        for filename in os.listdir(procedure_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(procedure_dir, filename)
                
                file_chunks = chunk_procedure_json(filepath)
                all_chunks.extend(file_chunks)
                
                print(f"Đã chunking file {filename} thành {len(file_chunks)} chunks.")
        print(f"\nTổng cộng đã tạo ra: {len(all_chunks)} chunks từ toàn bộ dữ liệu Thủ tục.")
        
        output_file = "d:/Study/ML-DL/DL/MiniProject/AITroLyDichVuCong/data/procedure_chunks.jsonl"
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for chunk in all_chunks:
                out_f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                
        print(f"Đã lưu toàn bộ {len(all_chunks)} chunks vào file: {output_file}")
    else:
        print("Không tìm thấy thư mục. Vui lòng kiểm tra lại đường dẫn.")