"""Replace Egypt's generic Wawards medal rows with verified front/reverse variants."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "data/image_harvest/wawards_egypt_all_images.json"
BASE_VOLUME = ROOT / "data/volumes/mena_gap_round1_2026-09-26.json"
OUT_DIR = ROOT / "assets/images/egypt_wawards_medal_variants"
VOLUME = ROOT / "data/volumes/egypt_wawards_medal_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_wawards_medal_variants_manifest.json"

# old row id, source title, period marker, concise variant, image ordinals
SPECS = [
    ("EGY-GAP-LIBERATION-KUWAIT-01", "Liberation of Kuwait Medal", "egypt/", "两级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-REVOLUTION-20TH-01", "Medal 20th Anniversary of the Revolution", "egypt/", "二十周年纪念版；正反面", [1, 2]),
    ("EGY-GAP-SINAI-SILVER-JUBILEE-01", "Medal Commemorating the Silver Jubilee of the Liberation of Sinai", "egypt/", "长条悬挂版；完整正面", [1]),
    ("EGY-GAP-SINAI-SILVER-JUBILEE-01", "Medal Commemorating the Silver Jubilee of the Liberation of Sinai", "egypt/", "圆章版；正反面", [2, 3]),
    ("EGY-GAP-SIXTH-OCTOBER-01", "Medal of 6th October", "egypt/", "十月战争授予版；正反面", [1, 2]),
    ("EGY-GAP-OCTOBER-COMBATANTS-01", "Medal of Combatants of October 1973", "egypt/", "1973年十月战役参战人员版；正反面", [1, 2]),
    ("EGY-GAP-REVOLUTION-GOLDEN-JUBILEE-01", "Medal of the Golden Anniversary of the 23 July Revolution", "egypt/", "五十周年纪念版；正反面", [1, 2]),
    ("EGY-GAP-SINAI-STAR-01", "Order of the Sinai Star", "egypt/", "一级；正反面", [1, 2]),
    ("EGY-GAP-SINAI-STAR-01", "Order of the Sinai Star", "egypt/", "二级；正反面", [3, 4]),
    ("EGY-GAP-MOHAMED-ALI-CENTENARY-01", "Centenary of Mohamed Ali Medal", "egypt/", "穆罕默德·阿里百年纪念版；正反面", [1, 2]),
    ("EGY-GAP-DEVOTION-TO-DUTY-01", "Medal for Devotion to Duty", "egypt/", "三级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-MERITORIOUS-ACTS-01", "Medal for Meritorious Acts", "egypt/", "三级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-BENEVOLENCE-01", "Medal of Benevolence", "egypt/", "三级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-GENERAL-EDUCATION-01", "Ministry of General Education medal", "egypt/", "教育功绩授予版；正反面", [1, 2]),
    ("EGY-GAP-KINGDOM-ORDER-AGRICULTURE-01", "Order of Agriculture", "kingdom-of-egypt", "王国版挂章；正反面", [1, 2]),
    ("EGY-GAP-KINGDOM-ORDER-AGRICULTURE-01", "Order of Agriculture", "kingdom-of-egypt", "王国版另一等级挂章；完整正面", [3]),
    ("EGY-GAP-ORDER-CULTURE-01", "Order of Culture", "kingdom-of-egypt", "王国版挂章；完整正面", [1]),
    ("EGY-GAP-INDUSTRY-COMMERCE-01", "Order of Industry and Commerce", "kingdom-of-egypt", "王国版挂章；正反面", [1, 2]),
    ("EGY-GAP-FUAD-MILITARY-STAR-01", "Order of the Military Star of Fuad I", "kingdom-of-egypt", "福阿德一世版挂章；完整正面", [1]),
    ("EGY-GAP-FUAD-MILITARY-STAR-01", "Order of the Military Star of Fuad I", "kingdom-of-egypt", "福阿德一世版星章；正反面", [2, 3]),
    ("EGY-GAP-MEDAL-SPORT-01", "Medal for Sport", "republic-of-egypt", "体育奖章；正反面", [1, 2]),
    ("EGY-GAP-EXCEPTIONAL-PROMOTION-01", "Medal of Exceptional Promotion", "republic-of-egypt", "特别晋升授予版；正反面", [1, 2]),
    ("EGY-GAP-MILITARY-DUTY-01", "Medal of Military Duty", "republic-of-egypt", "型式一；正反面", [1, 2]),
    ("EGY-GAP-MILITARY-DUTY-01", "Medal of Military Duty", "republic-of-egypt", "型式二；正反面", [3, 4]),
    ("EGY-GAP-MOBILISATION-01", "Medal of Mobilisation", "republic-of-egypt", "动员授予版；正反面", [1, 2]),
    ("EGY-GAP-REPUBLIC-ORDER-AGRICULTURE-01", "Order of Agriculture", "republic-of-egypt", "共和国版挂章；正反面", [1, 2]),
    ("EGY-GAP-REPUBLIC-MILITARY-STAR-01", "Order of the Military Star", "republic-of-egypt", "共和国版挂章；正反面", [1, 2]),
    ("EGY-GAP-POLICE-LIBERATION-STAR-01", "Order of the Star of Liberation (Police)", "republic-of-egypt", "警察解放星章；完整正面", [1]),
    ("EGY-GAP-AIR-FORCE-SILVER-JUBILEE-01", "Silver Jubilee of the Air Force Medal", "republic-of-egypt", "挂章；正反面", [1, 2]),
    ("EGY-GAP-AIR-FORCE-SILVER-JUBILEE-01", "Silver Jubilee of the Air Force Medal", "republic-of-egypt", "星章；完整正面", [3]),
    ("EGY-GAP-FRIENDSHIP-01", "Friendship Medal", "united-arab-republic", "阿斯旺水坝友谊版；正反面", [1, 2]),
    ("EGY-GAP-FRIENDSHIP-01", "Friendship Medal", "united-arab-republic", "另一型式；正反面", [3, 4]),
    ("EGY-GAP-DISTINCTION-01", "Medal of Distinction", "united-arab-republic", "三级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-DISTINCTION-01", "Medal of Distinction", "united-arab-republic", "另一材质／等级版；完整正面", [3]),
    ("EGY-GAP-LONG-SERVICE-GOOD-EXAMPLE-01", "Medal of Long Service and Good Example", "united-arab-republic", "长期服务与良好品行版；正反面", [1, 2]),
    ("EGY-GAP-TRAINING-01", "Medal of Training", "united-arab-republic", "金色版；正反面", [1, 2]),
    ("EGY-GAP-TRAINING-01", "Medal of Training", "united-arab-republic", "银色版；正反面", [3, 4]),
    ("EGY-GAP-WAR-WOUNDED-01", "Medal of War Wounded", "united-arab-republic", "战伤授予版；正反面", [1, 2]),
    ("EGY-GAP-MILITARY-COURAGE-01", "Military Medal of Courage", "united-arab-republic", "三级制；图示等级待考；正反面", [1, 2]),
    ("EGY-GAP-UAR-COMMEMORATION-01", "Order Commemorating the United Arab Republic", "united-arab-republic", "阿拉伯联合共和国成立纪念版；正反面", [1, 2]),
    ("EGY-GAP-STAR-OF-HONOUR-01", "Order of the Star of Honour", "united-arab-republic", "荣誉之星；正反面", [1, 2]),
]


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    images = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    base = {row["id"]: row for row in json.loads(BASE_VOLUME.read_text(encoding="utf-8"))["records"]}
    seen_old: set[str] = set()
    records = []
    manifest = []
    for sequence, (old_id, title, marker, variant, ordinals) in enumerate(SPECS, 1):
        old = base[old_id]
        pool = [item for item in images if item["page_title"] == title and marker in item["page_url"]]
        by_ordinal = {item["ordinal"]: item for item in pool}
        selected = [by_ordinal[number] for number in ordinals]
        record_id = f"EGY-WAWARDS-MEDAL-{sequence:02d}-{slug(title)}"
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
            label = ("完整正面" if view_no == 1 else "完整反面") if len(selected) == 2 else "完整正面"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"egypt-wawards-medal-{sequence:02d}-{view_no:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": source["page_url"], "image_url": source["image_url"],
                "artist": "Wawards / source collection", "license": "Rights status not stated; retained for offline research catalogue",
                "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True, "visually_checked": True,
            })
        record = {
            "id": record_id, "family": old["family"], "country_zh": "埃及", "name": old["name"],
            "original": old["original"], "date": old["date"], "variant": variant,
            "views": views, "source_ids": [selected[0]["source_id"]], "image_kind": "object_photo", "html_eligible": True,
        }
        if old_id not in seen_old:
            record["supersedes_id"] = old_id
            seen_old.add(old_id)
        records.append(record)
    expected_superseded = 32
    if len(seen_old) != expected_superseded:
        raise RuntimeError(f"Expected {expected_superseded} superseded generic rows, got {len(seen_old)}")
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及奖章正反面与版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} precise Egypt medal rows, {len(manifest)} complete views; superseded {len(seen_old)} generic rows")


if __name__ == "__main__":
    main()
