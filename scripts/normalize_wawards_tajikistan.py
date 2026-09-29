from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_tajikistan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
MEDALBOOK = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_tajikistan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR = ROOT / "assets/images/wawards_tajikistan"
VOLUME = ROOT / "data/volumes/tajikistan_wawards_variants.json"
MANIFEST = ROOT / "data/volumes/tajikistan_wawards_variants_manifest.json"

ZH = {
    "TJK001": "塔吉克斯坦英雄",
    "TJK002": "塔吉克斯坦总统之星勋章",
    "TJK003": "金冠勋章",
    "TJK004": "伊斯莫伊利·索莫尼勋章",
    "TJK005": "友谊勋章",
    "TJK006": "斯皮塔门勋章",
    "TJK007": "荣耀勋章",
    "TJK008": "勇敢奖章",
    "TJK009": "功绩服务奖章",
    "TJK010": "仁慈奖章",
    "TJK011": "塔吉克斯坦英勇边防卫士奖章",
    "TJK012": "武装力量优秀服务奖章",
    "TJK013": "武装力量成立5周年奖章",
    "TJK014": "武装力量成立10周年奖章",
    "TJK015": "武装力量成立15周年奖章",
    "TJK016": "武装力量成立20周年奖章",
    "TJK017": "武装力量成立25周年奖章",
    "TJK018": "警察成立75周年奖章",
    "TJK019": "警察成立80周年奖章",
    "TJK020": "内卫部队成立20周年奖章",
    "TJK021": "侦查机关成立50周年奖章",
    "TJK022": "禁毒署成立10周年奖章",
    "TJK023": "总统卫队成立5周年奖章",
    "TJK024": "紧急情况委员会成立20周年奖章",
    "TJK025": "检察机关成立85周年奖章",
    "TJK026": "内务部合作奖章",
    "TJK027": "塔吉克斯坦司法机关成立90周年奖章",
    "TJK028": "打击非法毒品贩运局成立15周年奖章",
    "TJK029": "国民卫队成立10周年奖章",
    "TJK030": "警察成立85周年奖章",
    "TJK031": "武装力量成立30周年奖章",
    "TJK032": "边防部队成立20周年纪念章",
    "TJK033": "边防部队成立25周年纪念章",
    "TJK034": "边防部队成立30周年纪念章",
    "TJK035": "内务部学院周年纪念章",
}

# Each tuple is (row suffix, variant label, [(image number, view label)]).
ROWS = {
    "TJK001": [("gold-star", "“金星”特别标志", [(1, "完整正面")])],
    "TJK002": [("star", "星章版（具体等级待考）", [(1, "完整正面")])],
    "TJK003": [("badge", "挂章（具体等级待考）", [(1, "完整正面")])],
    "TJK004": [
        ("pendant", "佩章版（具体等级待考）", [(2, "完整正面")]),
        ("breast-star", "星章版（具体等级待考）", [(3, "完整正面")]),
    ],
    "TJK005": [("badge", "章饰", [(1, "完整正面"), (2, "完整背面")])],
    "TJK006": [("badge", "星形章饰", [(2, "完整正面")])],
    "TJK007": [
        ("breast-star", "星章版", [(1, "完整正面"), (2, "完整背面")]),
        ("pendant", "挂章版", [(3, "完整正面"), (4, "完整背面")]),
        ("white-pendant", "白色星章挂章版（具体等级待考）", [(5, "盒装完整正面")]),
    ],
    "TJK008": [("medal", "奖章", [(2, "完整正面"), (3, "完整背面")])],
    "TJK009": [
        ("straight-ribbon", "直式绶带版", [(1, "完整正面"), (2, "完整背面")]),
        ("pentagonal-ribbon", "五角形绶带版", [(3, "完整正面"), (4, "完整背面")]),
    ],
    "TJK010": [("medal", "奖章", [(1, "完整正面"), (2, "完整背面")])],
    "TJK011": [("medal", "奖章", [(1, "完整正面"), (2, "完整背面")])],
    "TJK012": [
        ("type-a", "版型A（具体年资待考）", [(1, "完整正面"), (2, "完整背面")]),
        ("type-b", "版型B（具体年资待考）", [(3, "完整正面"), (4, "完整背面")]),
        ("type-c", "版型C（具体年资待考）", [(5, "完整正面"), (6, "完整背面")]),
    ],
}

for number in range(13, 36):
    catalog_id = f"TJK{number:03d}"
    if catalog_id in ROWS:
        continue
    if catalog_id in {"TJK014", "TJK017", "TJK031", "TJK032", "TJK033", "TJK034", "TJK035"}:
        picks = [(1, "完整正面")]
    elif catalog_id in {"TJK027", "TJK030"}:
        picks = [(1, "完整正面")]
    else:
        picks = [(1, "完整正面"), (2, "完整背面")]
    ROWS[catalog_id] = [("medal", "纪念章" if catalog_id not in {"TJK026"} else "合作奖章", picks)]


