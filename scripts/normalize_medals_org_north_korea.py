"""Normalize the completed ODM North Korea directory against existing MedalBook rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medals_org_north_korea.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medals_org_north_korea_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x.get("status") == "downloaded"}
OUT_DIR = ROOT / "assets/images/medals_org_north_korea"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# index, Chinese name, family, date, variant, selected images, optional superseded record.
ROWS = [
    (0, "朝鲜民主主义人民共和国英雄金星奖章", "PRK-HERO-OF-DPRK", "1950年设立", "金星奖章；低清参考", [2], "PRK-MB-062-V01"),
    (1, "朝鲜民主主义人民共和国劳动英雄金星奖章", "PRK-HERO-LABOUR", "1951年设立", "金星奖章；低清参考", [2, 3], None),
    (6, "李舜臣将军勋章", "PRK-ORDER-ADMIRAL-YI-SUN-SIN", "1950年设立", "二级；低清参考", [3, 4], None),
    (7, "劳动勋章", "PRK-ORD-12", "1951年设立", "第二型；低清参考", [1, 2], "PRK-MB-042-V01"),
    (8, "三大革命红旗勋章", "PRK-ORDER-THREE-REVOLUTIONS", "1986年设立", "勋章；低清参考", [2, 3], "PRK-MB-060-V01"),
    (9, "祖国解放战争胜利40周年纪念勋章", "PRK-ORDER-WAR-VICTORY-40", "1993年", "纪念勋章；低清参考", [2, 3], "PRK-MB-022-V01"),
    (10, "矿业服务荣誉勋章", "PRK-ORDER-MINING-HONOUR", "1973年设立", "一级；低清参考", [1, 2], None),
    (10, "矿业服务荣誉勋章", "PRK-ORDER-MINING-HONOUR", "1973年设立", "二级；低清参考", [3, 4], None),
    (10, "矿业服务荣誉勋章", "PRK-ORDER-MINING-HONOUR", "1973年设立", "三级；低清参考", [5, 6], None),
    (11, "军事工程服役荣誉勋章", "PRK-ORDER-MILITARY-ENGINEERING-SERVICE", "朝鲜民主主义人民共和国时期", "三级·服役10年章；低清参考", [1, 2], None),
    (12, "朝鲜民主主义人民共和国成立20周年纪念勋章", "PRK-ORDER-DPRK-20", "1968年", "纪念勋章；低清参考", [1, 2], None),
    (13, "人民军建军60周年纪念勋章", "PRK-ORDER-PEOPLES-ARMY-60", "1992年", "纪念勋章；低清参考", [1, 2], "PRK-MB-025-V01"),
    (14, "军事服役荣誉勋章", "PRK-ORDER-MILITARY-SERVICE-HONOUR", "1973年设立", "三级；低清参考", [1, 2], "PRK-MB-049-V01"),
    (16, "朝鲜民主主义人民共和国友谊勋章", "PRK-ORDER-FRIENDSHIP", "1985年设立", "一级章饰；低清参考", [1], None),
    (16, "朝鲜民主主义人民共和国友谊勋章", "PRK-ORDER-FRIENDSHIP", "1985年设立", "一级副章（星章）；低清参考", [2], None),
]

records = []
manifest = []
used_hashes: set[str] = set()
per_index_sequence: dict[int, int] = {}
for idx, name, family, date, variant, picks, supersedes in ROWS:
    raw = RAW[idx]
    per_index_sequence[idx] = per_index_sequence.get(idx, 0) + 1
    seq = per_index_sequence[idx]
    rid = f"PRK-ODM-{idx:03d}-V{seq:02d}"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medals_org_north_korea/{idx:03d}_{seq:02d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"PRK-ODM-{idx:03d}-{seq:02d}-VIEW{n}"
        views.append({"key": view_key, "label": "完整正面" if n == 1 else "完整背面"})
        manifest.append({
            "key": f"prk-odm-{idx:03d}-{seq:02d}-{image_index:02d}", "record_id": rid, "view_key": view_key,
            "local_path": local_rel, "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "ODM / medals.org.uk object image", "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"], "sha256": item["sha256"],
            "decoded": True, "visually_checked": True,
        })
    record = {
        "id": rid, "family": family, "country_zh": "朝鲜", "name": name, "original": raw["original_name"],
        "date": date, "variant": variant, "views": views, "source_ids": [raw["source_id"]], "image_kind": "object_photo", "html_eligible": True,
    }
    if supersedes:
        record["supersedes_id"] = supersedes
    records.append(record)

unpictured = [
    {"source_id": RAW[idx]["source_id"], "name": RAW[idx]["page_title"], "date": RAW[idx]["instituted_text"], "page_url": RAW[idx]["page_url"], "status": "来源仅提供绶带图，未以绶带代替章体"}
    for idx in (2, 4)
]

(ROOT / "data/volumes/north_korea_medals_org_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "朝鲜 · ODM", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/north_korea_medals_org_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"rows": len(records), "families": len({r['family'] for r in records}), "views": len(manifest), "upgrades": sum('supersedes_id' in r for r in records), "unpictured": len(unpictured)}, ensure_ascii=False))
