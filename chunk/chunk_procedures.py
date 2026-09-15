import json
import argparse
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def chunk_procedure_json(filepath):
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
    parser = argparse.ArgumentParser(
        description="Tạo JSONL chunks từ procedure records."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "procedure",
        help="Thư mục chứa PROC_*.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "procedure_chunks.jsonl",
        help="File JSONL đầu ra",
    )
    args = parser.parse_args()

    procedure_dir = args.input_dir
    all_chunks = []

    if not procedure_dir.exists():
        raise SystemExit(f"Không tìm thấy thư mục dữ liệu: {procedure_dir}")

    for filepath in sorted(procedure_dir.glob("PROC_*.json")):
        file_chunks = chunk_procedure_json(filepath)
        all_chunks.extend(file_chunks)
                
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200, 
            chunk_overlap=20,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        safe_chunks_for_sbert = []
        for doc_idx, chunk in enumerate(all_chunks):
            text = chunk["page_content"]
            split_texts = text_splitter.split_text(text)
            for split_idx, split_txt in enumerate(split_texts):
                new_metadata = chunk["metadata"].copy()
                # Tạo ID duy nhất: [Mã văn bản]_[Thứ tự chunk gốc]_[Thứ tự cắt đệ quy]
                new_metadata["chunk_id"] = f"{new_metadata['doc_id']}_c{doc_idx}_s{split_idx}"
                
                safe_chunks_for_sbert.append({
                    "page_content": split_txt,
                    "metadata": new_metadata
                })
                
        print(f"Từ {len(all_chunks)} chunks gốc, đã chia thành {len(safe_chunks_for_sbert)} chunks an toàn cho SBERT.")
        
        output_file = args.output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('w', encoding='utf-8') as out_f:
            for chunk in safe_chunks_for_sbert:
                out_f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                
        print(f"Đã lưu vào file: {output_file}")
