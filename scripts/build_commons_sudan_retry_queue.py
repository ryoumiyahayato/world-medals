"""Build a resumable thumbnail retry queue from the completed Sudan Commons sweep."""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/commons_sudan.jsonl"
OUT = ROOT / "data/image_harvest/commons_sudan_full_body_retry.json"


def thumbnail_url(url: str, width: int) -> str:
    clean = url.split("?", 1)[0]
    parsed = urllib.parse.urlparse(clean)
    marker = "/wikipedia/commons/"
    tail = parsed.path.split(marker, 1)[1]
    filename = tail.rsplit("/", 1)[-1]
    # Commons currently accepts only its standard thumbnail widths.
    target_width = 250 if width < 500 else (500 if width < 960 else 960)
    thumb_name = f"{target_width}px-{filename}"
    if filename.lower().endswith(".svg"):
        thumb_name += ".png"
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{tail}/{thumb_name}"


def main() -> None:
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    queue = []
    for row in rows:
        if not row.get("likely_object") or row.get("local_raw_image") or (row.get("height") or 0) < 150:
            continue
        queue.append({
            "source_id": row["source_id"], "file_title": row["file_title"],
            "page_title": row["page_title"], "page_url": row["page_url"],
            "original_image_url": row["original_image_url"],
            "thumbnail_retry_url": thumbnail_url(row["original_image_url"], int(row["width"])),
            "width": row["width"], "height": row["height"], "categories": row["categories"],
            "status": "DOWNLOAD_RETRY_PENDING",
        })
    OUT.write_text(json.dumps({
        "as_of": "2026-09-27", "source_sweep_status": "complete",
        "selection": "likely award object and height >= 150px; ribbon-only files excluded",
        "pending": queue,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"queued {len(queue)} complete-object candidates for thumbnail retry")


if __name__ == "__main__":
    main()
