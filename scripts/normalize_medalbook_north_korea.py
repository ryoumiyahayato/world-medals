"""Normalize the completed MedalBook North Korea sweep into pictured catalogue rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_north_korea.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_north_korea_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_north_korea"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# record index: Chinese name, stable family, date label, variant, selected views.
# Every selection was checked against the four locally generated contact sheets.
ROWS = {
    0: ("农业功勋奖章", "PRK-MEDAL-AGRICULTURAL-MERIT", "1974年设立", "奖章", [2, 1]),
    1: ("朝鲜解放纪念奖章", "PRK-MEDAL-LIBERATION", "1948年设立", "奖章", [1, 3]),
    2: ("朝鲜总联成立20周年纪念章", "PRK-MEDAL-CHONGRYON-20", "1975年", "纪念章；低清参考", [1]),
    6: ("祖国解放战争纪念奖章", "PRK-MEDAL-FATHERLAND-LIBERATION-WAR", "1950–1953年", "奖章", [1, 3]),
    14: ("军事功勋奖章", "PRK-MEDAL-MILITARY-MERIT", "1949年设立", "第一型", [2, 4]),
    16: ("军事服役荣誉奖章", "PRK-MEDAL-MILITARY-SERVICE-HONOUR", "约1990年代", "奖章", [1, 3]),
    17: ("劳动功勋奖章", "PRK-MEDAL-MERITORIOUS-LABOUR", "1949年设立", "奖章", [1, 2]),
    22: ("祖国解放战争胜利40周年纪念勋章", "PRK-ORDER-WAR-VICTORY-40", "1993年", "纪念勋章", [1, 3]),
    25: ("人民军建军60周年纪念勋章", "PRK-ORDER-PEOPLES-ARMY-60", "1992年", "纪念勋章", [2, 1]),
    28: ("首都建设纪念勋章", "PRK-ORDER-CAPITAL-CONSTRUCTION", "1992年", "纪念勋章；低清参考", [1, 2]),
    29: ("朝鲜民主主义人民共和国建国纪念勋章", "PRK-ORDER-DPRK-FOUNDATION", "1978年起", "建国30／40周年型", [1, 2]),
    37: ("自由独立勋章", "PRK-ORDER-FREEDOM-INDEPENDENCE", "1951年设立", "链章；完整成套正面", [1]),
    39: ("自由独立勋章", "PRK-ORDER-FREEDOM-INDEPENDENCE", "1951年设立", "二级", [2, 1]),
    42: ("劳动勋章", "PRK-ORD-12", "约1970年代起", "第二型", [1, 2]),
    46: ("军事工程服役荣誉勋章", "PRK-ORDER-MILITARY-ENGINEERING-SERVICE", "朝鲜民主主义人民共和国时期", "服役30年章", [2, 1]),
    47: ("军事服役荣誉勋章", "PRK-ORDER-MILITARY-SERVICE-HONOUR", "1951年设立", "一级", [1, 3]),
    48: ("军事服役荣誉勋章", "PRK-ORDER-MILITARY-SERVICE-HONOUR", "1951年设立", "二级", [2, 1]),
    49: ("军事服役荣誉勋章", "PRK-ORDER-MILITARY-SERVICE-HONOUR", "1951年设立", "三级", [2, 1]),
    53: ("战士荣誉勋章", "PRK-ORDER-SOLDIERS-HONOUR", "1950年设立", "一级", [1, 2]),
    54: ("战士荣誉勋章", "PRK-ORDER-SOLDIERS-HONOUR", "1950年设立", "二级", [1, 2]),
    57: ("国旗勋章", "PRK-ORDER-NATIONAL-FLAG", "1948年设立", "一级", [1, 2]),
    58: ("国旗勋章", "PRK-ORDER-NATIONAL-FLAG", "1948年设立", "二级", [1, 3]),
    59: ("国旗勋章", "PRK-ORDER-NATIONAL-FLAG", "1948年设立", "三级", [3, 2]),
    60: ("三大革命红旗勋章", "PRK-ORDER-THREE-REVOLUTIONS", "1986年设立", "勋章", [1, 3]),
    62: ("朝鲜民主主义人民共和国英雄金星奖章", "PRK-HERO-OF-DPRK", "1950年设立", "金星奖章；低清参考", [1]),
}

records = []
manifest = []
used_hashes: set[str] = set()
for idx, (name, family, date, variant, picks) in ROWS.items():
    raw = RAW[idx]
    rid = f"PRK-MB-{idx:03d}-V01"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_north_korea/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"PRK-MB-{idx:03d}-VIEW{n}"
        label = "完整正面" if n == 1 else "完整背面"
        if idx == 37:
            label = "完整成套正面"
        views.append({"key": view_key, "label": label})
        manifest.append({
            "key": f"prk-mb-{idx:03d}-{image_index:02d}", "record_id": rid, "view_key": view_key,
            "local_path": local_rel, "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "MedalBook catalogue object image", "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"],
            "decoded": True, "visually_checked": True,
        })
    records.append({
        "id": rid, "family": family, "country_zh": "朝鲜", "name": name, "original": raw["original_name"],
        "date": date, "variant": variant, "views": views, "source_ids": [raw["source_id"]],
        "image_kind": "object_photo", "html_eligible": True,
    })

unpictured = []
for idx, raw in enumerate(RAW):
    if idx in ROWS:
        continue
    reason = "有记载未配图"
    if idx == 61:
        reason = "目录仅有未证实为官方图式的绘图，暂不进入正文"
    unpictured.append({"source_id": raw["source_id"], "name": raw["page_title"], "date": "待考", "page_url": raw["page_url"], "status": reason})

(ROOT / "data/volumes/north_korea_medalbook_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "朝鲜 · MedalBook", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/north_korea_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured": len(unpictured)}, ensure_ascii=False))
