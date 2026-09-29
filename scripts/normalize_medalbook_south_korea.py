"""Normalize the MedalBook South Korea sweep and split Korean Empire material correctly."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_south_korea.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_south_korea_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x.get("status") == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_south_korea"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# index: country, Chinese name, family, date, exact pictured variant, selected images.
ROWS = {
    5: ("韩国", "韩国陆军创设40周年纪念章", "ROK-MED-ARMY-40", "约1988年", "纪念章", [2, 4]),
    6: ("韩国", "反游击战服役奖章", "ROK-MED-ANTI-GUERRILLA", "1954–1955年", "智异山作战服役章", [4, 3]),
    11: ("大韩帝国", "隆熙帝即位纪念章", "KOR-EMP-MED-ENTHRONEMENT", "1907年", "即位纪念章", [2, 1]),
    15: ("大韩帝国", "隆熙帝西南巡幸纪念章", "KOR-EMP-MED-IMPERIAL-TOUR", "1909年", "巡幸纪念章", [2, 6]),
    18: ("韩国", "韩国战争服役奖章", "ROK-MED-KOREAN-WAR-SERVICE", "1950–1953年", "服役奖章", [2, 1]),
    39: ("韩国", "越南战争服役奖章", "ROK-MED-VIETNAM-SERVICE", "1965–1970年", "服役奖章", [1, 2]),
    40: ("韩国", "负伤奖章", "ROK-MED-WOUND", "大韩民国时期", "一级", [1, 3]),
    41: ("韩国", "负伤奖章", "ROK-MED-WOUND", "大韩民国时期", "二级", [2, 1]),
    89: ("大韩帝国", "八卦章", "KOR-EMP-ORD-05", "1901年设立", "一等大绶章章饰；历史目录照片", [1]),
    90: ("大韩帝国", "八卦章", "KOR-EMP-ORD-05", "1901年设立", "二等章副章（星章）", [2, 1]),
    92: ("大韩帝国", "八卦章", "KOR-EMP-ORD-05", "1901年设立", "三等章（领绶）", [1, 5]),
    96: ("大韩帝国", "八卦章", "KOR-EMP-ORD-05", "1901年设立", "七等章；历史目录照片", [1]),
    98: ("大韩帝国", "金尺大勋章", "KOR-EMP-ORD-01", "1900年设立", "大绶章章饰", [3, 4]),
    99: ("大韩帝国", "金尺大勋章", "KOR-EMP-ORD-01", "1900年设立", "大绶章副章（星章）", [2, 7]),
    100: ("大韩帝国", "李花大勋章", "KOR-EMP-ORD-03", "1900年设立", "大绶章章饰", [5]),
    101: ("大韩帝国", "李花大勋章", "KOR-EMP-ORD-03", "1900年设立", "大绶章副章（星章）", [3, 2]),
    113: ("大韩帝国", "太极章", "KOR-EMP-ORD-04", "1900年设立", "一等大绶章章饰", [1]),
    114: ("大韩帝国", "太极章", "KOR-EMP-ORD-04", "1900年设立", "二等章副章（星章）", [4, 6]),
    116: ("大韩帝国", "太极章", "KOR-EMP-ORD-04", "1900年设立", "三等章（领绶）", [1]),
}

records_by_country = {"韩国": [], "大韩帝国": []}
images_by_country = {"韩国": [], "大韩帝国": []}
used_hashes: set[str] = set()
for idx, (country, name, family, date, variant, picks) in ROWS.items():
    raw = RAW[idx]
    prefix = "ROK" if country == "韩国" else "KOR-EMP"
    rid = f"{prefix}-MB-{idx:03d}-V01"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_south_korea/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"{prefix}-MB-{idx:03d}-VIEW{n}"
        views.append({"key": view_key, "label": "完整正面" if n == 1 else "完整背面"})
        images_by_country[country].append({
            "key": f"{prefix.lower()}-mb-{idx:03d}-{image_index:02d}", "record_id": rid, "view_key": view_key,
            "local_path": local_rel, "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "MedalBook catalogue object image", "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"],
            "decoded": True, "visually_checked": True,
        })
    records_by_country[country].append({
        "id": rid, "family": family, "country_zh": country, "name": name, "original": raw["original_name"],
        "date": date, "variant": variant, "views": views, "source_ids": [raw["source_id"]],
        "image_kind": "historical_catalogue" if "历史目录" in variant else "object_photo", "html_eligible": True,
    })

empire_indices = {3, 4, 8, 11, 14, 15, *range(78, 122)}
pending_by_country = {"韩国": [], "大韩帝国": []}
excluded = []
for idx, raw in enumerate(RAW):
    if idx in ROWS:
        continue
    if idx == 17:
        excluded.append({"source_id": raw["source_id"], "name": raw["page_title"], "reason": "association award; retained outside the state-award main catalogue"})
        continue
    country = "大韩帝国" if idx in empire_indices else "韩国"
    status = "有记载未配图"
    if idx == 25:
        status = "原站唯一图片返回HTTP 404"
    elif idx == 94:
        status = "仅有人物佩章照片，章体不完整"
    pending_by_country[country].append({"source_id": raw["source_id"], "name": raw["page_title"], "date": "待考", "page_url": raw["page_url"], "status": status})

outputs = [
    ("韩国", "south_korea_medalbook_differential.json", "south_korea_medalbook_differential_manifest.json", "韩国 · MedalBook 差集"),
    ("大韩帝国", "korean_empire_medalbook_variants.json", "korean_empire_medalbook_variants_manifest.json", "大韩帝国 · MedalBook"),
]
for country, volume_name, manifest_name, label in outputs:
    (ROOT / "data/volumes" / volume_name).write_text(
        json.dumps({"as_of": "2026-09-28", "volume": label, "records": records_by_country[country]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes" / manifest_name).write_text(
        json.dumps({"as_of": "2026-09-28", "images": images_by_country[country], "unpictured_candidates": pending_by_country[country], "excluded_candidates": excluded if country == "韩国" else []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "south_korea": {"rows": len(records_by_country['韩国']), "families": len({r['family'] for r in records_by_country['韩国']}), "views": len(images_by_country['韩国']), "pending": len(pending_by_country['韩国'])},
    "korean_empire": {"rows": len(records_by_country['大韩帝国']), "families": len({r['family'] for r in records_by_country['大韩帝国']}), "views": len(images_by_country['大韩帝国']), "pending": len(pending_by_country['大韩帝国'])},
    "excluded": len(excluded),
}, ensure_ascii=False))
