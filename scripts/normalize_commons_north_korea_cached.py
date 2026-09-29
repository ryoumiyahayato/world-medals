"""Normalize the currently cached, visually checked Commons North Korea objects."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROWS = [json.loads(line) for line in (ROOT / "data/raw_candidates/commons_north_korea.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
BY_SOURCE = {row["source_id"]: row for row in ROWS}
OUT_DIR = ROOT / "assets/images/commons_north_korea"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# source id, record id, family, Chinese name, date, pictured variant, supersedes.
SELECTED = [
    ("commons-north-korea-0001", "PRK-COM-1949-MILITARY-MERIT-V01", "PRK-MEDAL-MILITARY-MERIT", "军事功勋奖章", "1949年起", "1949年早期三种制作变体；同图含完整正背面", None),
    ("commons-north-korea-0007", "PRK-COM-CHONGRYON20-V01", "PRK-MEDAL-CHONGRYON-20", "朝鲜总联成立20周年纪念章", "1975年", "纪念章；完整正面", "PRK-MB-002-V01"),
    ("commons-north-korea-0009", "PRK-COM-DPRK-FOUNDATION-MEDAL-V01", "PRK-MEDAL-DPRK-FOUNDATION", "朝鲜民主主义人民共和国建国纪念奖章", "朝鲜民主主义人民共和国时期", "版型待考；完整正面", None),
    ("commons-north-korea-0011", "PRK-COM-FATHERLAND-LIBERATION-MEDAL-V01", "PRK-MEDAL-FATHERLAND-LIBERATION", "祖国解放纪念奖章", "朝鲜民主主义人民共和国时期", "完整正面；低清参考", None),
]

records, manifest = [], []
for source_id, rid, family, name, date, variant, supersedes in SELECTED:
    row = BY_SOURCE[source_id]
    src = ROOT / row["local_raw_image"]
    ext = src.suffix.lower()
    local_rel = f"assets/images/commons_north_korea/{source_id.removeprefix('commons-north-korea-')}{ext}"
    shutil.copy2(src, ROOT / local_rel)
    with Image.open(src) as im:
        width, height = im.size
        im.verify()
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    view_key = rid + "-VIEW1"
    record = {
        "id": rid, "family": family, "country_zh": "朝鲜", "name": name,
        "original": row["file_title"].removeprefix("File:"), "date": date, "variant": variant,
        "views": [{"key": view_key, "label": "完整正背面合图" if "正背面" in variant else "完整正面"}],
        "source_ids": [source_id], "image_kind": "object_photo", "html_eligible": True,
    }
    if supersedes:
        record["supersedes_id"] = supersedes
    records.append(record)
    manifest.append({
        "key": rid.lower() + "-image", "record_id": rid, "view_key": view_key, "local_path": local_rel,
        "source_page": row["page_url"], "image_url": row.get("original_image_url"), "artist": row.get("artist"),
        "license": row.get("license"), "dimensions": [width, height], "bytes": src.stat().st_size,
        "sha256": digest, "decoded": True, "visually_checked": True,
    })

unpictured = [
    {"source_id": "commons-north-korea-commons-rate-limit", "name": "Commons朝鲜勋奖章分类树限流文件", "date": "待续传", "page_url": "https://commons.wikimedia.org/wiki/Category:Orders,_decorations_and_medals_of_North_Korea", "status": "95个原图请求受HTTP 429限制；文件页与原图地址已保存，未以缩略预览冒充完成"}
]
excluded = [
    {"source_id": "commons-north-korea-0006", "name": "Chollima Honour Badge", "reason": "荣誉徽章，保留为相关门类候选"},
    {"source_id": "commons-north-korea-0014", "name": "人民军建军纪念勋章", "reason": "与既有本地图文件载荷相同"},
    {"source_id": "commons-north-korea-0015", "name": "建国20周年纪念勋章", "reason": "与既有本地图文件载荷相同"},
    {"source_id": "commons-north-korea-0026", "name": "Military Merit Medal ribbon graphic", "reason": "仅绶带图"},
    {"source_id": "commons-north-korea-0121", "name": "Order of Kim Il Sung BAR", "reason": "仅绶带图"},
    {"source_id": "commons-north-korea-0122", "name": "Order of the National Flag I Class BAR", "reason": "仅绶带图"},
    {"source_id": "commons-north-korea-0123", "name": "Order of the National Flag II Class BAR", "reason": "仅绶带图"},
]

(ROOT / "data/volumes/north_korea_commons_cached_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "朝鲜 · Commons当前缓存", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/north_korea_commons_cached_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured, "excluded_candidates": excluded}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"rows": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "upgrades": sum('supersedes_id' in r for r in records), "excluded": len(excluded)}, ensure_ascii=False))
