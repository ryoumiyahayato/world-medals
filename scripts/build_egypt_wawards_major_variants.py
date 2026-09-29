"""Build visually distinct grade/component rows for Egypt's major orders."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "data/image_harvest/wawards_egypt_all_images.json"
OUT_DIR = ROOT / "assets/images/egypt_wawards_major_variants"
VOLUME = ROOT / "data/volumes/egypt_wawards_major_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_wawards_major_variants_manifest.json"

# title, URL period marker, family, Chinese name, original, date, variant, source image ordinals
SPECS = [
    ("Order of Ismail", "kingdom-of-egypt", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；埃及王国时期", "挂章；正反面", [1, 2]),
    ("Order of Ismail", "kingdom-of-egypt", "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "1915年设立；埃及王国时期", "星章；正反面", [3, 4]),
    ("Order of Muhammad Ali", "kingdom-of-egypt", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1915年设立；埃及王国时期", "一期挂章；正反面合图", [1]),
    ("Order of Muhammad Ali", "kingdom-of-egypt", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1915年设立；埃及王国时期", "一期星章；完整正面", [2]),
    ("Order of Muhammad Ali", "kingdom-of-egypt", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1919年改版；埃及王国时期", "二期大绶挂章；正反面", [3, 4]),
    ("Order of Muhammad Ali", "kingdom-of-egypt", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "1919年改版；埃及王国时期", "二期星章；完整正面", [5]),
    ("Order of Muhammad Ali", "kingdom-of-egypt", "MENA7-ORDER-OF-MUHAMMAD-ALI", "穆罕默德·阿里勋章", "Order of Muhammad Ali", "埃及王国时期", "附属奖章／低阶章；正反面", [6, 7]),
    ("Order of the Nile", "kingdom-of-egypt", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "大绶级套装；绶带、挂章与星章", [1]),
    ("Order of the Nile", "kingdom-of-egypt", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "星章；正反面", [2, 3]),
    ("Order of the Nile", "kingdom-of-egypt", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1915年设立；埃及王国时期", "颈章／挂章；正反面", [4, 5]),
    ("Order of the Virtues", "kingdom-of-egypt", "MENA7-ORDER-OF-THE-VIRTUES", "美德勋章（尼尚·卡迈勒）", "Order of the Virtues / Nishan al-Kamal", "1915年设立；埃及王国时期", "王国版挂章；完整正面", [1]),
    ("Order of the Virtues", "kingdom-of-egypt", "MENA7-ORDER-OF-THE-VIRTUES", "美德勋章（尼尚·卡迈勒）", "Order of the Virtues / Nishan al-Kamal", "1915年设立；埃及王国时期", "王国版星章；完整正面", [2]),
    ("Order of Independence", "republic-of-egypt", "MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "Order of Independence", "1955年设立", "挂章；正反面", [1, 2]),
    ("Order of Independence", "republic-of-egypt", "MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "Order of Independence", "1955年设立", "星章；正反面", [3, 4]),
    ("Order of Merit", "republic-of-egypt", "MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "وسام الاستحقاق / Order of Merit", "1953年设立；1972年法律重定", "挂章；正反面", [1, 2]),
    ("Order of Merit", "republic-of-egypt", "MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "وسام الاستحقاق / Order of Merit", "1953年设立；1972年法律重定", "星章；正反面", [3, 4]),
    ("Order of Sciences and Arts", "republic-of-egypt", "EGY-GAP-SCIENCES-ARTS", "科学与艺术勋章", "Order of Sciences and Arts", "1953年设立", "星章；完整正面", [2]),
    ("Order of Sciences and Arts", "republic-of-egypt", "EGY-GAP-SCIENCES-ARTS", "科学与艺术勋章", "Order of Sciences and Arts", "1953年设立", "挂章；完整正面", [3]),
    ("Order of Sport", "republic-of-egypt", "EGY-GAP-ORDER-SPORT", "体育勋章", "Order of Sport", "1952年设立", "星章；正反面", [1, 2]),
    ("Order of Sport", "republic-of-egypt", "EGY-GAP-ORDER-SPORT", "体育勋章", "Order of Sport", "1952年设立", "挂章；完整正面", [3]),
    ("Order of the Nile", "republic-of-egypt", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1953年设立；共和国时期", "共和国版大绶挂章；完整正面", [1]),
    ("Order of the Nile", "republic-of-egypt", "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "1953年设立；共和国时期", "共和国版星章；正反面", [2, 3]),
    ("Order of the Republic", "republic-of-egypt", "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；1972年法律重定", "挂章；正反面", [1, 2]),
    ("Order of the Republic", "republic-of-egypt", "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；1972年法律重定", "星章；完整正面", [3]),
    ("Order of the Virtues", "republic-of-egypt", "MENA7-ORDER-OF-THE-VIRTUES", "美德勋章（尼尚·卡迈勒）", "Order of the Virtues / Nishan al-Kamal", "1915年设立；共和国时期继续授予", "共和国版一等；完整正面", [1]),
    ("Order of the Virtues", "republic-of-egypt", "MENA7-ORDER-OF-THE-VIRTUES", "美德勋章（尼尚·卡迈勒）", "Order of the Virtues / Nishan al-Kamal", "1915年设立；共和国时期继续授予", "共和国版二等；完整正面", [2]),
]


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    images = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    records = []
    manifest = []
    for sequence, (title, marker, family, name, original, date, variant, ordinals) in enumerate(SPECS, 1):
        pool = [item for item in images if item["page_title"] == title and marker in item["page_url"]]
        by_ordinal = {item["ordinal"]: item for item in pool}
        selected = [by_ordinal[number] for number in ordinals]
        record_id = f"EGY-WAWARDS-MAJOR-{sequence:02d}-{slug(title)}"
        views = []
        for view_no, source in enumerate(selected, 1):
            source_path = ROOT / source["local_path"]
            target = OUT_DIR / f"{sequence:02d}-{slug(title).lower()}-{view_no:02d}{source_path.suffix.lower()}"
            shutil.copyfile(source_path, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{record_id}-V{view_no}"
            if len(selected) == 2:
                label = "完整正面" if view_no == 1 else "完整反面"
            else:
                label = "完整图样"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"egypt-wawards-major-{sequence:02d}-{view_no:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": source["page_url"], "image_url": source["image_url"],
                "artist": "Wawards / source collection", "license": "Rights status not stated; retained for offline research catalogue",
                "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "埃及", "name": name, "original": original,
            "date": date, "variant": variant, "views": views, "source_ids": [selected[0]["source_id"]],
            "image_kind": "object_photo", "html_eligible": True,
        })
        if sequence == 18:
            records[-1]["supersedes_id"] = "EGY-GAP-SCIENCES-ARTS-01"
        elif sequence == 19:
            records[-1]["supersedes_id"] = "EGY-GAP-ORDER-SPORT-01"
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及主要勋章等级与组件", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} Egypt major-order variant rows, {len(manifest)} complete local views")


if __name__ == "__main__":
    main()
