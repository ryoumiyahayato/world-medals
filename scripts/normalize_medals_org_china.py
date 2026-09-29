"""Normalize the completed ODM People's Republic of China directory."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medals_org_china.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP = json.loads((ROOT / "data/source_sweeps/medals_org_china_2026-09-28.json").read_text(encoding="utf-8"))
item = next(x for x in SWEEP["items"] if x["record_index"] == 0 and x["status"] == "downloaded")
out_dir = ROOT / "assets/images/medals_org_china"
out_dir.mkdir(parents=True, exist_ok=True)
ext = Path(item["local_path"]).suffix.lower() or ".jpg"
local_rel = f"assets/images/medals_org_china/000_01{ext}"
shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)

record = {
    "id": "PRC-ODM-000-V01", "family": "PRC-MEDAL-SINO-SOVIET-FRIENDSHIP", "country_zh": "中华人民共和国",
    "name": "中苏友谊万岁奖章", "original": RAW[0]["original_name"], "date": "1951年发行",
    "variant": "奖章；低清完整参考", "views": [{"key": "PRC-ODM-000-VIEW1", "label": "完整正面"}],
    "source_ids": [RAW[0]["source_id"]], "image_kind": "object_photo", "html_eligible": True,
}
manifest = [{
    "key": "prc-odm-000-01", "record_id": record["id"], "view_key": "PRC-ODM-000-VIEW1", "local_path": local_rel,
    "source_page": RAW[0]["page_url"], "image_url": item["url"], "artist": "ODM / medals.org.uk object image",
    "license": "Source terms apply; retained for offline research catalogue", "dimensions": [item["width"], item["height"]],
    "bytes": item["bytes"], "sha256": item["sha256"], "decoded": True, "visually_checked": True,
}]
unpictured = [
    {"source_id": r["source_id"], "name": r["page_title"], "date": r["instituted_text"], "page_url": r["page_url"], "status": "有记载未配图"}
    for r in RAW[1:]
]
(ROOT / "data/volumes/peoples_republic_china_medals_org.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "中华人民共和国 · ODM", "records": [record]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/peoples_republic_china_medals_org_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"records": 1, "families": 1, "views": 1, "unpictured": len(unpictured)}, ensure_ascii=False))
