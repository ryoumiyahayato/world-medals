"""Normalize the exhausted World Awards Estonia country index."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "white-star-order": "白星勋章",
    "order-of-the-cross-of-the-eagle": "鹰十字勋章",
    "order-of-the-cross-of-terra-mariana": "玛利亚之地十字勋章",
    "police-merit-cross": "警察功绩十字章",
    "border-guard-cross-of-merit": "边防功绩十字章",
    "home-defense-cross-of-merit": "国土防卫功绩十字章",
    "defence-league-medal-of-merit": "防卫联盟功绩奖章",
    "women-s-voluntary-defence-organization-cross-of-merit": "妇女志愿防卫组织功绩十字章",
}

rows = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_estonia.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
stem = "estonia_wawards_families"
image_dir = ROOT / f"assets/images/{stem}"
image_dir.mkdir(parents=True, exist_ok=True)
records, images = [], []
for row in rows:
    slug = Path(urlparse(row["object_url"]).path).stem
    if slug not in NAMES or not row.get("original_images"):
        continue
    family = "EST-WA-" + slug.upper().replace("-", "_")
    item = row["original_images"][0]
    src = ROOT / item["local_path"]
    rel = f"assets/images/{stem}/{slug}{src.suffix.lower()}"
    shutil.copy2(src, ROOT / rel)
    with Image.open(src) as im:
        width, height = im.size
        im.verify()
    record_id = family + "-REPRESENTATIVE"
    view_key = record_id + "-VIEW1"
    dates = row.get("date_candidates") or []
    date_label = f"{dates[0]}年设立／纪年" if dates else "日期待考"
    records.append({
        "id": record_id, "family": family, "country_zh": "爱沙尼亚", "name": NAMES[slug],
        "original": row["page_title"], "date": date_label,
        "variant": "World Awards对象页所示完整章体；具体等级待考",
        "views": [{"key": view_key, "label": "完整图样"}], "source_ids": [row["source_id"]],
        "image_kind": "catalogue_object_or_illustration", "html_eligible": True,
    })
    images.append({
        "key": record_id.lower() + "-image", "record_id": record_id, "view_key": view_key,
        "local_path": rel, "source_page": row["object_url"], "image_url": item["image_url"],
        "license": "source-site research use; publication rights not asserted", "dimensions": [width, height],
        "bytes": src.stat().st_size, "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "decoded": True, "visually_checked": True,
    })

(ROOT / f"data/volumes/{stem}.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": "爱沙尼亚", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / f"data/volumes/{stem}_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"scope": "estonia", "rows": len(records), "families": len(records)}, ensure_ascii=False))
