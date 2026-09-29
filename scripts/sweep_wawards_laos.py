from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://wawards.org"
SOURCES = [
    ("kingdom", "order-of-a-million-elephants-and-white-parasol", "https://wawards.org/en/laos/kingdom-of-laos/order-of-a-million-elephants-and-white-parasol.html", ROOT / "sources/pages/wawards_laos_million_elephants.html"),
    ("kingdom", "order-of-feminine-merit", "https://wawards.org/en/laos/kingdom-of-laos/order-of-feminine-merit.html", ROOT / "sources/pages/wawards_laos_feminine_merit.html"),
    ("republic", "order-for-victory-in-the-revolution", "https://wawards.org/en/laos/people-s-republic-of-laos/order-for-victory-in-the-revolution.html", ROOT / "sources/pages/wawards_laos_victory_revolution.html"),
]
RAW_DIR = ROOT / "assets/raw/wawards_laos"
RAW_OUT = ROOT / "data/raw_candidates/wawards_laos.jsonl"
SWEEP_OUT = ROOT / "data/source_sweeps/wawards_laos_2026-09-28.json"


def download(url: str, target: Path) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["curl.exe", "-L", "--fail", "--retry", "2", "--connect-timeout", "20", "--max-time", "90", "-A", "Mozilla/5.0", "-o", str(target), url], cwd=ROOT, capture_output=True)
    return result.returncode == 0 and target.exists() and target.stat().st_size > 0


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records, failures = [], []
    for polity, slug, page_url, page_path in SOURCES:
        body = page_path.read_text(encoding="utf-8", errors="replace")
        image_urls = []
        for href in re.findall(r'href="([^"]*/images/laos/[^"]+\.(?:jpg|jpeg|png))"', body, re.I):
            absolute = urljoin(BASE, href)
            if absolute not in image_urls:
                image_urls.append(absolute)
        local_images = []
        for image_no, image_url in enumerate(image_urls, 1):
            suffix = Path(urlparse(image_url).path).suffix.lower() or ".jpg"
            target = RAW_DIR / f"{polity}__{slug}_{image_no:02d}{suffix}"
            if not target.exists() and not download(image_url, target):
                failures.append({"url": image_url, "stage": "image"})
                continue
            with Image.open(target) as decoded:
                decoded.verify()
            with Image.open(target) as decoded:
                width, height = decoded.size
            local_images.append({"view_no": image_no, "image_url": image_url, "local_path": target.relative_to(ROOT).as_posix(), "width": width, "height": height, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        title = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
        title = re.sub(r"\s+", " ", title.group(1)).strip() if title else slug.replace("-", " ").title()
        records.append({"source_id": f"wawards-laos-{polity}-{slug}", "historical_polity": polity, "page_title": title, "working_name_zh": "待归并", "name_original": title, "name_en": title, "date_candidates": [], "category": "order", "grade_material_clues": "待核", "object_url": page_url, "image_page_url": page_url, "original_images": local_images, "notes": "Complete currently listed Wawards Laos object page.", "status": "harvested" if local_images else "UNPICTURED"})
    RAW_OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    report = {"source_id": "wawards_laos_current_lists", "accessed": date.today().isoformat(), "scope": "Both current Wawards Laos list pages and every linked award object page and image", "status": "complete" if not failures and len(records) == 3 else "partial", "planned_object_pages": 3, "processed_object_pages": len(records), "downloaded_images": sum(len(r["original_images"]) for r in records), "failures": failures, "raw_output": RAW_OUT.relative_to(ROOT).as_posix()}
    SWEEP_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
