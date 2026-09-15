from playwright.sync_api import sync_playwright
import time
import json
import datetime
import re
import unicodedata

def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace('\u200e', '').replace('\u200f', '').replace('\u200b', '')
    cleaned = unicodedata.normalize('NFC', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()

def extract_div_table(page, heading_text):
    pattern = re.compile(f"^\s*{heading_text}\s*$", re.IGNORECASE)
    heading_locator = page.get_by_text(pattern)
    
    if heading_locator.count() == 0:
        print(f"Không tìm thấy tiêu đề bảng: {heading_text}")
        return []
        
    content_locator = heading_locator.first.locator("xpath=./following-sibling::div[1]")
    if content_locator.count() == 0:
        content_locator = heading_locator.first.locator("xpath=./parent::*/following-sibling::div[1]")
        
    if content_locator.count() == 0:
        print(f"Không tìm thấy khối chứa bảng của: {heading_text}")
        return []

    rows = content_locator.locator("xpath=.//div[contains(@class, 'md:flex-row')]")
    row_count = rows.count()
    if row_count == 0:
        rows = content_locator.locator("xpath=./div/div")
        row_count = rows.count()

    table_data = []
    for i in range(row_count):
        cells = rows.nth(i).locator("xpath=./div")
        cell_count = cells.count()
        
        if cell_count > 0:
            row_data = [cells.nth(j).inner_text().strip() for j in range(cell_count)]
            table_data.append(row_data)
    return table_data

def extract_general_info(page):
    general_info = {}
    grid_container = page.locator("div.grid.grid-cols-1.md\:grid-cols-2").first
    
    if grid_container.count() > 0:
        items = grid_container.locator("xpath=./div[contains(@class, 'flex')]")
        total = items.count()
        
        for i in range(total):
            item = items.nth(i)
            sub_divs = item.locator("xpath=./div")
            if sub_divs.count() >= 2:
                key = sub_divs.nth(0).inner_text().strip()
                val = sub_divs.nth(1).inner_text().strip()
                if key:
                    general_info[key] = val
                    
    return general_info

def extract_execution_methods(page):
    methods = []
    heading = page.locator("h4").filter(has_text=re.compile("Cách Thức Thực Hiện", re.IGNORECASE)).first
    
    if heading.count() == 0:
        return methods

    container = heading.locator("xpath=following-sibling::div[1]")
    if container.count() == 0:
        return methods

    raw_text = container.inner_text().strip()
    if not raw_text:
        return methods

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    data_lines = [l for l in lines if l not in ["Hình thức nộp", "Thời gian", "Phí, lệ phí", "Mô tả"]]

    known_methods = ["Trực tuyến", "Dịch vụ bưu chính", "Trực tiếp"]
    
    current_method = None
    for item in data_lines:
        if item in known_methods:
            current_method = {
                "method": item,
                "processing_time": "",
                "fee": "",
                "description": ""
            }
            methods.append(current_method)
        elif current_method:
            if not current_method["processing_time"]:
                current_method["processing_time"] = item
            elif not current_method["fee"]:
                current_method["fee"] = item
            elif not current_method["description"]:
                current_method["description"] = item

    return methods

def extract_steps(raw_text):
    if not raw_text:
        return []
    
    lines = [clean_text(line) for line in raw_text.split('\n')]
    
    steps_list = []
    
    current_chunk = ""
    
    for line in lines:
        if not line:
            continue

        if line.startswith("-"):
            if current_chunk:
                steps_list.append(current_chunk.strip())
            current_chunk = line
        else:
            if current_chunk:
                if line.startswith("+") or line.startswith("(i"):
                    current_chunk += "\n  " + line 
                else:
                    current_chunk += " " + line 
            else:
                current_chunk = line
    
    if current_chunk:
        steps_list.append(current_chunk.strip())
            
    return steps_list

def extract_notes(page):
    notes_list = []
    
    heading = page.locator("h5").filter(has_text=re.compile(r"\*?\s*Lưu ý", re.IGNORECASE)).first
    
    if heading.count() == 0:
        return notes_list

    container = heading.locator("xpath=following-sibling::div[1]")
    
    if container.count() == 0 or not container.inner_text().strip():
        container = heading.locator("xpath=./parent::*/following-sibling::div[1]")

    if container.count() > 0:
        raw_text = container.first.inner_text().strip()
        if raw_text:
            lines = [clean_text(l) for l in raw_text.split('\n') if l.strip()]
            
            current_note = ""
            for line in lines:
                if line.startswith(('-', '*', '•')):
                    if current_note:
                        notes_list.append(current_note.strip())
                    current_note = line
                else:
                    if current_note:
                        current_note += " " + line
                    else:
                        current_note = line
                        
            if current_note:
                notes_list.append(current_note.strip())

    return notes_list

def crawl(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            page.goto(url)
            page.wait_for_load_state("networkidle")
            time.sleep(2) 
            info_table = extract_general_info(page)

            raw_data = {}
            danh_sach_muc = [
                "Thủ tục hành chính liên quan",
                "Trình tự thực hiện", 
                "Căn cứ pháp lý", 
                "Cơ quan thực hiện",
                "Yêu cầu, điều kiện thực hiện",
                "Kết quả xử lý",
                "Từ khóa",
                "Mô tả"
            ]

            for muc in danh_sach_muc:
                try:
                    pattern = re.compile(f"^\s*{muc}\s*$", re.IGNORECASE)
                    heading_locator = page.get_by_text(pattern)
                    
                    if heading_locator.count() > 0:
                        noidung = ""
                        sibling_locator = heading_locator.first.locator("xpath=./following-sibling::*[1]")
                        if sibling_locator.count() > 0:
                            noidung = sibling_locator.first.inner_text().strip()
                        if not noidung:
                            parent_sibling = heading_locator.first.locator("xpath=./parent::*/following-sibling::*[1]")
                            if parent_sibling.count() > 0:
                                noidung = parent_sibling.first.inner_text().strip()
                        raw_data[muc] = noidung
                    else:
                        raw_data[muc] = None
                except Exception as e:
                    print(f"Lỗi khi bóc {muc}: {e}")

            bang_ho_so = extract_div_table(page, "Thành phần hồ sơ")
            execution_methods_list = extract_execution_methods(page)

            documents_list = []
            for row in bang_ho_so:
                if len(row) == 1 and "Tên giấy tờ" in row[0]:
                    raw_text = row[0]
                    
                    text_norm = re.sub(r'\n[\t ]+\n[\t ]+\n|\n[\t ]+\n|\t', '|', raw_text)
                    
                    row_parts = re.split(r'\n{2,}', text_norm)
                    
                    for part in row_parts:
                        if "Tên giấy tờ" in part or not part.strip():
                            continue 
                            
                        cols = [c.strip() for c in part.split('|') if c.strip()]
                        
                        if len(cols) > 0:
                            ten = cols[0]
                            sl = cols[-1] if len(cols) > 1 else ""
                            mau = cols[1] if len(cols) >= 3 else ""
                            
                            documents_list.append({
                                "ten_giay_to": clean_text(ten),
                                "so_luong": clean_text(sl)
                            })
                            
                elif len(row) >= 3 and row[0] != "Tên giấy tờ":
                    documents_list.append({
                        "ten_giay_to": row[0],
                        "so_luong": row[2]
                    })

            raw_target_audience = info_table.get("Đối tượng thực hiện", "")
            target_audience = [dt.strip() for dt in raw_target_audience.split(",") if dt.strip()]

            raw_steps_and_notes = raw_data.get("Trình tự thực hiện", "")
            steps_list = extract_steps(raw_steps_and_notes)
            notes_list = extract_notes(page)

            raw_id = info_table.get("Mã thủ tục", "")
            proc_id = f"PROC_{raw_id.replace('.', '_')}" if raw_id else "PROC_UNKNOWN"

            structured_json = {
                "id": proc_id,
                "national_code": raw_id,
                "life_event": ["sinh_con"],
                "target_audience": target_audience,
                "domain": info_table.get("Lĩnh vực", ""),
                "procedure_type": info_table.get("Loại thủ tục", ""),
                
                "procedure": {
                    "name": info_table.get("Tên thủ tục", raw_data.get("ten_thu_tuc", "")),
                    "eligibility": raw_data.get("Yêu cầu, điều kiện thực hiện", ""),
                    "documents": documents_list,
                    "steps": steps_list,
                    "notes": notes_list,
                    "authority": raw_data.get("Cơ quan thực hiện", ""),
                    "execution_methods": execution_methods_list,
                    "online_portal_url": url
                },

                "relations": {
                    "prerequisites": [],
                    "next_steps": [],
                    "related_benefits": []
                },

                "jurisdiction": {
                    "level": info_table.get("Cấp thực hiện", ""),
                    "location": "Toàn quốc"
                },

                "source": {
                    "name": "Cổng Dịch vụ công Quốc gia",
                    "url": url,
                    "effective_date": "",
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            }

            output_filename = f"{proc_id}.json"
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(structured_json, f, ensure_ascii=False, indent=4)
                
            print(f"\nĐã lưu thành công dữ liệu vào file: {output_filename}")

        except Exception as e:
            print(f"Lỗi toàn cục: {e}")
        finally:
            browser.close()
            print("Đã đóng trình duyệt.")

if __name__ == "__main__":
    test_url = "https://dichvucong.gov.vn/thu-tuc-hanh-chinh/019f9217-74e4-73e4-a228-bb4a73425e67"
    crawl(test_url)