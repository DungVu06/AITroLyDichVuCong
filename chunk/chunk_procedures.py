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
    
    base_metadata = {
        "doc_id": proc_id,
        "life_event": data.get("life_event", []),
        "domain": data.get("domain", ""),
        "relations": data.get("relations", {})
    }
    
    procedure_info = data.get("procedure", {})
    proc_name = procedure_info.get("name", "Không rõ tên thủ tục")
    
    chunks = []
    
    # --- 1. Chunk Hồ sơ ---
    documents = procedure_info.get("documents", [])
    for doc in documents:
        ten_giay_to = doc.get('ten_giay_to', '').strip()
        so_luong = doc.get('so_luong', '').strip()
        if ten_giay_to:
            doc_content = f"Thành phần hồ sơ cần nộp để thực hiện {proc_name} (Mã: {proc_id}) bao gồm:\n- {ten_giay_to} (Số lượng: {so_luong})"
            meta = base_metadata.copy()
            meta["chunk_type"] = "document_item"
            chunks.append({"page_content": doc_content, "metadata": meta})

    # --- 2. Chunk Trình tự thực hiện ---
    steps = procedure_info.get("steps", [])
    for i, step in enumerate(steps, 1):
        if step.strip():
            step_content = f"Trình tự thực hiện {proc_name} (Mã: {proc_id}) - Bước {i}:\n{step.strip()}"
            meta = base_metadata.copy()
            meta["chunk_type"] = "step_item"
            chunks.append({"page_content": step_content, "metadata": meta})

    # --- 3. Chunk Cách thức & Lệ phí ---
    exec_methods = procedure_info.get("execution_methods", [])
    if exec_methods:
        method_texts = []
        for method in exec_methods:
            method_texts.append(f"- Hình thức: {method.get('method', '')}. Thời gian: {method.get('processing_time', '')}. Lệ phí: {method.get('fee', '')}.")
        
        method_content = f"Cách thức thực hiện, thời gian giải quyết và lệ phí của {proc_name} (Mã: {proc_id}):\n" + "\n".join(method_texts)
        meta = base_metadata.copy()
        meta["chunk_type"] = "execution_methods"
        chunks.append({"page_content": method_content, "metadata": meta})

    # --- 4. Chunk Lưu ý ---
    notes = procedure_info.get("notes", [])
    for note in notes:
        if note.strip():
            note_content = f"Lưu ý quan trọng khi thực hiện {proc_name} (Mã: {proc_id}):\n{note.strip()}"
            meta = base_metadata.copy()
            meta["chunk_type"] = "note_item"
            chunks.append({"page_content": note_content, "metadata": meta})
            
    return chunks

if __name__ == "__main__":
    # SỬA ĐƯỜNG DẪN TRỎ VÀO NORMALIZED_RECORDS
    parser = argparse.ArgumentParser(
        description="Tạo JSONL chunks từ procedure records."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "procedure/normalized_records",
        help="Thư mục chứa PROC_*.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "chunks" / "procedure_chunks.jsonl",
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
        
        # CHÚ Ý: chunk_size tính bằng KÝ TỰ (Characters). 1000 ký tự tương đương ~200 từ.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        safe_chunks_for_sbert = []
        for doc_idx, chunk in enumerate(all_chunks):
            text = chunk["page_content"]
            split_texts = text_splitter.split_text(text)
            for split_idx, split_txt in enumerate(split_texts):
                new_metadata = chunk["metadata"].copy()
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
