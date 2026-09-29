from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_laos.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP = json.loads((ROOT / "data/source_sweeps/medalbook_laos_images_2026-09-28.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/medalbook_laos"
VOLUME = ROOT / "data/volumes/laos_kingdom_medalbook_variants.json"
MANIFEST = ROOT / "data/volumes/laos_kingdom_medalbook_variants_manifest.json"

SELECT = {
    0: [5, 7], 3: [3, 5], 6: [1, 3], 8: [1], 10: [1], 11: [2, 4], 12: [4, 3],
    14: [3, 2], 15: [1, 2], 19: [1], 21: [1], 22: [2, 1], 23: [2, 1],
    36: [3, 2], 37: [3, 4], 38: [1, 2], 39: [1, 2],
}

META = {
    0: ("LAO-KINGDOM-COMBAT-VETERANS-MEDAL", "战斗老兵奖章", "章饰", "1957年设立"),
    3: ("LAO-KINGDOM-GOVERNMENT-GRATITUDE-MEDAL", "政府感恩奖章", "章饰", "1960年代"),
    6: ("LAO-KINGDOM-MILLION-ELEPHANTS-WHITE-PARASOL", "万象白伞勋章", "指挥官级", "1909年设立"),
    8: ("LAO-KINGDOM-MILLION-ELEPHANTS-WHITE-PARASOL", "万象白伞勋章", "大绶级星章", "1909年设立"),
    10: ("LAO-KINGDOM-MILLION-ELEPHANTS-WHITE-PARASOL", "万象白伞勋章", "大军官级星章", "1909年设立"),
    11: ("LAO-KINGDOM-MILLION-ELEPHANTS-WHITE-PARASOL", "万象白伞勋章", "骑士级", "1909年设立"),
    12: ("LAO-KINGDOM-MILLION-ELEPHANTS-WHITE-PARASOL", "万象白伞勋章", "军官级", "1909年设立"),
    14: ("LAO-KINGDOM-AGRICULTURAL-MERIT", "农业功绩勋章", "骑士级", "1950年设立"),
    15: ("LAO-KINGDOM-AGRICULTURAL-MERIT", "农业功绩勋章", "军官级", "1950年设立"),
    19: ("LAO-KINGDOM-FEMININE-MERIT", "妇女功绩勋章", "铜质级", "1962年设立"),
    21: ("LAO-KINGDOM-FEMININE-MERIT", "妇女功绩勋章", "银质级", "1962年设立"),
    22: ("LAO-KINGDOM-MERIT-IN-EDUCATION", "教育功绩勋章", "指挥官级", "1955年设立"),
    23: ("LAO-KINGDOM-MERIT-IN-EDUCATION", "教育功绩勋章", "骑士级", "1955年设立"),
    36: ("LAO-KINGDOM-ORDER-OF-THE-REIGN", "御世勋章", "II型·二等", "1923年设立；1927、1948年修订"),
    37: ("LAO-KINGDOM-ORDER-OF-THE-REIGN", "御世勋章", "II型·三等", "1923年设立；1927、1948年修订"),
    38: ("LAO-KINGDOM-ORDER-OF-THE-REIGN", "御世勋章", "I型·一等", "1923年设立；1927、1948年修订"),
    39: ("LAO-KINGDOM-ORDER-OF-THE-REIGN", "御世勋章", "I型·二等", "1923年设立；1927、1948年修订"),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = {(item["record_index"], item["image_index"]): item for item in SWEEP["items"] if item["status"] == "downloaded"}
    records, images, hashes = [], [], set()
    for index in SELECT:
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
            relative = f"assets/images/medalbook_laos/{index:03d}_{safe_slug}_{image_no:02d}{source_path.suffix.lower()}"
            shutil.copy2(source_path, ROOT / relative)
            view_key = f"{record_id}-VIEW{order}"
            views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
            images.append({
                "key": f"laos-medalbook-{index:03d}-{image_no:02d}", "record_id": record_id, "view_key": view_key,
                "local_path": relative, "source_page": source["page_url"], "image_url": item["url"],
                "artist": "MedalBook catalogue object photograph", "license": "Source terms apply; retained for offline research catalogue",
                "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"],
                "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "老挝王国（1947–1975）", "name": name,
            "original": source["page_title"], "date": date_text, "variant": variant, "views": views,
            "source_ids": [source["source_id"]], "image_kind": "object_photo", "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-28", "volume": "老挝王国（1947–1975）", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-28", "images": images,
        "unpictured_candidates": [],
        "excluded_candidates": [{"kind": "duplicate_angles_and_closeups", "count": SWEEP["downloaded"] - len(images), "reason": "同等级重复角度和局部特写未进入正文"}],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "families": len({r['family'] for r in records}), "views": len(images), "unpictured_pages": len(RAW) - len(SELECT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
