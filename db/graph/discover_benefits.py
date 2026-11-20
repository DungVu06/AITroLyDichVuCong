"""Generate reviewable procedure-to-benefit candidates from normalized data.

The pipeline uses broad legal-benefit cues for candidate recall, then Gemini
Flash for evidence-grounded extraction and pair verification. It
never writes to Neo4j. Review records are JSONL and remain pending until edited
to ``approved``.

Example::

    python -m db.graph.discover_benefits --top-k 30
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from rag.core.config import PROJECT_ROOT, load_env_file


PROMPT_VERSION = "benefit-discovery-v2-cues-bm25"
CUE_GROUPS = {
    "entitlement": ("có quyền", "được hưởng", "được nhận", "được cấp", "được hưởng chế độ"),
    "payment_support": ("trợ cấp", "được hỗ trợ", "được thanh toán", "được hoàn trả", "bồi thường"),
    "exemption_reduction": ("được miễn", "được giảm", "không phải nộp", "miễn nộp", "giảm trừ"),
    "priority_guarantee": ("được ưu tiên", "được bảo lưu", "được bố trí", "được bảo đảm"),
    "benefit_details": ("đối tượng hưởng", "điều kiện hưởng", "mức hưởng", "thời gian hưởng", "thời hạn hưởng"),
}
STRONG_CUE_GROUPS = {"entitlement", "payment_support", "exemption_reduction", "priority_guarantee"}
STOP_WORDS = set("và của là cho người các được trong với theo khi thì hoặc về tại từ một những đó này có phải như đến đã sẽ không nếu đối với".split())
TOKEN_RE = re.compile(r"[\w]+", flags=re.UNICODE)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BenefitSectionExtraction(StrictModel):
    section_id: str
    category: Literal[
        "benefit_rule", "eligibility", "amount_or_duration",
        "application_process", "exception", "cross_reference",
        "non_benefit", "insufficient_context",
    ]
    is_benefit_related: bool
    benefit_title: str | None = None
    benefit_type: str | None = None
    beneficiaries: list[str] = Field(default_factory=list)
    trigger: str | None = None
    conditions: list[str] = Field(default_factory=list)
    amount_or_duration: str | None = None
    evidence_quotes: list[str] = Field(default_factory=list)
    field_evidence: dict[str, list[str]] = Field(default_factory=dict)
    rationale: str


class BenefitSectionExtractionBatch(StrictModel):
    items: list[BenefitSectionExtraction]


class ProcedureBenefitMatch(StrictModel):
    is_related: bool
    relation_basis: Literal[
        "explicit_procedure_reference", "same_life_event",
        "same_target_group", "access_path", "other", "insufficient_evidence",
    ]
    reason: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def read_records(directory: Path, pattern: str) -> list[dict[str, Any]]:
    return [read_json(path) for path in sorted(directory.glob(pattern))]


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def norm(value: str) -> str:
    value = unicodedata.normalize("NFC", value).casefold()
    return re.sub(r"\s+", " ", value).strip()


def hash_key(*parts: str) -> str:
    payload = "\0".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def section_identifier(law_id: str, section: dict[str, Any], index: int) -> str:
    return clean(section.get("normalized_id")) or f"{law_id}:section:{index:04d}"


def procedure_query(record: dict[str, Any]) -> str:
    procedure = record.get("procedure") or {}
    parts = [
        clean(procedure.get("name")),
        clean(procedure.get("eligibility")),
        clean(record.get("domain")),
        " ".join(clean(x) for x in record.get("life_event", []) if clean(x)),
        " ".join(clean(x) for x in record.get("target_audience", []) if clean(x)),
    ]
    return "\n".join(part for part in parts if part)


def section_context(
    section: dict[str, Any], sections_by_id: dict[str, dict[str, Any]],
) -> str:
    parent_id = clean(section.get("parent_section_id"))
    ancestors: list[str] = []
    seen: set[str] = set()
    while parent_id and parent_id in sections_by_id and parent_id not in seen and len(ancestors) < 4:
        seen.add(parent_id)
        parent = sections_by_id[parent_id]
        heading = clean(parent.get("heading"))
        if heading:
            ancestors.append(heading)
        parent_id = clean(parent.get("parent_section_id"))
    return " > ".join(reversed(ancestors))


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value or "").casefold()
    return re.sub(r"\s+", " ", value).strip()


def matched_benefit_cues(section: dict[str, Any]) -> list[dict[str, str]]:
    heading = normalize_text(clean(section.get("heading")))
    body = normalize_text(clean(section.get("text")))
    full = f"{heading}\n{body}"
    matches = []
    for group, cues in CUE_GROUPS.items():
        for cue in cues:
            if cue in full:
                matches.append({"group": group, "cue": cue, "in_heading": cue in heading})
    # Broad terms only recall a section when accompanied by another benefit
    # signal in the heading/body, reducing matches on generic agency duties.
    strong = any(item["group"] in STRONG_CUE_GROUPS for item in matches)
    if not strong:
        return [item for item in matches if item["in_heading"] and item["group"] == "benefit_details"]
    return matches


def bm25_tokens(value: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(normalize_text(value))
            if len(token) > 1 and token not in STOP_WORDS]


def bm25_scores(query: str, documents: dict[str, str], k1: float = 1.5, b: float = 0.75) -> dict[str, float]:
    """Small dependency-free BM25 implementation over benefit candidates."""
    query_terms = set(bm25_tokens(query))
    tokenized = {key: bm25_tokens(value) for key, value in documents.items()}
    if not tokenized:
        return {}
    average_length = sum(map(len, tokenized.values())) / len(tokenized)
    frequencies: dict[str, int] = {}
    for tokens in tokenized.values():
        for term in set(tokens):
            frequencies[term] = frequencies.get(term, 0) + 1
    count = len(tokenized)
    scores = {}
    for key, tokens in tokenized.items():
        length = len(tokens)
        score = 0.0
        for term in query_terms:
            tf = tokens.count(term)
            if not tf:
                continue
            df = frequencies.get(term, 0)
            idf = math.log(1 + (count - df + 0.5) / (df + 0.5))
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * length / max(average_length, 1)))
        scores[key] = round(score, 6)
    return scores


def load_cache(path: Path) -> tuple[dict[str, dict[str, Any]], Any]:
    cache: dict[str, dict[str, Any]] = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    item = json.loads(line)
                    cache[str(item["key"])] = item["value"]
    path.parent.mkdir(parents=True, exist_ok=True)
    return cache, path.open("a", encoding="utf-8")


def load_existing_reviews(path: Path) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return existing
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid review JSONL at {path}:{line_number}") from exc
            if isinstance(record, dict) and record.get("candidate_id"):
                existing[str(record["candidate_id"])] = record
    return existing


def call_structured(client: Any, model: str, prompt: str, schema: type[BaseModel]) -> BaseModel:
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": schema.model_json_schema(),
        },
    )
    if not interaction.output_text:
        raise RuntimeError("Gemini returned an empty response")
    return schema.model_validate_json(interaction.output_text)


def section_batch_prompt(items: list[tuple[dict[str, Any], dict[str, Any], str]]) -> str:
    payload = []
    for law, section, context in items:
        content = law.get("content") or {}
        payload.append({
            "section_id": section["id"],
            "law_title": clean(content.get("title")),
            "law_number": clean(content.get("document_number")),
            "heading": clean(section.get("heading")),
            "parent_context": context,
            "section_text": clean(section.get("text")),
            "matched_cues": section.get("matched_cues", []),
        })
    return f"""Bạn phân loại các section pháp luật tiếng Việt để xây danh mục chế độ quyền lợi.
