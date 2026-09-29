"""Build the complete Egypt block from Spink auction 26001 (lots 322-324)."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "assets/raw/egypt_spink_26001"
IMAGE_DIR = ROOT / "assets/images/egypt_spink_26001"
VOLUME = ROOT / "data/volumes/egypt_spink26001.json"
MANIFEST = ROOT / "data/volumes/egypt_spink26001_manifest.json"
RAW_CANDIDATES = ROOT / "data/raw_candidates/spink26001_egypt.jsonl"
SWEEP = ROOT / "data/source_sweeps/spink26001_egypt_2026-09-27.json"

LOTS = [
    {
        "lot": 322,
        "id": "EGY-SPINK26001-NILE-SECOND-BICHAI-1934-35",
        "family": "MENA7-ORDER-OF-THE-NILE",
        "name": "尼罗河勋章",
        "original": "Order of the Nile",
        "date": "1934—1935年制作",
        "variant": "二等（大官级）套装；Bichai（开罗）制；颈章与星章；完整正面",
        "description": "Second Class set: neck Badge and breast Star; Bichai, Cairo; Cairo hallmarks 1934-35.",
    },
    {
        "lot": 323,
        "id": "EGY-SPINK26001-NILE-NECK-LATTES-1922-23",
        "family": "MENA7-ORDER-OF-THE-NILE",
        "name": "尼罗河勋章",
        "original": "Order of the Nile",
        "date": "1922—1923年制作",
        "variant": "颈章；Lattes（开罗）制；银、鎏金银及珐琅；完整正反面",
        "description": "Neck Badge by Lattes, Cairo; silver, silver-gilt and enamel; Cairo hallmarks 1922-23.",
    },
    {
        "lot": 324,
        "id": "EGY-SPINK26001-MERIT-FIRST-SET",
        "family": "MENA7-ORDER-OF-MERIT-EGYPT",
        "name": "埃及功绩勋章",
        "original": "Order of Merit",
        "date": "共和国时期；制作年代待考",
        "variant": "一等大绶套装；绶章与星章；银、鎏金银及珐琅；完整正面",
        "description": "First Class set: sash Badge and breast Star; silver, silver-gilt and enamel; both hallmarked.",
    },
]


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    images = []
    candidates = []
    for item in LOTS:
        lot = item["lot"]
        source = RAW_DIR / f"26001_{lot}_1.jpg"
        target = IMAGE_DIR / f"lot_{lot}.jpg"
        shutil.copy2(source, target)
        with Image.open(target) as image:
            dimensions = list(image.size)
            image.verify()
        view_key = f"EGY-SPINK26001-{lot}-V1"
        record = {
            "id": item["id"],
            "family": item["family"],
            "country_zh": "埃及",
            "name": item["name"],
            "original": item["original"],
            "date": item["date"],
            "variant": item["variant"],
            "views": [{"key": view_key, "label": "完整套装图" if lot != 323 else "完整正反面"}],
            "source_ids": ["spink_auction_26001_egypt"],
            "image_kind": "object_photo",
            "html_eligible": True,
        }
        records.append(record)
        page = f"https://www.spink.com/lot/26001000{lot}"
        image_url = f"https://d3ums4016ncdkp.cloudfront.net/auction/large/26001/26001_{lot}_1.jpg"
        images.append({
            "key": f"egypt-spink26001-{lot}",
            "record_id": item["id"],
            "view_key": view_key,
            "local_path": target.relative_to(ROOT).as_posix(),
            "source_page": page,
            "image_url": image_url,
            "artist": f"Spink & Son, auction 26001 lot {lot}",
            "license": "All rights reserved; retained for offline research catalogue",
            "dimensions": dimensions,
            "bytes": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "decoded": True,
            "visually_checked": True,
        })
        candidates.append({
            "source_id": "spink_auction_26001_egypt",
            "source_item_id": f"lot-{lot}",
            "page_title": f"Spink 26001 lot {lot} — {item['original']}",
            "working_name_zh": item["name"],
            "original_names": [item["original"]],
            "date_candidates": [item["date"]],
            "category": "formal order",
            "grades_or_classes": [item["variant"].split("；", 1)[0]],
            "grade_material_clues": item["description"],
            "object_page_url": page,
            "image_page_urls": [page],
            "original_image_urls": [image_url],
            "notes": "Complete Egypt block in the auction listing; image visually matched to the lot text.",
            "status": "NORMALIZED_AND_PICTURED",
        })

    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 · Spink 26001", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RAW_CANDIDATES.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source_id": "spink_auction_26001_egypt",
        "status": "completed_bounded_section",
        "boundary": "Complete auction 26001 catalogue listing checked; Egypt block lots 322-324 processed",
        "catalogue_entries_checked": 1,
        "egypt_lots_processed": 3,
        "images_downloaded_and_decoded": 3,
        "formal_rows_added": 3,
        "formal_views_added": 3,
        "result": "Two dated Kingdom-period Order of the Nile maker variants and one Republic Order of Merit first-class set promoted.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("built Spink 26001 Egypt block: 3 variants and 3 complete images")


if __name__ == "__main__":
    main()
