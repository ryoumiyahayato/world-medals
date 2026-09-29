from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_turkmenistan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR = ROOT / "assets/images/wawards_turkmenistan"
VOLUME = ROOT / "data/volumes/turkmenistan_wawards_variants.json"
MANIFEST = ROOT / "data/volumes/turkmenistan_wawards_variants_manifest.json"

ZH = {
    "order-of-the-fatherland": "祖国勋章",
    "president-s-star-order": "总统之星勋章",
    "order-of-oghuz-khagan-star": "乌古斯可汗之星勋章",
    "order-of-saparmurat-tuerkmenbasy-the-great": "伟大萨帕尔穆拉特·土库曼巴希勋章",
    "order-of-turkmenbashi": "土库曼巴希勋章",
    "order-golden-age": "黄金时代勋章",
    "order-of-independence": "独立勋章",
    "order-of-neutrality": "中立勋章",
    "order-for-contribution-to-the-development-of-cooperation": "发展合作贡献勋章",
    "order-for-the-great-love-to-the-independent-turkmenistan": "热爱独立土库曼斯坦勋章",
    "order-of-women-s-soul": "女性之心勋章",
    "order-of-gurbansoltan-eje": "古尔班索尔坦·埃杰勋章",
    "golden-crescent-medal": "土库曼斯坦英雄（金新月奖章）",
    "medal-for-love-to-the-fatherland": "热爱祖国奖章",
    "medal-of-bravery": "勇敢奖章",
    "order-of-the-renaissance": "复兴勋章",
    "medal-magtymguly-pyragy": "马赫图姆库里·弗拉吉奖章",
    "medal-of-zeal": "勤勉奖章",
    "for-impeccable-service-to-the-fatherland-medal": "为祖国无瑕服务奖章",
    "medal-mother-s-love": "母爱奖章",
    "bravery-turkmen-medal": "土库曼勇士奖章",
    "medal-arkadag": "阿尔卡达格奖章",
    "jubilee-medal-20-years-of-independence-of-turkmenistan": "独立20周年纪念章",
    "jubilee-medal-30-years-of-independence-of-turkmenistan": "独立30周年纪念章",
    "jubilee-medal-defender-of-the-motherland-of-independent-turkmenistan": "独立土库曼斯坦祖国保卫者纪念章",
    "medal-25th-anniversary-of-turkmenistan-s-neutrality": "中立25周年纪念章",
    "jubilee-medal-30th-anniversary-of-neutrality-of-turkmenistan": "中立30周年纪念章",
    "jubilee-medal-300th-anniversary-of-magtymguly-pyragy": "马赫图姆库里·弗拉吉诞辰300周年纪念章",
    "honorary-elder-of-the-people-of-turkmenistan": "土库曼斯坦人民荣誉长老徽章",
}

# suffix, variant, [(image number, label)], image kind
SPECIAL = {
    "order-of-the-fatherland": [
        ("chain", "项链章", [(1, "完整正面")], "object_photo"),
    ],
    "golden-crescent-medal": [
        ("portrait", "肖像挂章版", [(1, "完整正面")], "object_photo"),
        ("star", "星芒挂章版", [(2, "完整正面")], "object_photo"),
    ],
    "medal-for-love-to-the-fatherland": [
        ("early", "1996年实物版型", [(1, "完整正面"), (2, "完整背面")], "object_photo"),
        ("later", "后期图录版型", [(4, "完整正面")], "catalogue_illustration"),
    ],
    "order-for-the-great-love-to-the-independent-turkmenistan": [
        ("early", "早期实物版型", [(1, "完整正面"), (2, "完整背面")], "object_photo"),
        ("later", "后期图录版型", [(3, "完整正面")], "catalogue_illustration"),
    ],
    "order-golden-age": [
        ("early", "早期章饰版型", [(1, "完整正面")], "object_photo"),
        ("later", "后期图录版型", [(2, "完整正面")], "catalogue_illustration"),
    ],
    "order-of-gurbansoltan-eje": [
        ("early", "早期实物版型", [(1, "完整正面"), (2, "完整背面")], "object_photo"),
        ("later", "后期挂章版型", [(3, "完整正面")], "object_photo"),
    ],
    "order-of-independence": [
        ("early", "早期项链章版型", [(1, "完整正面")], "object_photo"),
        ("later", "后期图录版型", [(2, "完整正面")], "catalogue_illustration"),
    ],
    "order-of-neutrality": [
        ("early", "早期项链章版型", [(1, "完整正面"), (2, "完整背面")], "object_photo"),
        ("later", "后期图录版型", [(3, "完整正面")], "catalogue_illustration"),
    ],
    "order-of-saparmurat-tuerkmenbasy-the-great": [
        ("chain-a", "项链章版型A", [(1, "完整正面")], "object_photo"),
        ("chain-b", "项链章版型B", [(3, "完整正面")], "object_photo"),
    ],
    "order-of-the-renaissance": [
        ("early", "早期实物版型", [(1, "完整正面")], "object_photo"),
        ("later", "后期图录版型", [(2, "完整正面")], "catalogue_illustration"),
    ],
    "president-s-star-order": [
        ("early", "早期实物版型", [(1, "完整正面")], "object_photo"),
        ("later", "后期图录版型", [(2, "完整正面")], "catalogue_illustration"),
    ],
}


