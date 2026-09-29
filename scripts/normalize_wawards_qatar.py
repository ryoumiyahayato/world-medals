"""Create one complete representative row for every pictured Qatar award page."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    json.loads(line)
    for line in (ROOT / "data/raw_candidates/wawards_qatar.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
NAMES = {
    "order-of-independence": "独立勋章",
    "order-of-merit": "功绩勋章",
    "medal-of-bravery-1978": "英勇奖章",
    "medal-for-outstanding-service-1978": "卓越服务奖章",
    "long-service-and-good-conduct-medal-1978": "长期服务与品行优良奖章",
    "order-of-military-gallantry": "军事英勇勋章",
    "order-of-military-duty": "军事职责勋章",
    "order-of-faithful-service": "忠诚服务勋章",
    "medal-of-honour": "荣誉奖章",
    "medal-of-innovation": "创新奖章",
    "medal-of-efficient-leadership": "高效领导奖章",
    "medal-of-efficient-training": "高效训练奖章",
    "medal-of-perfection": "精通奖章",
    "medal-of-combat": "战斗奖章",
    "medal-of-independence-anniversary": "独立纪念奖章",
    "land-forces-medal": "陆军奖章",
    "air-force-medal": "空军奖章",
    "naval-forces-medal": "海军奖章",
    "medal-of-accession-anniversary": "埃米尔即位纪念奖章",
    "martyr-s-order": "烈士勋章",
    "order-of-military-duty-2021": "军事职责勋章",
    "order-of-military-merit": "军事功绩勋章",
    "order-of-military-service": "军事服务勋章",
    "gallantry-order": "英勇勋章",
}
FAMILY_OVERRIDE = {
    "order-of-military-duty-2021": "order-of-military-duty",
}

OUT = ROOT / "assets/images/wawards_qatar"
OUT.mkdir(parents=True, exist_ok=True)
records = []
images = []
unpictured = []
for row in ROWS:
    slug = Path(urlparse(row["object_url"]).path).stem
    name = NAMES.get(slug, slug.replace("-", " "))
    family_slug = FAMILY_OVERRIDE.get(slug, slug)
    family = f"QAT-WAWARDS-{family_slug.upper().replace('-', '_')}"
    if not row["original_images"]:
        unpictured.append({"source_id": row["source_id"], "name": name, "reason": "source object page has no exposed full image"})
        continue
    item = row["original_images"][0]
    src = ROOT / item["local_path"]
    rel = f"assets/images/wawards_qatar/{slug}{src.suffix.lower()}"
    shutil.copy2(src, ROOT / rel)
    with Image.open(src) as im:
        w, h = im.size
        im.verify()
    rid = f"QAT-WAWARDS-{slug.upper().replace('-', '_')}-REPRESENTATIVE"
    view = rid + "-VIEW1"
    date = (row.get("date_candidates") or ["日期待考"])[0]
    if date != "日期待考":
        date = f"{date}年设立／纪年"
    variant = "World Awards对象页所示完整章体；具体等级待考"
    if slug == "order-of-military-duty-2021":
        variant = "2021年版；World Awards对象页所示完整章体；具体等级待考"
    records.append({
        "id": rid,
        "family": family,
        "country_zh": "卡塔尔国",
        "name": name,
        "original": row["page_title"],
        "date": date,
        "variant": variant,
        "views": [{"key": view, "label": "完整图样"}],
        "source_ids": [row["source_id"]],
        "image_kind": "catalogue_object_or_illustration",
        "html_eligible": True,
    })
    images.append({
        "key": rid.lower() + "-image",
        "record_id": rid,
        "view_key": view,
        "local_path": rel,
        "source_page": row["object_url"],
        "image_url": item["image_url"],
        "license": "source-site research use; publication rights not asserted",
        "dimensions": [w, h],
        "bytes": src.stat().st_size,
        "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "decoded": True,
        "visually_checked": True,
    })

(ROOT / "data/volumes/qatar_wawards_families.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "卡塔尔国", "records": records}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/qatar_wawards_families_manifest.json").write_text(
    json.dumps({
        "as_of": "2026-09-28",
        "images": images,
        "unpictured_candidates": unpictured,
        "notes": ["First pass establishes family coverage; all additional source images remain cached for grade-level normalization."],
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({
    "source_rows": len(ROWS),
    "rows": len(records),
    "families": len({record["family"] for record in records}),
    "views": len(images),
    "unpictured": len(unpictured),
}, ensure_ascii=False))
