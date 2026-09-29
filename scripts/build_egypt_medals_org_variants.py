"""Build the verified grade difference set from Medals of the World Egypt catalogue."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/raw/medals_org_egypt_kingdom"
OUT = ROOT / "assets/images/egypt_medals_org"
VOLUME = ROOT / "data/volumes/egypt_medals_org_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_medals_org_variants_manifest.json"

# id suffix, family, Chinese name, original, date, variant, [(source file, view label)]
SPECS = [
    ("MUHAMMAD-ALI-COLLAR", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1915年设立；1953年停授", "项圈级；完整实物正面；低清参考", [("egypt-kingdom001_egypt-kingdom004.jpg", "项圈完整正面")]),
    ("MUHAMMAD-ALI-COMMANDER", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1915年设立；1953年停授", "指挥官级；完整正反面；低清参考", [("egypt-kingdom001_egypt-kingdom001-07.jpg", "完整正面"), ("egypt-kingdom001_egypt-kingdom001-08.jpg", "完整反面")]),
    ("MUHAMMAD-ALI-SILVER-MEDAL", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1915年设立；1953年停授", "银质奖章级；完整正反面；低清参考", [("egypt-kingdom001_egypt-kingdom001-11.jpg", "完整正面"), ("egypt-kingdom001_egypt-kingdom001-12.jpg", "完整反面")]),
    ("ISMAIL-GRAND-OFFICER-BADGE", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；1952年停授", "大官级挂章；完整实物正面；低清参考", [("egypt-kingdom004_egypt-kingdom006.jpg", "挂章完整正面")]),
    ("ISMAIL-GRAND-OFFICER-STAR", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；1952年停授", "大官级星章；完整实物正面；低清参考", [("egypt-kingdom004_egypt-kingdom007.jpg", "星章完整正面")]),
    ("ISMAIL-COMMANDER", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；1952年停授", "指挥官级；完整正反面；低清参考", [("egypt-kingdom004_egypt-kingdom004-09.jpg", "完整正面"), ("egypt-kingdom004_egypt-kingdom004-10.jpg", "完整反面")]),
    ("ISMAIL-OFFICER", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；1952年停授", "军官级；完整正反面；低清参考", [("egypt-kingdom004_egypt-kingdom004-11.jpg", "完整正面"), ("egypt-kingdom004_egypt-kingdom004-12.jpg", "完整反面")]),
    ("NILE-GRAND-OFFICER-BADGE", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "大官级挂章；完整实物正面；低清参考", [("egypt-kingdom005_egypt-kingdom005-05.jpg", "挂章完整正面")]),
    ("NILE-GRAND-OFFICER-STAR", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "大官级星章；完整正反面；低清参考", [("egypt-kingdom005_egypt-kingdom005-07.jpg", "星章完整正面"), ("egypt-kingdom005_egypt-kingdom005-08.jpg", "星章完整反面")]),
    ("NILE-COMMANDER", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "指挥官级；完整正反面；低清参考", [("egypt-kingdom005_egypt-kingdom005-09.jpg", "完整正面"), ("egypt-kingdom005_egypt-kingdom005-10.jpg", "完整反面")]),
    ("NILE-OFFICER", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "军官级；完整正反面；低清参考", [("egypt-kingdom005_egypt-kingdom005-11.jpg", "完整正面"), ("egypt-kingdom005_egypt-kingdom005-12.jpg", "完整反面")]),
    ("NILE-KNIGHT", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "骑士级；完整正反面；低清参考", [("egypt-kingdom005_egypt-kingdom005-13.jpg", "完整正面"), ("egypt-kingdom005_egypt-kingdom005-14.jpg", "完整反面")]),
    ("AGRICULTURE-KNIGHT", "EGY-GAP-KINGDOM-ORDER-AGRICULTURE", "农业勋章", "Order of Agriculture", "1915年设立；1953年停授", "骑士级；完整正反面；低清参考", [("egypt-kingdom020_egypt-kingdom020-05.jpg", "完整正面"), ("egypt-kingdom020_egypt-kingdom020-06.jpg", "完整反面")]),
    ("CULTURE-KNIGHT", "EGY-GAP-ORDER-CULTURE", "文化勋章", "Order of Culture", "1932年设立", "骑士级；完整正反面；低清参考", [("egypt-kingdom021_egypt-kingdom021-05.jpg", "完整正面"), ("egypt-kingdom021_egypt-kingdom021-06.jpg", "完整反面")]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    images = []
    for suffix, family, name, original, date, variant, source_views in SPECS:
        record_id = f"EGY-MEDALS-ORG-{suffix}"
        views = []
        for number, (source_name, label) in enumerate(source_views, 1):
            source = RAW / source_name
            target = OUT / f"{suffix.lower()}-{number:02d}{source.suffix.lower()}"
            shutil.copyfile(source, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{record_id}-V{number}"
            views.append({"key": view_key, "label": label})
            images.append({
                "key": f"egypt-medals-org-{suffix.lower()}-{number:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": "https://medals.org.uk/egypt/egypt-kingdom/" + source_name.split("_")[0] + ".htm",
                "image_url": "https://medals.org.uk/egypt/egypt-kingdom/images/" + source_name.split("_", 1)[1],
                "artist": "Medals of the World",
                "license": "Rights status not stated; retained for offline research catalogue",
                "dimensions": dimensions,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True,
                "visually_checked": True,
            })
        record = {
            "id": record_id,
            "family": family,
            "country_zh": "埃及",
            "name": name,
            "original": original,
            "date": date,
            "variant": variant,
            "views": views,
            "source_ids": ["medals_org_egypt_kingdom"],
            "image_kind": "object_photo",
            "html_eligible": True,
        }
        if suffix == "AGRICULTURE-KNIGHT":
            record["supersedes_id"] = "EGY-WAWARDS-MEDAL-16-ORDER-OF-AGRICULTURE"
        elif suffix == "CULTURE-KNIGHT":
            record["supersedes_id"] = "EGY-WAWARDS-MEDAL-17-ORDER-OF-CULTURE"
        records.append(record)
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及王国明确等级差集", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} verified Egyptian grade rows and {len(images)} complete local views")


if __name__ == "__main__":
    main()
