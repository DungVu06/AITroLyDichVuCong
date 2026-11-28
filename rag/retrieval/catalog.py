"""Read-only overlay for official source snapshots and procedure dependencies."""

import hashlib
import json
import re
from pathlib import Path

from rag.core.config import PROJECT_ROOT
from rag.core.schemas import LegalBasisMetadata, SourceMetadata

DATA = PROJECT_ROOT / "data"
BASELINE = Path(__file__).with_name("source_versions.json")


def records(kind, data):
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((data / kind / "records").glob("*.json"))]


def procedure_catalog():
    return {r["id"]: r["procedure"]["name"] for r in records("procedure", DATA)}


def revision(record):
    # Ignore the observation timestamp when an identical law is crawled again.
    payload = dict(record, source={k: v for k, v in record["source"].items() if k != "crawled_at"})
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def number_key(code):
    return re.sub(r"^(?:thông tư|nghị định|nghị quyết|luật)\s*(?:số)?\s*", "", code.strip().casefold()).replace(" ", "")


def source_metadata(data=DATA, baseline=BASELINE):
    versions = json.loads(baseline.read_text(encoding="utf-8"))
    return inspect_versions(records("law", data), records("procedure", data), versions)


def inspect_versions(laws, procedures, versions):
    result = {}
    law_codes = {}
    for kind, items in (("law", laws), ("procedure", procedures)):
        for record in items:
            key = record["id"]
            source = record["source"]
            content = record.get("content", {})
            version = revision(record)
            meta = SourceMetadata(
                version=version,
                url=source.get("url"),
                effective_date=source.get("effective_date") or content.get("effective_date_raw"),
                observed_at=source.get("last_updated") or source.get("crawled_at"),
                scope=" · ".join(record["jurisdiction"].values()),
                validity=content.get("validity_raw") or record.get("version_control", {}).get("state"),
            )
            if versions.get(key) != version:
                meta.review.append(f"{key}: phiên bản nguồn khác mốc đối chứng, cần kiểm tra lại.")
            if kind == "law":
                law_codes[number_key(content.get("document_number", ""))] = key
                if (meta.validity or "").casefold() != "còn hiệu lực":
                    meta.review.append(f"{key}: {meta.validity or 'chưa xác minh hiệu lực'}.")
            else:
                related = record.get("relations", {})
                for base in related.get("legal_bases", []):
                    code = base.get("code", "").strip()
                    label = (code + " — " + base.get("name", "")).strip(" —")
                    meta.legal_bases.append(label)
                    law = result.get(law_codes.get(number_key(code)))
                    if law:
                        meta.legal_basis_metadata[label] = LegalBasisMetadata(
                            url=law.url,
                            effective_date=law.effective_date,
                            validity=law.validity,
                            review=list(law.review),
                        )
                        meta.review.extend(law.review)
                for benefit in related.get("related_benefits", []):
                    law_id = benefit["law_section_id"].partition("/")[0]
                    if law_id in result:
                        meta.review.extend(f"Kiểm tra lại phần quyền lợi ({benefit['law_section_id']}): {notice}"
                                           for notice in result[law_id].review)
                    else:
                        meta.review.append(f"{law_id}: thiếu bản nguồn cho quyền lợi liên quan.")
                if any(number_key(b.get("code", "")) not in law_codes
                       for b in related.get("legal_bases", [])):
                    meta.review.append("Một số căn cứ do thủ tục liệt kê chưa được đối chiếu hiệu lực.")
            meta.review = list(dict.fromkeys(meta.review))
            result[key] = meta
    return result
