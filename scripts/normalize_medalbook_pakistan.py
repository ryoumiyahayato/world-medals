"""Normalize every usable pictured object from the complete MedalBook Pakistan sweep."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_pakistan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_pakistan_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x.get("status") == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_pakistan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# source index: Chinese name, stable family, date, exact pictured variant, image indices.
ROWS = {
    16: ("伊斯兰历十四世纪纪念章", "PAK-MED-HIJRI", "1979年", "纪念章", [2, 3]),
    19: ("勇气奖章", "PAK-MED-TAMGHA-JURAT", "1957年设立", "Tamgha-i-Jur'at；战斗英勇奖章", [1]),
    20: ("英勇品行奖章", "PAK-MED-TAMGHA-BASALAT", "1957年设立", "Tamgha-i-Basalat；非战斗英勇奖章", [2]),
    23: ("服役奖章", "PAK-MED-SERVICE-LONG", "1957年设立", "银质版", [2, 4]),
    27: ("巴基斯坦独立纪念章", "PAK-MED-INDEPENDENCE", "1948年设立（纪念1947年独立）", "纪念章", [2, 1]),
    28: ("警察英勇奖章", "PAK-MED-POLICE-GALLANTRY", "1954年设立", "警察英勇版", [2]),
    40: ("勇气之星", "MENA7-SITARA-E-JURAT", "1957年设立", "Sitara-i-Jur'at；军官／准尉级战斗英勇章", [2]),
    42: ("1965年战争奖章", "PAK-MED-WAR-1965", "1965年", "1385 Tamgha-i-Jang", [2, 3]),
    122: ("服务勋章", "PAK-ORD-NISHAN-KHIDMAT", "1975–1986年", "第二型；四等章（Tamgha-i-Khidmat）", [2, 1]),
    125: ("服务勋章", "PAK-ORD-NISHAN-KHIDMAT", "1986年起", "第三型；二等章（Hilal-i-Khidmat）", [3, 2]),
}

records=[]; images=[]; used_hashes=set()
for idx,(name,family,date,variant,picks) in ROWS.items():
    raw=RAW[idx]; rid=f"PAK-MB-{idx:03d}-V01"; views=[]
    for n,image_index in enumerate(picks,1):
        item=IMAGE_BY_KEY[(idx,image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext=Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel=f"assets/images/medalbook_pakistan/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT/item["local_path"],ROOT/local_rel)
        view_key=f"PAK-MB-{idx:03d}-VIEW{n}"
        views.append({"key":view_key,"label":"完整正面" if n==1 else "完整背面"})
        images.append({
            "key":f"pak-mb-{idx:03d}-{image_index:02d}","record_id":rid,"view_key":view_key,
            "local_path":local_rel,"source_page":raw["page_url"],"image_url":item["url"],
            "artist":"MedalBook catalogue object image","license":"Source terms apply; retained for offline research catalogue",
            "dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],
            "decoded":True,"visually_checked":True,
        })
    records.append({
        "id":rid,"family":family,"country_zh":"巴基斯坦","name":name,"original":raw["original_name"],
        "date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],
        "image_kind":"object_photo","html_eligible":True,
    })

pending=[]
for idx,raw in enumerate(RAW):
    if idx not in ROWS:
        pending.append({"source_id":raw["source_id"],"name":raw["page_title"],"date":"待考","page_url":raw["page_url"],"status":"有记载未配完整图"})

(ROOT/"data/volumes/pakistan_medalbook_variants.json").write_text(
    json.dumps({"as_of":"2026-09-28","volume":"巴基斯坦 · MedalBook","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/pakistan_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending":len(pending)},ensure_ascii=False))
