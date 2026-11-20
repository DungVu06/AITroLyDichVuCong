"""Thiết lập quan hệ (relations) chuẩn giữa các thủ tục hành chính thuộc sự kiện Sinh con.

Quan hệ được thiết lập:
- Khai sinh (1.001193): Là bước đầu tiên -> next_steps: Thường trú (1.116788), BHYT (1.014137), Căn cước (1.116410)
- Thường trú, BHYT, Căn cước: prerequisites -> Khai sinh (1.001193)
- Cả 4 thủ tục đơn lẻ đều part_of -> Liên thông 4-trong-1 (3.000722)
- Liên thông (3.000722): sub_procedures -> bao gồm cả 4 thủ tục trên
- Tích hợp sẵn related_benefits từ file related_benefit_relations.json
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
RECORDS_DIR = ROOT_DIR / "data/procedure/records"
BENEFIT_REL_FILE = ROOT_DIR / "data/benefit_relation/related_benefit_relations.json"

PROCEDURE_GRAPH = {
    "PROC_1_001193": {
        "prerequisites": [],
        "next_steps": ["PROC_1_116788", "PROC_1_014137", "PROC_1_116410"],
        "part_of": ["PROC_3_000722"],
        "sub_procedures": []
    },
    "PROC_1_116788": {
        "prerequisites": ["PROC_1_001193"],
        "next_steps": [],
        "part_of": ["PROC_3_000722"],
        "sub_procedures": []
    },
    "PROC_1_014137": {
        "prerequisites": ["PROC_1_001193"],
        "next_steps": [],
        "part_of": ["PROC_3_000722"],
        "sub_procedures": []
    },
    "PROC_1_116410": {
        "prerequisites": ["PROC_1_001193"],
        "next_steps": [],
        "part_of": ["PROC_3_000722"],
        "sub_procedures": []
    },
    "PROC_3_000722": {
        "prerequisites": [],
        "next_steps": [],
        "part_of": [],
        "sub_procedures": ["PROC_1_001193", "PROC_1_116788", "PROC_1_014137", "PROC_1_116410"]
    }
}

def load_benefits():
    benefits_by_proc = {}
    if BENEFIT_REL_FILE.exists():
        with open(BENEFIT_REL_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                src = item.get("source_id")
                if src:
                    benefits_by_proc.setdefault(src, []).append({
                        "law_section_id": item.get("target_section_id"),
                        "scope": item.get("scope", "subtree"),
                        "note": item.get("note", "")
                    })
    return benefits_by_proc

def apply_relations():
    benefits_map = load_benefits()
    files = list(RECORDS_DIR.glob("PROC_*.json"))
    print(f"[*] Đang áp dụng quan hệ cho {len(files)} file trong: {RECORDS_DIR}")

    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            doc = json.load(f)

        proc_id = doc.get("id")
        if proc_id in PROCEDURE_GRAPH:
            relations = doc.setdefault("relations", {})
            mapping = PROCEDURE_GRAPH[proc_id]
            
            relations["prerequisites"] = mapping["prerequisites"]
            relations["next_steps"] = mapping["next_steps"]
            relations["part_of"] = mapping["part_of"]
            relations["sub_procedures"] = mapping["sub_procedures"]
            
            # Gán quyền lợi nếu có
            if proc_id in benefits_map:
                relations["related_benefits"] = benefits_map[proc_id]

            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            print(f"[+] Đã cập nhật relations cho: {proc_id}")

if __name__ == "__main__":
    apply_relations()
