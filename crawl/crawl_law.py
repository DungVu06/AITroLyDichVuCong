"""Thu thập metadata và nội dung văn bản pháp luật từ VBPL hoặc TVPL.

Với truy vấn VBPL, crawler chỉ chọn kết quả có trạng thái chính xác "Còn hiệu lực",
xếp theo ngày ban hành giảm dần và từ chối bản ghi parse section bị mất nội dung.
Trạng thái được đọc từ VBPL tại thời điểm crawl, không thay thế thẩm định pháp lý
hoặc kiểm tra hiệu lực của từng điều khoản.

Vi du (chay tu bat ky thu muc nao):
  python crawl/crawl_law.py --source vbpl --url 'https://vbpl.vn/...' --out data/law
  python crawl/crawl_law.py --source vbpl --query 'thuế thu nhập cá nhân' --limit 50
  python crawl/crawl_law.py --seed crawl/seed_law_urls.txt --out data/law --headed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlunparse

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ModuleNotFoundError:  # Allows data-only utilities to import this module.
    sync_playwright = None
    PlaywrightTimeoutError = TimeoutError


# Keep defaults independent of the current working directory. Explicit paths
# passed through CLI are still interpreted relative to the directory where the
# command is run, as is conventional for command-line tools.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def require_playwright() -> None:
    if sync_playwright is None:
        raise SystemExit(
            "Thiếu dependency Playwright. Cài bằng: "
            "python3 -m pip install playwright && python3 -m playwright install chromium"
        )


# Nhom chu de phap ly, tach khoi du lieu thu tuc hanh chinh.
LEGAL_TOPICS = {
    "thai_san_bhxh": ["thai sản", "thai san", "lao động nữ", "lao dong nu", "sinh con"],
    "tro_cap_sinh_con": ["trợ cấp", "tro cap", "dưỡng sức", "duong suc", "nuôi con nhỏ"],
    "bhyt_tre_em": ["bảo hiểm y tế", "bao hiem y te", "trẻ em dưới 6 tuổi", "the bhyt"],
    "khai_sinh": ["đăng ký khai sinh", "dang ky khai sinh", "giấy chứng sinh", "giay chung sinh"],
    "cu_tru_tre_em": ["đăng ký cư trú", "dang ky cu tru", "thường trú", "thuong tru", "tạm trú", "tam tru"],
    "quyen_loi_nguoi_me": ["nghỉ thai sản", "nghi thai san", "chế độ thai sản", "che do thai san"],
}


def clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\u200b", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def clean_legal_text(text: str) -> str:
    """Lam sach noi dung van ban nhung van giu nguyen y nghia phap ly."""
    lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.replace("\u00a0", " ").strip()
        # Bo bang Markdown rong/khong mang noi dung va dong phan cach.
        if re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?", line):
            continue
        if re.fullmatch(r"\|\s*\|?", line) or re.fullmatch(r"\*{3,}", line):
            continue
        line = re.sub(r"^\|\s*|\s*\|$", "", line)
        line = re.sub(r"\*{2,}", "", line)
        line = re.sub(r"(?<!\*)\*(?!\*)", "", line)
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)
    # Bo toan bo phan mo dau hanh chinh va dan nhap. Bat dau tu heading
    # phap ly dau tien, vi du: A. DOI TUONG, CHUONG I, MUC I, DIEU 1.
    body_start = None
    for index, line in enumerate(lines):
        if re.match(
            r"^(?:[A-ZĐ][\.\)\-–]\s+|CHƯƠNG\s+[IVXLCDM0-9]+|MỤC\s+[IVXLCDM0-9]+|Điều\s+\d+)\b",
            line,
            re.I,
        ):
            body_start = index
            break
    if body_start is not None and body_start > 0:
        lines = lines[body_start:]

    # Bo phan ky ten va noi nhan o cuoi van ban.
    end_markers = [r"^Nơi nhận\s*:", r"^Nơi nhận\s*:", r"^\(Đã ký\)\s*$"]
    for index, line in enumerate(lines):
        if any(re.search(marker, line, re.I) for marker in end_markers):
            lines = lines[:index]
            break

    # Giu xuong dong theo doan, loai dong trong lap lai.
    result = []
    previous_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue
        result.append(line)
        previous_blank = is_blank
    return "\n".join(result).strip()


CHAPTER_HEADING_RE = re.compile(r"^CHƯƠNG\s+[IVXLCDM0-9]+(?:[.:]?\s|$)", re.I)
NAMED_SECTION_HEADING_RE = re.compile(r"^MỤC\s+[IVXLCDM0-9]+(?:[.:]?\s|$)", re.I)
# Không dùng re.I và chỉ nhận I/V/X/L: nếu dùng re.I thì `c.`/`d.` bị
# hiểu nhầm là số La Mã; nếu nhận C/D thì `C.`/`D.` (phần lớn là part)
# cũng bị nhầm thành section.
ROMAN_SECTION_HEADING_RE = re.compile(r"^[IVXL]+[\.\)\-–]\s+.+")
ARTICLE_HEADING_RE = re.compile(r"^ĐIỀU\s+\d+(?:\s|[.:]|$)", re.I)
SUBSECTION_HEADING_RE = re.compile(r"^(?:TIỂU MỤC\s+\d+|KHOẢN\s+\d+|\d+)[\.\)\-–:]?\s+.+", re.I)
SUBPOINT_HEADING_RE = re.compile(r"^(?:[a-zđ]|\d+)\.\d+[\.\)]\s+.+")
# Không dùng re.I: `a.`/`b.` là point, còn `A.`/`B.` mới là part.
PART_HEADING_RE = re.compile(
    r"^(?:(?i:PHẦN)\s+[IVXLCDM0-9]+[.:]?|[A-HĐ][\.\)\-–])\s+.+"
)
POINT_HEADING_RE = re.compile(
    r"^(?:(?i:ĐIỂM)\s+[a-zđ]|[a-zđ])[\.\)\-–:]?\s+.+"
)


def classify_legal_heading(line: str) -> str | None:
    """Trả về cấp đề mục nếu cả dòng là một heading pháp lý.

    Heading chỉ được nhận ở đầu dòng. Cách này tránh tách nhầm `Điều 2`,
    `a)`... xuất hiện trong một câu dẫn chiếu ở phần nội dung.
    """
    line = (line or "").strip()
    if CHAPTER_HEADING_RE.match(line):
        return "chapter"
    if NAMED_SECTION_HEADING_RE.match(line) or ROMAN_SECTION_HEADING_RE.match(line):
        return "section"
    if ARTICLE_HEADING_RE.match(line):
        return "article"
    if SUBPOINT_HEADING_RE.match(line):
        return "subpoint"
    if SUBSECTION_HEADING_RE.match(line):
        return "subsection"
    if PART_HEADING_RE.match(line):
        return "part"
    if POINT_HEADING_RE.match(line):
        return "point"
    return None


def _quote_state_after_line(line: str, quote_stack: list[str], ascii_quote_open: bool) -> bool:
    quote_pairs = {"“": "”", "«": "»", "„": "”", "‘": "’"}
    for char in line:
        if char in quote_pairs:
            quote_stack.append(quote_pairs[char])
        elif quote_stack and char == quote_stack[-1]:
            quote_stack.pop()
    if line.count('"') % 2:
        ascii_quote_open = not ascii_quote_open
    return ascii_quote_open


def split_legal_sections(text: str) -> list[dict]:
    """Tách đề mục, giữ Điều/Khoản trong trích dẫn sửa đổi ở nội dung cha."""
    sections = []
    current = None
    quote_stack: list[str] = []
    ascii_quote_open = False
    in_amendment_quote = False
    pending_amendment_quote = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        starts_with_quote = line.startswith(('"', "“", "«", "„", "‘"))
        amendment_cue = re.search(
            r"(?:sửa đổi|bổ sung|thay thế).{0,160}(?:như sau|nội dung sau)",
            line,
            re.I,
        )
        if pending_amendment_quote and starts_with_quote:
            in_amendment_quote = True
            pending_amendment_quote = False
        elif pending_amendment_quote and not amendment_cue:
            pending_amendment_quote = False
        was_inside_quote = in_amendment_quote
        level = None if was_inside_quote else classify_legal_heading(line)
        if level:
            if current:
                current["text"] = "\n".join(current["_lines"]).strip()
                current["related_laws"] = extract_related_laws(current["text"])
                del current["_lines"]
                sections.append(current)
            current = {"heading": line, "level": level, "_lines": []}
        elif current:
            current["_lines"].append(line)
        if was_inside_quote:
            ascii_quote_open = _quote_state_after_line(line, quote_stack, ascii_quote_open)
            in_amendment_quote = bool(quote_stack) or ascii_quote_open
        elif amendment_cue:
            has_quote = any(mark in line for mark in ("\"", "“", "«", "„", "‘"))
            if has_quote:
                in_amendment_quote = True
                ascii_quote_open = _quote_state_after_line(line, quote_stack, False)
                in_amendment_quote = bool(quote_stack) or ascii_quote_open
            else:
                pending_amendment_quote = True
    if current:
        current["text"] = "\n".join(current["_lines"]).strip()
        current["related_laws"] = extract_related_laws(current["text"])
        del current["_lines"]
        sections.append(current)
    # Neu section khong co text thi van giu heading, tranh im lang lam mat
    # dieu/muc trong du lieu dau ra.
    return sections


def normalize_for_comparison(text: str) -> str:
    """Chuan hoa de so sanh noi dung, khong bi anh huong boi whitespace."""
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", text or "")).casefold()


def validate_section_split(full_text: str, sections: list[dict]) -> dict:
    """Kiem tra viec tach section co lam mat ky tu/noi dung hay khong."""
    reconstructed = "\n".join(
        "\n".join(item for item in (section.get("heading", ""), section.get("text", "")) if item)
        for section in sections
    )
    original_normalized = normalize_for_comparison(full_text)
    reconstructed_normalized = normalize_for_comparison(reconstructed)
    return {
        "is_lossless": original_normalized == reconstructed_normalized,
        "full_text_length": len(full_text),
        "reconstructed_length": len(reconstructed),
        "section_count": len(sections),
    }


def extract_related_laws(text: str) -> list[dict]:
    """Phat hien van ban duoc dan chieu trong pham vi mot section."""
    pattern = re.compile(
        r"(?P<kind>Luật|Bộ luật|Pháp lệnh|Nghị định|Thông tư liên tịch|Thông tư|"
        r"Quyết định|Nghị quyết|Chỉ thị)\s+"
        # So hieu phai bat dau bang chu so; tranh bat nham "Thong tu nay".
        r"(?:số\s+)?(?P<number>\d[0-9A-Za-zÀ-ỹ./-]*)"
        r"(?:\s+ngày\s+(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}))?",
        re.I,
    )
    relations = []
    seen = set()
    for match in pattern.finditer(text):
        kind = clean(match.group("kind"))
        number = clean(match.group("number"))
        date = clean(match.group("date") or "")
        key = (kind.casefold(), number.casefold(), date)
        if key in seen:
            continue
        seen.add(key)
        context_raw = text[max(0, match.start() - 160):match.start()]
        context = context_raw.casefold()
        referenced_location = extract_reference_location(context_raw)
        if "sửa đổi" in context or "bổ sung" in context:
            relation_type = "sửa_đổi_bổ_sung"
        # "... quy dinh trai voi Thong tu X ... deu bai bo" khong co nghia
        # la ban than Thong tu X bi bai bo; day chi la dan chieu.
        elif "trái với" in context or "trái với" in context:
            relation_type = "dẫn_chiếu"
        elif re.search(r"bãi bỏ\s*$", context):
            relation_type = "bãi_bỏ"
        elif "căn cứ" in context:
            relation_type = "căn_cứ"
        elif "thay thế" in context:
            relation_type = "thay_thế"
        else:
            relation_type = "dẫn_chiếu"
        relation = {
            "document_type": normalize_document_type(kind),
            "document_number": number,
            "issued_date_raw": date,
            "relation_type": relation_type,
        }
        if referenced_location:
            relation["referenced_location"] = referenced_location
        relations.append(relation)
    return relations


def extract_reference_location(context: str) -> str:
    """Lay pham vi duoc dan chieu, vi du 'muc A' hay 'khoan 1 Dieu 2'."""
    unit = (
        r"(?:điểm\s+[a-zđ]|khoản\s+\d+|mục\s+(?:[a-zđ]|\d+)|"
        r"chương\s+[ivxlcdm0-9]+|điều\s+\d+)"
    )
    location_pattern = re.compile(
        rf"(?P<location>{unit}(?:\s*(?:,|và)?\s*{unit}){{0,5}})"
        r"(?:\s+của)?\s*$",
        re.I,
    )
    matches = list(location_pattern.finditer(context))
    if not matches:
        return ""
    location = clean(matches[-1].group("location"))
    return location


def slug_id(url: str, title: str) -> str:
    value = re.search(r"(?:ItemID|id)[=/](\d+)", url, re.I)
    if value:
        return f"LAW_VBPL_{value.group(1)}"
    return "LAW_VBPL_" + hashlib.sha1((url + title).encode()).hexdigest()[:16]


def find_value(text: str, labels: list[str]) -> str:
    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]?\s*([^|\n]+)", text, re.I)
        if match:
            return clean(match.group(1))
    return ""


def find_attribute_value(text: str, label: str, all_labels: list[str]) -> str:
    """Lay mot gia tri trong tab Thuoc tinh, noi cac cap nam tren cung dong."""
    label_folded = clean(label).casefold()
    next_label_values = [
        item for item in all_labels
        if clean(item).casefold() != label_folded
        and not label_folded.endswith(clean(item).casefold())
    ]
    next_label_values.sort(key=len, reverse=True)
    next_labels = "|".join(re.escape(item) for item in next_label_values)
    next_boundary = rf"(?=\s+(?:{next_labels})\s*[:：]?|$)" if next_labels else r"(?=$)"
    pattern = rf"{re.escape(label)}(?!\w)\s*[:：]?\s*(.*?){next_boundary}"
    match = re.search(pattern, text, re.I)
    return clean(match.group(1)) if match else ""


def normalize_document_type(value: str) -> str:
    """Chi giu ten loai van ban, bo phan nganh/lai mo ta phia sau."""
    known_types = [
        "Hiến pháp", "Luật", "Bộ luật", "Nghị quyết", "Nghị định",
        "Quyết định", "Thông tư liên tịch", "Thông tư", "Chỉ thị",
        "Pháp lệnh", "Lệnh", "Công văn",
    ]
    value = clean(value)
    for item in sorted(known_types, key=len, reverse=True):
        if value.casefold().startswith(item.casefold()):
            return item
    return value


def tab_url(url: str, tab: str) -> str:
    """Tao URL tab theo co che tabs=... cua vbpl.vn."""
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["tabs"] = tab
    return urlunparse(parsed._replace(query=urlencode(query)))


def parse_vietnamese_date(value: str) -> date | None:
    """Parse ngày hiển thị phổ biến trên VBPL để lọc và xếp hạng."""
    text = clean(value)
    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if not match:
        match = re.search(
            r"(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
            text,
            re.I,
        )
    if match:
        day, month, year = map(int, match.groups())
    else:
        iso_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
        if not iso_match:
            return None
        year, month, day = map(int, iso_match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _wait_for_vbpl_document(page) -> None:
    try:
        page.wait_for_function(
            """() => { const t = document.body?.innerText || ''; return t.length > 300 && !t.includes('Đang tải dữ liệu...'); }""",
            timeout=60000,
        )
    except PlaywrightTimeoutError as exc:
        raise RuntimeError("VBPL chưa trả về thuộc tính văn bản (API có thể bị chặn hoặc đang lỗi).") from exc


def extract_vbpl_attributes(page, url: str) -> dict:
    """Đọc thuộc tính pháp lý trước khi quyết định tải toàn văn."""
    _wait_for_vbpl_document(page)
    open_tab(page, url, "thuoc-tinh")
    attributes_text = active_panel_text(page)
    labels = [
        "Loại văn bản", "Nhóm văn bản", "Số hiệu", "Trích yếu",
        "Ngày ban hành", "Lĩnh vực", "Ngày có hiệu lực", "Ngày hiệu lực",
        "Tình trạng hiệu lực", "Hiệu lực", "Ngày hết hiệu lực",
        "Ngày hết hiệu lực toàn bộ", "Cơ quan ban hành", "Chức danh", "Người ký",
    ]
    title = ""
    for heading in page.locator("h1, h2").all():
        candidate = clean(heading.inner_text())
        if len(candidate) > 20 and candidate not in ("Nội dung", "Thuộc tính"):
            title = candidate
            break
    return {
        "title": title,
        "document_number": find_attribute_value(attributes_text, "Số hiệu", labels),
        "issued_date_raw": find_attribute_value(attributes_text, "Ngày ban hành", labels),
        "effective_date_raw": (
            find_attribute_value(attributes_text, "Ngày có hiệu lực", labels)
            or find_attribute_value(attributes_text, "Ngày hiệu lực", labels)
        ),
        "expired_date_raw": (
            find_attribute_value(attributes_text, "Ngày hết hiệu lực toàn bộ", labels)
            or find_attribute_value(attributes_text, "Ngày hết hiệu lực", labels)
        ),
        "issuing_authority": find_attribute_value(attributes_text, "Cơ quan ban hành", labels),
        "document_type": normalize_document_type(
            find_attribute_value(attributes_text, "Loại văn bản", labels)
        ),
        "validity_raw": find_attribute_value(attributes_text, "Tình trạng hiệu lực", labels),
    }


def _eligible_vbpl_candidate(attributes: dict) -> tuple[bool, str, date | None]:
    status = clean(attributes.get("validity_raw", "")).casefold().rstrip(".")
    if not status:
        return False, "không đọc được tình trạng hiệu lực", None
    if status != "còn hiệu lực":
        return False, "trạng thái không phải 'Còn hiệu lực'", None
    issue_date = parse_vietnamese_date(attributes.get("issued_date_raw", ""))
    if issue_date is None:
        return False, "thiếu hoặc không đọc được ngày ban hành", None
    today = date.today()
    if issue_date > today:
        return False, "ngày ban hành ở tương lai", issue_date
    effective_date = parse_vietnamese_date(attributes.get("effective_date_raw", ""))
    if effective_date and effective_date > today:
        return False, "ngày có hiệu lực còn ở tương lai", issue_date
    expired_date = parse_vietnamese_date(attributes.get("expired_date_raw", ""))
    if expired_date and expired_date <= today:
        return False, "đã đến ngày hết hiệu lực", issue_date
    return True, "đủ điều kiện", issue_date


def _candidate_metadata_uncertain(attributes: dict) -> bool:
    status = clean(attributes.get("validity_raw", "")).casefold().rstrip(".")
    if not status:
        return True
    if status != "còn hiệu lực":
        return False
    today = date.today()
    issue_date = parse_vietnamese_date(attributes.get("issued_date_raw", ""))
    effective_date = parse_vietnamese_date(attributes.get("effective_date_raw", ""))
    expired_date = parse_vietnamese_date(attributes.get("expired_date_raw", ""))
    return (
        issue_date is None or issue_date > today
        or bool(effective_date and effective_date > today)
        or bool(expired_date and expired_date <= today)
    )


def _click_with_overlay_fallback(locator) -> None:
    """Click bình thường trước, dùng DOM click nếu popup phủ trang chặn pointer."""
    try:
        locator.click(timeout=2500)
    except PlaywrightTimeoutError:
        locator.evaluate("el => el.click()")


def open_tab(page, url: str, tab: str) -> None:
    # Tab du lieu that la Ant Design role=tab; tranh click vao menu div phia tren.
    tab_labels = {"thuoc-tinh": "Thuộc tính", "toan-van": "Nội dung"}
    label = tab_labels[tab]
    real_tab = page.get_by_role("tab", name=label, exact=True).first
    if real_tab.count() == 0:
        page.goto(tab_url(url, tab), wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        real_tab = page.get_by_role("tab", name=label, exact=True).first
    if real_tab.count() == 0:
        raise RuntimeError(f"Khong tim thay tab du lieu: {label}")
    _click_with_overlay_fallback(real_tab)
    panel_id = real_tab.get_attribute("aria-controls")
    page.wait_for_function(
        """(id) => {
            const tab = document.querySelector(`[role="tab"][aria-controls="${id}"]`);
            const panel = document.getElementById(id);
            return tab?.getAttribute('aria-selected') === 'true' && !!panel && panel.innerText.trim().length > 0;
        }""",
        arg=panel_id,
        timeout=60000,
    )
    page.wait_for_timeout(1000)


def active_panel_text(page) -> str:
    panel = page.locator('[role="tabpanel"][aria-hidden="false"]').first
    if panel.count() > 0:
        raw = panel.inner_text(timeout=15000)
    else:
        raw = page.locator("body").inner_text(timeout=15000)
    raw = unicodedata.normalize("NFC", raw or "").replace("\u00a0", " ")
    return "\n".join(re.sub(r"[ \t]+", " ", line).strip()
                       for line in raw.splitlines())


def extract(page, url: str, attributes: dict | None = None) -> dict:
    # Trang chi tiet la Next.js: HTML ban dau chi co skeleton, noi dung den tu API.
    _wait_for_vbpl_document(page)
    attributes = attributes or extract_vbpl_attributes(page, url)
    title = attributes.get("title") or clean(page.title())

    # Mở trực tiếp tab Nội dung bằng query tabs=toan-van.
    open_tab(page, url, "toan-van")
    content_text = clean_legal_text(active_panel_text(page))
    sections = split_legal_sections(content_text)
    section_validation = validate_section_split(content_text, sections)
    if not sections or not section_validation["is_lossless"]:
        raise RuntimeError(
            "Không lưu văn bản vì tách đề mục làm mất hoặc gộp nội dung "
            f"({section_validation['full_text_length']} -> {section_validation['reconstructed_length']} ký tự)."
        )
    links = []
    for a in page.locator("a").all():
        href = a.get_attribute("href")
        if href and (href.lower().endswith((".pdf", ".doc", ".docx")) or "download" in href.lower()):
            links.append(urljoin(url, href))
    folded = content_text.casefold()
    is_birth_related = any(term in folded for terms in LEGAL_TOPICS.values() for term in terms)
    record_id = slug_id(url, title)
    issued_date = parse_vietnamese_date(attributes.get("issued_date_raw", ""))
    effective_date = parse_vietnamese_date(attributes.get("effective_date_raw", ""))
    return {
        "id": record_id,
        "life_event": ["sinh_con"] if is_birth_related else [],
        "domain": "Pháp luật",
        "jurisdiction": {"level": "Toàn quốc", "location": "Việt Nam"},
        "source": {
            "name": "Cơ sở dữ liệu quốc gia về văn bản pháp luật",
            "url": url,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        },
        "relations": {"related_laws": [], "related_procedures": []},
        "content": {
            "title": title,
            "document_type": attributes.get("document_type", ""),
            "document_number": attributes.get("document_number", ""),
            "issuing_authority": attributes.get("issuing_authority", ""),
            "issued_date_raw": attributes.get("issued_date_raw", ""),
            "issued_date": issued_date.isoformat() if issued_date else None,
            "effective_date_raw": attributes.get("effective_date_raw", ""),
            "effective_date": effective_date.isoformat() if effective_date else None,
            "expired_date_raw": attributes.get("expired_date_raw", ""),
            "validity_raw": attributes.get("validity_raw", ""),
            "validity_checked_at": datetime.now(timezone.utc).isoformat(),
            "section_validation": section_validation,
            "full_text": content_text,
            "sections": sections,
            "attachments": sorted(set(links)),
        },
    }


VBPL_HOME_URL = "https://vbpl.vn/"
VBPL_SEARCH_METADATA: dict[str, dict] = {}


def _vbpl_search_fold(value: str) -> str:
    value = unicodedata.normalize("NFD", clean(value).casefold())
    return " ".join("".join(ch for ch in value if unicodedata.category(ch) != "Mn").split())


def _vbpl_detail_url(item: dict) -> str:
    item_id = str(item.get("id") or "").strip()
    if not item_id:
        return ""
    title = clean(item.get("title") or "van-ban")
    slug = unicodedata.normalize("NFD", title.casefold())
    slug = "".join(ch for ch in slug if unicodedata.category(ch) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-") or "van-ban"
    return f"https://vbpl.vn/van-ban/chi-tiet/{slug}--{item_id}"


def _vbpl_result_attributes(text: str) -> dict:
    """Read status and dates already shown in each VBPL result card."""
    labels = r"(?:Trạng thái|Ngày ban hành|Ngày hiệu lực|Ngày hết hiệu lực)"

    def field(label: str) -> str:
        match = re.search(
            rf"{label}\s*:\s*(.*?)(?=\s*(?:{labels})\s*:|$)",
            clean(text),
            re.I,
        )
        return clean(match.group(1)) if match else ""

    return {
        "validity_raw": field("Trạng thái"),
        "issued_date_raw": field("Ngày ban hành"),
        "effective_date_raw": field("Ngày hiệu lực"),
        "expired_date_raw": field("Ngày hết hiệu lực"),
    }


def _select_vbpl_full_text_mode(page) -> None:
    pattern = re.compile(r"nội\s*dung\s*toàn\s*văn|toàn\s*văn", re.I)
    for label in page.locator("label").all():
        if not pattern.search(clean(label.inner_text())):
            continue
        controls = label.locator("input[type=radio], input[type=checkbox]")
        if controls.count():
            control = controls.first
            if not control.is_checked():
                control.evaluate("el => el.click()")
            if control.is_checked():
                return
        _click_with_overlay_fallback(label)
        selected = label.evaluate(
            "el => el.getAttribute('aria-checked') === 'true' || "
            "el.className.toString().includes('checked') || "
            "!!el.querySelector('input:checked')"
        )
        if selected:
            return

    for control in page.locator("input[type=radio], input[type=checkbox]").all():
        context = control.evaluate(
            "el => [el.labels ? [...el.labels].map(x => x.innerText).join(' ') : '', "
            "el.parentElement?.innerText || '', el.parentElement?.parentElement?.innerText || ''].join(' ')"
        )
        if pattern.search(clean(context)):
            if not control.is_checked():
                control.evaluate("el => el.click()")
            if control.is_checked():
                return

    for select in page.locator("select").all():
        for option in select.locator("option").all():
            label = clean(option.inner_text())
            if pattern.search(label):
                select.select_option(value=option.get_attribute("value"))
                return

    controls = page.locator("label, input[type=radio], input[type=checkbox], select").evaluate_all(
        "els => els.map(el => (el.innerText || el.labels?.[0]?.innerText || el.value || '').trim()).filter(Boolean)"
    )
    raise RuntimeError(
        "Không tìm thấy lựa chọn 'Nội dung toàn văn' trên trang chủ VBPL. "
        f"URL={page.url}; lựa chọn tìm kiếm thấy được={controls[:20]}"
    )


def _reject_vbpl_optional_cookies(page) -> None:
    """Dismiss the VBPL cookie notice using its explicit reject control."""
    for control in page.locator("button, [role=button], a").all():
        label = _vbpl_search_fold(" ".join(filter(None, [
            control.inner_text(), control.get_attribute("aria-label"), control.get_attribute("title")
        ])))
        if label == "tu choi" and control.is_visible():
            print("[VBPL] Hộp cookie: chọn 'Từ chối'.", flush=True)
            _click_with_overlay_fallback(control)
            page.wait_for_timeout(400)
            return


def _vbpl_search_result_urls(page) -> list[str]:
    candidates = []
    for anchor in page.locator("a[href]").all():
        href = anchor.get_attribute("href")
        if not href:
            continue
        absolute = urljoin(page.url, href).split("#", 1)[0]
        parsed = urlparse(absolute)
        host = (parsed.hostname or "").casefold()
        path = parsed.path.casefold()
        params = {key.casefold(): value for key, value in parse_qsl(parsed.query)}
        item_id = next((params[key] for key in ("itemid", "id") if params.get(key)), "")
        if host != "vbpl.vn" and not host.endswith(".vbpl.vn"):
            continue
        row_text = ""
        row = anchor.locator("xpath=ancestor::li[1]")
        if row.count():
            row_text = row.inner_text()
        row_attributes = _vbpl_result_attributes(row_text)
        row_status = row_attributes.get("validity_raw", "").casefold()
        if row_status:
            if row_status != "còn hiệu lực":
                continue
        if item_id and re.search(r"vbpq-(?:toanvan|vanban|chitiet)", path):
            title = clean(anchor.inner_text())
            url = _vbpl_detail_url({"id": item_id, "title": title})
            if url:
                candidates.append(url)
                if row_status:
                    VBPL_SEARCH_METADATA[url] = row_attributes
        elif "/van-ban/chi-tiet/" in path:
            url = _canonical_url(absolute, "vbpl")
            candidates.append(url)
            if row_status:
                VBPL_SEARCH_METADATA[url] = row_attributes
    return list(dict.fromkeys(candidates))


def _vbpl_result_cards(page):
    """Current VBPL renders search results as clickable list items, not links."""
    return (
        page.locator("li")
        .filter(has_text=re.compile(r"Trạng thái\s*:", re.I))
        .filter(has_text=re.compile(r"Ngày ban hành\s*:", re.I))
    )


def _vbpl_result_card_urls(page) -> list[str]:
    """Open non-anchor result cards to learn their canonical detail URLs.

    The current VBPL React UI attaches navigation to result cards and leaves
    the title as plain text, so there is no href for the normal link scanner.
    Clicking a card lets the site's own router or a new tab supply the
    document ID and slug.
    """
    urls = []
    cards = _vbpl_result_cards(page)
    card_count = cards.count()
    for index in range(card_count):
        card = _vbpl_result_cards(page).nth(index)
        card_attributes = _vbpl_result_attributes(card.inner_text())
        if card_attributes["validity_raw"].casefold() != "còn hiệu lực":
            continue
        before_url = page.url
        title = card.evaluate(
            """el => {
                const text = node => (node.innerText || '').trim();
                const leaves = [...el.querySelectorAll('*')].filter(node =>
                    node.children.length === 0 && text(node).length > 20 &&
                    !/^(PDF|Lược đồ|Tải về|Trạng thái|Ngày ban hành|Ngày hiệu lực)/i.test(text(node))
                );
                return (leaves[0] ? text(leaves[0]) : text(el)).slice(0, 180);
            }"""
        )
        click_target = card.evaluate(
            """(el, titleText) => {
                const text = node => (node.innerText || '').trim();
                const leaf = [...el.querySelectorAll('*')].find(node =>
                    node.children.length === 0 && text(node).length > 20 &&
                    titleText.startsWith(text(node).slice(0, 100))
                );
                const start = leaf || el;
                const chain = [];
                for (let node = start; node; node = node.parentElement) {
                    chain.push(node);
                    if (node === el) break;
                }
                const propsFor = node => {
                    const key = Object.keys(node).find(name => name.startsWith('__reactProps$'));
                    return key ? node[key] : null;
                };
                const clickable = chain.find(node => {
                    const props = propsFor(node);
                    const style = getComputedStyle(node);
                    const label = text(node);
                    return !/^(PDF|Lược đồ|Tải về|Văn bản hợp nhất)$/i.test(label) &&
                        (typeof props?.onClick === 'function' || typeof node.onclick === 'function' ||
                         node.matches('a,button,[role="link"],[role="button"],[onclick]') ||
                         style.cursor === 'pointer');
                });
                const target = clickable || start;
                document.querySelectorAll('[data-vbpl-crawl-target]').forEach(node =>
                    node.removeAttribute('data-vbpl-crawl-target'));
                target.setAttribute('data-vbpl-crawl-target', '1');
                const props = propsFor(target);
                return {
                    tag: target.tagName, className: String(target.className || '').slice(0, 120),
                    text: text(target).slice(0, 120),
                    hasReactClick: typeof props?.onClick === 'function',
                    hasDomClick: typeof target.onclick === 'function',
                    cursor: getComputedStyle(target).cursor
                };
            }""",
            title,
        )
        opened_popups = []
        on_popup = lambda popup: opened_popups.append(popup)
        page.on("popup", on_popup)
        print(
            f"[VBPL] Thử mở kết quả {index + 1}/{card_count}: {title[:100]} "
            f"(target={click_target}).",
            flush=True,
        )
        try:
            target = page.locator('[data-vbpl-crawl-target="1"]').first
            try:
                target.click(timeout=1500)
            except PlaywrightTimeoutError:
                pass
            if not opened_popups and page.url == before_url:
                try:
                    page.wait_for_function(
                        "before => location.href !== before",
                        arg=before_url,
                        timeout=800,
                    )
                except PlaywrightTimeoutError:
                    pass
            if not opened_popups and page.url == before_url:
                try:
                    card.click(timeout=1200)
                except PlaywrightTimeoutError:
                    pass
            if not opened_popups and page.url == before_url:
                page.wait_for_function(
                    "before => location.href !== before",
                    arg=before_url,
                    timeout=1200,
                )
        except PlaywrightTimeoutError:
            print(
                f"[VBPL] Bấm kết quả không tạo URL mới hoặc popup; URL vẫn là {page.url}.",
                flush=True,
            )
            continue
        finally:
            page.remove_listener("popup", on_popup)

        popup = opened_popups[0] if opened_popups else None
        if popup:
            try:
                popup.wait_for_url(
                    re.compile(r"^https?://(?:[^/]+\.)?vbpl\.vn/"), timeout=15000
                )
                popup.wait_for_load_state("domcontentloaded", timeout=15000)
            except PlaywrightTimeoutError:
                pass
        detail_page = popup or page
        current_url = detail_page.url
        print(
            f"[VBPL] Điều hướng kết quả qua {'tab mới' if popup else 'tab hiện tại'}: {current_url}",
            flush=True,
        )
        parsed = urlparse(current_url)
        if (parsed.hostname or "").casefold().endswith("vbpl.vn") and (
            "/van-ban/chi-tiet/" in parsed.path.casefold()
            or re.search(r"/pages/i?vbpq-(?:toanvan|vanban|chitiet)\.aspx$", parsed.path, re.I)
        ):
            canonical_url = _canonical_url(current_url, "vbpl")
            urls.append(canonical_url)
            VBPL_SEARCH_METADATA[canonical_url] = card_attributes
            print(f"[VBPL] Lấy URL chi tiết từ mục kết quả: {title[:100]} -> {urls[-1]}", flush=True)

        if popup:
            popup.close()
        elif current_url != before_url:
            try:
                page.go_back(wait_until="domcontentloaded", timeout=15000)
            except PlaywrightTimeoutError:
                page.go_back(timeout=15000)
            page.wait_for_function(
                """() => [...document.querySelectorAll('li')].some(el =>
                    /Trạng thái\\s*:/i.test(el.innerText) && /Ngày ban hành\\s*:/i.test(el.innerText))""",
                timeout=20000,
            )
    return list(dict.fromkeys(urls))


def discover_urls(
    page, query: str, max_pages: int = 1000, target_candidates: int | None = None
) -> list[str]:
    """Search from the vbpl.vn home page with the full-text option selected."""
    print(f"[{query}] Mở trang chủ VBPL và chờ form tìm kiếm...", flush=True)
    page.goto(VBPL_HOME_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function(
        """() => document.querySelectorAll('input').length > 0 && (document.body?.innerText || '').length > 100""",
        timeout=30000,
    )
    page.wait_for_timeout(1000)
    _reject_vbpl_optional_cookies(page)
    _select_vbpl_full_text_mode(page)

    search_box = None
    for control in page.locator("input").all():
        input_type = (control.get_attribute("type") or "text").casefold()
        attrs = " ".join(filter(None, [
            control.get_attribute(name)
            for name in ("name", "id", "placeholder", "aria-label", "title")
        ])).casefold()
        if input_type in {"text", "search"} and control.is_visible() and any(
            token in attrs for token in ("keyword", "search", "từ khóa", "tu khoa", "tìm kiếm", "tim kiem")
        ):
            search_box = control
            break
    if search_box is None:
        search_box = next((
            control for control in page.locator("input").all()
            if (control.get_attribute("type") or "text").casefold() in {"text", "search"}
            and control.is_visible()
        ), None)
    if search_box is None:
        raise RuntimeError(f"Không tìm thấy ô từ khóa trên trang chủ VBPL ({page.url}).")

    search_box.fill(query)
    input_info = search_box.evaluate(
        "el => ({tag: el.tagName, id: el.id, name: el.name, placeholder: el.placeholder, value: el.value})"
    )
    print(f"[{query}] Đã nhập từ khóa vào ô: {input_info}.", flush=True)
    search_button = None
    for control in page.locator(
        "button, input[type=submit], input[type=button], [role=button], .ant-btn"
    ).all():
        label = _vbpl_search_fold(" ".join(filter(None, [
            control.inner_text(), control.get_attribute("value"), control.get_attribute("aria-label"),
            control.get_attribute("title"),
        ])))
        if label == "tim kiem":
            search_button = control
            break
    print(f"[{query}] Đã chọn 'Nội dung toàn văn', gửi từ khóa tìm kiếm...", flush=True)
    search_requests = []

    def log_search_request(request):
        parsed_request_url = urlparse(request.url)
        request_host = (parsed_request_url.hostname or "").casefold()
        if request.resource_type in {"xhr", "fetch", "document"} and (
            request_host == "vbpl.vn" or request_host.endswith(".vbpl.vn")
            or request_host.endswith(".moj.gov.vn")
        ):
            request_summary = f"{request.method} {request_host}{parsed_request_url.path}"
            search_requests.append(request_summary)
            print(f"[{query}] Request tìm kiếm: {request_summary}", flush=True)

    def log_search_response(response):
        request = response.request
        parsed_response_url = urlparse(response.url)
        response_host = (parsed_response_url.hostname or "").casefold()
        if request.resource_type in {"xhr", "fetch", "document"} and (
            response_host == "vbpl.vn" or response_host.endswith(".vbpl.vn")
            or response_host.endswith(".moj.gov.vn")
        ):
            response_summary = f"HTTP {response.status} {request.method} {response_host}{parsed_response_url.path}"
            print(f"[{query}] Phản hồi tìm kiếm: {response_summary}.", flush=True)
            if response.status >= 400:
                try:
                    print(f"[{query}] Nội dung lỗi API: {response.text()[:500]}", flush=True)
                except Exception:
                    pass

    page.on("request", log_search_request)
    page.on("response", log_search_response)
    if search_button is not None:
        print(f"[{query}] Bấm nút Tìm kiếm ({search_button.evaluate('el => el.tagName + "." + el.className')}).", flush=True)
        _click_with_overlay_fallback(search_button)
    else:
        submitted_form = search_box.evaluate(
            """el => {
                const form = el.form || el.closest('form');
                if (!form || !form.requestSubmit) return false;
                form.requestSubmit();
                return true;
            }"""
        )
        clicked_custom_control = False
        if submitted_form:
            print(f"[{query}] Gửi form tìm kiếm từ ô từ khóa.", flush=True)
        exact_text = page.get_by_text("Tìm kiếm", exact=True)
        if not submitted_form:
            for match in exact_text.all():
                if not match.is_visible():
                    continue
                if match.evaluate("el => !!el.closest('a')"):
                    continue
                match.evaluate(
                    """el => {
                        let node = el;
                        while (node && node !== document.body) {
                            const style = getComputedStyle(node);
                            if (node.matches('button,[role="button"],a,[onclick],.ant-btn') || style.cursor === 'pointer') {
                                node.click();
                                return;
                            }
                            node = node.parentElement;
                        }
                        el.click();
                    }"""
                )
                clicked_custom_control = True
                print(f"[{query}] Bấm phần tử giao diện có chữ Tìm kiếm.", flush=True)
                break
            if not clicked_custom_control:
                print(f"[{query}] Không thấy nút/form; gửi Enter từ ô từ khóa.", flush=True)
                search_box.press("Enter")
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except PlaywrightTimeoutError:
        pass
    try:
        page.wait_for_function(
            """() => {
                const text = document.body?.innerText || '';
                const hasDocLinks = !!document.querySelector('a[href*="/van-ban/chi-tiet/"]');
                const hasResultCards = [...document.querySelectorAll('li')].some(el =>
                    /Trạng thái\\s*:/i.test(el.innerText) && /Ngày ban hành\\s*:/i.test(el.innerText));
                const hasSearchStatus = /không\\s+(?:tìm\\s+thấy|có)\\s+(?:kết\\s+quả|văn\\s+bản)|tìm\\s+thấy\\s+\\d+\\s+văn\\s+bản/i.test(text);
                return hasDocLinks || hasResultCards || hasSearchStatus;
            }""",
            timeout=20000,
        )
    except PlaywrightTimeoutError:
        pass
    page.remove_listener("request", log_search_request)
    page.remove_listener("response", log_search_response)
    page.wait_for_timeout(700)
    if not search_requests:
        print(f"[{query}] Không thấy request tìm kiếm nào phát sinh từ giao diện.", flush=True)

    found = []
    seen_pages = set()
    for page_number in range(1, max_pages + 1):
        current_urls = _vbpl_search_result_urls(page)
        card_count = _vbpl_result_cards(page).count()
        if not current_urls and card_count:
            print(
                f"[{query}] Tìm thấy {card_count} mục; chỉ mở mục còn hiệu lực để lấy URL...",
                flush=True,
            )
            current_urls = _vbpl_result_card_urls(page)
        body_text = clean(page.locator("body").inner_text())
        if not current_urls and not found and not card_count:
            if re.search("kh\u00f4ng\\s+(?:t\u00ecm\\s+th\u1ea5y|c\u00f3)\\s+(?:k\u1ebft\\s+qu\u1ea3|v\u0103n\\s+b\u1ea3n)|0\\s+(?:k\u1ebft\\s+qu\u1ea3|v\u0103n\\s+b\u1ea3n)", body_text, re.I):
                print(f"[{query}] VBPL search returned zero full-text results.", flush=True)
                return []
            diagnostics = page.evaluate("""() => {
                const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                const inputs = [...document.querySelectorAll('input')].filter(visible).map(el => ({
                    type: el.type, id: el.id, name: el.name, placeholder: el.placeholder,
                    value: el.value, context: (el.parentElement?.innerText || '').trim().slice(0, 100)
                }));
                const actions = [...document.querySelectorAll('button,[role="button"],input[type="submit"],a')]
                    .filter(visible).map(el => ({
                        tag: el.tagName, text: (el.innerText || el.value || '').trim().slice(0, 80),
                        aria: el.getAttribute('aria-label'), title: el.title, href: el.href || ''
                    }));
                const docLinks = [...document.querySelectorAll('a[href]')].map(a => ({
                    text: (a.innerText || '').trim().slice(0, 100), href: a.href
                })).filter(a => /van-ban\\/chi-tiet|vbpq-(toanvan|vanban|chitiet)|ItemID=/i.test(a.href));
                const resultItems = [...document.querySelectorAll('li')]
                    .filter(el => /Trạng thái\\s*:/i.test(el.innerText) && /Ngày ban hành\\s*:/i.test(el.innerText))
                    .slice(0, 3).map(item => {
                        const nodes = [item, ...item.querySelectorAll('*')];
                        const attrs = el => Object.fromEntries([...el.attributes]
                            .filter(a => /^(id|class|role|href|title|tabindex|data-|aria-)/i.test(a.name))
                            .map(a => [a.name, a.value]).slice(0, 20));
                        const targets = nodes.map(el => {
                            const propsKey = Object.keys(el).find(key => key.startsWith('__reactProps$'));
                            const props = propsKey ? el[propsKey] : null;
                            const fiberKey = Object.keys(el).find(key => key.startsWith('__reactFiber$'));
                            const fiberProps = fiberKey ? el[fiberKey]?.memoizedProps : null;
                            const handlers = [props?.onClick, fiberProps?.onClick]
                                .filter(value => typeof value === 'function')
                                .map(fn => String(fn).slice(0, 360));
                            const style = getComputedStyle(el);
                            return {
                                tag: el.tagName, text: (el.innerText || '').trim().slice(0, 100),
                                cursor: style.cursor, attrs: attrs(el), handlers,
                                reactPropKeys: props ? Object.keys(props).slice(0, 25) : [],
                                fiberPropKeys: fiberProps ? Object.keys(fiberProps).slice(0, 25) : []
                            };
                        }).filter(el => el.handlers.length || el.attrs.href || el.attrs.role ||
                            el.attrs.tabindex || el.cursor === 'pointer' || /^(BUTTON|A)$/.test(el.tag));
                        const ancestors = [];
                        for (let el = item; el && el !== document.body && ancestors.length < 5; el = el.parentElement) {
                            ancestors.push({tag: el.tagName, attrs: attrs(el), cursor: getComputedStyle(el).cursor});
                        }
                        return {text: (item.innerText || '').trim().slice(0, 350), attrs: attrs(item), ancestors, targets: targets.slice(0, 15)};
                    });
                const lines = (document.body?.innerText || '').split(/\\n+/)
                    .map(x => x.trim()).filter(x => /kết quả|văn bản|tìm thấy|không có|không tìm/i.test(x)).slice(-30);
                return {inputs, actions: actions.slice(-25), documentLinks: docLinks.slice(0, 25), resultItems, resultText: lines};
            }""")
            raise RuntimeError(
                "Đã gửi từ khóa từ trang chủ nhưng chưa nhận diện được danh sách kết quả VBPL. "
                f"URL={page.url}; body={body_text[:400]!r}; browser_diagnostics={diagnostics}; "
                f"search_requests={search_requests}"
            )
        signature = tuple(current_urls) or tuple(
            clean(card.inner_text())[:240] for card in _vbpl_result_cards(page).all()
        )
        if signature in seen_pages:
            raise RuntimeError("VBPL search results repeated; stopping to avoid a pagination loop.")
        seen_pages.add(signature)
        found.extend(current_urls)
        print(
            f"[{query}] Search results page {page_number}: identified {len(current_urls)} eligible documents; "
            f"{len(set(found))} URLs total.",
            flush=True,
        )
        if target_candidates and len(set(found)) >= target_candidates:
            print(
                f"[{query}] Đã đủ {target_candidates} ứng viên để xếp hạng gần đây; dừng quét trang.",
                flush=True,
            )
            break
        next_link = None
        for anchor in page.locator("a, button, [role=button]").all():
            label = " ".join(filter(None, [
                anchor.inner_text(), anchor.get_attribute("title"), anchor.get_attribute("aria-label")
            ]))
            label_folded = _vbpl_search_fold(label)
            if (clean(anchor.get_attribute("rel") or "").casefold() == "next"
                    or re.fullmatch(r"\s*(?:trang sau|tiep(?: theo)?|sau|next|>)\s*", label_folded, re.I)):
                next_link = anchor
                break
        if next_link is None or not next_link.is_visible():
            break
        if page_number >= max_pages:
            raise RuntimeError(f"Reached VBPL result-page limit ({max_pages}).")
        old_signature = signature
        old_cards = _vbpl_result_cards(page)
        old_first_result = old_cards.first.inner_text()[:500] if old_cards.count() else ""
        next_link.click(timeout=10000)
        try:
            page.wait_for_function(
                """old => {
                    const first = [...document.querySelectorAll('li')].find(el =>
                        /Trạng thái\\s*:/i.test(el.innerText) && /Ngày ban hành\\s*:/i.test(el.innerText));
                    return first && first.innerText !== old;
                }""",
                arg=old_first_result,
                timeout=20000,
            )
        except PlaywrightTimeoutError:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
            except PlaywrightTimeoutError:
                pass
        page.wait_for_timeout(500)
        new_cards = _vbpl_result_cards(page)
        new_first_result = new_cards.first.inner_text()[:500] if new_cards.count() else ""
        if old_first_result and new_first_result == old_first_result:
            raise RuntimeError("Could not advance to the next VBPL results page.")
        next_urls = _vbpl_search_result_urls(page)
        if next_urls and tuple(next_urls) == old_signature:
            raise RuntimeError("Could not advance to the next VBPL results page.")
    return list(dict.fromkeys(found))


def _canonical_url(url: str, source: str) -> str:
    if source == "tvpl":
        try:
            from .tvpl_source import canonicalize_document_url
        except ImportError:
            from tvpl_source import canonicalize_document_url
        return canonicalize_document_url(url)
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    if not (host == "vbpl.vn" or host.endswith(".vbpl.vn")):
        raise ValueError(f"Không phải URL VBPL: {url}")
    query = {key: value for key, value in parse_qsl(parsed.query, keep_blank_values=True)
             if key.casefold() in {"itemid", "id", "dvid"}}
    path = parsed.path
    if re.search(r"/Pages/i?vbpq-(?!timkiem)[^/]+\.aspx$", path, re.I):
        path = re.sub(r"((?:i?vbpq)-)[^/]+\.aspx$", r"\1toanvan.aspx", path, flags=re.I)
    return urlunparse(parsed._replace(path=path, query=urlencode(query), fragment=""))


def _record_is_valid(path: Path, url: str) -> bool:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        content = record.get("content") or {}
        return (
            bool(record.get("id"))
            and (record.get("source") or {}).get("url") == url
            and len((content.get("full_text") or "").strip()) >= 40
            and isinstance(content.get("sections"), list)
        )
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def _existing_record_paths(out: Path, source: str) -> dict[str, Path]:
    records_dir = out / "records"
    if not records_dir.exists():
        return {}
    existing: dict[str, Path] = {}
    for path in records_dir.glob("LAW_*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            url = (record.get("source") or {}).get("url", "")
            if url:
                existing[_canonical_url(url, source)] = path
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return existing


def _write_record(record: dict, records_dir: Path) -> Path:
    records_dir.mkdir(parents=True, exist_ok=True)
    destination = records_dir / f"{record['id']}.json"
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(destination)
    return destination


def _report(out: Path, **event) -> None:
    out.mkdir(parents=True, exist_ok=True)
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with (out / "crawl_report.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")


def _crawl_one(page, url: str, source: str, *, pause_on_challenge: bool = False) -> dict:
    if source == "tvpl":
        try:
            from .tvpl_source import extract_record
        except ImportError:
            from tvpl_source import extract_record
        return extract_record(page, url, pause_on_challenge=pause_on_challenge)

    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    return extract(page, page.url)


def _process_one(
    page,
    url: str,
    source: str,
    out: Path,
    existing: dict[str, Path],
    refresh: bool,
    query: str = "",
    pause_on_error: bool = False,
) -> tuple[bool, str]:
    canonical = _canonical_url(url, source)
    old_path = existing.get(canonical)
    if old_path and not refresh and _record_is_valid(old_path, canonical):
        print(f"SKIP {old_path.stem} | Đã có bản ghi hợp lệ")
        _report(out, event="document", source=source, query=query, url=canonical,
                id=old_path.stem, status="skipped")
        return True, old_path.stem

    last_error = ""
    for attempt in range(1, 4):
        try:
            record = _crawl_one(page, canonical, source, pause_on_challenge=pause_on_error)
            if not record.get("id") or not (record.get("content") or {}).get("full_text"):
                raise RuntimeError("Trang không có nội dung quy định công khai để lưu.")
            path = _write_record(record, out / "records")
            existing[canonical] = path
            print(f"OK {record['id']} | {record['content']['title'][:100]}")
            _report(out, event="document", source=source, query=query, url=canonical,
                    id=record["id"], status="ok")
            return True, record["id"]
        except PlaywrightTimeoutError as exc:
            last_error = f"Timeout: {exc}"
            if attempt < 3:
                print(f"RETRY {attempt}/2 {canonical}")
        except Exception as exc:
            last_error = str(exc)
            break

    print(f"ERROR {canonical}: {last_error}")
    _report(out, event="document", source=source, query=query, url=canonical,
            status="error", error=last_error)
    if pause_on_error:
        try:
            input("Chromium vẫn đang mở để kiểm tra trang lỗi. Nhấn Enter để tiếp tục và đóng trình duyệt...")
        except EOFError:
            pass
    return False, last_error


def _process_url_list(
    page,
    urls: list[str],
    source: str,
    out: Path,
    limit: int,
    delay: float,
    refresh: bool,
    pause_on_error: bool,
) -> int:
    existing = _existing_record_paths(out, source)
    seen: set[str] = set()
    successes = 0
    for url in urls:
        try:
            canonical = _canonical_url(url, source)
        except ValueError as exc:
            print(f"ERROR {url}: {exc}")
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        success, detail_status = _process_one(
            page, canonical, source, out, existing, refresh,
            pause_on_error=pause_on_error,
        )
        successes += int(success)
        if not success and any(token in detail_status.casefold() for token in (
            "captcha", "access denied", "403", "đang chặn", "xác minh",
        )):
            break
        if successes >= limit:
            break
        time.sleep(delay)
    return successes


def _guard_search_pages(result_pages):
    try:
        yield from result_pages
    except Exception as exc:
        yield {"search_error": str(exc)}


def _run_vbpl_query(page, query: str, args) -> None:
    """Lọc toàn bộ kết quả theo hiệu lực, xếp hạng ngày ban hành rồi parse K."""
    try:
        candidate_buffer = args.candidate_count or max(args.limit + 5, args.limit * 3)
        print(
            f"[{query}] Mục tiêu gom {candidate_buffer} ứng viên còn hiệu lực "
            f"trước khi xếp hạng top {args.limit}.",
            flush=True,
        )
        urls = discover_urls(
            page, query, max_pages=args.max_search_pages,
            target_candidates=candidate_buffer,
        )
    except Exception as exc:
        reason = f"lỗi nguồn: {exc}"
        print(f"[{query}] {reason}")
        _report(args.out, event="query_summary", source="vbpl", query=query,
                status="error", discovered=0, eligible=0, successful=0,
                limit=args.limit, search_mode="full_text", stop_reason=reason)
        return

    print(f"[{query}] Khám phá xong: {len(urls)} URL khớp; đang kiểm tra hiệu lực/ngày ban hành...", flush=True)
    candidates = []
    metadata_errors = 0
    for index, url in enumerate(urls, start=1):
        row_attributes = VBPL_SEARCH_METADATA.get(url, {})
        needs_page_check = not (
            row_attributes.get("validity_raw") and row_attributes.get("issued_date_raw")
        )
        if needs_page_check:
            print(f"[{query}] Kiểm tra metadata văn bản {index}/{len(urls)}: {url}", flush=True)
        else:
            print(
                f"[{query}] Dùng trạng thái/ngày ngay trên kết quả "
                f"({index}/{len(urls)}): {row_attributes['validity_raw']}, "
                f"{row_attributes['issued_date_raw']}.",
                flush=True,
            )
        try:
            if needs_page_check:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(700)
                attributes = extract_vbpl_attributes(page, url)
            else:
                attributes = row_attributes
            eligible, reason, issue_date = _eligible_vbpl_candidate(attributes)
            if not eligible:
                needs_review = _candidate_metadata_uncertain(attributes)
                if needs_review:
                    metadata_errors += 1
                _report(args.out, event="candidate", source="vbpl", query=query,
                        url=url, status="needs_review" if needs_review else "excluded", reason=reason,
                        validity_raw=attributes.get("validity_raw", ""),
                        issued_date_raw=attributes.get("issued_date_raw", ""))
                continue
            candidates.append({"url": url, "attributes": attributes, "issue_date": issue_date})
            print(f"[{query}] Ứng viên hợp lệ ({issue_date.isoformat()}): {url}", flush=True)
        except Exception as exc:
            metadata_errors += 1
            print(f"[{query}] Lỗi đọc thuộc tính: {url} — {exc}", flush=True)
            _report(args.out, event="candidate", source="vbpl", query=query,
                    url=url, status="metadata_error", reason=str(exc))
        finally:
            if needs_page_check:
                time.sleep(args.delay)

    candidates.sort(key=lambda item: (-item["issue_date"].toordinal(), item["url"]))
    print(f"[{query}] Có {len(candidates)} ứng viên còn hiệu lực sau khi lọc metadata.", flush=True)
    if args.discover_only:
        selected = candidates[:args.limit]
        for rank, candidate in enumerate(selected, start=1):
            print(candidate["url"])
            _report(args.out, event="candidate", source="vbpl", query=query,
                    url=candidate["url"], status="ranked", rank=rank,
                    issued_date=candidate["issue_date"].isoformat())
        _report(args.out, event="query_summary", source="vbpl", query=query,
                status="partial" if metadata_errors else "discovered",
                discovered=len(urls), eligible=len(candidates), metadata_errors=metadata_errors,
                successful=len(selected), limit=args.limit, search_mode="full_text",
                stop_reason=("có ứng viên không đọc được thuộc tính; kết quả xếp hạng có thể chưa đầy đủ"
                             if metadata_errors else "đã xếp hạng URL đủ điều kiện"))
        preview_reason = (
            "thuộc tính chưa đọc được ở một số kết quả; thứ hạng có thể chưa đủ"
            if metadata_errors else "đã xếp hạng URL đủ điều kiện"
        )
        print(f"[{query}] {len(selected)}/{args.limit} — {preview_reason}")
        return

    successful = 0
    parse_errors = 0
    for candidate in candidates:
        if successful >= args.limit:
            break
        url = candidate["url"]
        print(f"[{query}] Đang tải và parse văn bản {successful + 1}/{args.limit}: {url}", flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(700)
            current_attributes = extract_vbpl_attributes(page, url)
            listed_status = (candidate.get("attributes") or {}).get("validity_raw", "")
            detail_status = current_attributes.get("validity_raw", "")
            if listed_status.casefold() == "còn hiệu lực":
                if detail_status and detail_status.casefold() != listed_status.casefold():
                    print(
                        f"[{query}] Trạng thái danh sách='{listed_status}', "
                        f"trang chi tiết='{detail_status}'; dùng trạng thái danh sách.",
                        flush=True,
                    )
                    _report(
                        args.out, event="candidate_status_conflict", source="vbpl",
                        query=query, url=url, listed_status=listed_status,
                        detail_status=detail_status,
                    )
                current_attributes["validity_raw"] = listed_status
            still_eligible, eligibility_reason, current_issue_date = _eligible_vbpl_candidate(current_attributes)
            if not still_eligible:
                needs_review = _candidate_metadata_uncertain(current_attributes)
                print(
                    f"[{query}] Bỏ qua khi recheck: {eligibility_reason}; "
                    f"trạng thái danh sách='{listed_status}', "
                    f"trạng thái chi tiết='{detail_status}'.",
                    flush=True,
                )
                if needs_review:
                    metadata_errors += 1
                _report(args.out, event="candidate", source="vbpl", query=query,
                        url=url, status="needs_review_on_recheck" if needs_review else "excluded_on_recheck",
                        reason=eligibility_reason, listed_validity_raw=listed_status,
                        detail_validity_raw=detail_status,
                        issued_date_raw=current_attributes.get("issued_date_raw", ""),
                        effective_date_raw=current_attributes.get("effective_date_raw", ""),
                        expired_date_raw=current_attributes.get("expired_date_raw", ""))
                continue
            if current_issue_date != candidate["issue_date"]:
                metadata_errors += 1
                _report(args.out, event="candidate", source="vbpl", query=query,
                        url=url, status="metadata_changed", reason="ngày ban hành đổi trong lúc crawl",
                        previous_issued_date=candidate["issue_date"].isoformat(),
                        current_issued_date=(current_issue_date.isoformat() if current_issue_date else None))
                continue
            record = extract(page, url, attributes=current_attributes)
            record_path = args.out / "records" / f"{record['id']}.json"
            search_matches = []
            if record_path.exists():
                try:
                    previous = json.loads(record_path.read_text(encoding="utf-8"))
                    search_matches = (previous.get("source") or {}).get("search_matches", [])
                except (OSError, ValueError, TypeError, AttributeError):
                    search_matches = []
            if not isinstance(search_matches, list):
                search_matches = []
            search_matches = [
                match for match in search_matches
                if isinstance(match, dict) and match.get("query") != query
            ]
            search_matches.append({
                "query": query,
                "rank": successful + 1,
                "issued_date": candidate["issue_date"].isoformat(),
            })
            record["source"]["search_matches"] = search_matches
            _write_record(record, args.out / "records")
            successful += 1
            _report(args.out, event="document", source="vbpl", query=query,
                    url=url, id=record["id"], status="ok",
                    rank=successful, issued_date=candidate["issue_date"].isoformat())
            print(f"OK {record['id']} | {record['content']['title'][:100]}")
        except Exception as exc:
            parse_errors += 1
            _report(args.out, event="candidate", source="vbpl", query=query,
                    url=url, status="parse_error", reason=str(exc),
                    issued_date=candidate["issue_date"].isoformat())
            print(f"SKIP {url}: {exc}")
        finally:
            time.sleep(args.delay)

    if successful >= args.limit and not metadata_errors:
        reason = "đủ giới hạn văn bản đạt kiểm tra"
        status = "complete"
    elif metadata_errors:
        reason = (
            f"đã chọn {successful}/{args.limit}; có ứng viên lỗi metadata nên "
            "thứ hạng có thể chưa đầy đủ"
        )
        status = "partial"
    elif parse_errors:
        reason = "đã xử lý ứng viên đủ điều kiện nhưng có lỗi tải hoặc parse nội dung"
        status = "partial"
    elif len(urls) == 0:
        reason = "không có kết quả tìm kiếm"
        status = "complete"
    else:
        reason = "đã xử lý hết ứng viên đủ điều kiện"
        status = "complete"
    print(f"[{query}] {successful}/{args.limit} — {reason}")
    _report(args.out, event="query_summary", source="vbpl", query=query,
            status=status, discovered=len(urls), eligible=len(candidates),
            metadata_errors=metadata_errors, parse_errors=parse_errors,
            search_mode="full_text",
            successful=successful, limit=args.limit, stop_reason=reason)


def _run_searches(page, args) -> None:
    try:
        from .tvpl_source import document_id, iter_search_result_pages
    except ImportError:
        from tvpl_source import document_id, iter_search_result_pages

    for query in args.query:
        if args.source == "vbpl":
            _run_vbpl_query(page, query, args)
            continue
        successes = 0
        discovered = 0
        seen: set[str] = set()
        reason = "hết kết quả"
        blocked = False
        existing = _existing_record_paths(args.out, args.source)

        if args.source == "tvpl":
            result_pages = iter_search_result_pages(page, query, pause_on_challenge=args.headed)
        for result_page in _guard_search_pages(result_pages):
            if isinstance(result_page, dict) and "search_error" in result_page:
                reason = f"lỗi nguồn: {result_page['search_error']}"
                break
            for url in result_page:
                if args.source == "tvpl":
                    key = document_id(url)
                else:
                    key = url
                if key in seen:
                    continue
                seen.add(key)
                if args.discover_only:
                    print(url)
                    discovered += 1
                    if discovered >= args.limit:
                        reason = "đủ giới hạn URL"
                        break
                    continue

                success, detail_status = _process_one(
                    page, url, args.source, args.out, existing, args.refresh,
                    query=query, pause_on_error=args.headed,
                )
                discovered += 1
                successes += int(success)
                if not success and any(token in detail_status.casefold() for token in (
                    "captcha", "access denied", "403", "đang chặn", "xác minh",
                )):
                    reason = f"lỗi nguồn: {detail_status}"
                    blocked = True
                    break
                if successes >= args.limit:
                    reason = "đủ giới hạn văn bản hợp lệ"
                    break
                time.sleep(args.delay)
            if blocked or (args.discover_only and discovered >= args.limit) or successes >= args.limit:
                break
            if result_page:
                time.sleep(args.delay)

        count = discovered if args.discover_only else successes
        status = "discovered" if args.discover_only else "complete"
        if reason.startswith("lỗi nguồn:"):
            status = "error"
        print(f"[{query}] {count}/{args.limit} — {reason}")
        _report(args.out, event="query_summary", source=args.source, query=query,
                status=status, discovered=discovered, successful=successes,
                limit=args.limit, stop_reason=reason)
        if args.headed and reason.startswith("lỗi nguồn:") and not blocked:
            try:
                input("Chromium vẫn đang mở để kiểm tra trang tìm kiếm. Nhấn Enter để tiếp tục và đóng trình duyệt...")
            except EOFError:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl văn bản pháp luật từ VBPL hoặc Thư Viện Pháp Luật")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", action="append", help="URL văn bản; lặp lại để thêm URL")
    group.add_argument("--seed", type=Path, help="File txt, mỗi dòng một URL")
    group.add_argument("--query", action="append", help="Từ khóa tìm kiếm; lặp lại để thêm từ khóa")
    parser.add_argument("--source", choices=("vbpl", "tvpl"), default="vbpl",
                        help="Nguồn văn bản (mặc định: vbpl)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Tối đa số văn bản hợp lệ cho mỗi từ khóa hoặc đợt URL (mặc định: 50)")
    parser.add_argument("--max-search-pages", type=int, default=20,
                        help="Số trang kết quả VBPL tối đa để quét (mặc định: 20; tăng nếu cần phủ rộng)")
    parser.add_argument(
        "--candidate-count", type=int,
        help=("Số văn bản còn hiệu lực tối đa cần gom trước khi xếp hạng; "
              "mặc định max(--limit * 3, --limit + 5)"),
    )
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "data" / "law")
    parser.add_argument("--headed", action="store_true", help="Hiện trình duyệt để quan sát trang hoặc kiểm tra chặn truy cập")
    parser.add_argument("--user-data-dir", type=Path,
                        help="Dùng profile Chromium hiện có; truyền thư mục User Data gốc")
    parser.add_argument("--profile-directory", default="Default",
                        help="Thư mục profile bên trong User Data, ví dụ Default hoặc 'Profile 1'")
    parser.add_argument("--channel", choices=("chrome", "msedge"),
                        help="Dùng Chrome hoặc Edge đã cài thay cho Chromium của Playwright")
    parser.add_argument("--trace-path", type=Path,
                        help="Lưu Playwright trace ZIP (DOM snapshots, screenshots, network) để điều tra lỗi")
    parser.add_argument("--delay", type=float, default=3.0, help="Khoảng nghỉ giữa các văn bản/trang tìm kiếm")
    parser.add_argument("--refresh", action="store_true", help="Tải lại các bản ghi đã có")
    parser.add_argument("--discover-only", action="store_true", help="Chỉ in tối đa K URL cho mỗi từ khóa")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit phải lớn hơn 0")
    if args.max_search_pages < 1:
        parser.error("--max-search-pages phải lớn hơn 0")
    if args.candidate_count is not None and args.candidate_count < 1:
        parser.error("--candidate-count phải lớn hơn 0")
    if args.delay < 0:
        parser.error("--delay không được âm")
    if args.discover_only and not args.query:
        parser.error("--discover-only chỉ dùng cùng --query")

    require_playwright()
    with sync_playwright() as pw:
        context_options = {
            "locale": "vi-VN",
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
            ),
            "headless": not args.headed,
        }
        if args.channel:
            context_options["channel"] = args.channel
        if args.user_data_dir:
            profile_root = args.user_data_dir.expanduser().resolve()
            context_options["args"] = [f"--profile-directory={args.profile_directory}"]
            context = pw.chromium.launch_persistent_context(str(profile_root), **context_options)
            browser = None
        else:
            context_options.pop("headless")
            context = pw.chromium.launch(headless=not args.headed, channel=args.channel).new_context(
                locale=context_options["locale"], user_agent=context_options["user_agent"]
            )
            browser = context.browser
        trace_path = args.trace_path.expanduser().resolve() if args.trace_path else None
        if trace_path:
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            print(f"Playwright trace đang ghi: {trace_path}", flush=True)
        page = context.new_page()
        try:
            if args.query:
                _run_searches(page, args)
            else:
                if args.url:
                    urls = args.url
                else:
                    seed_path = args.seed
                    if not seed_path.is_absolute() and not seed_path.exists():
                        project_candidate = PROJECT_ROOT / seed_path
                        if project_candidate.exists():
                            seed_path = project_candidate
                    urls = [
                        line.strip() for line in seed_path.read_text(encoding="utf-8").splitlines()
                        if line.strip() and not line.lstrip().startswith("#")
                    ]
                _process_url_list(page, urls, args.source, args.out, args.limit,
                                  args.delay, args.refresh, args.headed)
        finally:
            if trace_path:
                context.tracing.stop(path=str(trace_path))
                print(f"Playwright trace đã lưu: {trace_path}", flush=True)
            if browser:
                browser.close()
            else:
                context.close()


if __name__ == "__main__":
    main()
