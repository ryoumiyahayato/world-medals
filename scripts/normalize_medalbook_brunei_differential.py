from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_brunei.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP = json.loads((ROOT / "data/source_sweeps/medalbook_brunei_images_2026-09-28.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/medalbook_brunei"

# Only material differentials from the already merged World Awards catalogue.
# Selections were made after visual review of all three contact sheets.
SELECT = {
    0: [2, 1],
    16: [1],
    23: [1], 24: [1], 25: [1], 26: [1], 27: [1], 28: [1], 29: [1], 30: [1],
    32: [1], 34: [1], 35: [1],
    41: [1], 42: [1], 44: [4, 1],
    60: [1], 61: [1], 62: [1],
    66: [3, 5],
}

META = {
    0: ("BRN-AWARD-ARMED-FORCES-SERVICE-MEDAL", "武装部队服务奖章", "章饰；正背", "1975年设立"),
    16: ("BRN-AWARD-SULTAN-OMAR-ALI-SAIFUDDIN-MEDAL", "苏丹奥马尔·阿里·赛义夫丁奖章", "一级", "1959年设立"),
    23: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "一级绶章", "1968年8月1日设立"),
    24: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "一级星章", "1968年8月1日设立"),
    25: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "一级项链章", "1968年8月1日设立"),
    26: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "二级挂章", "1968年8月1日设立"),
    27: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "二级星章", "1968年8月1日设立"),
    28: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "三级", "1968年8月1日设立"),
    29: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "四级", "1968年8月1日设立"),
    30: ("BRN-AWARD-MOST-ILLUSTRIOUS-ISLAMIC-RELIGIOUS-ORDER", "至显赫伊斯兰宗教勋章", "五级", "1968年8月1日设立"),
    32: ("BRN-AWARD-MOST-EXALTED-ORDER-OF-FAMOUS-VALOUR", "至高卓著英勇勋章", "二级挂章", "1968年8月1日设立"),
    34: ("BRN-AWARD-MOST-EXALTED-ORDER-OF-FAMOUS-VALOUR", "至高卓著英勇勋章", "二级星章", "1968年8月1日设立"),
    35: ("BRN-AWARD-MOST-EXALTED-ORDER-OF-FAMOUS-VALOUR", "至高卓著英勇勋章", "三级", "1968年8月1日设立"),
    41: ("BRN-AWARD-MOST-BLESSED-ORDER-OF-LOYALTY", "至福忠诚勋章", "I型·二级挂章", "1959年11月28日设立"),
    42: ("BRN-AWARD-MOST-BLESSED-ORDER-OF-LOYALTY", "至福忠诚勋章", "I型·二级星章", "1959年11月28日设立"),
    44: ("BRN-AWARD-MOST-BLESSED-ORDER-OF-LOYALTY", "至福忠诚勋章", "I型·四级；正背", "1959年11月28日设立"),
    60: ("BRN-AWARD-MOST-ILLUSTRIOUS-ORDER-OF-SPLENDID-VALOUR", "至显赫英勇勋章", "二级挂章", "1968年8月1日设立"),
    61: ("BRN-AWARD-MOST-ILLUSTRIOUS-ORDER-OF-SPLENDID-VALOUR", "至显赫英勇勋章", "二级星章", "1968年8月1日设立"),
    62: ("BRN-AWARD-MOST-ILLUSTRIOUS-ORDER-OF-SPLENDID-VALOUR", "至显赫英勇勋章", "三级", "1968年8月1日设立"),
    66: ("BRN-AWARD-MOST-HONOURABLE-ORDER-OF-THE-CROWN", "至尊王冠勋章", "大指挥官级挂章；正背", "1954年3月1日设立"),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = {(item["record_index"], item["image_index"]): item for item in SWEEP["items"] if item["status"] == "downloaded"}
    records, images, hashes = [], [], set()
    for index, picks in SELECT.items():
        source = RAW[index]
        family, name, variant, date_text = META[index]
        record_id = f"{family}-MEDALBOOK-{index:03d}"
        views = []
        for order, image_no in enumerate(picks, 1):
            item = items[(index, image_no)]
            if item["sha256"] in hashes:
                raise ValueError(f"duplicate selected payload {index}:{image_no}")
            hashes.add(item["sha256"])
            source_path = ROOT / item["local_path"]
            with Image.open(source_path) as decoded:
                decoded.verify()
            safe_slug = re.sub(r"[^a-z0-9-]+", "-", Path(source["page_url"]).name.lower()).strip("-")
            relative = f"assets/images/medalbook_brunei/{index:03d}_{safe_slug}_{image_no:02d}{source_path.suffix.lower()}"
            shutil.copy2(source_path, ROOT / relative)
            view_key = f"{record_id}-VIEW{order}"
            views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
            images.append({
                "key": f"brunei-medalbook-{index:03d}-{image_no:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": relative, "source_page": source["page_url"],
                "image_url": item["url"], "artist": "MedalBook catalogue object photograph",
                "license": "Source terms apply; retained for offline research catalogue",
                "dimensions": [item["width"], item["height"]], "bytes": item["bytes"],
                "sha256": item["sha256"], "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "文莱达鲁萨兰国", "name": name,
            "original": source["page_title"], "date": date_text, "variant": variant, "views": views,
            "source_ids": [source["source_id"]], "image_kind": "object_photo", "html_eligible": True,
        })
    (ROOT / "data/volumes/brunei_medalbook_differential.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": "文莱达鲁萨兰国", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes/brunei_medalbook_differential_manifest.json").write_text(json.dumps({
        "as_of": "2026-09-28", "images": images,
        "unpictured_candidates": [],
        "excluded_candidates": [
            {"kind": "object_pages_without_exposed_images", "count": len(RAW) - len([r for r in RAW if r['original_image_urls']]), "reason": "对象页有目录记录但无公开实物图；保留在原始候选层"},
            {"kind": "overlap_and_redundant_angles", "count": SWEEP["downloaded"] - len(images), "reason": "与已入编Wawards版型重合，或为同件重复角度、局部特写及章盒"},
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "net_new_families": 1, "views": len(images), "unpictured_pages": len(RAW) - len([r for r in RAW if r['original_image_urls']])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
