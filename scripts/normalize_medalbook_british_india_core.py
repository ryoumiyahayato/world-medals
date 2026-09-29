"""Normalize the completed MedalBook British India core-family sweep."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_british_india_core.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_british_india_core_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_british_india_core"
OUT_DIR.mkdir(parents=True, exist_ok=True)

POLITY = "东印度公司／英属印度（1837–1947）"

# index: Chinese name, family, date, variant, image picks, image nature.
ROWS = {
  0:("印度杰出服务奖章","BIND-MEDAL-DISTINGUISHED-SERVICE","1907年设立","奖章",[1,2],"object_photo"),
  2:("凯萨—印度奖章","BIND-MEDAL-KAISAR-I-HIND","1900年设立","一级·金质",[2,4],"object_photo"),
  3:("凯萨—印度奖章","BIND-MEDAL-KAISAR-I-HIND","1900年设立","二级·银质",[4,5],"object_photo"),
  4:("凯萨—印度奖章","BIND-MEDAL-KAISAR-I-HIND","1900年设立","三级·铜质",[3,4],"object_photo"),
  5:("英属印度勋章","BIND-ORDER-BRITISH-INDIA","1837年设立","一级章饰",[1,6],"object_photo"),
  6:("英属印度勋章","BIND-ORDER-BRITISH-INDIA","1837年设立","二级章饰",[3,4],"object_photo"),
  9:("印度功绩勋章","BIND-ORDER-MERIT","1837年设立","文职组·二级",[1,3],"object_photo"),
  11:("印度功绩勋章","BIND-ORDER-MERIT","1837年设立","军事组·一级",[1],"object_photo"),
  12:("印度功绩勋章","BIND-ORDER-MERIT","1837年设立","军事组·二级；正背合图",[1],"object_photo"),
  13:("印度功绩勋章","BIND-ORDER-MERIT","1837年设立","军事组·三级",[3,1],"object_photo"),
  14:("印度皇冠勋章","BIND-ORDER-CROWN-INDIA","1878年设立","成员章",[4,5],"object_photo"),
  15:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","链饰；历史图录插图",[1],"historical_catalogue"),
  16:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","成员章",[4,1],"object_photo"),
  17:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","大指挥官级章饰",[4,3],"object_photo"),
  18:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","大指挥官级星章",[2,3],"object_photo"),
  19:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","指挥官级章饰",[7,3],"object_photo"),
  20:("印度帝国勋章","BIND-ORDER-INDIAN-EMPIRE","1878年设立","指挥官级星章",[2,3],"object_photo"),
  21:("印度之星勋章","BIND-ORDER-STAR-INDIA","1861年设立","链饰；历史图录插图",[1],"historical_catalogue"),
  22:("印度之星勋章","BIND-ORDER-STAR-INDIA","1861年设立","指挥官级章饰；低清参考",[1,3],"object_photo"),
  24:("印度之星勋章","BIND-ORDER-STAR-INDIA","1861年设立","成员章；低清参考",[1],"object_photo"),
  25:("印度之星勋章","BIND-ORDER-STAR-INDIA","1861年设立","大指挥官级章饰",[3,4],"object_photo"),
  26:("印度之星勋章","BIND-ORDER-STAR-INDIA","1861年设立","大指挥官级星章",[1,2],"object_photo"),
}

records, manifest, used_hashes = [], [], set()
for idx, (name, family, date, variant, picks, image_kind) in ROWS.items():
    raw = RAW[idx]
    rid = f"BIND-MB-{idx:03d}-V01"
    views = []
    for number, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_british_india_core/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"BIND-MB-{idx:03d}-VIEW{number}"
        if image_kind == "historical_catalogue":
            label = "历史图录插图"
        elif idx == 12:
            label = "完整正背"
        else:
            label = "完整正面" if number == 1 else "完整背面"
        views.append({"key": view_key, "label": label})
        manifest.append({
            "key": f"bind-mb-{idx:03d}-{image_index:02d}", "record_id": rid,
            "view_key": view_key, "local_path": local_rel,
            "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "MedalBook catalogue image",
            "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"],
            "sha256": item["sha256"], "decoded": True, "visually_checked": True,
        })
    records.append({
        "id": rid, "family": family, "country_zh": POLITY, "name": name,
        "original": raw["original_name"], "date": date, "variant": variant,
        "views": views, "source_ids": [raw["source_id"]],
        "image_kind": image_kind, "html_eligible": True,
    })

unpictured = [
    {"source_id": row["source_id"], "name": row["page_title"], "date": "待考",
     "page_url": row["page_url"], "status": "有记载未配图" if row["page_title"] not in {"Civilian Division", "Military Division"} else "目录分支，不是奖励条目"}
    for index, row in enumerate(RAW) if index not in ROWS
]
(ROOT / "data/volumes/british_india_medalbook_core.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "东印度公司／英属印度 · MedalBook 核心家族", "records": records}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/british_india_medalbook_core_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured_or_branch": len(unpictured)}, ensure_ascii=False))
