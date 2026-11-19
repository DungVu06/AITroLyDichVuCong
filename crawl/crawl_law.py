"""Thu thap metadata va noi dung van ban phap luat tu VBPL hoac TVPL.

Chi luu JSON da chuan hoa vao thu muc records; khong luu HTML raw.
Khong dung crawler de tu dong ket luan van ban con hieu luc. Hieu luc va
quan he thay the/phap ly can duoc kiem tra lai tu trang van ban.

Vi du (chay tu bat ky thu muc nao):
  python crawl/crawl_law.py --source vbpl --url 'https://vbpl.vn/...' --out data/law
  python crawl/crawl_law.py --source tvpl --query 'thuế thu nhập cá nhân' --limit 50
  python crawl/crawl_law.py --seed crawl/seed_law_urls.txt --out data/law --headed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
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


CHAPTER_HEADING_RE = re.compile(r"^CHƯƠNG\s+[IVXLCDM0-9]+(?:\s|$)", re.I)
NAMED_SECTION_HEADING_RE = re.compile(r"^MỤC\s+[IVXLCDM0-9]+(?:\s|$)", re.I)
# Không dùng re.I và chỉ nhận I/V/X/L: nếu dùng re.I thì `c.`/`d.` bị
# hiểu nhầm là số La Mã; nếu nhận C/D thì `C.`/`D.` (phần lớn là part)
# cũng bị nhầm thành section.
ROMAN_SECTION_HEADING_RE = re.compile(r"^[IVXL]+[\.\)\-–]\s+.+")
ARTICLE_HEADING_RE = re.compile(r"^ĐIỀU\s+\d+(?:\s|[.:]|$)", re.I)
SUBSECTION_HEADING_RE = re.compile(r"^\d+[\.\)\-–]\s+.+")
SUBPOINT_HEADING_RE = re.compile(r"^(?:[a-zđ]|\d+)\.\d+[\.\)]\s+.+")
# Không dùng re.I: `a.`/`b.` là point, còn `A.`/`B.` mới là part.
PART_HEADING_RE = re.compile(r"^[A-HĐ][\.\)\-–]\s+.+")
POINT_HEADING_RE = re.compile(r"^[a-zđ][\.\)\-–]\s+.+")


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


def split_legal_sections(text: str) -> list[dict]:
    """Tách văn bản theo các heading phổ biến của văn bản pháp luật."""
    sections = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        level = classify_legal_heading(line)
        if level:
            if current:
                current["text"] = "\n".join(current["_lines"]).strip()
                current["related_laws"] = extract_related_laws(current["text"])
                del current["_lines"]
                sections.append(current)
            current = {"heading": line, "level": level, "_lines": []}
        elif current:
            current["_lines"].append(line)
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
    next_labels = "|".join(re.escape(item) for item in all_labels if item != label)
    pattern = rf"{re.escape(label)}\s*[:：]?\s*(.*?)(?=\s+(?:{next_labels})\s*[:：]?|$)"
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
    real_tab.click()
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


def extract(page, url: str) -> dict:
    # Trang chi tiet la Next.js: HTML ban dau chi co skeleton, noi dung den tu API.
    try:
        page.wait_for_function(
            """() => { const t = document.body?.innerText || ''; return t.length > 500 && !t.includes('Đang tải dữ liệu...'); }""",
            timeout=60000,
        )
    except PlaywrightTimeoutError:
        raise RuntimeError("VBPL chua tra ve noi dung van ban (API co the bi chan hoac dang loi).")
    content_text = clean_legal_text(active_panel_text(page))
    title = clean(page.title()) or find_value(content_text, ["Tên văn bản", "Tên văn bản pháp luật"])

    # Thuộc tính là tab riêng; mở trực tiếp bằng query tabs=thuoc-tinh.
    open_tab(page, url, "thuoc-tinh")
    attributes_text = active_panel_text(page)
    # Tieu de chinh la heading lon trong panel Thuoc tinh, khong phai title
    # cua trinh duyet (von co them "| CSDL quoc gia ve phap luat").
    for heading in page.locator("h1, h2").all():
        candidate = clean(heading.inner_text())
        if len(candidate) > 20 and candidate not in ("Nội dung", "Thuộc tính"):
            title = candidate
            break
    attribute_labels = [
        "Loại văn bản", "Nhóm văn bản", "Số hiệu", "Trích yếu",
        "Ngày ban hành", "Lĩnh vực", "Ngày có hiệu lực",
        "Tình trạng hiệu lực", "Ngày hết hiệu lực", "Cơ quan ban hành",
        "Chức danh", "Người ký",
    ]
    number = find_attribute_value(attributes_text, "Số hiệu", attribute_labels)
    issue_date = find_attribute_value(attributes_text, "Ngày ban hành", attribute_labels)
    effective_date = find_attribute_value(attributes_text, "Ngày có hiệu lực", attribute_labels)
    issuer = find_attribute_value(attributes_text, "Cơ quan ban hành", attribute_labels)
    kind = normalize_document_type(
        find_attribute_value(attributes_text, "Loại văn bản", attribute_labels)
    )
    status = find_attribute_value(attributes_text, "Tình trạng hiệu lực", attribute_labels)

    # Mở trực tiếp tab Nội dung bằng query tabs=toan-van.
    open_tab(page, url, "toan-van")
    content_text = clean_legal_text(active_panel_text(page))
    sections = split_legal_sections(content_text)
    section_validation = validate_section_split(content_text, sections)
    if not section_validation["is_lossless"]:
        print(
            f"WARNING {url}: sections khong khop full_text "
            f"({section_validation['full_text_length']} -> "
            f"{section_validation['reconstructed_length']} ky tu)"
        )
    links = []
    for a in page.locator("a").all():
        href = a.get_attribute("href")
        if href and (href.lower().endswith((".pdf", ".doc", ".docx")) or "download" in href.lower()):
            links.append(urljoin(url, href))
    folded = content_text.casefold()
    is_birth_related = any(term in folded for terms in LEGAL_TOPICS.values() for term in terms)
    record_id = slug_id(url, title)
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
            "document_type": kind,
            "document_number": number,
            "issuing_authority": issuer,
            "issued_date_raw": issue_date,
            "effective_date_raw": effective_date,
            "validity_raw": status,
            "full_text": content_text,
            "sections": sections,
            "attachments": sorted(set(links)),
        },
    }


def discover_urls(page, query: str, max_pages: int = 3) -> list[str]:
    """Tim link trang chi tiet van ban tu o tim kiem tren vbpl.vn.

    Giao dien vbpl co the thay doi, nen thu nhieu selector va loc lai theo
    mau URL. Ham nay khong tai file; chi tra ve cac URL de crawl tiep.
    """
    page.goto("https://vbpl.vn/pages/vbpq-timkiem.aspx", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    inputs = page.locator("input").all()
    search_box = None
    for item in inputs:
        attrs = " ".join(filter(None, [item.get_attribute(x) for x in ("name", "id", "placeholder", "aria-label")] )).casefold()
        if any(word in attrs for word in ("search", "tim kiem", "tìm kiếm", "keyword", "tu khoa", "từ khóa")):
            search_box = item
            break
    # Mot so ban giao dien ASP.NET dat ten input la ctl00$... khong co chu
    # 'search'. Khi do chon textbox visible dau tien (bo qua input an).
    if search_box is None:
        for item in inputs:
            typ = (item.get_attribute("type") or "text").casefold()
            if typ in ("text", "search") and item.is_visible():
                search_box = item
                break
    if search_box is None:
        raise RuntimeError("Khong tim thay o tu khoa tren trang tim kiem vbpl.vn.")
    search_box.fill(query)
    try:
        search_box.press("Enter")
    except Exception:
        buttons = page.locator("button, input[type=submit], input[type=button]").all()
        for button in buttons:
            label = " ".join(filter(None, [button.inner_text(), button.get_attribute("value"), button.get_attribute("aria-label")])).casefold()
            if any(word in label for word in ("tìm", "tim", "search")):
                button.click()
                break
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)

    found = []
    seen = set()
    for _ in range(max_pages):
        for anchor in page.locator("a[href]").all():
            href = anchor.get_attribute("href")
            if not href:
                continue
            absolute = urljoin(page.url, href).split("#", 1)[0]
            parsed = urlparse(absolute)
            path = parsed.path.casefold()
            if parsed.netloc.endswith("vbpl.vn") and any(token in path for token in ("vbpq", "van-ban", "toanvan", "chitiet")):
                if absolute not in seen:
                    seen.add(absolute)
                    found.append(absolute)
        next_link = page.locator("a").filter(has_text=re.compile(r"^(Trang sau|Tiếp|Next|>)$", re.I)).first
        if next_link.count() == 0 or not next_link.is_visible():
            break
        next_link.click()
        page.wait_for_timeout(1200)
    return found


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
    return urlunparse(parsed._replace(fragment=""))


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


def _crawl_one(page, url: str, source: str) -> dict:
    if source == "tvpl":
        try:
            from .tvpl_source import extract_record
        except ImportError:
            from tvpl_source import extract_record
        return extract_record(page, url)

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
            record = _crawl_one(page, canonical, source)
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
    return False, last_error


def _process_url_list(
    page,
    urls: list[str],
    source: str,
    out: Path,
    limit: int,
    delay: float,
    refresh: bool,
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
        success, detail_status = _process_one(page, canonical, source, out, existing, refresh)
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


def _run_searches(page, args) -> None:
    try:
        from .tvpl_source import document_id, iter_search_result_pages
    except ImportError:
        from tvpl_source import document_id, iter_search_result_pages

    for query in args.query:
        successes = 0
        discovered = 0
        seen: set[str] = set()
        reason = "hết kết quả"
        blocked = False
        existing = _existing_record_paths(args.out, args.source)

        if args.source == "tvpl":
            result_pages = iter_search_result_pages(page, query)
        else:
            # Trang VBPL thường trả về 20 kết quả; đọc thêm trang đệm để có thể
            # tiếp tục sau các URL lỗi mà không tải toàn bộ thư viện.
            page_cap = max(3, ((args.limit + 19) // 20) * 2 + 2)
            try:
                urls = discover_urls(page, query, max_pages=page_cap)
            except Exception as exc:
                reason = f"lỗi nguồn: {exc}"
                print(f"[{query}] {reason}")
                _report(args.out, event="query_summary", source=args.source, query=query,
                        status="error", discovered=0, successful=0,
                        limit=args.limit, stop_reason=reason)
                continue
            result_pages = (urls[index:index + 20] for index in range(0, len(urls), 20))

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
                    page, url, args.source, args.out, existing, args.refresh, query=query
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
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "data" / "law")
    parser.add_argument("--headed", action="store_true", help="Hiện trình duyệt để quan sát trang hoặc kiểm tra chặn truy cập")
    parser.add_argument("--delay", type=float, default=3.0, help="Khoảng nghỉ giữa các văn bản/trang tìm kiếm")
    parser.add_argument("--refresh", action="store_true", help="Tải lại các bản ghi đã có")
    parser.add_argument("--discover-only", action="store_true", help="Chỉ in tối đa K URL cho mỗi từ khóa")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit phải lớn hơn 0")
    if args.delay < 0:
        parser.error("--delay không được âm")
    if args.discover_only and not args.query:
        parser.error("--discover-only chỉ dùng cùng --query")

    require_playwright()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        context = browser.new_context(locale="vi-VN", user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"))
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
                                  args.delay, args.refresh)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
