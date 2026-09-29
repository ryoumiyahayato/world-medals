"""Normalize the completed MedalBook Manchukuo sweep into pictured catalogue rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_manchukuo.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_manchukuo_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_manchukuo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# record index: Chinese name, stable family, date label, variant label, selected images,
# image nature. Selections were checked against five local contact sheets.
ROWS = {
    0: ("国境战争奖章", "MCK-MEDAL-BORDER-WAR", "1939年", "奖章", [1, 2], "object_photo"),
    5: ("访日纪念章", "MCK-MEDAL-IMPERIAL-VISIT-JAPAN", "1935年", "奖章", [2, 3], "object_photo"),
    7: ("满洲国红十字会名誉会员章", "MCK-MEDAL-RED-CROSS-HONORARY", "约1930年代", "名誉会员章", [2, 1], "historical_catalogue"),
    8: ("满洲国红十字会有功章", "MCK-MEDAL-RED-CROSS-MERIT", "1938年", "有功章", [1, 3], "object_photo"),
    10: ("公共服务奖章", "MCK-MEDAL-PUBLIC-SERVICE", "1932–1945年", "奖章；同图含正反面", [1], "historical_catalogue"),
    15: ("建国纪念章", "MCK-MEDAL-NATIONAL-FOUNDATION-COMMEMORATIVE", "1932年", "纪念章；同图含正反面", [1], "historical_catalogue"),
    16: ("建国功劳章", "MCK-MEDAL-NATIONAL-FOUNDATION-MERIT", "1932–1934年", "功劳章", [1, 2], "object_photo"),
    17: ("建国神庙创建纪念章", "MCK-MEDAL-NATIONAL-SHRINE-FOUNDATION", "1940年", "纪念章", [3, 2], "object_photo"),
    20: ("大勋位兰花章", "MCK-ORDER-ORCHID-BLOSSOM", "1934年设立", "大绶章章饰；历史图录插图", [1], "historical_catalogue"),
    21: ("大勋位兰花章", "MCK-ORDER-ORCHID-BLOSSOM", "1934年设立", "大绶章副章（星章）；历史图录插图", [1], "historical_catalogue"),
    22: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "一等大绶章章饰", [1, 5], "object_photo"),
    23: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "一等大绶章副章（星章）", [4, 7], "object_photo"),
    24: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "二等章章饰", [6, 4], "object_photo"),
    25: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "二等章副章（星章）", [2, 3], "object_photo"),
    26: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "三等章（领绶）", [3, 1], "object_photo"),
    27: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "四等章（襟绶结花）", [2, 1], "object_photo"),
    28: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "五等章；历史图录插图", [1], "historical_catalogue"),
    29: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "六等章", [1, 3], "object_photo"),
    31: ("景云章", "MCK-ORDER-AUSPICIOUS-CLOUDS", "1934年设立", "八等章", [2, 3], "object_photo"),
    32: ("龙光章", "MCK-ORDER-ILLUSTRIOUS-DRAGON", "1934年设立", "大绶章章饰；历史图录插图", [1], "historical_catalogue"),
    33: ("龙光章", "MCK-ORDER-ILLUSTRIOUS-DRAGON", "1934年设立", "大绶章副章（星章）；历史图录插图", [1], "historical_catalogue"),
    34: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "一等大绶章章饰", [3, 2], "object_photo"),
    35: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "一等大绶章副章（星章）；历史图录插图", [1], "historical_catalogue"),
    36: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "二等章章饰", [3, 2], "object_photo"),
    37: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "二等章副章（星章）；历史图录插图", [1], "historical_catalogue"),
    38: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "三等章（领绶）", [4, 5], "object_photo"),
    39: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "四等章（襟绶结花）", [3, 2], "object_photo"),
    40: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "五等章", [1, 2], "object_photo"),
    41: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "六等章", [4, 6], "object_photo"),
    43: ("柱国章", "MCK-ORDER-PILLARS-OF-STATE", "1936年设立", "八等章", [4, 1], "object_photo"),
}

records = []
manifest = []
used_hashes: set[str] = set()
for idx, (name, family, date, variant, picks, image_kind) in ROWS.items():
    raw = RAW[idx]
    rid = f"MCK-MB-{idx:03d}-V01"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_manchukuo/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"MCK-MB-{idx:03d}-VIEW{n}"
        if len(picks) == 1:
            label = "完整正面" if "同图含正反面" not in variant else "完整正反面合图"
        else:
            label = "完整正面" if n == 1 else "完整背面"
        views.append({"key": view_key, "label": label})
        manifest.append({
            "key": f"mck-mb-{idx:03d}-{image_index:02d}",
            "record_id": rid,
            "view_key": view_key,
            "local_path": local_rel,
            "source_page": raw["page_url"],
            "image_url": item["url"],
            "artist": "MedalBook catalogue image",
            "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]],
            "bytes": item["bytes"],
            "sha256": item["sha256"],
            "decoded": True,
            "visually_checked": True,
        })
    records.append({
        "id": rid,
        "family": family,
        "country_zh": "满洲国（1932–1945）",
        "name": name,
        "original": raw["original_name"],
        "date": date,
        "variant": variant,
        "views": views,
        "source_ids": [raw["source_id"]],
        "image_kind": image_kind,
        "html_eligible": True,
    })

unpictured = []
for idx, raw in enumerate(RAW):
    if idx in ROWS:
        continue
    unpictured.append({
        "source_id": raw["source_id"],
        "name": raw["page_title"],
        "date": "待考",
        "page_url": raw["page_url"],
        "status": "有记载未配图",
    })

(ROOT / "data/volumes/manchukuo_medalbook_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "满洲国（1932–1945）· MedalBook", "records": records}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/manchukuo_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured": len(unpictured)}, ensure_ascii=False))
