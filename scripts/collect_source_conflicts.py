"""Collect explicit source-sweep conflicts without re-researching each item."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_candidates"
OUT = ROOT / "data" / "conflicts" / "ottoman_source_conflicts_2026-09-26.jsonl"


def main() -> None:
    conflicts = []
    for path in sorted(RAW_DIR.glob("*_ottoman.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            flags = row.get("flags") or []
            if isinstance(flags, str):
                flags = [flags]
            status = str(row.get("status", ""))
            conflict_flags = [str(flag) for flag in flags if "CONFLICT" in str(flag).upper()]
            if "conflict" not in status.lower() and not conflict_flags:
                continue
            conflicts.append({
                "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "source_line": line_number,
                "source_id": row.get("source_id"),
                "page_title": row.get("page_title") or row.get("title") or row.get("title_guess"),
                "conflict_type": conflict_flags or [status],
                "date_candidates": row.get("date_candidates") or row.get("date_clues") or [],
                "page_url": row.get("page_url") or row.get("source_url") or row.get("product_url"),
                "resolution_status": "UNRESOLVED_SOURCE_SWEEP",
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        for row in conflicts:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"conflicts": len(conflicts), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
