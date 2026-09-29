"""Normalize the complete ODM India directory as a differential batch."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medals_org_india.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medals_org_india_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medals_org_india"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IND = "印度共和国（1950–）"
DOM = "印度自治领（1947–1950）"

# source index, stable suffix, polity, Chinese name, family, date, pictured
# variant, selected images. Ribbon-only pages are deliberately omitted.
ROWS = [
  (1,"01",IND,"印度国宝勋章","IND-ORDER-BHARAT-RATNA","1954年设立","章饰；低清参考",[2,3]),
  (4,"01",IND,"阿育王轮奖章","IND-MEDAL-ASHOKA-CHAKRA","1952年设立","原始一级型；低清参考",[2,3]),
  (14,"01",IND,"印度警察独立纪念章","IND-MEDAL-POLICE-INDEPENDENCE","1950年","奖章；低清参考",[2,3]),
  (15,"01",IND,"英勇轮章","IND-MEDAL-VIR-CHAKRA","1950年设立","奖章；低清参考",[2,3]),
  (18,"01",IND,"三十年长期服役奖章","IND-MEDAL-LS-30","1980年设立","奖章；低清参考",[2,3]),
  (21,"01",DOM,"印度独立纪念章","DOM-IND-MEDAL-INDEPENDENCE-1947","1949年设立","1947纪年型；低清参考",[2,3]),
  (22,"01",IND,"国家学员团长期服役奖章","IND-MEDAL-NCC-LS","日期待考","七年服役型；低清参考",[2,3]),
  (23,"01",IND,"国家学员团长期服役奖章","IND-MEDAL-NCC-LS","日期待考","十二年服役型；低清参考",[2,3]),
  (24,"01",IND,"国防警卫军团奖章","IND-MEDAL-DEFENCE-SECURITY-CORPS","1964年设立","普通型；低清参考",[2,3]),
  (25,"01",IND,"高级国防警卫军团奖章","IND-MEDAL-DEFENCE-SECURITY-CORPS","1964年设立","高级型；低清参考",[2,3]),
  (26,"01",IND,"领土军奖章","IND-MEDAL-TERRITORIAL-ARMY","1952年设立","奖章；低清参考",[2,3]),
  (27,"01",IND,"领土军勋章","IND-DECORATION-TERRITORIAL-ARMY","1952年设立","勋章；低清参考",[2,3]),
  (28,"01",IND,"长期服役与良好品行奖章","IND-MEDAL-LSGC","1957年设立","酒红白边绶带版；低清参考",[3,5]),
  (28,"02",IND,"长期服役与良好品行奖章","IND-MEDAL-LSGC","1957年设立","灰蓝红边绶带版；低清参考",[4,6]),
  (29,"01",IND,"海岸警卫队奖章","IND-MEDAL-COAST-GUARD","日期待考","奖章；低清参考",[2,3]),
  (30,"01",IND,"功绩服务奖章","IND-MEDAL-MERITORIOUS-SERVICE","1957年设立","酒红白边绶带版；低清参考",[3,5]),
  (30,"02",IND,"功绩服务奖章","IND-MEDAL-MERITORIOUS-SERVICE","1957年设立","灰蓝红边绶带版；低清参考",[4,6]),
]

records, manifest, used_hashes = [], [], set()
for idx, suffix, country, name, family, date, variant, picks in ROWS:
    raw = RAW[idx]
    rid = f"IND-ODM-{idx:03d}-V{suffix}"
    views = []
    for number, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medals_org_india/{idx:03d}_{suffix}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"IND-ODM-{idx:03d}-V{suffix}-VIEW{number}"
        views.append({"key": view_key, "label": "完整正面" if number == 1 else "完整背面"})
        manifest.append({
            "key": f"ind-odm-{idx:03d}-{suffix}-{image_index:02d}", "record_id": rid,
            "view_key": view_key, "local_path": local_rel,
            "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "ODM / medals.org.uk directory image",
            "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"],
            "sha256": item["sha256"], "decoded": True, "visually_checked": True,
        })
    records.append({
        "id": rid, "family": family, "country_zh": country, "name": name,
        "original": raw["original_name"], "date": date, "variant": variant,
        "views": views, "source_ids": [raw["source_id"]], "image_kind": "object_photo",
        "html_eligible": True,
    })

selected_indices = {row[0] for row in ROWS}
unpictured = [
    {"source_id": row["source_id"], "name": row["page_title"], "date": row.get("instituted_text") or "待考",
     "page_url": row["page_url"], "status": "仅绶带图／有记载未配完整章图" if index not in selected_indices else "已有同章种来源差集记录"}
    for index, row in enumerate(RAW) if index not in selected_indices
]
(ROOT / "data/volumes/india_medals_org_differential.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "印度共和国／印度自治领 · ODM 差集", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/india_medals_org_differential_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured_or_ribbon_only": len(unpictured)}, ensure_ascii=False))
