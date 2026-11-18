"""Thu thập metadata và nội dung thủ tục hành chính từ Cổng Dịch vụ công Quốc gia (dichvucong.gov.vn).

Cơ chế hoạt động:
  - Khởi chạy Playwright để mở trang thủ tục.
  - Intercept (bắt gói tin) REST API gốc của Cổng DVCQG: /api/v1/configuring/formality/get-formality-by-citizen.
  - Chuẩn hóa trực tiếp từ dữ liệu JSON gốc sang Schema của dự án bằng Rule (chính xác 100%, không bị dính HTML rác).
  - Tự động bóc tách:
      + Thành phần hồ sơ (tên, số lượng bản chính/sao, mã giấy tờ, tính bắt buộc)
      + Trình tự các bước (chia nhỏ danh sách steps)
      + Căn cứ pháp lý (legal_bases: tên văn bản, số hiệu) phục vụ Knowledge Graph
      + Cơ quan giải quyết (tự động fallback unitGroupsExecuting/departmentsExecuting)
      + Quản lý phiên bản & Hiệu lực (proposal_number, effective_date, state, last_updated)

Ví dụ sử dụng:
  # Crawl 1 URL cụ thể:
  python crawl/crawl_procedures.py --url "https://dichvucong.gov.vn/thu-tuc-hanh-chinh/019d2bfd-3fe0-70ac-b9d6-5e9e20d6eef7" --out tests

  # Crawl toàn bộ danh sách từ file seed:
  python crawl/crawl_procedures.py --seed crawl/seed_procedures_urls.csv --out tests
"""

import os
import re
import csv
import json
import argparse
import datetime
import unicodedata
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