Mỗi item là một section độc lập. Chỉ căn cứ vào văn bản được cung cấp; không dùng kiến thức ngoài.
Trả field_evidence cho beneficiaries, trigger, conditions, amount_or_duration, benefit_type:
mỗi giá trị không rỗng phải có ít nhất một quote nguyên văn hỗ trợ từ section_text. Không có
căn cứ thì để trường rỗng. benefit_title có thể diễn đạt ngắn gọn nhưng phải được evidence_quotes
hỗ trợ trực tiếp. Có thể tách nhiều quyền lợi khác nhau; không lặp cùng một quyền lợi trong item.
Phân biệt quyền lợi với trách nhiệm cơ quan, thủ tục và dẫn chiếu. Nếu không đủ căn cứ, chọn
insufficient_context hoặc non_benefit. Trả đúng một kết quả cho mỗi section_id.
Trả đúng một kết quả cho mỗi section_id được cung cấp, không bỏ và không tự thêm ID.

SECTIONS: {json.dumps(payload, ensure_ascii=False)}
"""


def match_prompt(
    procedure: dict[str, Any], benefit: dict[str, Any], evidence: list[dict[str, Any]],
) -> str:
    record = procedure["record"]
    detail = record.get("procedure") or {}
    proc_context = {
        "name": clean(detail.get("name")),
        "eligibility": clean(detail.get("eligibility")),
        "domain": clean(record.get("domain")),
        "life_event": record.get("life_event") or [],
        "target_audience": record.get("target_audience") or [],
    }
    evidence_payload = [
        {"evidence_id": item["evidence_id"], "quote": item["quote"],
         "section_heading": item["heading"], "law_title": item["law_title"]}
        for item in evidence
    ]
    return f"""Xác định xem chế độ quyền lợi này có đáng gợi ý cùng thủ tục hành chính không.
