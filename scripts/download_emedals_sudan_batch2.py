"""Download the complete eMedals Sudan batch-2 product image sets."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/raw_candidates/emedals_sudan_catalog.jsonl"
RAW = ROOT / "assets/raw/sudan_emedals"
CONTACT = ROOT / "sources/pages/emedals_sudan_catalog/batch2_contact.jpg"
RAW_CANDIDATES = ROOT / "data/raw_candidates/emedals_sudan.jsonl"
SWEEP = ROOT / "data/source_sweeps/emedals_sudan_batch2_2026-09-27.json"
HANDLES = {
    "an-english-made-order-of-the-sudanese-republic-w1625",
    "sudan-republic-a-set-of-three-medals-for-conscientious-work-w7547rl1",
    "sudan-republic-an-order-of-sport-ii-class-merit-medal-w6371",
    "sudan-republic-order-of-the-two-niles-i-class-grand-badge-by-spink-son-ltd-c1965-w8804",
    "sudan-republic-police-long-and-distinguished-service-order-w6190",
}
HEADERS = {"User-Agent": "world-medals research catalogue/1.0"}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in CATALOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = [row for row in rows if row["handle"] in HANDLES]
    if len(selected) != len(HANDLES):
        raise SystemExit(f"expected {len(HANDLES)} products, got {len(selected)}")

    downloaded: list[tuple[str, Path]] = []
    for row in selected:
        item = row["handle"].rsplit("-", 1)[-1].upper()
        for index, url in enumerate(row["image_original_urls"], start=1):
            suffix = Path(urlparse(url).path).suffix or ".jpg"
            target = RAW / f"{item}_{index:02d}{suffix}"
            if not target.exists():
                with urlopen(Request(url, headers=HEADERS), timeout=60) as response:
                    target.write_bytes(response.read())
            with Image.open(target) as image:
                image.verify()
            downloaded.append((f"{item} {index}", target))

    thumb_w, thumb_h = 220, 220
    columns = 5
    rows_count = (len(downloaded) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * thumb_w, rows_count * (thumb_h + 28)), "white")
    draw = ImageDraw.Draw(canvas)
    for number, (label, path) in enumerate(downloaded):
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8))
            x = (number % columns) * thumb_w + (thumb_w - image.width) // 2
            y = (number // columns) * (thumb_h + 28) + (thumb_h - image.height) // 2
            canvas.paste(image, (x, y))
            draw.text(((number % columns) * thumb_w + 4, (number // columns) * (thumb_h + 28) + thumb_h + 4), label, fill="black")
    canvas.save(CONTACT, quality=88)
    existing = [json.loads(line) for line in RAW_CANDIDATES.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_url = {row.get("page_url"): row for row in existing}
    for row in selected:
        item = row["handle"].rsplit("-", 1)[-1].lower()
        product_url = row["product_url"]
        by_url[product_url] = {
            "source_id": f"emedals-{item}",
            "source_system": "eMedals Sudan collection sweep",
            "scope": "Republic of Sudan",
            "page_title": row["title"],
            "page_url": product_url,
            "candidate_name": row["title"],
            "grade_material_clues": row["description"],
            "image_urls": row["image_original_urls"],
            "local_raw_images": [
                f"assets/raw/sudan_emedals/{item.upper()}_{index:02d}{Path(urlparse(url).path).suffix or '.jpg'}"
                for index, url in enumerate(row["image_original_urls"], start=1)
            ],
            "status": "PROMOTED_FORMAL_VARIANT",
            "notes": "Full product image set downloaded and decoded; only reviewed complete-object views or complete-object crops are used in formal rows.",
            "access_date": "2026-09-27",
        }
    ordered = sorted(by_url.values(), key=lambda row: (row.get("source_id", ""), row.get("page_url", "")))
    RAW_CANDIDATES.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ordered), encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source_id": "emedals_sudan_batch2",
        "status": "completed_bounded_item_batch_from_completed_collection_sweep",
        "item_handles": sorted(HANDLES),
        "product_pages": len(selected),
        "images_downloaded_and_decoded": len(downloaded),
        "formal_rows_added": 8,
        "formal_complete_views_added": 16,
        "pending_variants_resolved": 3,
        "new_pictured_families_added": 3,
        "notes": "Conscientious Work grades and Police LDSO full/mini rows use complete-object crops from source group photographs; source originals remain archived.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"downloaded/verified {len(downloaded)} files; contact sheet {CONTACT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
