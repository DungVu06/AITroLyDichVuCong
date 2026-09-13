import json
import os

def chunk_procedure_json_v2(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    proc_id = data.get("id", "")
    life_event = data.get("life_event", [])
    domain = data.get("domain", "")
    
    procedure_info = data.get("procedure", {})
    proc_name = procedure_info.get("name", "Không rõ tên thủ tục")
    
    chunks = []
    
    # --- 1. Chunk Hồ sơ (Mỗi giấy tờ là 1 chunk riêng biệt) ---
    documents = procedure_info.get("documents", [])
    for doc in documents:
        ten_giay_to = doc.get('ten_giay_to', '').strip()
        so_luong = doc.get('so_luong', '').strip()
        
        # Chỉ tạo chunk nếu có nội dung
        if ten_giay_to:
            doc_content = f"Thành phần hồ sơ cần nộp để thực hiện {proc_name} (Mã: {proc_id}) bao gồm:\n- {ten_giay_to} (Số lượng: {so_luong})"
            chunks.append({
                "page_content": doc_content,
                "metadata": {"doc_id": proc_id, "chunk_type": "document_item", "life_event": life_event, "domain": domain}
            })

    # --- 2. Chunk Trình tự thực hiện (Mỗi bước là 1 chunk riêng biệt) ---
    steps = procedure_info.get("steps", [])
    for i, step in enumerate(steps, 1):
        if step.strip():
            step_content = f"Trình tự thực hiện {proc_name} (Mã: {proc_id}) - Bước {i}:\n{step.strip()}"
            chunks.append({
                "page_content": step_content,
                "metadata": {"doc_id": proc_id, "chunk_type": "step_item", "life_event": life_event, "domain": domain}
            })

    # --- 3. Chunk Cách thức & Lệ phí ---
    exec_methods = procedure_info.get("execution_methods", [])
    if exec_methods:
        method_texts = []
        for method in exec_methods:
            method_texts.append(f"- Hình thức: {method.get('method', '')}. Thời gian: {method.get('processing_time', '')}. Lệ phí: {method.get('fee', '')}.")
        
        method_content = f"Cách thức thực hiện, thời gian giải quyết và lệ phí của {proc_name} (Mã: {proc_id}):\n" + "\n".join(method_texts)
        chunks.append({
            "page_content": method_content,
            "metadata": {"doc_id": proc_id, "chunk_type": "execution_methods", "life_event": life_event, "domain": domain}
        })

    # --- 4. Chunk Lưu ý (Mỗi lưu ý là 1 chunk riêng biệt) ---
    notes = procedure_info.get("notes", [])
    for note in notes:
        if note.strip():
            note_content = f"Lưu ý quan trọng khi thực hiện {proc_name} (Mã: {proc_id}):\n{note.strip()}"
            chunks.append({
                "page_content": note_content,
                "metadata": {"doc_id": proc_id, "chunk_type": "note_item", "life_event": life_event, "domain": domain}
            })
            
    return chunks

# ==========================================
if __name__ == "__main__":
    procedure_dir = r"d:\Study\ML-DL\DL\MiniProject\AITroLyDichVuCong\data\procedure"
    all_chunks = []

    if os.path.exists(procedure_dir):
        for filename in os.listdir(procedure_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(procedure_dir, filename)
                file_chunks = chunk_procedure_json_v2(filepath)
                all_chunks.extend(file_chunks)
                
        print(f"Tổng cộng đã tạo ra: {len(all_chunks)} chunks đê đưa vào Vector DB.")
        
        output_file = r"d:\Study\ML-DL\DL\MiniProject\AITroLyDichVuCong\data\procedure_chunks_v2.jsonl"
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for chunk in all_chunks:
                out_f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                
        print(f"Đã lưu vào file: {output_file}")