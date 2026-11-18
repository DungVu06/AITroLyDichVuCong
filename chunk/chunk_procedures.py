import json
import argparse
from pathlib import Path
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def recursive_char_split(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> list[str]:
    """
    Hàm chia text thuần Python không cần phụ thuộc thư viện bên ngoài (langchain).
    Tách theo các điểm ngắt tự nhiên: dòng đôi, xuống dòng, dấu chấm, dấu cách.
    """
    if len(text) <= chunk_size:
        return [text]

    separators = ["\n\n", "\n", ". ", " ", ""]
    
    def _split(t: str, seps: list[str]) -> list[str]:
        if not seps or len(t) <= chunk_size:
            return [t] if t else []
        sep = seps[0]
        if sep == "":
            # Cắt trực tiếp theo độ dài nếu không còn dấu phân cách
            return [t[i:i + chunk_size] for i in range(0, len(t), chunk_size - chunk_overlap)]
        
        parts = t.split(sep)
        splits = []
        current = ""
        for p in parts:
            piece = (current + sep + p) if current else p
            if len(piece) <= chunk_size:
                current = piece
            else:
                if current:
                    splits.append(current)
                if len(p) > chunk_size:
                    splits.extend(_split(p, seps[1:]))
                    current = ""
                else:
                    current = p
        if current:
            splits.append(current)
        return splits

    return _split(text, separators)


def chunk_procedure_json(filepath):
    """
    Phân tách 1 bản ghi procedure JSON thành các semantic chunks chuyên biệt:
    1. Đối tượng & Điều kiện thực hiện (eligibility)
    2. Từng thành phần hồ sơ giấy tờ (document_item)
    3. Từng bước thực hiện (step_item)
    4. Cách thức, thời gian & lệ phí (execution_methods)
    5. Lưu ý bổ sung (note_item - nếu có)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    proc_id = data.get("id", "")
    procedure_info = data.get("procedure", {})
    proc_name = procedure_info.get("name", "Không rõ tên thủ tục")
    authority = procedure_info.get("authority", "")
    level = data.get("jurisdiction", {}).get("level", "")
    location = data.get("jurisdiction", {}).get("location", "Toàn quốc")
    effective_date = data.get("source", {}).get("effective_date", "")
    source_url = data.get("source", {}).get("url", "")
    target_audience = data.get("target_audience", [])
    
    # Metadata toàn diện gắn kèm từng chunk để lọc (filter) trên Vector DB & trích dẫn
    base_metadata = {
        "doc_id": proc_id,
        "national_code": data.get("national_code", ""),
        "procedure_name": proc_name,
        "authority": authority,
        "jurisdiction_level": level,
        "jurisdiction_location": location,
        "effective_date": effective_date,
        "target_audience": target_audience,
        "life_event": data.get("life_event", []),
        "domain": data.get("domain", ""),
        "source_url": source_url,
        "relations": data.get("relations", {})
    }
    
    chunks = []

    # --- 1. Chunk Đối tượng & Điều kiện / Yêu cầu thực hiện ---
    eligibility = procedure_info.get("eligibility", "").strip()
    elig_parts = []
    if target_audience:
        elig_parts.append(f"- Đối tượng thực hiện: {', '.join(target_audience)}.")
    if eligibility and eligibility.lower() not in ["không", "không có", "không có thông tin"]:
        elig_parts.append(f"- Yêu cầu, điều kiện thực hiện:\n{eligibility}")

    if elig_parts:
        elig_content = f"Đối tượng và điều kiện thực hiện {proc_name} (Mã: {proc_id}):\n" + "\n".join(elig_parts)
        meta = base_metadata.copy()
        meta["chunk_type"] = "eligibility"
        chunks.append({"page_content": elig_content, "metadata": meta})
    
    # --- 2. Chunk Thành phần Hồ sơ ---
    documents = procedure_info.get("documents", [])
    for doc in documents:
        ten_giay_to = doc.get('ten_giay_to', '').strip()
        so_luong = doc.get('so_luong', '').strip()
        is_required = doc.get('bat_buoc', False)
        req_str = " (Bắt buộc)" if is_required else " (Theo trường hợp / nếu có)"

        if ten_giay_to:
            qty_str = f" - Số lượng: {so_luong}" if so_luong else ""
            doc_content = f"Thành phần hồ sơ cần nộp để thực hiện {proc_name} (Mã: {proc_id}):\n- {ten_giay_to}{qty_str}{req_str}."
            meta = base_metadata.copy()
            meta["chunk_type"] = "document_item"
            meta["is_required"] = is_required
            chunks.append({"page_content": doc_content, "metadata": meta})

    # --- 3. Chunk Trình tự thực hiện ---
    steps = procedure_info.get("steps", [])
    for i, step in enumerate(steps, 1):
        if step.strip():
            step_content = f"Trình tự thực hiện {proc_name} (Mã: {proc_id}) - Bước {i}:\n{step.strip()}"
            meta = base_metadata.copy()
            meta["chunk_type"] = "step_item"
            meta["step_number"] = i
            chunks.append({"page_content": step_content, "metadata": meta})

    # --- 4. Chunk Cách thức, Thời gian giải quyết & Lệ phí ---
    exec_methods = procedure_info.get("execution_methods", [])
    if exec_methods:
        method_texts = []
        for method in exec_methods:
            m_name = method.get('method', '')
            p_time = method.get('processing_time', '')
            p_fee = method.get('fee', '')
            p_desc = method.get('description', '')

            desc_part = f" ({p_desc})" if p_desc else ""
            method_texts.append(f"- Hình thức: {m_name}. Thời gian giải quyết: {p_time}. Lệ phí: {p_fee}{desc_part}.")
        
        authority_part = f"Cơ quan tiếp nhận và giải quyết: {authority}.\n" if authority else ""
        method_content = f"Cách thức nộp hồ sơ, thời gian giải quyết và lệ phí của {proc_name} (Mã: {proc_id}):\n{authority_part}" + "\n".join(method_texts)
        meta = base_metadata.copy()
        meta["chunk_type"] = "execution_methods"
        chunks.append({"page_content": method_content, "metadata": meta})

    # --- 5. Chunk Lưu ý bổ sung (nếu có) ---
    notes = procedure_info.get("notes", [])
    for note in notes:
        if note.strip():
            note_content = f"Lưu ý quan trọng khi thực hiện {proc_name} (Mã: {proc_id}):\n{note.strip()}"
            meta = base_metadata.copy()
            meta["chunk_type"] = "note_item"
            chunks.append({"page_content": note_content, "metadata": meta})
            
    return chunks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tạo JSONL chunks từ procedure records."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "procedure" / "normalized_records",
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

    # 1. Thu thập chunks ngữ nghĩa từ từng file
    files = sorted(procedure_dir.glob("PROC_*.json"))
    print(f"[*] Đang đọc {len(files)} file thủ tục từ: {procedure_dir}")

    for filepath in files:
        file_chunks = chunk_procedure_json(filepath)
        all_chunks.extend(file_chunks)

    # 2. Split an toàn cho Vietnamese SBERT (đảm bảo không vượt quá context window)
    safe_chunks_for_sbert = []
    for doc_idx, chunk in enumerate(all_chunks):
        text = chunk["page_content"]
        split_texts = recursive_char_split(text, chunk_size=1000, chunk_overlap=100)
        for split_idx, split_txt in enumerate(split_texts):
            new_metadata = chunk["metadata"].copy()
            new_metadata["chunk_id"] = f"{new_metadata['doc_id']}_c{doc_idx}_s{split_idx}"
            
            safe_chunks_for_sbert.append({
                "page_content": split_txt,
                "metadata": new_metadata
            })
            
    print(f"[+] Từ {len(all_chunks)} chunks ngữ nghĩa gốc, đã chia thành {len(safe_chunks_for_sbert)} chunks an toàn cho SBERT.")
    
    # 3. Ghi file đầu ra (bên ngoài vòng lặp)
    output_file = args.output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open('w', encoding='utf-8') as out_f:
        for chunk in safe_chunks_for_sbert:
            out_f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
            
    print(f"[✔] Đã lưu thành công vào file: {output_file}")
