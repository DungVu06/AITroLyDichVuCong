"""Thêm trường relations.related_benefit vào procedure normalized records.

Trường được thêm dưới dạng một mảng rỗng để người dùng điền thủ công.
Ví dụ sau khi điền:

    "relations": {
      "related_benefit": [
        {
          "law_section_id": "LAW_VBPL_xxx/part:B/section:I",
          "scope": "subtree",
          "note": "Chế độ trợ cấp liên quan"
        }
      ]
    }

Script không ghi đè trường related_benefit đã tồn tại.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]


def add_field(input_dir: Path, field_name: str = "related_benefit") -> tuple[int, int]:
    """Thêm field cho các file PROC_*.json và trả về (số file, số file thay đổi)."""
    paths = sorted(input_dir.glob("PROC_*.json"))
    if not paths:
        raise SystemExit(f"Không tìm thấy PROC_*.json trong {input_dir}")

    changed = 0
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            record: dict[str, Any] = json.load(handle)

        relations = record.setdefault("relations", {})
        if not isinstance(relations, dict):
            raise ValueError(f"Trường relations phải là object: {path}")

        if field_name in relations:
            if not isinstance(relations[field_name], list):
                raise ValueError(
                    f"Trường relations.{field_name} phải là array: {path}"
                )
            continue

        relations[field_name] = []
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        changed += 1

    return len(paths), changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=ROOT_DIR / "data" / "procedure" / "normalized_records",
        help="Thư mục chứa các file procedure normalized",
    )
    parser.add_argument(
        "--field-name",
        default="related_benefit",
        help="Tên field cần thêm trong object relations",
    )
    args = parser.parse_args()

    total, changed = add_field(args.input_dir, args.field_name)
    print(f"Đã kiểm tra {total} procedure records.")
    print(f"Đã thêm relations.{args.field_name} vào {changed} file.")
    print("Bạn có thể điền law_section_id và scope trong các file normalized records.")


if __name__ == "__main__":
    main()