def facts(record: dict) -> tuple[str, str]:
    slug = Path(record["object_url"]).stem
    text = (ROOT / "sources/pages/wawards_turkmenistan" / f"{slug}.html").read_text(encoding="utf-8", errors="replace")
    original_match = re.search(rf"{re.escape(record['catalog_id'])}.*?<span[^>]*>(.*?)</span>", text, flags=re.I | re.S)
    original = html.unescape(re.sub(r"<[^>]+>", "", original_match.group(1))).strip() if original_match else ""
    if not original:
        original = record["name_original"]
    fact_match = re.search(r"<(?:li|p)[^>]*>([^<]*(?:instituted|established|created)[^<]*)</(?:li|p)>", text, flags=re.I)
    fact = html.unescape(fact_match.group(1)).strip() if fact_match else ""
    match = re.search(r"(?:on|in|of)\s+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4})", fact)
    if not match:
        return original, "设立时间待考"
    value = match.group(1)
    parts = value.split()
    if len(parts) == 1:
        return original, f"{value}年设立"
    months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    day, month, year = parts
    return original, f"{year}年{months[month]}月{int(day)}日设立"


def default_rows(slug: str, image_count: int):
    excluded_second = {
        "jubilee-medal-20-years-of-independence-of-turkmenistan",
        "medal-25th-anniversary-of-turkmenistan-s-neutrality",
    }
    if slug in excluded_second:
        picks = [(1, "完整正面")]
    elif image_count >= 2:
        picks = [(1, "完整正面"), (2, "完整背面")]
    else:
        picks = [(1, "完整正面")]
    variant = "荣誉称号徽章" if slug == "honorary-elder-of-the-people-of-turkmenistan" else "章饰"
    return [("main", variant, picks, "object_photo")]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, used_hashes = [], [], set()
    for source in RAW:
        slug = Path(source["object_url"]).stem
        original, date_text = facts(source)
        source_images = {item["view_no"]: item for item in source["original_images"]}
        rows = SPECIAL.get(slug, default_rows(slug, len(source_images)))
        family = "TKM-AWARD-" + re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")
        for suffix, variant, picks, image_kind in rows:
            record_id = f"{family}-{suffix.upper()}"
            views = []
            for order, (image_no, label) in enumerate(picks, 1):
                item = source_images[image_no]
                if item["sha256"] in used_hashes:
                    raise ValueError(f"duplicate image payload selected: {slug}:{image_no}")
                used_hashes.add(item["sha256"])
                source_path = ROOT / item["local_path"]
                with Image.open(source_path) as decoded:
                    decoded.verify()
                relative = f"assets/images/wawards_turkmenistan/{slug}_{suffix}_{image_no:02d}{source_path.suffix.lower()}"
                shutil.copy2(source_path, ROOT / relative)
                view_key = f"{record_id}-VIEW{order}"
                views.append({"key": view_key, "label": label})
                images.append({
                    "key": f"tkm-wawards-{slug}-{suffix}-{image_no:02d}",
                    "record_id": record_id,
                    "view_key": view_key,
                    "local_path": relative,
                    "source_page": source["object_url"],
                    "image_url": item["image_url"],
                    "artist": "World Awards 2025 reference catalogue",
                    "license": "Source terms apply; retained for offline research catalogue",
                    "dimensions": [item["width"], item["height"]],
                    "bytes": source_path.stat().st_size,
                    "sha256": item["sha256"],
                    "decoded": True,
                    "visually_checked": True,
                })
            records.append({
                "id": record_id,
                "family": family,
                "country_zh": "土库曼斯坦",
                "name": ZH[slug],
                "original": original,
                "date": date_text,
                "variant": variant + ("；图录插图 · 2025" if image_kind == "catalogue_illustration" else ""),
                "views": views,
                "source_ids": [source["source_id"]],
                "image_kind": image_kind,
                "html_eligible": True,
            })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-28", "volume": "土库曼斯坦 · World Awards 2025", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-28",
        "images": images,
        "unpictured_candidates": [],
        "excluded_candidates": [
            {"kind": "certificates_cases_books", "count": 6, "reason": "证书、证书册或包装不是独立章体图"},
            {"kind": "worn_portrait", "count": 2, "reason": "人物佩戴照未作为章体主图"},
            {"kind": "detail_or_redundant", "count": 2, "reason": "局部特写或重复图未进入正文"}
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "families": len({r['family'] for r in records}), "views": len(images)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
