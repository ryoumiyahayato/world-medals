"""Merge the official Irish Defence Forces book's text-only variants."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/unpictured/ireland_defence_forces_medals_2010.json"
TARGET = ROOT / "data/unpictured.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    signatures = {(row["family"], row.get("known_grade", "")) for row in target}
    added = 0
    for item in source["items"]:
        known_grade = f"{item['variant']}；官方图册第{item['pdf_page']}页文字记录"
        signature = (item["family"], known_grade)
        if signature in signatures:
            continue
        target.append(
            {
                "family": item["family"],
                "name": item["name"],
                "original": item["original"],
                "date": "待考",
                "known_grade": known_grade,
                "category": "主编",
                "source_ids": ["IE-DF-MEDALS-2010"],
                "reason": item["reason"],
            }
        )
        signatures.add(signature)
        added += 1
    TARGET.write_text(json.dumps(target, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"appended={added} total_unpictured={len(target)}")


if __name__ == "__main__":
    main()
