"""Public-page search and extraction helpers for Thư Viện Pháp Luật.

This module deliberately reads only public search results and document text. It
does not log in, submit forms other than public keyword searches, or work around
CAPTCHAs/access controls.
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterator
from urllib.parse import urlencode, urljoin, urlparse, urlunparse


BASE_URL = "https://thuvienphapluat.vn"
SEARCH_URL = f"{BASE_URL}/page/tim-van-ban.aspx"
DOCUMENT_PATH_RE = re.compile(r"^/van-ban/.+-\d+\.aspx$", re.I)
DOCUMENT_ID_RE = re.compile(r"-(\d+)\.aspx$", re.I)


def canonicalize_document_url(url: str) -> str:
    """Return a stable TVPL detail URL without tracking or fragment data."""
    absolute = urljoin(BASE_URL, url)
    parsed = urlparse(absolute)
    if parsed.netloc.casefold() not in {"thuvienphapluat.vn", "www.thuvienphapluat.vn"}:
        raise ValueError(f"Không phải URL văn bản TVPL: {url}")
    if not DOCUMENT_PATH_RE.fullmatch(parsed.path):
        raise ValueError(f"Không phải đường dẫn văn bản TVPL: {url}")
    return urlunparse(("https", "thuvienphapluat.vn", parsed.path, "", "", ""))


def document_id(url: str) -> str:
    match = DOCUMENT_ID_RE.search(urlparse(canonicalize_document_url(url)).path)
    if not match:
        raise ValueError(f"Không tìm thấy mã văn bản trong URL: {url}")
    return match.group(1)


def search_page_url(query: str, page_number: int) -> str:
    """Build the public search URL using the site's observed query fields."""
    params = {
        "area": "0",
        "fields": "",
        "keyword": query,
        "lan": "1",
        "match": "True",
        "org": "0",
        "page": str(page_number),
        "scan": "0",
        "signer": "0",
        "sort": "1",
        "status": "0",
        "type": "0",
    }
    return f"{SEARCH_URL}?{urlencode(params)}"


def _page_guard(page) -> None:
    body_text = page.locator("body").inner_text(timeout=15000)
    folded = body_text.casefold()
    signals = (
        "access denied", "403 forbidden", "captcha", "xác minh bạn không phải",
        "verify you are human", "checking your browser", "unusual traffic",
    )
    matched = next((token for token in signals if token in folded), None)
    if matched:
        position = folded.find(matched)
        excerpt = " ".join(body_text[max(0, position - 100):position + 220].split())
        raise RuntimeError(
            f"TVPL đang chặn hoặc yêu cầu xác minh (dấu hiệu: {matched!r}; "
            f"URL: {page.url}; đoạn trang: {excerpt!r})."
        )


def _result_links(page) -> list[str]:
    """Extract visible detail links while excluding site chrome and sidebars."""
    rows = page.locator("body").evaluate(
        """body => Array.from(body.querySelectorAll('a[href]')).map(a => {
          const href = a.href || '';
          const text = (a.innerText || a.getAttribute('aria-label') || '').trim();
          const excluded = a.closest('header, nav, footer, aside, [role="navigation"]');
          const style = getComputedStyle(a);
          const visible = !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length)
            && style.visibility !== 'hidden' && style.display !== 'none';
          return {href, text, excluded: !!excluded, visible};
        }).filter(x => x.visible && !x.excluded && x.text.length > 8)"""
    )
    found: list[str] = []
    seen: set[str] = set()
    for row in rows:
        try:
            url = canonicalize_document_url(row["href"])
        except (KeyError, TypeError, ValueError):
            continue
        if url not in seen:
            seen.add(url)
            found.append(url)
    return found


