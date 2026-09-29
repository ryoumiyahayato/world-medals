"""Build a reviewed high-resolution maker/grade batch from the full eMedals Egypt sweep."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/raw_candidates/emedals_egypt_catalog.jsonl"
HARVEST = ROOT / "data/image_harvest/emedals_egypt_catalog.json"
OUT = ROOT / "assets/images/egypt_emedals_variants"
VOLUME = ROOT / "data/volumes/egypt_emedals_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_emedals_variants_manifest.json"

# suffix, source position, ordinals, family, name, original, date, variant, labels
SPECS = [
    ("NILE-GRAND-OFFICER-LATTES-1928", 1, [2, 3], "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "约1928年；二型", "大官级挂章；J. Lattes（开罗）；银质、局部镀金及珐琅；完整正反面", ["完整正面", "完整反面"]),
    ("NILE-FIFTH-LATTES-1925", 2, [1, 2], "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "约1925—1926年", "五等；Lattes制；银质、局部镀金及珐琅；完整正反面", ["完整正面", "完整反面"]),
    ("NILE-GRAND-CROSS-STAR-LATTES-1925", 3, [1, 2], "MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "Order of the Nile", "约1925年；二型", "大十字级星章；Lattes制；银质、金质中央饰及珐琅；完整正反面", ["星章完整正面", "星章完整反面"]),
    ("REPUBLIC-GRAND-OFFICER-BADGE-BICHAY", 8, [3, 4], "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "Order of the Republic", "1972年后二型", "大官级挂章；T. Bichay制；银质镀金及珐琅；完整正反面", ["挂章完整正面", "挂章完整反面"]),
    ("REPUBLIC-GRAND-OFFICER-STAR-BICHAY", 8, [7, 8], "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "Order of the Republic", "1972年后二型", "大官级星章；T. Bichay制；完整正反面", ["星章完整正面", "星章完整反面"]),
    ("HONOUR-STAR-TYPE2-BOMISA", 14, [2, 3], "EGY-GAP-STAR-OF-HONOUR", "荣誉之星勋章", "Order of the Star of Honour", "1972—1984年二型", "单级星章；Bomisa（西班牙）制；银、镀银及珐琅；完整正反面", ["完整正面", "完整反面"]),
    ("REPUBLIC-GRAND-OFFICER-BADGE-FUCHS", 45, [4, 5], "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "Order of the Republic", "1953—1972年一型", "大官级挂章；Z. Fuchs（开罗）制；银质及珐琅；完整正反面", ["挂章完整正面", "挂章完整反面"]),
    ("REPUBLIC-GRAND-OFFICER-STAR-FUCHS", 45, [7, 8], "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "Order of the Republic", "1953—1972年一型", "大官级星章；Z. Fuchs（开罗）制；银质及珐琅；完整正反面", ["星章完整正面", "星章完整反面"]),
    ("MERIT-SECOND-BADGE-BICHAY-1960", 47, [3, 4], "MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "Order of Merit", "约1960年", "二等大官级挂章；Fahmy T. Bichay（开罗）制；完整正反面", ["挂章完整正面", "挂章完整反面"]),
    ("MERIT-SECOND-STAR-BICHAY-1960", 47, [6, 7], "MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "Order of Merit", "约1960年", "二等大官级星章；Fahmy T. Bichay（开罗）制；完整正反面", ["星章完整正面", "星章完整反面"]),
    ("ISMAIL-GOLD-COMMANDER-LATTES-1925", 58, [2, 3], "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "约1925—1926年", "目录称一等指挥官级；Lattes制；18K金及珐琅；完整正反面", ["完整正面", "完整反面"]),
    ("ISMAIL-OFFICER-LATTES", 64, [2, 3], "MENA7-ORDER-OF-ISMAIL", "伊斯梅尔勋章", "Order of Ismail", "埃及王国时期", "军官级；目录称法国制造、Lattes标记；银、金及珐琅；完整正反面", ["完整正面", "完整反面"]),
    ("SPORT-COMMANDER-BICHAY", 69, [4, 5], "EGY-GAP-ORDER-SPORT", "体育勋章", "Order of Sport", "共和国时期", "一等指挥官级；Bichay（开罗）制；完整正反面", ["完整正面", "完整反面"]),
    ("DISTINGUISHED-SERVICE-BRONZE", 79, [3, 4], "EGY-MEDALS-ORG-DISTINGUISHED-SERVICE", "杰出服务奖章", "Distinguished Service Medal", "时期待考", "铜质；29毫米；整体悬挂结构；完整正反面", ["完整正面", "完整反面"]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = {item["source_position"]: item for item in (json.loads(line) for line in CANDIDATES.read_text(encoding="utf-8").splitlines() if line.strip())}
    harvested = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    by_product = {}
    for item in harvested:
        by_product.setdefault(item["product_id"], {})[item["ordinal"]] = item
    records = []
    manifest = []
    for suffix, position, ordinals, family, name, original, date, variant, labels in SPECS:
        candidate = candidates[position]
        product_id = candidate["source_product_id"]
        record_id = f"EGY-EMEDALS-{suffix}"
        views = []
        for number, (ordinal, label) in enumerate(zip(ordinals, labels), 1):
            source = by_product[product_id][ordinal]
            source_path = ROOT / source["local_path"]
            target = OUT / f"{suffix.lower()}-{number:02d}{source_path.suffix.lower()}"
            shutil.copyfile(source_path, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{record_id}-V{number}"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"egypt-emedals-{suffix.lower()}-{number:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": candidate["object_page_url"], "image_url": source["image_url"],
                "artist": "eMedals / source collection", "license": "All rights reserved; retained for offline research catalogue",
                "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "埃及", "name": name, "original": original,
            "date": date, "variant": variant, "views": views, "source_ids": ["emedals_egypt_catalog"],
            "image_kind": "object_photo", "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 eMedals 制造商与等级版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} eMedals Egypt maker/grade rows and {len(manifest)} complete local views")


if __name__ == "__main__":
    main()
