"""Tao chunks cho cac van ban phap luat da duoc normalize va tach section.

Input mac dinh:
    data/law/normalized_records/LAW_*.json

Output mac dinh:
    data/law_chunks.jsonl

Format moi dong JSONL:
    {"page_content": "...", "metadata": {...}}

Moi section trong content.sections[] duoc xem la mot chunk goc. Chunk goc
qua dai se duoc tach lai bang cung cau hinh voi chunk_procedures.py de phu
hop voi gioi han input cua model embedding.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def clean(value: Any) -> str:
    """Chuan hoa gia tri text nhung khong thay doi noi dung phap ly."""
    return " ".join(str(value or "").split())


def referenced_laws_text(related_laws: list[dict[str, Any]]) -> str:
    """Tao dong context ngan cho cac van ban duoc dan chieu trong section."""
    references = []
    for law in related_laws or []:
        document_type = clean(law.get("document_type"))
        document_number = clean(law.get("document_number"))
        issued_date = clean(law.get("issued_date_raw"))
        relation_type = clean(law.get("relation_type"))
        referenced_location = clean(law.get("referenced_location"))

        reference = " ".join(
            item for item in (
                document_type,
                document_number,
                f"ngày {issued_date}" if issued_date else "",
                f"tại {referenced_location}" if referenced_location else "",
            )
            if item
        )
        if relation_type:
            reference = f"{reference} ({relation_type})"
        if reference:
            references.append(reference)

    if not references:
        return ""
    return "Văn bản được dẫn chiếu: " + "; ".join(references) + "."


def build_page_content(record: dict[str, Any], section: dict[str, Any]) -> str:
    """Ghep context cua van ban voi noi dung section de embedding."""
    content = record.get("content", {})
    heading = clean(section.get("heading"))
    text = str(section.get("text") or "").strip()

    header = [
        f"Văn bản pháp luật: {clean(content.get('title'))}",
        f"Loại văn bản: {clean(content.get('document_type'))}",
        f"Số hiệu: {clean(content.get('document_number'))}",
        f"Cơ quan ban hành: {clean(content.get('issuing_authority'))}",
        f"Vị trí trong văn bản: {heading}",
    ]

    citation = referenced_laws_text(section.get("related_laws", []))
    parts = ["\n".join(header), "Nội dung pháp lý:\n" + text]
    if citation:
        parts.append(citation)
    return "\n\n".join(parts)


def build_chunk(
    record: dict[str, Any], section: dict[str, Any], section_index: int
) -> dict[str, Any] | None:
    """Tao mot chunk; bo qua section chi co heading nhung khong co noi dung."""
    section_text = str(section.get("text") or "").strip()
    if not section_text:
        return None

    metadata = {
        "doc_id": record["id"],
        "chunk_type": "section",
        "life_event": record.get("life_event", []),
        "domain": clean(record.get("domain")),
        "section_index": section_index,
        "heading": clean(section.get("heading")),
        "section_level": clean(section.get("level")),
    }
    return {
        "page_content": build_page_content(record, section),
        "metadata": metadata,
    }


def split_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Tach cac chunk goc qua dai theo cung logic voi chunk_procedures.py."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    safe_chunks = []
    for doc_idx, chunk in enumerate(chunks):
        split_texts = text_splitter.split_text(chunk["page_content"])
        for split_idx, split_text in enumerate(split_texts):
            metadata = chunk["metadata"].copy()
            metadata["chunk_id"] = (
                f"{metadata['doc_id']}_c{doc_idx}_s{split_idx}"
            )
            safe_chunks.append(
                {"page_content": split_text, "metadata": metadata}
            )

    return safe_chunks


def chunk_laws(input_dir: Path, output_file: Path) -> tuple[int, int]:
    """Doc normalized records va ghi chunks. Tra ve (so_record, so_chunk)."""
    records = sorted(input_dir.glob("LAW_*.json"))
    if not records:
        raise FileNotFoundError(
            f"Không tìm thấy file LAW_*.json trong {input_dir}"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    record_count = 0
    raw_chunks = []

    for record_file in records:
        with record_file.open("r", encoding="utf-8") as handle:
            record = json.load(handle)

        if not record.get("id"):
            raise ValueError(f"Record thiếu id: {record_file}")

        record_count += 1
        sections = record.get("content", {}).get("sections", [])
        for section_index, section in enumerate(sections):
            chunk = build_chunk(record, section, section_index)
            if chunk is not None:
                raw_chunks.append(chunk)

    safe_chunks = split_chunks(raw_chunks)
    with output_file.open("w", encoding="utf-8") as output:
        for chunk in safe_chunks:
            output.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return record_count, len(safe_chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tạo JSONL chunks từ data/law/normalized_records/LAW_*.json"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/law/normalized_records"),
        help="Thư mục chứa các law normalized records",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/law_chunks.jsonl"),
        help="File JSONL đầu ra",
    )
    args = parser.parse_args()

    record_count, chunk_count = chunk_laws(args.input_dir, args.output)
    print(
        f"Đã xử lý {record_count} văn bản, tạo {chunk_count} chunks: "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()