Chỉ dùng thông tin thủ tục, quyền lợi và evidence bên dưới. Cùng life_event đơn thuần
không đủ để khẳng định liên hệ; nếu không có cơ sở rõ, đặt is_related=false.
Đây là gợi ý liên quan, không phải kết luận người dân đủ điều kiện hưởng.
supporting_evidence_ids chỉ gồm evidence_id được cung cấp và thực sự hỗ trợ lý do.

PROCEDURE: {json.dumps(proc_context, ensure_ascii=False)}
BENEFIT: {json.dumps(benefit, ensure_ascii=False)}
EVIDENCE: {json.dumps(evidence_payload, ensure_ascii=False)}
"""


def verified_field_values(result: BenefitSectionExtraction, section_text: str) -> dict[str, Any]:
    """Keep extracted values only when their supplied quotes support them."""
    fields = ("beneficiaries", "trigger", "conditions", "amount_or_duration", "benefit_type")
    normalized_text = normalize_text(section_text)
    values: dict[str, Any] = {}
    field_quotes: dict[str, list[str]] = {}
    for field_name in fields:
        raw = getattr(result, field_name)
        candidates = raw if isinstance(raw, list) else ([raw] if raw else [])
        quotes = result.field_evidence.get(field_name, [])
        valid_values = []
        valid_quotes = []
        for value in candidates:
            value_norm = normalize_text(clean(value))
            for quote in quotes:
                quote_norm = normalize_text(clean(quote))
                if quote_norm and quote_norm in normalized_text and value_norm and value_norm in quote_norm:
                    valid_values.append(clean(value))
                    valid_quotes.append(clean(quote))
                    break
        values[field_name] = list(dict.fromkeys(valid_values)) if isinstance(raw, list) else (valid_values[0] if valid_values else None)
        field_quotes[field_name] = list(dict.fromkeys(valid_quotes))
    values["field_evidence"] = field_quotes
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--procedure-dir", type=Path, default=PROJECT_ROOT / "data/procedure/normalized_records")
    parser.add_argument("--law-dir", type=Path, default=PROJECT_ROOT / "data/law/normalized_records")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/benefit_relation/discovery_review.jsonl")
    parser.add_argument("--cache", type=Path, default=PROJECT_ROOT / "data/benefit_relation/discovery.cache.jsonl")
    parser.add_argument("--top-k", type=int, default=30, help="Maximum BM25-ranked benefits per procedure")
    parser.add_argument("--max-sections", type=int, default=0, help="Optional cap for trial runs; 0 means no cap")
    args = parser.parse_args()

    load_env_file()
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY or GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_BENEFIT_MODEL", "gemini-3.8-flash").strip()
    procedures = read_records(args.procedure_dir, "PROC_*.json")
    laws = read_records(args.law_dir, "LAW_*.json")
    if not procedures or not laws:
        raise SystemExit("Both normalized procedure and law directories must contain records")

    sections: dict[str, dict[str, Any]] = {}
    law_by_section: dict[str, dict[str, Any]] = {}
    sections_by_law: dict[str, dict[str, dict[str, Any]]] = {}
    for law in laws:
        law_id = clean(law.get("id"))
        content = law.get("content") or {}
        by_id: dict[str, dict[str, Any]] = {}
        for index, section in enumerate(content.get("sections") or []):
            if not isinstance(section, dict):
                continue
            section_id = section_identifier(law_id, section, index)
            item = {**section, "id": section_id, "law_id": law_id, "order": index}
            sections[section_id] = item
            law_by_section[section_id] = law
            by_id[section_id] = item
        sections_by_law[law_id] = by_id

    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit(
            "Gemini SDK is unavailable in this Python environment. "
            "Activate the project venv, then run: "
            "python -m pip install google-genai==2.23.0"
        ) from exc

    cache, cache_handle = load_cache(args.cache)
    prior_reviews = load_existing_reviews(args.output)
    client = genai.Client(api_key=api_key)
    section_candidates: set[str] = set()
    cue_provenance: dict[str, list[dict[str, str]]] = {}
    for sid, section in sections.items():
        cues = matched_benefit_cues(section)
        if cues:
            section_candidates.add(sid)
            cue_provenance[sid] = cues
    # If a parent heading announces a benefit, inspect its descendants too;
    # eligibility and amounts are often stated in separate child sections.
    for sid in list(section_candidates):
        parent_heading_has_cue = cue_provenance[sid] and any(item["in_heading"] for item in cue_provenance[sid])
        if parent_heading_has_cue:
            for child_id, child in sections.items():
                ancestor_id = clean(child.get("parent_section_id"))
                seen: set[str] = set()
                while ancestor_id and ancestor_id in sections and ancestor_id not in seen:
                    if ancestor_id == sid:
                        section_candidates.add(child_id)
                        cue_provenance.setdefault(child_id, [{"group": "inherited_heading", "cue": sid, "in_heading": False}])
                        break
                    seen.add(ancestor_id)
                    ancestor_id = clean(sections[ancestor_id].get("parent_section_id"))

    try:
        if args.max_sections:
            section_candidates = set(sorted(section_candidates)[:args.max_sections])

        extracted: dict[str, dict[str, Any]] = {}
        uncached: list[tuple[str, str]] = []
        for section_id in sorted(section_candidates):
            section = sections[section_id]
            law = law_by_section[section_id]
            parent_context = section_context(section, sections_by_law[section["law_id"]])
            key = hash_key(PROMPT_VERSION, model_name, section_id, clean(section.get("text")), clean(section.get("heading")), parent_context)
            if key in cache:
                result = BenefitSectionExtraction.model_validate(cache[key])
                results = [result]
            else:
                uncached.append((section_id, key))
                continue

            for item in results:
                if item.section_id == section_id:
                    extracted[section_id] = item.model_dump(mode="json")

        # Batch independent sections to reduce API overhead. Cache each result
        # independently so a changed law only invalidates its own section.
        for start in range(0, len(uncached), 8):
            batch = uncached[start:start + 8]
            prompt_items = []
            for section_id, _key in batch:
                section = sections[section_id]
                law = law_by_section[section_id]
                prompt_items.append((law, section, section_context(section, sections_by_law[section["law_id"]])))
            response = call_structured(client, model_name, section_batch_prompt(prompt_items), BenefitSectionExtractionBatch)
            by_id = {item.section_id: item for item in response.items}
            for section_id, key in batch:
                result = by_id.get(section_id)
                if result is None:
                    # A missing item is a model contract error; fail rather than
                    # silently dropping a potentially relevant legal section.
                    raise ValueError(f"Gemini omitted section {section_id} from a classification batch")
                cache[key] = result.model_dump(mode="json")
                cache_handle.write(json.dumps({"key": key, "value": cache[key]}, ensure_ascii=False) + "\n")
                cache_handle.flush()
                extracted[section_id] = result.model_dump(mode="json")

        validated_extractions: dict[str, dict[str, Any]] = {}
        for section_id, result_data in extracted.items():
            section = sections[section_id]
            result = BenefitSectionExtraction.model_validate(result_data)
            law = law_by_section[section_id]
            section_text = clean(section.get("text"))
            valid_quotes = [quote.strip() for quote in result.evidence_quotes
                            if quote.strip() and normalize_text(quote.strip()) in normalize_text(section_text)]
            if not result.is_benefit_related or result.category in {"non_benefit", "insufficient_context"}:
                continue
            if not result.benefit_title or not valid_quotes:
                continue
            verified_fields = verified_field_values(result, section_text)
            validated_extractions[section_id] = {
                **result.model_dump(mode="json"),
                **verified_fields,
                "evidence_quotes": valid_quotes,
                "section_id": section_id,
                "law_id": section["law_id"],
                "heading": clean(section.get("heading")),
                "law_title": clean((law.get("content") or {}).get("title")),
                "source_url": clean((law.get("source") or {}).get("url")),
                "life_events": law.get("life_event") or [],
                "cue_provenance": cue_provenance.get(section_id, []),
            }
        extracted = validated_extractions

        grouped: dict[str, dict[str, Any]] = {}
        for extracted_item in extracted.values():
            benefit_key = norm(extracted_item["benefit_title"])
            group = grouped.setdefault(benefit_key, {
                "benefit_id": "BEN_" + hash_key(benefit_key)[:16],
                "benefit_title": extracted_item["benefit_title"].strip(),
                "benefit_type": extracted_item.get("benefit_type"),
                "beneficiaries": [], "triggers": [], "conditions": [],
                "amount_or_duration": [], "evidence": [], "life_events": [],
            })
            group["beneficiaries"] = list(dict.fromkeys([*group["beneficiaries"], *extracted_item["beneficiaries"]]))
            group["triggers"] = list(dict.fromkeys([*group["triggers"], *([extracted_item["trigger"]] if extracted_item.get("trigger") else [])]))
            group["conditions"] = list(dict.fromkeys([*group["conditions"], *extracted_item["conditions"]]))
            group["amount_or_duration"] = list(dict.fromkeys([*group["amount_or_duration"], *([extracted_item["amount_or_duration"]] if extracted_item.get("amount_or_duration") else [])]))
            group["life_events"] = list(dict.fromkeys([
                *group["life_events"], *extracted_item["life_events"],
            ]))
            for quote_index, quote in enumerate(extracted_item["evidence_quotes"]):
                group["evidence"].append({
                    "evidence_id": f"{extracted_item['section_id']}#q{quote_index + 1}",
                    "section_id": extracted_item["section_id"],
                    "law_id": extracted_item["law_id"],
                    "heading": extracted_item["heading"],
                    "law_title": extracted_item["law_title"],
                    "quote": quote,
                    "source_url": extracted_item["source_url"],
                    "category": extracted_item["category"],
                    "field_evidence": extracted_item.get("field_evidence", {}),
                    "cue_provenance": extracted_item.get("cue_provenance", []),
                })

        procedure_lookup = {clean(record.get("id")): {"record": record, "query": procedure_query(record)} for record in procedures}
        review_records: list[dict[str, Any]] = []
        for procedure_id, procedure in procedure_lookup.items():
            proc_record = procedure["record"]
            proc_events = {norm(clean(x)) for x in proc_record.get("life_event", []) if clean(x)}
            benefit_documents = {
                benefit_id: " ".join([
                    benefit["benefit_title"], *benefit["beneficiaries"], *benefit["triggers"],
                    *benefit["conditions"], *benefit["amount_or_duration"],
                    " ".join(item["heading"] for item in benefit["evidence"]),
                ])
                for benefit_id, benefit in grouped.items()
            }
            scores = bm25_scores(procedure["query"], benefit_documents)
            ranked_ids = sorted(scores, key=lambda item: (-scores[item], item))
            selected_ids = set(sorted(
                (item for item in ranked_ids if scores[item] > 0),
                key=lambda item: (-scores[item], item),
            )[:args.top_k])
            for benefit_id, benefit in grouped.items():
                benefit_events = {norm(clean(x)) for x in benefit["life_events"] if clean(x)}
                same_event = bool(proc_events & benefit_events)
                if benefit_id not in selected_ids and not same_event:
                    continue
                match_key = hash_key(
                    PROMPT_VERSION, model_name, procedure_id, procedure["query"],
                    benefit["benefit_id"],
                    json.dumps(benefit, ensure_ascii=False, sort_keys=True, default=list),
                )
                if match_key in cache:
                    match = ProcedureBenefitMatch.model_validate(cache[match_key])
                else:
                    match = call_structured(client, model_name, match_prompt(procedure, benefit, benefit["evidence"]), ProcedureBenefitMatch)
                    cache[match_key] = match.model_dump(mode="json")
                    cache_handle.write(json.dumps({"key": match_key, "value": cache[match_key]}, ensure_ascii=False) + "\n")
                    cache_handle.flush()
                valid_evidence_ids = {item["evidence_id"] for item in benefit["evidence"]}
                supported_ids = [item for item in match.supporting_evidence_ids if item in valid_evidence_ids]
                if not match.is_related or not supported_ids:
                    continue
                rank = scores.get(benefit_id, 0.0)
                candidate_id = "CAND_" + hash_key(procedure_id, benefit["benefit_id"])[:16]
                candidate_record = {
                    "candidate_id": candidate_id,
                    "procedure_id": procedure_id,
                    "benefit_id": benefit["benefit_id"],
                    "benefit_title": benefit["benefit_title"],
                    "benefit_type": benefit["benefit_type"],
                    "beneficiaries": benefit["beneficiaries"],
                    "triggers": benefit["triggers"],
                    "conditions": benefit["conditions"],
                    "amount_or_duration": benefit["amount_or_duration"],
                    "aliases": [],
                    "status": "pending",
                    "relation_basis": match.relation_basis,
                    "reason": match.reason,
                    "supporting_evidence_ids": supported_ids,
                    "evidence": benefit["evidence"],
                    "ranking": {"score": rank, "bm25_score": rank, "same_life_event": same_event,
                                "matched_tokens": sorted(set(bm25_tokens(procedure["query"])) & set(bm25_tokens(benefit_documents[benefit_id]))),
                                "candidate_sources": [*(["bm25"] if rank > 0 else []), *(["same_life_event"] if same_event else [])]},
                    "pipeline_version": PROMPT_VERSION,
                    "model": model_name,
                }
                prior = prior_reviews.get(candidate_id)
                if prior:
                    if prior.get("benefit_title"):
                        candidate_record["benefit_title"] = prior["benefit_title"]
                    candidate_record["aliases"] = list(dict.fromkeys([
                        *candidate_record["aliases"], *[clean(x) for x in prior.get("aliases", []) if clean(x)],
                    ]))
                    prior_evidence = [
                        item for item in prior.get("evidence", [])
                        if isinstance(item, dict)
                        and clean(item.get("section_id")) in sections
                        and clean(item.get("quote"))
                        and clean(item.get("quote")) in clean(sections[clean(item.get("section_id"))].get("text"))
                    ]
                    current_evidence = {
                        (item["evidence_id"], item["quote"])
                        for item in candidate_record["evidence"]
                    }
                    previous_evidence = {
                        (clean(item.get("evidence_id")), clean(item.get("quote")))
                        for item in prior_evidence
                    }
                    evidence_unchanged = (
                        current_evidence == previous_evidence
                        and prior.get("reason") == candidate_record["reason"]
                        and prior.get("relation_basis") == candidate_record["relation_basis"]
                        and prior.get("benefit_title") == candidate_record["benefit_title"]
                    )
                    if evidence_unchanged:
                        candidate_record["status"] = prior.get("status", "pending")
                        candidate_record["evidence"] = prior_evidence
                        candidate_record["supporting_evidence_ids"] = [
                            clean(item.get("evidence_id")) for item in prior_evidence if clean(item.get("evidence_id"))
                        ]
                review_records.append(candidate_record)

        review_records.sort(key=lambda item: (-item["ranking"]["score"], item["procedure_id"], item["benefit_title"].casefold()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for item in review_records:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Discovered {len(extracted)} benefit-bearing sections; wrote {len(review_records)} review candidates to {args.output}")
    finally:
        cache_handle.close()


if __name__ == "__main__":
    main()
