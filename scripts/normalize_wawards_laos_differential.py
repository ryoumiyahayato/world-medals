from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_laos.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR = ROOT / "assets/images/wawards_laos"


def write_one(source: dict, *, stem: str, family: str, country: str, name: str, date_text: str, variant: str, picks: list[int]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_no = {item["view_no"]: item for item in source["original_images"]}
    record_id = family + "-WAWARDS"
    views, images = [], []
    for order, image_no in enumerate(picks, 1):
        item = by_no[image_no]
        source_path = ROOT / item["local_path"]
        with Image.open(source_path) as decoded:
            decoded.verify()
        relative = f"assets/images/wawards_laos/{stem}_{image_no:02d}{source_path.suffix.lower()}"
        shutil.copy2(source_path, ROOT / relative)
        view_key = f"{record_id}-VIEW{order}"
        views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
        images.append({"key": f"laos-wawards-{stem}-{image_no:02d}", "record_id": record_id, "view_key": view_key, "local_path": relative, "source_page": source["object_url"], "image_url": item["image_url"], "artist": "World Awards reference catalogue", "license": "Source terms apply; retained for offline research catalogue", "dimensions": [item["width"], item["height"]], "bytes": source_path.stat().st_size, "sha256": item["sha256"], "decoded": True, "visually_checked": True})
    record = {"id": record_id, "family": family, "country_zh": country, "name": name, "original": source["page_title"], "date": date_text, "variant": variant, "views": views, "source_ids": [source["source_id"]], "image_kind": "object_photo", "html_eligible": True}
    (ROOT / "data/volumes" / f"{stem}.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": country, "records": [record]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes" / f"{stem}_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": [], "excluded_candidates": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    feminine = next(row for row in RAW if "feminine-merit" in row["object_url"])
    victory = next(row for row in RAW if "victory-in-the-revolution" in row["object_url"])
    write_one(feminine, stem="laos_kingdom_wawards_differential", family="LAO-KINGDOM-FEMININE-MERIT", country="老挝王国（1947–1975）", name="妇女功绩勋章", date_text="1962年设立", variant="金质级", picks=[1, 2])
    write_one(victory, stem="laos_pdr_wawards_variants", family="LAO-PDR-ORDER-VICTORY-REVOLUTION", country="老挝人民民主共和国（1975–）", name="革命胜利勋章", date_text="1975年设立", variant="图录所示级别；正背", picks=[1, 2])
    print(json.dumps({"rows": 2, "net_new_families": 1, "views": 4}, ensure_ascii=False))


if __name__ == "__main__":
    main()
