"""Demonstrate a law-version change in memory using the local source records."""

from copy import deepcopy
import json

from rag.retrieval.catalog import BASELINE, DATA, inspect_versions, records


def main():
    laws = records("law", DATA)
    procedures = records("procedure", DATA)
    versions = json.loads(BASELINE.read_text(encoding="utf-8"))
    before = inspect_versions(laws, procedures, versions)
    law_id = next(b["law_section_id"].split("/")[0] for p in procedures
                  for b in p["relations"].get("related_benefits", []))
    updated = deepcopy(laws)
    law = next(item for item in updated if item["id"] == law_id)
    law["content"]["validity_raw"] = "Hết hiệu lực toàn bộ (mô phỏng)"
    after = inspect_versions(updated, procedures, versions)
    print("Mô phỏng trong bộ nhớ:", law_id)
    print("Phiên bản:", before[law_id].version[:12], "→", after[law_id].version[:12])
    for procedure in procedures:
        key = procedure["id"]
        added = [notice for notice in after[key].review if notice not in before[key].review]
        if added:
            print(procedure["procedure"]["name"], "—", " ".join(added))


if __name__ == "__main__":
    main()
