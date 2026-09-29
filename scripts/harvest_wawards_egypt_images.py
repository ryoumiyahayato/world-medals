"""Extract and cache every Egypt object image linked by the completed Wawards sweep."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/wawards_egypt.jsonl"
OUT_DIR = ROOT / "assets/raw/wawards_egypt"
OUT_MANIFEST = ROOT / "data/image_harvest/wawards_egypt_all_images.json"
PATTERN = re.compile(r'(?:href|src)=["\'](/images/egypt/[^"\']+?\.(?:jpe?g|png|webp))["\']', re.I)


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "world-medals-research/1.0 (offline catalogue; respectful one-time cache)"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row.get("source_system") == "Wawards Egypt"]
    images = []
    failures = []
    for row in rows:
        html = (ROOT / row["cache_file"]).read_text(encoding="utf-8", errors="ignore")
        paths = sorted(set(PATTERN.findall(html)))
        for ordinal, remote_path in enumerate(paths, 1):
            url = "https://wawards.org" + remote_path
            suffix = Path(remote_path).suffix.lower() or ".jpg"
            filename = f"{row['source_id']}-{ordinal:02d}{suffix}"
            target = OUT_DIR / filename
            try:
                if not target.exists():
                    target.write_bytes(get(url))
                    time.sleep(0.35)
                payload = target.read_bytes()
                with Image.open(target) as image:
                    image.verify()
                with Image.open(target) as image:
                    dimensions = list(image.size)
                images.append({
                    "source_id": row["source_id"], "page_title": row["page_title"],
                    "page_url": row["page_url"], "image_url": url,
                    "local_path": target.relative_to(ROOT).as_posix(), "ordinal": ordinal,
                    "dimensions": dimensions, "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(), "decoded": True,
                    "visual_status": "pending_review",
                })
            except (OSError, urllib.error.URLError, ValueError) as exc:
                failures.append({"source_id": row["source_id"], "page_title": row["page_title"], "image_url": url, "error": str(exc)})
    report = {
        "schema": "world-medals.image_harvest.manifest.v1", "batch_id": "WAWARDS-EGYPT-ALL-20260927",
        "as_of": "2026-09-27", "source": "Wawards Egypt completed period indexes",
        "pages_processed": len(rows), "linked_images_found": len(images) + len(failures),
        "downloaded_and_decoded": len(images), "failures": failures, "images": images,
    }
    OUT_MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"pages={len(rows)} decoded={len(images)} failures={len(failures)}")


if __name__ == "__main__":
    main()
