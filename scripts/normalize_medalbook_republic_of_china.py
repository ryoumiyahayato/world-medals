"""Normalize the completed MedalBook Republic of China sweep into pictured rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_republic_of_china.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_republic_of_china_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_republic_of_china"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# index: Chinese working name, stable family, date, pictured grade/type, selected images,
# image nature, optional superseded generic row. Selections were checked against all seven sheets.
ROWS = {
    6: ("直隶赈灾功勋章", "ROC-WARLORD-CATASTROPHE-RELIEF", "1912–1928年", "一等；历史图录插图", [1], "historical_catalogue", None),
    7: ("直隶赈灾功勋章", "ROC-WARLORD-CATASTROPHE-RELIEF", "1912–1928年", "二等；历史图录插图", [1], "historical_catalogue", None),
    10: ("直隶赈灾功勋章", "ROC-WARLORD-CATASTROPHE-RELIEF", "1912–1928年", "五等；历史图录插图", [1], "historical_catalogue", None),
    26: ("剿匪功绩章", "ROC-WARLORD-SUPPRESSION-BANDITS", "约1921年", "直隶地区版", [1, 3], "object_photo", None),
    28: ("共和功绩章", "ROC-WARLORD-REPUBLIC-MERIT", "1912年", "二等；历史图录插图", [1], "historical_catalogue", None),
    30: ("共和功绩章", "ROC-WARLORD-REPUBLIC-MERIT", "1912–1928年", "一等；历史图录插图", [1], "historical_catalogue", None),
    33: ("爱国军功勋章", "ROC-WARLORD-PATRIOT-ARMY-MERIT", "1922年", "一等", [1, 3], "object_photo", None),
    45: ("袁世凯就职纪念章", "ROC-MEDAL-YUAN-INAUGURATION", "1913年", "就职纪念章；历史图录插图", [1], "historical_catalogue", None),
    51: ("曹锟就职纪念章", "ROC-MEDAL-CAO-KUN-INAUGURATION", "1923年", "就职纪念章；历史图录插图", [1], "historical_catalogue", None),
    56: ("曹锟功绩章", "ROC-MEDAL-CAO-KUN-MERIT", "约1923年", "功绩章；历史图录插图", [1], "historical_catalogue", None),
    61: ("第一次世界大战服役奖章", "ROC-MEDAL-WWI-SERVICE", "约1920年", "军官版", [1, 2], "object_photo", None),
    65: ("王承斌功绩章", "ROC-MEDAL-WANG-CHENGBIN-MERIT", "约1924年", "功绩章；历史图录插图", [1], "historical_catalogue", None),
    68: ("吴佩孚功绩章", "ROC-MEDAL-WU-PEIFU-MERIT", "1912–1928年", "功绩章；历史图录插图", [1], "historical_catalogue", None),
    70: ("吴佩孚资格奖章", "ROC-MEDAL-WU-PEIFU-QUALIFICATION", "约1915–1928年", "资格奖章；历史图录插图", [1], "historical_catalogue", None),
    71: ("吴佩孚神枪手奖章", "ROC-MEDAL-WU-PEIFU-SHARPSHOOTER", "约1915–1928年", "射击奖励章", [1, 2], "object_photo", None),
    73: ("徐世昌就职纪念章", "ROC-MEDAL-XU-SHICHANG-INAUGURATION", "1918年", "就职纪念章；历史图录插图", [1], "historical_catalogue", None),
    76: ("袁世凯功绩章", "ROC-MEDAL-YUAN-MERIT", "约1913年", "一等", [3], "object_photo", None),
    84: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "一等大绶章章饰；历史图录插图", [1], "historical_catalogue", None),
    85: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "一等星章", [1, 3], "object_photo", None),
    86: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "二等大绶章章饰；历史图录插图", [1], "historical_catalogue", None),
    87: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "二等星章", [7, 6], "object_photo", None),
    88: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "三等领绶章；历史图录插图", [1], "historical_catalogue", None),
    91: ("宝光嘉禾勋章", "ROC-ORDER-BRILLIANT-GOLDEN-GRAIN", "1912–1916年", "五等襟绶章", [2, 1], "object_photo", None),
    110: ("宝鼎勋章", "ROC-ORD-03", "1929年设立", "四等领绶章；历史图录插图", [1], "historical_catalogue", "ROC-ORD-03-V01"),
    112: ("宝鼎勋章", "ROC-ORD-03", "1929年设立", "五等领绶章", [3, 2], "object_photo", None),
    126: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "一等大绶章章饰", [1, 2], "object_photo", None),
    128: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "二等大绶章章饰；历史图录插图", [1], "historical_catalogue", None),
    129: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "二等星章；历史图录插图", [1], "historical_catalogue", None),
    130: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "三等领绶章；历史图录插图", [1], "historical_catalogue", None),
    132: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "五等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    133: ("采玉勋章", "ROC-ORDER-BRILLIANT-JADE", "1933年设立", "六等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    134: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "一等大绶章章饰", [2, 3], "object_photo", None),
    135: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "一等星章", [2, 6], "object_photo", None),
    136: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "二等大绶章章饰", [4, 2], "object_photo", None),
    137: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "二等星章", [1, 7], "object_photo", None),
    138: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "三等领绶章", [1, 3], "object_photo", None),
    139: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "四等襟绶章", [7, 4], "object_photo", None),
    141: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "五等襟绶章", [3, 7], "object_photo", None),
    142: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "六等襟绶章", [6], "object_photo", None),
    143: ("嘉禾勋章", "ROC-ORDER-GOLDEN-GRAIN", "1912年设立", "七等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    145: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "一等大绶章章饰；历史图录插图", [1], "historical_catalogue", None),
    146: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "一等星章", [2], "object_photo", None),
    147: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "二等大绶章章饰", [2, 3], "object_photo", None),
    148: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "二等星章", [2, 4], "object_photo", None),
    149: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "三等领绶章", [2, 1], "object_photo", None),
    151: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "四等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    153: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "五等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    154: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "六等襟绶章；历史图录插图", [1], "historical_catalogue", None),
    155: ("文虎勋章", "ROC-ORDER-STRIPED-TIGER", "1912–1928年", "七等襟绶章", [5, 6], "object_photo", None),
}

records, manifest, used_hashes = [], [], set()
for idx, (name, family, date, variant, picks, image_kind, supersedes) in ROWS.items():
    raw = RAW[idx]
    rid = f"ROC-MB-{idx:03d}-V01"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_republic_of_china/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"ROC-MB-{idx:03d}-VIEW{n}"
        views.append({"key": view_key, "label": "完整正面" if n == 1 else "完整背面"})
        manifest.append({
            "key": f"roc-mb-{idx:03d}-{image_index:02d}", "record_id": rid, "view_key": view_key,
            "local_path": local_rel, "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "MedalBook catalogue image", "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"],
            "decoded": True, "visually_checked": True,
        })
    record = {
        "id": rid, "family": family, "country_zh": "中华民国", "name": name, "original": raw["original_name"],
        "date": date, "variant": variant, "views": views, "source_ids": [raw["source_id"]],
        "image_kind": image_kind, "html_eligible": True,
    }
    if supersedes:
        record["supersedes_id"] = supersedes
    records.append(record)

unpictured = [{"source_id": r["source_id"], "name": r["page_title"], "date": "待考", "page_url": r["page_url"], "status": "有记载未配图"}
              for i, r in enumerate(RAW) if i not in ROWS]
(ROOT / "data/volumes/republic_of_china_medalbook_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "中华民国 · MedalBook", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/republic_of_china_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured": len(unpictured)}, ensure_ascii=False))
