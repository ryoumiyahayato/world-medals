from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_cambodia.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP = json.loads((ROOT / "data/source_sweeps/medalbook_cambodia_images_2026-09-28.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/medalbook_cambodia"

# record index: selected complete front/reverse image numbers
SELECT = {
    0: [1, 2], 2: [6, 2], 3: [2, 1], 4: [3, 4], 5: [1, 2], 8: [1, 2],
    10: [3, 4], 11: [6, 4], 12: [1, 3], 14: [1, 3], 15: [2, 4], 16: [1, 3],
    22: [1, 2], 24: [5, 1], 29: [5, 4], 30: [4, 2],
    64: [1], 84: [3, 4], 96: [1, 2], 111: [6, 5], 112: [2, 7], 116: [2, 3],
}

META = {
    0: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-NORODOM-I", "诺罗敦一世御世纪念章", "铜质级", "诺罗敦一世时期"),
    2: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-NORODOM-I", "诺罗敦一世御世纪念章", "银质级", "诺罗敦一世时期"),
    3: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-SISOWATH-I", "西索瓦一世御世纪念章", "铜质级", "1926年设立"),
    4: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-SISOWATH-I", "西索瓦一世御世纪念章", "金质级", "1926年设立"),
    5: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-SISOWATH-I", "西索瓦一世御世纪念章", "银质级", "1926年设立"),
    8: ("KHM-AWARD-MEDAL-OF-THE-REIGN-OF-KING-SISOWATH-MONIVONG", "西索瓦·莫尼旺御世纪念章", "银质级", "1928年设立"),
    10: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "指挥官级", "1864年设立"),
    11: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "大十字级挂章", "1864年设立"),
    12: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "大十字级星章", "1864年设立"),
    14: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "大军官级星章", "1864年设立"),
    15: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "骑士级", "1864年设立"),
    16: ("KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA", "柬埔寨王家勋章", "军官级", "1864年设立"),
    22: ("KHM-AWARD-ROYAL-ORDER-OF-MONISARAPHON", "莫尼萨拉蓬王家勋章", "骑士级", "1905年设立"),
    24: ("KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA", "索瓦塔拉王家勋章", "指挥官级", "1923年设立"),
    29: ("KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA", "索瓦塔拉王家勋章", "骑士级", "1923年设立"),
    30: ("KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA", "索瓦塔拉王家勋章", "军官级", "1923年设立"),
    64: ("KHM-AWARD-MEDAL-PEOPLES-SOCIALIST-COMMUNITY", "人民社会主义共同体奖章", "章饰", "设立时间待考"),
    84: ("KHM-AWARD-NATIONAL-ORDER-OF-INDEPENDENCE", "国家独立勋章", "大军官级星章", "1963年设立"),
    96: ("KHM-AWARD-ORDER-OF-THE-QUEEN", "王后勋章", "骑士级", "1962年设立"),
    111: ("KHM-AWARD-ROYAL-ORDER-OF-SAHAMETREI", "萨哈梅特雷王家勋章", "大十字级挂章", "1948年设立"),
    112: ("KHM-AWARD-ROYAL-ORDER-OF-SAHAMETREI", "萨哈梅特雷王家勋章", "大十字级星章", "1948年设立"),
    116: ("KHM-AWARD-ROYAL-ORDER-OF-SAHAMETREI", "萨哈梅特雷王家勋章", "军官级", "1948年设立"),
}


def build(indices: list[int], country_zh: str, stem: str) -> tuple[int, int, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = {(item["record_index"], item["image_index"]): item for item in SWEEP["items"] if item["status"] == "downloaded"}
    records, images, hashes = [], [], set()
    for index in indices:
        source = RAW[index]
        family, name, variant, date_text = META[index]
        record_id = f"{family}-MEDALBOOK-{index:03d}"
        views = []
        for order, image_no in enumerate(SELECT[index], 1):
            item = items[(index, image_no)]
            if item["sha256"] in hashes:
                raise ValueError(f"duplicate selected payload {index}:{image_no}")
            hashes.add(item["sha256"])
            source_path = ROOT / item["local_path"]
            with Image.open(source_path) as decoded:
                decoded.verify()
            safe_slug = re.sub(r"[^a-z0-9-]+", "-", Path(source["page_url"]).name.lower()).strip("-")
            relative = f"assets/images/medalbook_cambodia/{index:03d}_{safe_slug}_{image_no:02d}{source_path.suffix.lower()}"
            shutil.copy2(source_path, ROOT / relative)
            view_key = f"{record_id}-VIEW{order}"
            views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
            images.append({
                "key": f"cambodia-medalbook-{index:03d}-{image_no:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": relative,
                "source_page": source["page_url"],
                "image_url": item["url"],
                "artist": "MedalBook catalogue object photograph",
                "license": "Source terms apply; retained for offline research catalogue",
                "dimensions": [item["width"], item["height"]],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "decoded": True,
                "visually_checked": True,
            })
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": country_zh,
            "name": name,
            "original": source["page_title"],
            "date": date_text,
            "variant": variant,
            "views": views,
            "source_ids": [source["source_id"]],
            "image_kind": "object_photo",
            "html_eligible": True,
        })
    (ROOT / "data/volumes" / f"{stem}.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": country_zh, "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes" / f"{stem}_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": [], "excluded_candidates": [{"kind": "same_family_redundant_or_detail_images", "count": 71, "reason": "同等级重复角度、局部特写、章盒及已由更完整图覆盖的对象未进入正文"}]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(records), len({r["family"] for r in records}), len(images)


def main() -> None:
    protectorate = build([0, 2, 3, 4, 5, 8, 10, 11, 12, 14, 15, 16, 22, 24, 29, 30], "柬埔寨保护国（1863–1948）", "cambodia_protectorate_medalbook_variants")
    kingdom = build([64, 84, 96, 111, 112, 116], "柬埔寨王国（1948–1970）", "cambodia_kingdom_medalbook_differential")
    print(json.dumps({"protectorate": protectorate, "kingdom_1948_1970": kingdom}, ensure_ascii=False))


if __name__ == "__main__":
    main()
