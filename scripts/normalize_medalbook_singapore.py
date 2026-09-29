from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_singapore.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP = json.loads((ROOT / "data/source_sweeps/medalbook_singapore_images_2026-09-28.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/medalbook_singapore"
SELECT = {30: [1], 31: [5, 6], 37: [1, 3]}
META = {
    30: ("SGP-AWARD-SAF-GOOD-SERVICE", "新加坡武装部队良好服务奖章", "五年良好服务章", "设立时间待考"),
    31: ("SGP-AWARD-SAF-LONG-SERVICE-GOOD-CONDUCT", "新加坡武装部队长期服务与品行优良奖章", "十二年服务章；正背", "设立时间待考"),
    37: ("SGP-AWARD-POLICE-GOOD-SERVICE", "新加坡警察良好服务奖章", "五年良好服务章；2004年铭文修订型；正背", "1994年设立；2004年修订"),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = {(item["record_index"], item["image_index"]): item for item in SWEEP["items"] if item["status"] == "downloaded"}
    records, images, hashes = [], [], set()
    for index, picks in SELECT.items():
        source = RAW[index]
        family, name, variant, date_text = META[index]
        record_id = family + "-MEDALBOOK"
        views = []
        for order, image_no in enumerate(picks, 1):
            item = items[(index, image_no)]
            if item["sha256"] in hashes:
                raise ValueError(f"duplicate selected payload {index}:{image_no}")
            hashes.add(item["sha256"])
            source_path = ROOT / item["local_path"]
            with Image.open(source_path) as decoded:
                decoded.verify()
            relative = f"assets/images/medalbook_singapore/{index:03d}_{image_no:02d}{source_path.suffix.lower()}"
            shutil.copy2(source_path, ROOT / relative)
            view_key = f"{record_id}-VIEW{order}"
            views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
            images.append({"key": f"singapore-medalbook-{index:03d}-{image_no:02d}", "record_id": record_id, "view_key": view_key, "local_path": relative, "source_page": source["page_url"], "image_url": item["url"], "artist": "MedalBook catalogue object photograph", "license": "Source terms apply; retained for offline research catalogue", "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"], "decoded": True, "visually_checked": True})
        records.append({"id": record_id, "family": family, "country_zh": "新加坡共和国", "name": name, "original": source["page_title"], "date": date_text, "variant": variant, "views": views, "source_ids": [source["source_id"]], "image_kind": "object_photo", "html_eligible": True})
    (ROOT / "data/volumes/singapore_medalbook_variants.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": "新加坡共和国", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes/singapore_medalbook_variants_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": [], "excluded_candidates": [{"kind": "unpictured_object_pages", "count": 65, "reason": "目录有记录但未公开完整实物图；保留原始候选"}, {"kind": "duplicate_angles", "count": 6, "reason": "重复正面或局部角度未进入正文"}]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "families": len(records), "views": len(images)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
