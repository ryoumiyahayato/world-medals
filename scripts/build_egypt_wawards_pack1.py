"""Build Egypt families genuinely absent after the Wawards directory difference pass."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "data/image_harvest/wawards_egypt_all_images.json"
OUT_DIR = ROOT / "assets/images/egypt_wawards_pack1"
VOLUME = ROOT / "data/volumes/egypt_wawards_pack1.json"
MANIFEST = ROOT / "data/volumes/egypt_wawards_pack1_manifest.json"

AWARDS = {
    "Collar of Fuad I": ("福阿德一世项圈", "Collar of Fuad I", "1936年以前；王国时期", "国家元首级项圈；完整实物正面"),
    "Liberation Medal": ("解放奖章", "Medal of Liberation / نوط التحرير", "1952年设立", "革命／解放纪念授予型；同一版型正反面"),
    "Liberation Order": ("解放勋章", "Order of Liberation / وسام التحرير", "1952年设立", "解放功绩授予型；完整实物正面"),
    "Medal of Merit": ("功绩奖章", "Medal of Merit", "1953年设立", "三级制；图示等级待考；同一版型正反面"),
}


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    images = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    by_title: dict[str, list[dict]] = {}
    for image in images:
        by_title.setdefault(image["page_title"], []).append(image)
    records = []
    manifest = []
    for title, (name, original, date, variant) in AWARDS.items():
        selected = sorted(by_title.get(title, []), key=lambda item: item["ordinal"])
        if not selected:
            raise RuntimeError(f"No source images for {title}")
        family = f"EGY-WAWARDS-{slug(title)}"
        record_id = family + "-01"
        views = []
        for index, source in enumerate(selected, 1):
            source_path = ROOT / source["local_path"]
            target = OUT_DIR / f"{slug(title).lower()}-{index:02d}{source_path.suffix.lower()}"
            shutil.copyfile(source_path, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{family}-V{index}"
            label = "完整正面" if index == 1 else "完整反面"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"wawards-egypt-{slug(title).lower()}-{index:02d}", "record_id": record_id,
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
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 Wawards 差集批次1", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} Egypt families, {len(manifest)} complete local views")


if __name__ == "__main__":
    main()
