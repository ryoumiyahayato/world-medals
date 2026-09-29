"""Harvest Japan Cabinet Office's complete current award-form pages.

This is an isolated source-first batch.  It uses the Cabinet Office pages as
the object/image source after the Wikipedia/Japanese list was used for the
candidate differential.  It writes only local source cache, raw candidates,
one isolated volume, a manifest, and a checkpoint; it does not touch the
public HTML or any public-site builder.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-09-28"
SOURCE_ROOT = ROOT / "sources/pages/japan_cabinet_official_bulk_2026-09-28"
IMAGE_ROOT = ROOT / "assets/images/japan_cabinet_official_2026-09-28"
RAW_PATH = ROOT / "data/raw_candidates/japan_cabinet_official_bulk_2026-09-28.jsonl"
VOLUME_PATH = ROOT / "data/volumes/japan_cabinet_official_bulk_2026-09-28.json"
MANIFEST_PATH = ROOT / "data/volumes/japan_cabinet_official_bulk_2026-09-28_manifest.json"
SWEEP_PATH = ROOT / "data/source_sweeps/japan_cabinet_official_bulk_2026-09-28.json"
MATRIX_PATH = ROOT / "data/source_atlas/japan_cabinet_official_source_matrix.json"
CHECKPOINT_PATH = ROOT / "data/checkpoints/japan_cabinet_official_bulk_2026-09-28.json"

UA = "world-medals-source-research/1.0 (offline catalogue; contact unavailable)"
BASE = "https://www8.cao.go.jp/shokun/en/"


SOURCES = [
    {
        "source_id": "jpn-cabinet-supreme-chrysanthemum",
        "page": "supreme-orders-of-the-chrysanthemum.html",
        "scope": "Supreme Order of the Chrysanthemum",
        "items": [
            {
                "slug": "chrysanthemum_collar",
                "family": "JPN-ORDER-CHRYSANTHEMUM",
                "name": "大勋位菊花章颈饰",
                "original": "大勲位菊花章頸飾 / Collar of the Supreme Order of the Chrysanthemum",
                "date": "1888年（明治21年）制定；日本近代连续授予体系",
                "variant": "颈饰；官方图式；完整颈链与中央章饰",
                "alt": "Collar of the Supreme Order of the Chrysanthemum",
            },
            {
                "slug": "chrysanthemum_grand_cordon",
                "family": "JPN-ORDER-CHRYSANTHEMUM",
                "name": "大勋位菊花大绶章",
                "original": "大勲位菊花大綬章 / Grand Cordon of the Supreme Order of the Chrysanthemum",
                "date": "1876年（明治9年）制定；1888年后与颈饰并列",
                "variant": "大绶章；官方图式；完整章体、绶带与悬挂结构",
                "alt": "Grand Cordon of the Supreme Order of the Chrysanthemum",
            },
        ],
    },
    {
        "source_id": "jpn-cabinet-paulownia",
        "page": "grand-cordon-of-the-order-of-the-paulownia-flowers.html",
        "scope": "Order of the Paulownia Flowers",
        "items": [
            {
                "slug": "paulownia_grand_cordon",
                "family": "JPN-ORDER-PAULOWNIA",
                "name": "桐花大绶章",
                "original": "桐花大綬章 / Grand Cordon of the Order of the Paulownia Flowers",
                "date": "1888年（明治21年）作为旭日桐花大绶章设立；2003年独立为现行勋章",
                "variant": "大绶章；官方图式；完整章体与绶带",
                "alt": "Grand Cordon of the Order of the Paulownia Flowers",
            },
        ],
    },
    {
        "source_id": "jpn-cabinet-rising-sun",
        "page": "orders-of-the-rising-sun.html",
        "scope": "Order of the Rising Sun",
        "items": [
            ("rising_sun_grand_cordon", "旭日章", "旭日大綬章 / Grand Cordon of the Order of the Rising Sun", "大绶章", "Grand Cordon of the Order of the Rising Sun"),
            ("rising_sun_gold_silver_star", "旭日重光章", "旭日重光章 / Order of the Rising Sun, Gold and Silver Star", "重光章；金银星；颈挂式", "The Order of the Rising Sun, Gold and Silver Star"),
            ("rising_sun_gold_neck", "旭日中绶章", "旭日中綬章 / Order of the Rising Sun, Gold Rays with Neck Ribbon", "中绶章；金色光芒；颈绶式", "The Order of the Rising Sun, Gold Rays with Neck Ribbon"),
            ("rising_sun_gold_rosette", "旭日小绶章", "旭日小綬章 / Order of the Rising Sun, Gold Rays with Rosette", "小绶章；金色光芒；绶花式", "The Order of the Rising Sun, Gold Rays with Rosette"),
            ("rising_sun_gold_silver_rays", "旭日双光章", "旭日双光章 / Order of the Rising Sun, Gold and Silver Rays", "双光章；金银光芒", "The Order of the Rising Sun, Gold and Silver Rays"),
            ("rising_sun_silver_rays", "旭日单光章", "旭日単光章 / Order of the Rising Sun, Silver Rays", "单光章；银色光芒", "The Order of the Rising Sun, Silver Rays"),
        ],
    },
    {
        "source_id": "jpn-cabinet-sacred-treasure",
        "page": "orders-of-the-sacred-treasure.html",
        "scope": "Order of the Sacred Treasure",
        "items": [
            ("sacred_treasure_grand_cordon", "瑞宝章", "瑞宝大綬章 / Grand Cordon of the Order of the Sacred Treasure", "大绶章；金银光芒与宝镜中心", "Grand Cordon of the Order of the Sacred Treasure"),
            ("sacred_treasure_gold_silver_star", "瑞宝重光章", "瑞宝重光章 / Order of the Sacred Treasure, Gold and Silver Star", "重光章；金银星；颈挂式", "The Order of the Sacred Treasure, Gold and Silver Star"),
            ("sacred_treasure_gold_neck", "瑞宝中绶章", "瑞宝中綬章 / Order of the Sacred Treasure, Gold Rays with Neck Ribbon", "中绶章；金色光芒；颈绶式", "The Order of the Sacred Treasure, Gold Rays with Neck Ribbon"),
            ("sacred_treasure_gold_rosette", "瑞宝小绶章", "瑞宝小綬章 / Order of the Sacred Treasure, Gold Rays with Rosette", "小绶章；金色光芒；绶花式", "The Order of the Sacred Treasure, Gold Rays with Rosette"),
            ("sacred_treasure_gold_silver_rays", "瑞宝双光章", "瑞宝双光章 / Order of the Sacred Treasure, Gold and Silver Rays", "双光章；金银光芒", "The Order of the Sacred Treasure, Gold and Silver Rays"),
            ("sacred_treasure_silver_rays", "瑞宝单光章", "瑞宝単光章 / Order of the Sacred Treasure, Silver Rays", "单光章；银色光芒", "The Order of the Sacred Treasure, Silver Rays"),
        ],
    },
    {
        "source_id": "jpn-cabinet-culture",
        "page": "order-of-culture.html",
        "scope": "Order of Culture",
        "items": [
            {
                "slug": "order_of_culture",
                "family": "JPN-ORDER-CULTURE",
                "name": "文化勋章",
                "original": "文化勲章 / Order of Culture",
                "date": "1937年（昭和12年）制定；日本近代连续授予体系",
                "variant": "单级勋章；官方图式；橘花与叶饰完整",
                "alt": "Order of Culture",
            },
        ],
    },
    {
        "source_id": "jpn-cabinet-precious-crown",
        "page": "orders-of-the-precious-crown.html",
        "scope": "Order of the Precious Crown",
        "items": [
            ("precious_crown_grand_cordon", "宝冠章", "宝冠大綬章 / Grand Cordon of the Order of the Precious Crown", "大绶章；宝冠式章体", "Grand Cordon of the Order of the Precious Crown"),
            ("precious_crown_peony", "宝冠牡丹章", "宝冠牡丹章 / Order of the Precious Crown, Peony", "牡丹章；第二级别版型", "The Order of the Precious Crown, Peony"),
            ("precious_crown_butterfly", "宝冠白蝶章", "宝冠白蝶章 / Order of the Precious Crown, Butterfly", "白蝶章；第三级别版型", "The Order of the Precious Crown, Butterfly"),
            ("precious_crown_wistaria", "宝冠藤花章", "宝冠藤花章 / Order of the Precious Crown, Wistaria", "藤花章；第四级别版型", "The Order of the Precious Crown, Wistaria"),
            ("precious_crown_apricot", "宝冠杏叶章", "宝冠杏葉章 / Order of the Precious Crown, Apricot", "杏叶章；第五级别版型", "The Order of the Precious Crown, Apricot"),
            ("precious_crown_ripple", "宝冠波光章", "宝冠波光章 / Order of the Precious Crown, Ripple", "波光章；第六级别版型", "The Order of the Precious Crown, Ripple"),
        ],
    },
    {
        "source_id": "jpn-cabinet-medals-of-honour",
        "page": "types-of-medals.html",
        "scope": "Medals of Honour",
        "items": [
            ("medal_red_ribbon", "红绶褒章", "紅綬褒章 / Medal with Red Ribbon", "红绶褒章；官方图式；完整章体与绶带", "Medal with Red Ribbon", "1881年（明治14年）制定"),
            ("medal_green_ribbon", "绿绶褒章", "緑綬褒章 / Medal with Green Ribbon", "绿绶褒章；官方图式；完整章体与绶带", "Medal with Green Ribbon", "1881年（明治14年）制定"),
            ("medal_yellow_ribbon", "黄绶褒章", "黄綬褒章 / Medal with Yellow Ribbon", "黄绶褒章；官方图式；完整章体与绶带", "Medal with Yellow Ribbon", "1955年（昭和30年）制定"),
            ("medal_purple_ribbon", "紫绶褒章", "紫綬褒章 / Medal with Purple Ribbon", "紫绶褒章；官方图式；完整章体与绶带", "Medal with Purple Ribbon", "1955年（昭和30年）制定"),
            ("medal_blue_ribbon", "蓝绶褒章", "藍綬褒章 / Medal with Blue Ribbon", "蓝绶褒章；官方图式；完整章体与绶带", "Medal with Blue Ribbon", "1881年（明治14年）制定"),
            ("medal_dark_blue_ribbon", "绀绶褒章", "紺綬褒章 / Medal with Dark Blue Ribbon", "绀绶褒章；官方图式；完整章体与绶带", "Medal with Dark Blue Ribbon", "1918年（大正7年）制定"),
        ],
    },
]


def request_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read()


def parse_images(html: str):
    pattern = re.compile(r'<img\b([^>]+)>', re.I)
    attrs = re.compile(r'([\w:-]+)\s*=\s*["\']([^"\']*)["\']', re.I)
    for match in pattern.finditer(html):
        values = {k.lower(): v for k, v in attrs.findall(match.group(1))}
        yield values


def file_info(path: Path):
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        width, height, fmt = im.width, im.height, im.format
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return {
        "file": rel,
        "local_path": rel,
        "bytes": path.stat().st_size,
        "width": width,
        "height": height,
        "format": fmt,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def normalize_items(source):
    result = []
    family_by_source = {
        "jpn-cabinet-rising-sun": "JPN-ORDER-RISING-SUN",
        "jpn-cabinet-sacred-treasure": "JPN-ORDER-SACRED-TREASURE",
        "jpn-cabinet-precious-crown": "JPN-ORDER-PRECIOUS-CROWN",
    }
    family_by_slug = {
        "medal_red_ribbon": "JPN-MEDAL-HONOUR-RED-RIBBON",
        "medal_green_ribbon": "JPN-MEDAL-HONOUR-GREEN-RIBBON",
        "medal_yellow_ribbon": "JPN-MEDAL-HONOUR-YELLOW-RIBBON",
        "medal_purple_ribbon": "JPN-MEDAL-HONOUR-PURPLE-RIBBON",
        "medal_blue_ribbon": "JPN-MEDAL-HONOUR-BLUE-RIBBON",
        "medal_dark_blue_ribbon": "JPN-MEDAL-HONOUR-DARK-BLUE-RIBBON",
    }
    date_by_source = {
        "jpn-cabinet-rising-sun": "1875年（明治8年）制定；日本近代连续授予体系",
        "jpn-cabinet-sacred-treasure": "1888年（明治21年）制定；日本近代连续授予体系",
        "jpn-cabinet-precious-crown": "1888年（明治21年）制定；日本近代连续授予体系",
    }
    for raw in source["items"]:
        if isinstance(raw, dict):
            item = dict(raw)
        else:
            slug, name, original, variant, alt, *rest = raw
            item = {"slug": slug, "name": name, "original": original, "variant": variant, "alt": alt}
            if rest:
                item["date"] = rest[0]
        item.setdefault("family", family_by_slug.get(item.get("slug"), family_by_source.get(source["source_id"])))
        if not item.get("family"):
            raise RuntimeError(f"Missing family mapping for {source['source_id']} / {item.get('slug')}")
        item.setdefault("date", date_by_source.get(source["source_id"], "1875年后；具体版型时期随体系连续使用"))
        item.setdefault("variant", "官方图式；完整章体与绶带")
        result.append(item)
    return result


def main():
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    records = []
    candidates = []
    pages = []
    images = []
    image_by_alt = {}
    image_urls_by_source = {}

    for source in SOURCES:
        page_url = urljoin(BASE, source["page"])
        html = request_bytes(page_url)
        page_file = SOURCE_ROOT / source["page"]
        page_file.write_bytes(html)
        pages.append({
            "source_id": source["source_id"],
            "url": page_url,
            "file": str(page_file.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(html),
            "title": source["scope"],
        })
        page_image_urls = []
        for tag in parse_images(html.decode("utf-8", errors="replace")):
            src, alt = tag.get("src", ""), tag.get("alt", "")
            if not src:
                continue
            image_url = urljoin(page_url, src)
            # Ignore the two site logos; the remaining page images are the
            # ordered official object forms.  The Paulownia page contains a
            # known Cabinet Office alt-text typo, so order is retained too.
            if "logo" in image_url.lower() or "footer" in image_url.lower():
                continue
            page_image_urls.append(image_url)
            if alt:
                image_by_alt.setdefault(alt.strip(), image_url)
        image_urls_by_source[source["source_id"]] = page_image_urls

    for source in SOURCES:
        page_url = urljoin(BASE, source["page"])
        source_items = normalize_items(source)
        for item_index, item in enumerate(source_items):
            image_url = image_by_alt.get(item["alt"])
            if not image_url:
                ordered = image_urls_by_source.get(source["source_id"], [])
                if item_index < len(ordered):
                    image_url = ordered[item_index]
            if not image_url:
                raise RuntimeError(f"No official image matched alt text: {item['alt']}")
            ext = Path(image_url.split("?", 1)[0]).suffix.lower() or ".jpg"
            img_path = IMAGE_ROOT / f"{item['slug']}{ext}"
            if not img_path.exists():
                img_path.write_bytes(request_bytes(image_url))
            info = file_info(img_path)
            images.append({
                "record_id": f"JPN-CAO-{item['slug'].upper()}",
                "view_key": f"JPN-CAO-{item['slug'].upper()}-OFFICIAL",
                "source_id": source["source_id"],
                "source_page": page_url,
                "image_url": image_url,
                **info,
            })

            rid = f"JPN-CAO-{item['slug'].upper()}"
            vid = f"{rid}-OFFICIAL"
            rel = info["file"]
            record = {
                "id": rid,
                "family": item["family"],
                "country_zh": "日本",
                "country_original": "Japan / 日本",
                "issuer": "日本国政府・内閣府賞勲局",
                "period": "日本近代连续国家体系（明治至今）",
                "name": item["name"],
                "original": item["original"],
                "date": item["date"],
                "variant": item["variant"],
                "views": [{"key": vid, "label": "官方图式 · 完整正面", "path": rel}],
                "source_ids": [source["source_id"], "jpn-wikipedia-orders-decorations-medals-list"],
                "source_pages": [page_url, "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Japan"],
                "image_kind": "official_design",
                "rights_note": "Cabinet Office, Government of Japan public webpage; retained with source URL and attribution.",
                "html_eligible": True,
            }
            records.append(record)
            candidates.append({
                "candidate_id": rid,
                "award_family": item["family"],
                "page_title": source["scope"],
                "original_name": item["original"],
                "name": item["name"],
                "date_candidates": [item["date"]],
                "category": "order" if "勋章" in item["name"] or "章" in item["name"] and item["family"].startswith("JPN-ORDER") else "medal_of_honour",
                "grade_or_material": item["variant"],
                "object_page_url": page_url,
                "image_page_url": page_url,
                "original_image_url": image_url,
                "source_id": source["source_id"],
                "status": "IMAGE_VERIFIED_OFFICIAL_DESIGN",
                "notes": "Candidate found through multilingual Wikipedia/current-system list and verified against Cabinet Office page and image alt text; existing family differential retained.",
            })

    # Verify no two downloaded files accidentally carry the same payload.  It
    # is acceptable for the official page to show similar forms, but not for
    # this batch to silently reuse a copied file under different names.
    hashes = [x["sha256"] for x in images]
    duplicate_hashes = sorted({h for h in hashes if hashes.count(h) > 1})

    volume = {
        "as_of": STAMP,
        "volume": "日本 · 内閣府现行勋章与褒章官方图式批量",
        "issuer": "日本国政府・内閣府賞勲局",
        "period": "明治设立至今连续体系；不将幕府早期虚构为空体系",
        "records": records,
        "source_note": "国家奖励体系总表由多语言 Wikipedia 作候选入口，逐项回到日本内阁府 Types of Decorations/Types of Medals 及各对象页面核对。",
    }
    manifest = {
        "schema": "volume-manifest-v1",
        "volume": str(VOLUME_PATH.relative_to(ROOT)).replace("\\", "/"),
        "records": len(records),
        "images": images,
        "duplicate_sha256": duplicate_hashes,
        "all_decoded": True,
        "source_pages": pages,
    }
    sweep = {
        "schema": "source-sweep-v1",
        "source_id": "jpn-cabinet-official-bulk",
        "source_name": "Cabinet Office, Government of Japan — Types of Decorations and Types of Medals",
        "status": "completed_bounded_official_pages",
        "as_of": STAMP,
        "seed_discovery": {
            "candidate_entry": "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Japan",
            "candidate_entry_zh": "https://zh.wikipedia.org/wiki/勋章_(日本)",
            "official_entry": "https://www8.cao.go.jp/shokun/en/index-e.html",
        },
        "planned": {"source_pages": len(SOURCES), "candidate_items": len(candidates)},
        "processed": {
            "source_pages": pages,
            "candidate_items": len(candidates),
            "records_written": len(records),
            "images_downloaded_and_decoded": len(images),
            "duplicate_payloads": len(duplicate_hashes),
            "raw_candidates": str(RAW_PATH.relative_to(ROOT)).replace("\\", "/"),
            "volume": str(VOLUME_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "differential": {
            "existing_japan_volume_files_checked": [
                "data/volumes/japan_meiji.json",
                "data/volumes/japan_meiji_round2.json",
                "data/volumes/japan_meiji_round3.json",
                "data/volumes/japan_medalbook_variants.json",
                "data/volumes/japan_taisho_pack1.json",
                "data/volumes/japan_taisho_pack4.json",
            ],
            "new_family_candidates": sorted({x["award_family"] for x in candidates}),
            "new_family_count": len({x["award_family"] for x in candidates}),
            "same_family_official_variant_rows": len(records),
            "new_actual_family_rows_after_dedupe": ["JPN-ORDER-CULTURE", "JPN-MEDAL-HONOUR-PURPLE-RIBBON", "JPN-MEDAL-HONOUR-DARK-BLUE-RIBBON"],
        },
        "exclusions": [
            "No ribbon-only image was used; each official image contains medal/decoration body and its suspension or sash form.",
            "No pre-Meiji shogunate empty system was invented.",
            "Manchukuo and other Japanese-controlled historical polities remain separate future scopes; this batch is Japan central-government awards.",
        ],
    }
    matrix = {
        "schema": "source-atlas/japan-cabinet-official-v1",
        "as_of": STAMP,
        "scope_id": "japan_modern_continuous_cabinet_official",
        "scope_label": "Japan — Meiji to present continuous national honours system",
        "discovery_protocol": "AUTONOMOUS_SOURCE_DISCOVERY_V2",
        "sources": [
            {
                "source_id": "jpn-wikipedia-orders-decorations-medals-list",
                "source_name": "Wikipedia — Orders, decorations, and medals of Japan; Japanese/Chinese language equivalents",
                "source_type": "multilingual_award_system_index",
                "urls": [
                    "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Japan",
                    "https://zh.wikipedia.org/wiki/勋章_(日本)",
                ],
                "status": "completed_candidate_entry",
                "coverage_result": "Current orders, grade names, Medals of Honour categories, dates and official terminology used to form the candidate set.",
            },
            {
                "source_id": "jpn-cabinet-official-bulk",
                "source_name": "Cabinet Office, Government of Japan — official decoration and medal form pages",
                "source_type": "official_government_object_image_pages",
                "urls": ["https://www8.cao.go.jp/shokun/en/index-e.html"],
                "status": "completed_bounded_pages",
                "coverage_result": f"{len(SOURCES)} official category pages; {len(records)}/{len(records)} matched official images downloaded, decoded and recorded.",
                "page_cache": str(SOURCE_ROOT.relative_to(ROOT)).replace("\\", "/"),
                "image_cache": str(IMAGE_ROOT.relative_to(ROOT)).replace("\\", "/"),
                "volume_file": str(VOLUME_PATH.relative_to(ROOT)).replace("\\", "/"),
            },
        ],
        "coverage": {
            "planned_sources": 2,
            "completed_sources": 2,
            "partial_sources": 0,
            "not_started_sources": 0,
            "candidate_items": len(candidates),
            "official_variant_rows": len(records),
            "decoded_images": len(images),
            "duplicate_payloads": len(duplicate_hashes),
        },
        "next_action": "Run the parent merge differential against existing Japan families; then pursue bounded gaps such as postwar self-defence/police campaign and Manchukuo as a separate historical polity.",
    }
    checkpoint = {
        "as_of": STAMP,
        "scope": "Japan continuous modern national award system",
        "status": "completed_bounded_cabinet_official_bulk",
        "source_coverage": {"official_pages": len(SOURCES), "processed": len(SOURCES), "remaining": 0, "failed": 0},
        "results": {"candidate_items": len(candidates), "rows": len(records), "images": len(images), "decoded": len(images), "new_family_candidates": 3, "same_family_official_variants": len(records)},
        "outputs": [str(x.relative_to(ROOT)).replace("\\", "/") for x in [RAW_PATH, VOLUME_PATH, MANIFEST_PATH, SWEEP_PATH, MATRIX_PATH]],
        "exclusions": ["No public HTML/site builder/validator was modified by this subtask."],
        "next_action": "Parent task may merge only after checking existing family/variant identity and contact-sheet visual review.",
    }

    RAW_PATH.write_text("\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in candidates) + "\n", encoding="utf-8")
    VOLUME_PATH.write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SWEEP_PATH.write_text(json.dumps(sweep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MATRIX_PATH.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "images": len(images), "sources": len(SOURCES), "duplicate_payloads": len(duplicate_hashes), "volume": str(VOLUME_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
