"""Publish exact-grade Sudan variants from individual Spink archive lots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/raw/spink_sudan/20003_1504_1.jpg"
DEST = ROOT / "assets/images/sudan_spink_archive/20003_1504_medal_merit_ii.jpg"
VOLUME = ROOT / "data/volumes/sudan_spink_archive_variants.json"
MANIFEST = ROOT / "data/volumes/sudan_spink_archive_variants_manifest.json"
RAW = ROOT / "data/raw_candidates/spink_sudan_archive_exact.jsonl"
SWEEP = ROOT / "data/source_sweeps/spink_sudan_archive_exact_2026-09-27.json"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as source:
        if source.size != (1100, 573):
            raise RuntimeError(f"Unexpected source geometry: {source.size}")
        # Lot order and description explicitly identify the first two objects
        # as Merit I and Merit II.  Keep the complete ribbon, suspension and
        # medal of the second object, without any adjacent award.
        crop_box = (285, 8, 550, 565)
        crop = source.crop(crop_box)
        crop.save(DEST, quality=95)
    with Image.open(DEST) as image:
        width, height = image.size
        image.verify()

    record_id = "SDN-SPINK-20003-1504-MERIT-II"
    view_key = record_id + "-VIEW-1"
    record = {
        "id": record_id,
        "family": "MENA7-MEDAL-FOR-MERIT",
        "country_zh": "苏丹",
        "name": "苏丹功绩奖章",
        "original": "Medal of Merit, II Class",
        "date": "苏丹民主共和国时期；2020年拍卖记录",
        "variant": "二等；银质；完整实物正面；由四件组图裁取",
        "views": [{"key": view_key, "label": "二等完整正面"}],
        "source_ids": ["spink-20003-lot1504"],
        "image_kind": "object_photo_crop",
        "html_eligible": True,
        "supersedes_id": "SDN-MB-PENDING-MEDAL-FOR-MERIT-II-CLASS",
    }
    image_row = {
        "key": view_key,
        "record_id": record_id,
        "view_key": view_key,
        "local_path": DEST.relative_to(ROOT).as_posix(),
        "source_id": "spink-20003-lot1504",
        "source_page": "https://spink.com/lot/20003001504",
        "source_original_url": "https://d3ums4016ncdkp.cloudfront.net/auction/large/20003/20003_1504_1.jpg",
        "image_kind": "object_photo_crop",
        "source_group_image": SOURCE.relative_to(ROOT).as_posix(),
        "crop_box_ltrb": list(crop_box),
        "width": width,
        "height": height,
        "sha256": hashlib.sha256(DEST.read_bytes()).hexdigest(),
        "visual_check": "complete ribbon, suspension and medal visible; adjacent awards excluded; source description identifies the second object as Medal of Merit II Class",
        "rights_note": "Spink auction archive photograph; retained for offline research catalogue use subject to source terms",
    }
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹：Spink拍卖档案明确等级补充", "records": [record]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "source": "Spink auction 20003 lot 1504", "images": [image_row]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raw_row = {
        "source_id": "spink-20003-lot1504",
        "source_system": "Spink auction archive",
        "scope": "Republic of Sudan",
        "page_title": "Sudan, Democratic Republic, Medal of Merit (2), 1st Class; 2nd Class; Medal of Independence (2)",
        "page_url": "https://spink.com/lot/20003001504",
        "candidate_names": ["Medal of Merit, I Class", "Medal of Merit, II Class", "Medal of Independence"],
        "image_urls": [image_row["source_original_url"]],
        "local_raw_images": [SOURCE.relative_to(ROOT).as_posix()],
        "crop_records": [{"candidate": "Medal of Merit, II Class", "box_ltrb": list(crop_box), "published": DEST.relative_to(ROOT).as_posix()}],
        "status": "PROMOTED_EXACT_VARIANT",
        "access_date": "2026-09-27",
    }
    RAW.write_text(json.dumps(raw_row, ensure_ascii=False) + "\n", encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source_id": "spink_20003_lot1504",
        "status": "completed_exact_lot",
        "lot_objects": 4,
        "published_new_variants": 1,
        "not_duplicated": ["Medal of Merit, I Class", "Medal of Independence (two examples)"],
        "source_page_cache": "sources/pages/spink_sudan/20003_1504.html",
        "source_image": SOURCE.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("published Spink 20003 lot 1504: Sudan Medal for Merit II Class")


if __name__ == "__main__":
    main()