def page_facts(record: dict) -> tuple[str, str]:
    page_path = ROOT / "sources/pages/wawards_tajikistan" / f"{Path(record['object_url']).stem}.html"
    text = page_path.read_text(encoding="utf-8", errors="replace")
    original_match = re.search(rf"{record['catalog_id']}.*?<span[^>]*>(.*?)</span>", text, flags=re.I | re.S)
    original = html.unescape(re.sub(r"<[^>]+>", "", original_match.group(1))).strip() if original_match else record["name_original"]
    fact_match = re.search(r"<(?:li|p)[^>]*>([^<]*(?:instituted|established|created)[^<]*)</(?:li|p)>", text, flags=re.I)
    fact = html.unescape(fact_match.group(1)).strip() if fact_match else ""
    date_match = re.search(r"(?:on|in|of)\s+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4})", fact)
    if not date_match:
        return original, "设立时间待考"
    raw_date = date_match.group(1)
    parts = raw_date.split()
    if len(parts) == 1:
        return original, f"{raw_date}年设立"
    months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    day, month, year = parts
    return original, f"{year}年{months[month]}月{int(day)}日设立"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_id = {record["catalog_id"]: record for record in RAW}
    records, images, used_hashes = [], [], set()
    for catalog_id in sorted(ROWS):
        source = by_id[catalog_id]
        original, date_text = page_facts(source)
        source_images = {item["view_no"]: item for item in source["original_images"]}
        for suffix, variant, picks in ROWS[catalog_id]:
            record_id = f"TJK-WAWARDS-{catalog_id[3:]}-{suffix.upper()}"
            views = []
            for view_order, (image_no, label) in enumerate(picks, 1):
                item = source_images[image_no]
                if item["sha256"] in used_hashes:
                    raise ValueError(f"duplicate image payload selected: {catalog_id}:{image_no}")
                used_hashes.add(item["sha256"])
                source_path = ROOT / item["local_path"]
                with Image.open(source_path) as decoded:
                    decoded.verify()
                extension = source_path.suffix.lower() or ".jpg"
                relative = f"assets/images/wawards_tajikistan/{catalog_id.lower()}_{suffix}_{image_no:02d}{extension}"
                destination = ROOT / relative
                shutil.copy2(source_path, destination)
                view_key = f"{record_id}-VIEW{view_order}"
                views.append({"key": view_key, "label": label})
                images.append({
                    "key": f"tjk-wawards-{catalog_id.lower()}-{suffix}-{image_no:02d}",
                    "record_id": record_id,
                    "view_key": view_key,
                    "local_path": relative,
                    "source_page": source["object_url"],
                    "image_url": item["image_url"],
                    "artist": "World Awards reference catalogue object photograph",
                    "license": "Source terms apply; retained for offline research catalogue",
                    "dimensions": [item["width"], item["height"]],
                    "bytes": source_path.stat().st_size,
                    "sha256": item["sha256"],
                    "decoded": True,
                    "visually_checked": True,
                })
            records.append({
                "id": record_id,
                "family": f"TJK-AWARD-{catalog_id[3:]}",
                "country_zh": "塔吉克斯坦共和国",
                "name": ZH[catalog_id],
                "original": original,
                "date": date_text,
                "variant": variant,
                "views": views,
                "source_ids": [source["source_id"]],
                "image_kind": "object_photo",
                "html_eligible": True,
            })

    pictured_terms = {
        "chasorat", "meritorious worker", "valiant border", "75 years", "80 years", "10th anniversary of the armed",
        "15th anniversary of the armed", "5th anniversary of the armed", "shafkat", "hero of tajik", "friendship",
    }
    unpictured = []
    for item in MEDALBOOK:
        title = item["page_title"]
        low = title.lower()
        if any(term in low for term in pictured_terms):
            continue
        # Generic World Awards photographs cannot safely be assigned to MedalBook's named classes.
        unpictured.append({
            "source_id": item["source_id"],
            "name": title,
            "date": "待考",
            "source_page": item["page_url"],
            "reason": "目录已核对；现有图未能可靠对应到该具体等级，保留为有记载未配图候选",
        })

    VOLUME.write_text(json.dumps({"as_of": "2026-09-28", "volume": "塔吉克斯坦共和国 · World Awards 2025", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-28",
        "images": images,
        "unpictured_candidates": unpictured,
        "excluded_candidates": [
            {"kind": "certificates_cases_books", "count": 13, "reason": "证书、证章盒、证书册不是独立章体图，未进入正文"},
            {"kind": "cropped_closeups", "count": 3, "reason": "局部近照裁掉绶带或悬挂结构，未进入正文"},
            {"kind": "comparison_image", "count": 1, "reason": "同图含两个未单独标级的散章，仅留作内部参考"},
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "families": len({r['family'] for r in records}), "views": len(images), "unpictured": len(unpictured)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