def iter_search_result_pages(page, query: str) -> Iterator[list[str]]:
    """Yield one page of search result URLs at a time in website order."""
    visited_signatures: set[tuple[str, ...]] = set()
    page_number = 1
    while True:
        page.goto(search_page_url(query, page_number), wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_function(
                r"""() => {
                  const body = document.body?.innerText || '';
                  return body.includes('Kết quả') || body.includes('Không tìm thấy')
                    || body.includes('không tìm thấy') || body.includes('403')
                    || body.toLowerCase().includes('captcha');
                }""",
                timeout=15000,
            )
        except Exception:
            # A complete page without the summary is still inspected so that
            # an access error is reported clearly by _page_guard below.
            pass
        _page_guard(page)
        links = _result_links(page)
        signature = tuple(document_id(url) for url in links)
        if not signature or signature in visited_signatures:
            break
        visited_signatures.add(signature)
        yield links
        page_number += 1
        # Protect against a broken paging control returning synthetic pages.
        if page_number > 10000:
            raise RuntimeError("Dừng phân trang sau 10.000 trang bảo vệ.")


def _regulatory_container(page) -> dict:
    """Choose the smallest non-chrome DOM container holding the law body."""
    candidates = page.locator("body").evaluate(
        r"""body => {
          const nodes = Array.from(body.querySelectorAll('article, main, section, div, td, table'));
          const rows = [];
          for (const node of nodes) {
            if (node.closest('header, nav, footer, aside, [role="navigation"]')) continue;
            const text = (node.innerText || '').replace(/\u00a0/g, ' ').trim();
            if (text.length < 80) continue;
            const hasArticleOne = /^\s*Điều\s+1(?:[.:\s]|$)/im.test(text);
            const hasChapter = /^\s*(?:CHƯƠNG\s+[IVXLCDM0-9]+|MỤC\s+[IVXLCDM0-9]+)\b/im.test(text);
            if (!hasArticleOne && !hasChapter) continue;
            const articles = Array.from(text.matchAll(/^\s*Điều\s+(\d+)\b/gim))
              .map(m => m[1]);
            const attachments = Array.from(node.querySelectorAll('a[href]'))
              .map(a => a.href)
              .filter(href => /\.(pdf|docx?)(?:[?#]|$)/i.test(href));
            rows.push({text, length: text.length, articles: new Set(articles).size,
              hasArticleOne, hasChapter, tag: node.tagName, attachments});
          }
          rows.sort((a, b) => b.articles - a.articles || a.length - b.length);
          return rows.slice(0, 30);
        }"""
    )
    viable = [
        row for row in candidates
        if row.get("hasArticleOne") or (row.get("hasChapter") and row.get("articles", 0) > 0)
    ]
    if not viable:
        raise RuntimeError("Không tìm thấy vùng nội dung quy định công khai trên trang văn bản.")
    return viable[0]


def _select_regulations(text: str) -> str:
    """Keep articles/clauses and stop before signature or attached appendices."""
    lines = [
        re.sub(r" {2,}", " ", line.replace("\xa0", " ").replace("\t", " | ")).strip()
        for line in text.splitlines()
    ]
    lines = [line for line in lines if line]
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^(?:Điều\s+1\b|CHƯƠNG\s+[IVXLCDM0-9]+\b|MỤC\s+[IVXLCDM0-9]+\b)", line, re.I):
            start = index
            break
    if start is None:
        raise RuntimeError("Vùng nội dung tìm thấy nhưng không có heading quy định nhận diện được.")
    lines = lines[start:]

    end_marker = re.compile(
        r"^(?:Nơi\s+nhận\s*:|PHỤ\s+LỤC(?:\s.*|$)|Mẫu\s+số\s+\d+\b.*|"
        r"TM\.\s+CHÍNH\s+PHỦ\b|KT\.\s+THỦ\s+TƯỚNG\b)$",
        re.I,
    )
    for index, line in enumerate(lines[1:], start=1):
        if end_marker.match(line):
            lines = lines[:index]
            break
        if re.match(r"^(?:PHÓ\s+)?(?:THỦ\s+TƯỚNG|BỘ\s+TRƯỞNG|CHỦ\s+TỊCH)\s*$", line, re.I):
            lines = lines[:index]
            break

    result = "\n".join(lines).strip()
    if not result or not re.search(r"^Điều\s+\d+\b", result, re.I | re.M):
        raise RuntimeError("Không trích xuất được phần điều khoản để lưu.")
    return result


def extract_record(page, url: str) -> dict:
    """Read one public TVPL detail page and return the shared law-record shape."""
    try:
        from .crawl_law import (
            LEGAL_TOPICS, clean, find_attribute_value, normalize_document_type,
            split_legal_sections, validate_section_split,
        )
    except ImportError:  # Supports direct execution of crawl/crawl_law.py.
        from crawl_law import (
            LEGAL_TOPICS, clean, find_attribute_value, normalize_document_type,
            split_legal_sections, validate_section_split,
        )

    canonical_url = canonicalize_document_url(url)
    page.goto(canonical_url, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_function(
            r"""() => {
              const t = document.body?.innerText || '';
              return /^\s*Điều\s+1/m.test(t) || /^\s*CHƯƠNG\s+I/m.test(t)
                || t.includes('403') || t.toLowerCase().includes('captcha');
            }""",
            timeout=20000,
        )
    except Exception:
        pass
    _page_guard(page)

    body_text = page.locator("body").inner_text(timeout=15000)
    document_region = _regulatory_container(page)
    regulations = _select_regulations(document_region["text"])

    title = ""
    for heading in page.locator("h1").all():
        candidate = clean(heading.inner_text())
        if len(candidate) >= 12 and "thư viện pháp luật" not in candidate.casefold():
            title = candidate
            break
    if not title:
        title = clean(page.title()).split(" | ")[0].split(" mới nhất")[0]

    labels = [
        "Số hiệu", "Loại văn bản", "Nhóm văn bản", "Trích yếu", "Ngày ban hành",
        "Ngày có hiệu lực", "Ngày hiệu lực", "Tình trạng", "Tình trạng hiệu lực", "Nơi ban hành",
        "Cơ quan ban hành", "Người ký",
    ]
    number = find_attribute_value(body_text, "Số hiệu", labels)
    kind = find_attribute_value(body_text, "Loại văn bản", labels)
    issue_date = find_attribute_value(body_text, "Ngày ban hành", labels)
    effective_date = find_attribute_value(body_text, "Ngày có hiệu lực", labels)
    if not effective_date:
        effective_date = find_attribute_value(body_text, "Ngày hiệu lực", labels)
    validity = find_attribute_value(body_text, "Tình trạng hiệu lực", labels)
    if not validity:
        validity = find_attribute_value(body_text, "Tình trạng", labels)
    issuer = find_attribute_value(body_text, "Nơi ban hành", labels)
    if not issuer:
        issuer = find_attribute_value(body_text, "Cơ quan ban hành", labels)

    kind = normalize_document_type(kind)
    sections = split_legal_sections(regulations)
    validation = validate_section_split(regulations, sections)
    if not validation["is_lossless"]:
        raise RuntimeError("Các section không khớp toàn văn đã chọn; không lưu record không toàn vẹn.")

    attachments = []
    for href in document_region.get("attachments", []):
        host = (urlparse(href).hostname or "").casefold()
        if host == "thuvienphapluat.vn" or host.endswith(".thuvienphapluat.vn"):
            attachments.append(href)

    folded = regulations.casefold()
    is_birth_related = any(term in folded for terms in LEGAL_TOPICS.values() for term in terms)
    return {
        "id": f"LAW_TVPL_{document_id(canonical_url)}",
        "life_event": ["sinh_con"] if is_birth_related else [],
        "domain": "Pháp luật",
        "jurisdiction": {"level": "Chưa xác định", "location": "Chưa xác định"},
        "source": {
            "name": "Thư Viện Pháp Luật",
            "url": canonical_url,
            "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        },
        "relations": {"related_laws": [], "related_procedures": []},
        "content": {
            "title": title,
            "document_type": kind,
            "document_number": number,
            "issuing_authority": issuer,
            "issued_date_raw": issue_date,
            "effective_date_raw": effective_date,
            "validity_raw": validity,
            "full_text": regulations,
            "sections": sections,
            "attachments": sorted(set(attachments)),
        },
    }