def clean_text(text: str) -> str:
    """Làm sạch ký tự ẩn, chuẩn hóa unicode NFC và khoảng trắng."""
    if not text:
        return ""
    cleaned = text.replace('\u200e', '').replace('\u200f', '').replace('\u200b', '').replace('\xa0', ' ')
    cleaned = unicodedata.normalize('NFC', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()


def split_steps(raw_steps_text: str) -> list[str]:
    """Tách trình tự thực hiện thành từng bước chuẩn xác."""
    if not raw_steps_text:
        return []

    lines = [clean_text(l) for l in raw_steps_text.split('\n') if clean_text(l)]
    steps = []
    current_step = ""

    # Nhận diện đầu mục mới: a), b) hoặc Bước 1: hoặc 1. hoặc - hoặc +
    pattern = r'^([a-z]\)|\d+[\.\)]|Bước\s*\d+[:\.-]|\-|\+)'

    for line in lines:
        if re.match(pattern, line, re.IGNORECASE):
            if current_step:
                steps.append(current_step.strip())
            current_step = line
        else:
            if current_step:
                current_step += "\n" + line
            else:
                current_step = line

    if current_step:
        steps.append(current_step.strip())

    return steps if steps else [clean_text(raw_steps_text)]


def extract_authority(d: dict) -> str:
    """Trích xuất cơ quan thực hiện, tự động dự phòng nếu trường executingAgencies bị rỗng."""
    direct_agency = clean_text(d.get("executingAgencies", ""))
    if direct_agency:
        return direct_agency

    # Fallback 1: Lấy từ unitGroupsExecuting (ví dụ: 'Ủy ban nhân dân cấp xã', 'Công an Xã')
    unit_groups = d.get("unitGroupsExecuting", [])
    if unit_groups:
        names = [clean_text(u.get("name", "")) for u in unit_groups if u.get("name")]
        if names:
            return ", ".join(names)

    # Fallback 2: Lấy từ departmentsExecuting
    dept_groups = d.get("departmentsExecuting", [])
    if dept_groups:
        names = [clean_text(u.get("name", "")) for u in dept_groups if u.get("name")]
        if names:
            return ", ".join(names)

    # Fallback 3: Dựa vào cấp thực hiện
    if d.get("isWard"):
        return "Ủy ban nhân dân / Công an cấp Xã"
    if d.get("isProvince"):
        return "Cơ quan chuyên môn cấp Tỉnh"
    if d.get("isMinistry"):
        return clean_text(d.get("departmentPromulgateName", "Cơ quan cấp Bộ"))

    return "Cơ quan có thẩm quyền theo quy định"


def map_api_to_schema(api_data: dict, source_url: str, life_events: list[str] = None) -> dict:
    """Chuyển đổi dữ liệu JSON từ API Cổng DVCQG sang Schema chuẩn của dự án."""
    d = api_data.get("data", {})
    if "data" in d and isinstance(d["data"], dict):
        d = d["data"]

    code = d.get("code") or d.get("codeNotation") or ""
    proc_id = f"PROC_{code.replace('.', '_')}" if code else f"PROC_{d.get('id', 'UNKNOWN')}"

    # 1. Trích xuất Thành phần hồ sơ / Giấy tờ
    documents = []
    for case in d.get("executionCases", []):
        for comp in case.get("profileComponents", []):
            orig_qty = comp.get("originalQty", 0)
            copy_qty = comp.get("copyQty", 0)
            qty_parts = []
            if orig_qty > 0:
                qty_parts.append(f"{orig_qty} Bản chính")
            if copy_qty > 0:
                qty_parts.append(f"{copy_qty} Bản sao")
            qty_str = ", ".join(qty_parts) if qty_parts else "Theo quy định"

            documents.append({
                "ten_giay_to": clean_text(comp.get("name", "")),
                "so_luong": qty_str,
                "bat_buoc": comp.get("required", False),
                "ma_giay_to": comp.get("code", "")
            })

    # 2. Trình tự thực hiện (steps)
    raw_steps_list = d.get("executionSteps", [])
    steps = []
    for s in raw_steps_list:
        desc = s.get("description", "")
        if desc:
            steps.extend(split_steps(desc))

    # 3. Cách thức thực hiện & Lệ phí
    execution_methods = []
    method_map = {
        "ONLINE": "Trực tuyến",
        "DIRECT": "Trực tiếp",
        "POSTAL": "Dịch vụ bưu chính"
    }
    for m in d.get("executionMethods", []):
        sub_method = m.get("submissionMethod", "")
        method_name = method_map.get(sub_method, sub_method)

        fees_info = []
        for fee in m.get("fees", []):
            val = fee.get("value", 0)
            currency = fee.get("currencyName", "VNĐ")
            desc = fee.get("description", "")
            if val == 0:
                fees_info.append("Miễn phí")
            else:
                fee_txt = f"{val:,} {currency}"
                if desc:
                    fee_txt += f" ({desc})"
                fees_info.append(fee_txt)
        fee_str = "; ".join(fees_info) if fees_info else "Miễn phí"

        proc_time = m.get("processingTime", "")
        unit = m.get("processingTimeUnit", "")
        unit_str = "ngày làm việc" if "WORKING_DAY" in unit else "ngày"
        time_str = f"{proc_time} {unit_str}".strip() if proc_time else ""

        execution_methods.append({
            "method": method_name,
            "processing_time": time_str,
            "fee": fee_str,
            "description": clean_text(m.get("description", ""))
        })

    # 4. Căn cứ pháp lý (legal_bases cho Knowledge Graph)
    legal_bases = []
    for lb in d.get("legalBasisesDetails", []):
        legal_bases.append({
            "name": clean_text(lb.get("name", "")),
            "code": clean_text(lb.get("code", "")).strip()
        })

    # 5. Đối tượng thực hiện
    target_audiences = [clean_text(s.get("name", "")) for s in d.get("subjectTypesDetails", []) if s.get("name")]
    if not target_audiences and d.get("formalityTargetType"):
        target_audiences = d.get("formalityTargetType")

    # 6. Cấp thực hiện (Jurisdiction Level)
    level = "Cấp tỉnh" if d.get("isProvince") else (
            "Cấp xã" if d.get("isWard") else (
            "Cấp Bộ" if d.get("isMinistry") else "Toàn quốc"))

    # 7. Metadata phiên bản & Ngày ban hành / Hiệu lực
    proposal = d.get("procedureProposal", {}) or {}
    proposal_no = proposal.get("proposalNumber") or proposal.get("decisionNumber") or ""
    pub_date_ms = proposal.get("decisionDate") or proposal.get("publicationDate")
    effective_date_str = ""
    if pub_date_ms:
        try:
            effective_date_str = datetime.datetime.fromtimestamp(pub_date_ms / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            effective_date_str = ""

    structured_json = {
        "id": proc_id,
        "national_code": code,
        "life_event": life_events or ["sinh_con"],
        "target_audience": target_audiences,
        "domain": clean_text(d.get("categoriesDetails", [{}])[0].get("name", "") if d.get("categoriesDetails") else ""),
        "procedure_type": d.get("formalityType", ""),

        "procedure": {
            "name": clean_text(d.get("name", "")),
            "eligibility": clean_text(d.get("requirementsAndConditions", "")),
            "documents": documents,
            "steps": steps,
            "authority": extract_authority(d),
            "execution_methods": execution_methods,
            "online_portal_url": source_url
        },

        "relations": {
            "legal_bases": legal_bases,
            "prerequisites": [],
            "next_steps": [],
            "part_of": [],
            "related_benefits": []
        },

        "jurisdiction": {
            "level": level,
            "location": "Toàn quốc"
        },

        "source": {
            "name": "Cổng Dịch vụ công Quốc gia",
            "url": source_url,
            "effective_date": effective_date_str,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")
        },

        "version_control": {
            "proposal_number": proposal_no,
            "state": d.get("state", "ACTIVE"),
            "raw_id": d.get("id", "")
        }
    }
    return structured_json


def crawl_single_url(page, url: str, output_dir: str, save_raw: bool = True) -> dict | None:
    """Crawl một URL cụ thể bằng cách lắng nghe response API."""
    uuid = url.rstrip("/").split("/")[-1]
    captured_data = []

    def handle_response(response):
        if response.request.resource_type in ["xhr", "fetch"]:
            try:
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                    if "get-formality-by-citizen" in response.url or (uuid in response.url and "formality" in response.url):
                        captured_data.append(data)
            except Exception:
                pass

    page.on("response", handle_response)
    print(f"\n[*] Đang truy cập: {url}")

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"[!] Cảnh báo khi tải trang ({url}): {e}")

    # Bỏ lắng nghe handler này cho trang tiếp theo
    page.remove_listener("response", handle_response)

    if not captured_data:
        print(f"[-] Không bắt được API formality cho: {url}")
        return None

    raw_api_payload = captured_data[0]
    structured = map_api_to_schema(raw_api_payload, url)

    # 1. Lưu file JSON chuẩn hóa
    proc_id = structured["id"]
    clean_file = os.path.join(output_dir, f"{proc_id}.json")
    with open(clean_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    print(f"[+] Đã lưu file chuẩn hóa: {clean_file}")

    # 2. Lưu file RAW nếu cần đối chiếu
    if save_raw:
        raw_file = os.path.join(output_dir, f"RAW_{proc_id.replace('PROC_', '')}.json")
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_api_payload, f, ensure_ascii=False, indent=2)

    return structured


def run_crawler(url: str = None, seed_path: str = None, output_dir: str = "tests", save_raw: bool = True):
    """Điều phối crawl một URL hoặc toàn bộ danh sách từ file seed CSV."""
    os.makedirs(output_dir, exist_ok=True)

    urls_to_crawl = []
    if seed_path and os.path.exists(seed_path):
        with open(seed_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 3:
                    u = row[2].strip()
                    if u.startswith("http"):
                        urls_to_crawl.append(u)
    elif url:
        urls_to_crawl.append(url)

    if not urls_to_crawl:
        print("[-] Không có URL nào để crawl.")
        return

    print(f"[+] Tìm thấy {len(urls_to_crawl)} URL cần crawl...")

    with sync_playwright() as p:
        # Bắt buộc headless=False để vượt qua WAF Cloudflare/Bộ Thông tin của DVCQG
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for idx, u in enumerate(urls_to_crawl, 1):
            print(f"--- Tiến trình: [{idx}/{len(urls_to_crawl)}] ---")
            crawl_single_url(page, u, output_dir, save_raw=save_raw)

        browser.close()
        print("\n[✔] Hoàn thành toàn bộ quá trình crawl!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl dữ liệu thủ tục DVC Quốc gia qua API intercept.")
    parser.add_argument("--url", type=str, default=None, help="Crawl 1 URL thủ tục đơn lẻ")
    parser.add_argument("--seed", type=str, default="crawl/seed_procedures_urls.csv", help="Đường dẫn file seed CSV")
    parser.add_argument("--out", type=str, default="tests", help="Thư mục xuất file JSON")
    parser.add_argument("--no-raw", action="store_true", help="Không lưu file RAW API")
    args = parser.parse_args()

    run_crawler(
        url=args.url,
        seed_path=args.seed if not args.url else None,
        output_dir=args.out,
        save_raw=not args.no_raw
    )
