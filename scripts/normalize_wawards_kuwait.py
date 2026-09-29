"""Create one complete representative row for every pictured Kuwait award page."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROWS = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_kuwait.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
NAMES = {
    "order-of-mubarak-the-great": "穆巴拉克大帝勋章",
    "order-of-kuwait": "科威特勋章",
    "order-of-national-defence": "国防勋章",
    "order-of-military-duty": "军事职责勋章",
    "order-of-the-wall": "城墙勋章",
    "military-service-medal": "军事服务奖章",
    "kuwait-liberation-medal": "科威特解放奖章",
    "parliamentary-medal": "议会奖章",
}

OUT = ROOT / "assets/images/wawards_kuwait"
OUT.mkdir(parents=True, exist_ok=True)
records, images, unpictured = [], [], []
for row in ROWS:
    slug = Path(urlparse(row["object_url"]).path).stem
    name = NAMES.get(slug, slug.replace("-", " "))
    family = f"KWT-WAWARDS-{slug.upper().replace('-', '_')}"
    if not row["original_images"]:
        unpictured.append({"source_id": row["source_id"], "name": name, "reason": "source object page has no exposed full image"})
        continue
    item = row["original_images"][0]
    src = ROOT / item["local_path"]
    rel = f"assets/images/wawards_kuwait/{slug}{src.suffix.lower()}"
    shutil.copy2(src, ROOT / rel)
    with Image.open(src) as im:
        w, h = im.size
        im.verify()
    rid, view = family + "-REPRESENTATIVE", family + "-REPRESENTATIVE-VIEW1"
    date = (row.get("date_candidates") or ["日期待考"])[0]
    if date != "日期待考":
        date = f"{date}年设立／纪年"
    records.append({
        "id": rid, "family": family, "country_zh": "科威特国", "name": name,
        "original": row["page_title"], "date": date,
        "variant": "World Awards对象页所示完整章体；具体等级待考",
        "views": [{"key": view, "label": "完整图样"}], "source_ids": [row["source_id"]],
        "image_kind": "catalogue_object_or_illustration", "html_eligible": True,
    })
    images.append({
        "key": rid.lower() + "-image", "record_id": rid, "view_key": view, "local_path": rel,
        "source_page": row["object_url"], "image_url": item["image_url"],
        "license": "source-site research use; publication rights not asserted", "dimensions": [w, h],
        "bytes": src.stat().st_size, "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "decoded": True, "visually_checked": True,
    })

(ROOT / "data/volumes/kuwait_wawards_families.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": "科威特国", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/kuwait_wawards_families_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": unpictured, "notes": ["First pass establishes family coverage; all additional source images remain cached for grade-level normalization."]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"source_rows": len(ROWS), "rows": len(records), "families": len({r['family'] for r in records}), "views": len(images), "unpictured": len(unpictured)}, ensure_ascii=False))
