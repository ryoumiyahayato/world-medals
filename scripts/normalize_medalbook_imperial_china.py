"""Normalize the completed MedalBook Imperial China sweep into Qing catalogue rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_imperial_china.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_imperial_china_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_imperial_china"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# record index: Chinese name, stable family, date, pictured variant, selected image indices,
# image nature, optional explicit single-image label. All selections were checked against the
# eight local contact sheets; ribbon-only and detail-only frames are not selected.
ROWS = {
    0: ("驻柏林使馆纪念章", "QNG-MEDAL-BERLIN-LEGATION", "1896年", "鎏金版；历史图录插图", [1], "historical_catalogue", None),
    1: ("驻柏林使馆纪念章", "QNG-MEDAL-BERLIN-LEGATION", "1896年", "银质版", [3, 2], "object_photo", None),
    5: ("维多利亚女王钻禧中国功牌", "QNG-DECORATION-CHINESE-MERIT-1897", "1897年", "一等", [2], "object_photo", None),
    6: ("维多利亚女王钻禧中国功牌", "QNG-DECORATION-CHINESE-MERIT-1897", "1897年", "二等", [1], "object_photo", None),
    7: ("维多利亚女王钻禧中国功牌", "QNG-DECORATION-CHINESE-MERIT-1897", "1897年", "三等", [1], "object_photo", None),
    10: ("驻伦敦使馆纪念章", "QNG-MEDAL-LONDON-LEGATION", "1896年", "李鸿章西行纪念", [1], "object_photo", None),
    15: ("太平天国战事功牌", "QNG-MEDAL-TAIPING-MERIT", "1862–1864年", "银质版；历史图录插图", [1], "historical_catalogue", None),
    18: ("皇嗣诞生奉祝纪念章", "QNG-MEDAL-ROYAL-BIRTH-BLESSING", "清末", "纪念章", [1, 3], "object_photo", None),
    20: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "头等第二品（红宝石）；历史图录插图", [1], "historical_catalogue", None),
    21: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "头等第三品（珊瑚）", [1, 2], "object_photo", None),
    22: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "二等第一品章饰", [1], "object_photo", None),
    23: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "二等第一品星章；历史图录插图", [1], "historical_catalogue", None),
    24: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "二等第二品章饰", [1, 4], "object_photo", None),
    25: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "二等第二品星章", [1, 2], "object_photo", None),
    27: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "二等第三品领绶章；历史图录插图", [1], "historical_catalogue", None),
    28: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "三等第一品章饰；历史图录插图", [1], "historical_catalogue", None),
    29: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "三等第一品星章", [2, 1], "object_photo", None),
    30: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "三等第二品章饰；历史图录正反面合图", [3], "historical_catalogue", "完整正反面合图"),
    32: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "三等第三品章饰；历史图录正反面合图", [1], "historical_catalogue", "完整正反面合图"),
    33: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "三等第三品星章；历史图录插图", [1], "historical_catalogue", None),
    34: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "1882年设立；第一式", "四等章", [5, 3], "object_photo", None),
    37: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "头等第一品星章", [1, 3], "object_photo", None),
    40: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "头等第三品大绶章章饰", [2, 1], "object_photo", None),
    41: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "头等第三品星章", [1, 2], "object_photo", None),
    42: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第一品领绶章", [6, 3], "object_photo", None),
    43: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第一品星章；历史图录插图", [1], "historical_catalogue", None),
    44: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第二品领绶章；历史图录插图", [1], "historical_catalogue", None),
    45: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第二品星章；历史图录插图", [1], "historical_catalogue", None),
    46: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第三品领绶章；历史图录插图", [1], "historical_catalogue", None),
    47: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "二等第三品星章", [6, 7], "object_photo", None),
    48: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "三等第一品领绶章；历史图录插图", [1], "historical_catalogue", None),
    49: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "三等第一品星章；历史图录插图", [1], "historical_catalogue", None),
    50: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "三等第二品领绶章（盒装）", [4], "object_photo", None),
    51: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "三等第二品星章", [2, 5], "object_photo", None),
    52: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "三等第三品星章", [4, 6], "object_photo", None),
    53: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "四等章", [1, 2], "object_photo", None),
    54: ("双龙宝星", "QNG-ORDER-DOUBLE-DRAGON", "约1900–1912年；第二式", "五等章", [2, 1], "object_photo", None),
    55: ("宝星功牌", "QNG-ORDER-IMPERIAL-DRAGON-PAO-HSING", "1862年设立", "铜质功牌", [1, 5], "object_photo", None),
    56: ("宝星功牌", "QNG-ORDER-IMPERIAL-DRAGON-PAO-HSING", "1862年设立", "一等；历史图录正反面合图", [3], "historical_catalogue", "完整正反面合图"),
    57: ("宝星功牌", "QNG-ORDER-IMPERIAL-DRAGON-PAO-HSING", "1862年设立", "蓝色宝石版；历史图录正反面合图", [1], "historical_catalogue", "完整正反面合图"),
    58: ("宝星功牌", "QNG-ORDER-IMPERIAL-DRAGON-PAO-HSING", "1862年设立", "绿色宝石版", [5, 8], "object_photo", None),
    60: ("宝星功牌", "QNG-ORDER-IMPERIAL-DRAGON-PAO-HSING", "1862年设立", "白色宝石版；历史图录正反面合图", [1], "historical_catalogue", "完整正反面合图"),
}

records = []
manifest = []
used_hashes: set[str] = set()
for idx, (name, family, date, variant, picks, image_kind, single_label) in ROWS.items():
    raw = RAW[idx]
    rid = f"QNG-MB-{idx:03d}-V01"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_imperial_china/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"QNG-MB-{idx:03d}-VIEW{n}"
        label = single_label if len(picks) == 1 and single_label else ("完整正面" if n == 1 else "完整背面")
        views.append({"key": view_key, "label": label})
        manifest.append({
            "key": f"qng-mb-{idx:03d}-{image_index:02d}",
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
        "country_zh": "大清帝国（1644–1912）",
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

(ROOT / "data/volumes/qing_medalbook_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "大清帝国（1644–1912）· MedalBook", "records": records}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/qing_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "unpictured": len(unpictured)}, ensure_ascii=False))
