"""Tổng hợp tất cả căn cứ pháp lý (legal bases) từ 5 thủ tục hành chính.
Xuất ra 2 file:
- crawl/legal_bases_summary.json (dễ dàng dùng code để crawl tự động)
- crawl/legal_bases_summary.md (dễ đọc, tra cứu số hiệu để tìm link vbpl.vn)
"""

import json
import glob
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT_DIR / "data/procedure/records"
OUT_JSON = ROOT_DIR / "crawl/legal_bases_summary.json"
OUT_MD = ROOT_DIR / "crawl/legal_bases_summary.md"

def extract_summary():
    legal_bases_map = {}
    files = sorted(RECORDS_DIR.glob("PROC_*.json"))

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            doc = json.load(f)
        proc_id = doc.get("id")
        proc_name = doc.get("procedure", {}).get("name")
        for lb in doc.get("relations", {}).get("legal_bases", []):
            raw_code = lb.get("code", "").strip()
            raw_name = lb.get("name", "").strip()
            if not raw_code and not raw_name:
                continue

            # Chuẩn hóa mã số (ví dụ 'Thông tư số 03/2023/TT-BTP' -> '03/2023/TT-BTP')
            norm_code = re.sub(r"^(Thông tư|Nghị định|Luật|Nghị quyết)\s*(số)?\s*", "", raw_code, flags=re.IGNORECASE).strip()
            norm_code = norm_code.replace(" ", "")

            # Phân loại văn bản
            doc_type = "Khác"
            combined_text = f"{raw_code} {raw_name}"
            if re.search(r"\bLuật\b", combined_text, re.IGNORECASE):
                doc_type = "Luật"
            elif re.search(r"\bNghị định\b", combined_text, re.IGNORECASE) or "NĐ-CP" in norm_code:
                doc_type = "Nghị định"
            elif re.search(r"\bThông tư\b", combined_text, re.IGNORECASE) or "TT-" in norm_code:
                doc_type = "Thông tư"
            elif re.search(r"\bNghị quyết\b", combined_text, re.IGNORECASE) or "NQ-CP" in norm_code:
                doc_type = "Nghị quyết"

            key = norm_code if norm_code else raw_name
            if key not in legal_bases_map:
                legal_bases_map[key] = {
                    "so_hieu": norm_code,
                    "loai_van_ban": doc_type,
                    "ten_van_ban": raw_name,
                    "thu_tuc_ap_dung": []
                }
            usage_str = f"{proc_id} ({proc_name})"
            if usage_str not in legal_bases_map[key]["thu_tuc_ap_dung"]:
                legal_bases_map[key]["thu_tuc_ap_dung"].append(usage_str)

    # 1. Ghi file JSON
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(list(legal_bases_map.values()), f, ensure_ascii=False, indent=2)

    # 2. Ghi file Markdown
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Danh mục Căn cứ Pháp lý (Legal Bases) của 5 Thủ tục Hành chính\n\n")
        f.write(f"Tổng số văn bản quy phạm pháp luật trích dẫn: **{len(legal_bases_map)} văn bản**.\n\n")
        f.write("| STT | Số hiệu | Loại văn bản | Tên văn bản | Thủ tục áp dụng |\n")
        f.write("| :---: | :--- | :---: | :--- | :--- |\n")
        for idx, (k, item) in enumerate(legal_bases_map.items(), 1):
            procs = "<br>".join(item["thu_tuc_ap_dung"])
            sh = item["so_hieu"]
            lvb = item["loai_van_ban"]
            tvb = item["ten_van_ban"]
            f.write(f"| {idx} | `{sh}` | {lvb} | {tvb} | {procs} |\n")

    print(f"[✔] Đã tổng hợp thành công {len(legal_bases_map)} căn cứ pháp lý vào:")
    print(f"    - JSON: {OUT_JSON}")
    print(f"    - Markdown: {OUT_MD}")

if __name__ == "__main__":
    extract_summary()
