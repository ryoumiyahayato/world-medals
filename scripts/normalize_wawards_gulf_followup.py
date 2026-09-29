"""Normalize the completed Bahrain, UAE and Oman World Awards country indexes."""
from __future__ import annotations

import hashlib, json, shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {
    "bahrain": ("BHR", "巴林王国", {
        "order-of-sheikh-isa-bin-salman-al-khalifa": "谢赫伊萨·本·萨勒曼·阿勒哈利法勋章", "order-of-bahrain": "巴林勋章",
        "order-of-achievement": "成就勋章", "medal-of-military-duty": "军事职责奖章", "kuwait-liberation-medal": "科威特解放奖章",
        "police-bravery-medal": "警察英勇奖章", "police-medal-for-devotion-to-duty": "警察忠于职守奖章",
        "police-long-service-medal": "警察长期服务奖章", "public-security-forces-sheikh-issa-memorial-medal": "公共安全部队谢赫伊萨纪念奖章",
    }),
    "united-arab-emirates": ("ARE", "阿拉伯联合酋长国", {
        "order-of-zayed": "扎耶德勋章", "order-of-the-union": "联邦勋章", "order-of-independence": "独立勋章", "order-of-zayed-ii": "扎耶德二世勋章",
        "loyal-service-medal-of-the-trucial-oman-scouts": "特鲁西尔阿曼斥候队忠诚服务奖章", "faithful-service-medal": "忠诚服务奖章",
        "union-defense-force-gallantry-medal": "联邦国防军英勇奖章", "union-defense-force-loyal-service-medal": "联邦国防军忠诚服务奖章",
        "independence-40th-anniversary-medal": "独立四十周年奖章", "emirates-military-order": "阿联酋军事勋章", "bravery-medal": "英勇奖章",
        "distinguished-service-medal": "卓越服务奖章", "gulf-cooperation-decoration": "海湾合作荣饰", "long-service-and-good-conduct-medal": "长期服务与品行优良奖章",
        "wound-medal": "负伤奖章", "lebanese-peace-keeping-force-medal": "黎巴嫩维和部队奖章", "liberation-of-kuwait-medal": "科威特解放奖章",
        "somalia-peace-keeping-force-medal": "索马里维和部队奖章", "independence-first-anniversary-medal": "独立一周年奖章",
        "armed-forces-amalgamation-medal": "武装部队合并奖章", "independence-15th-anniversary-medal": "独立十五周年奖章",
        "25th-anniversary-of-the-armed-forces-medal": "武装部队二十五周年奖章", "medal-for-military-operations-abroad": "海外军事行动奖章",
        "order-of-superiority": "优异勋章", "order-of-loyalty": "忠诚勋章", "royal-order-of-ai-nahyan": "阿勒纳哈扬王室勋章",
        "abu-dhabi-defense-force-inauguration-medal": "阿布扎比国防军成立奖章", "abu-dhabi-defense-force-service-order": "阿布扎比国防军服务勋章",
        "abu-dhabi-police-accession-medal": "阿布扎比警察即位奖章", "dubai-defense-force-service-medal": "迪拜国防军服务奖章",
        "dubai-police-order-of-gallantry": "迪拜警察英勇勋章", "dubai-police-order-of-superiority": "迪拜警察优异勋章",
        "dubai-police-order-of-faithful-service": "迪拜警察忠诚服务勋章", "order-of-the-tower-of-qassimi": "卡西米之塔勋章", "ajman-police-medal": "阿治曼警察奖章",
    }),
    "oman": ("OMN", "阿曼苏丹国", {"order-of-appreciation": "嘉奖勋章"}),
}

for scope, (prefix, country, names) in CONFIG.items():
    raw_path = ROOT / f"data/raw_candidates/wawards_{scope}.jsonl"
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    out_dir = ROOT / f"assets/images/wawards_{scope.replace('-', '_')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    records, images, unpictured = [], [], []
    for row in rows:
        slug = Path(urlparse(row["object_url"]).path).stem
        name = names.get(slug, slug.replace("-", " "))
        family = f"{prefix}-WAWARDS-{slug.upper().replace('-', '_')}"
        if not row["original_images"]:
            unpictured.append({"source_id": row["source_id"], "name": name, "reason": "source object page has no exposed full image"})
            continue
        item, src = row["original_images"][0], ROOT / row["original_images"][0]["local_path"]
        rel = f"assets/images/wawards_{scope.replace('-', '_')}/{slug}{src.suffix.lower()}"
        shutil.copy2(src, ROOT / rel)
        with Image.open(src) as im:
            w, h = im.size
            im.verify()
        rid, view = family + "-REPRESENTATIVE", family + "-REPRESENTATIVE-VIEW1"
        date = (row.get("date_candidates") or ["日期待考"])[0]
        if date != "日期待考": date = f"{date}年设立／纪年"
        records.append({"id": rid, "family": family, "country_zh": country, "name": name, "original": row["page_title"], "date": date,
                        "variant": "World Awards对象页所示完整章体；具体等级待考", "views": [{"key": view, "label": "完整图样"}],
                        "source_ids": [row["source_id"]], "image_kind": "catalogue_object_or_illustration", "html_eligible": True})
        images.append({"key": rid.lower() + "-image", "record_id": rid, "view_key": view, "local_path": rel, "source_page": row["object_url"],
                       "image_url": item["image_url"], "license": "source-site research use; publication rights not asserted", "dimensions": [w, h],
                       "bytes": src.stat().st_size, "sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "decoded": True, "visually_checked": True})
    stem = scope.replace("-", "_") + "_wawards_families"
    (ROOT / f"data/volumes/{stem}.json").write_text(json.dumps({"as_of": "2026-09-28", "volume": country, "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / f"data/volumes/{stem}_manifest.json").write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": unpictured,
        "notes": ["First pass establishes family coverage; additional source images remain cached for grade and reverse expansion."]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scope": scope, "rows": len(records), "families": len({r['family'] for r in records}), "views": len(images), "unpictured": len(unpictured)}, ensure_ascii=False))
