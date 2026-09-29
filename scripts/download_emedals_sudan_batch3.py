"""Cache and inspect the eMedals M0620-10 Sudan two-order group."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/raw_candidates/emedals_sudan_catalog.jsonl"
RAW = ROOT / "assets/raw/sudan_emedals"
CONTACT = ROOT / "sources/pages/emedals_sudan_catalog/batch3_contact.jpg"
SWEEP = ROOT / "data/source_sweeps/emedals_sudan_batch3_2026-09-27.json"
RAW_CANDIDATES = ROOT / "data/raw_candidates/emedals_sudan.jsonl"
HANDLE = "two-orders-and-decorations-m0620-10"


def main() -> None:
    rows = [json.loads(line) for line in CATALOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    row = next(item for item in rows if item["handle"] == HANDLE)
    paths = []
    for index, url in enumerate(row["image_original_urls"], start=1):
        suffix = Path(urlparse(url).path).suffix or ".jpg"
        target = RAW / f"M0620-10_{index:02d}{suffix}"
        if not target.exists():
            with urlopen(Request(url, headers={"User-Agent": "world-medals research catalogue/1.0"}), timeout=60) as response:
                target.write_bytes(response.read())
        with Image.open(target) as image:
            image.verify()
        paths.append(target)

    canvas = Image.new("RGB", (1000, 280), "white")
    draw = ImageDraw.Draw(canvas)
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((320, 240))
            x = index * 333 + (333 - image.width) // 2
            y = (240 - image.height) // 2
            canvas.paste(image, (x, y))
            draw.text((index * 333 + 8, 250), f"M0620-10 image {index + 1}", fill="black")
    canvas.save(CONTACT, quality=90)
    existing = [json.loads(line) for line in RAW_CANDIDATES.read_text(encoding="utf-8").splitlines() if line.strip()]
    product_url = row["product_url"]
    candidate = {
        "source_id": "emedals-m0620-10",
        "source_system": "eMedals Sudan collection sweep",
        "scope": "Republic of Sudan",
        "page_title": row["title"],
        "page_url": product_url,
        "candidate_name": "Order of Civil Accomplishment and Order of Political Accomplishment",
        "grade_material_clues": row["description"],
        "image_urls": row["image_original_urls"],
        "local_raw_images": [path.relative_to(ROOT).as_posix() for path in paths],
        "status": "PROMOTED_FORMAL_VARIANTS",
        "notes": "Both named orders were isolated as complete front and reverse crops from the retained source group photographs.",
        "access_date": "2026-09-27"
    }
    by_url = {item.get("page_url"): item for item in existing}
    by_url[product_url] = candidate
    RAW_CANDIDATES.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in sorted(by_url.values(), key=lambda item: item.get("source_id", ""))), encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source_id": "emedals_sudan_batch3",
        "status": "completed_bounded_item_batch",
        "item": "M0620-10",
        "title": row["title"],
        "product_url": row["product_url"],
        "description": row["description"],
        "images_downloaded_and_decoded": len(paths),
        "local_raw_images": [path.relative_to(ROOT).as_posix() for path in paths],
        "formal_rows_added": 2,
        "formal_complete_views_added": 4,
        "new_families_added": 0,
        "notes": "Civil Accomplishment and Political Accomplishment are existing families; each complete object was cropped from the shared front and reverse group photographs while originals were preserved.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"downloaded/verified {len(paths)} M0620-10 images")


if __name__ == "__main__":
    main()
