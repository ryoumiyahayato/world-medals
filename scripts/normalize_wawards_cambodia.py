from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_cambodia.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR = ROOT / "assets/images/wawards_cambodia"

ZH = {
    "royal-order-of-cambodia": "柬埔寨王家勋章",
    "royal-order-of-sahametrei": "萨哈梅特雷王家勋章",
    "national-order-of-independence": "国家独立勋章",
    "order-of-the-queen": "王后勋章",
    "royal-order-of-sowathara": "索瓦塔拉王家勋章",
    "royal-order-of-monisaraphon": "莫尼萨拉蓬王家勋章",
    "royal-order-of-industrial-merit": "工业功绩王家勋章",
    "roayl-order-of-labor-merit": "劳动功绩王家勋章",
    "faithful-service-order": "忠诚服务勋章",
    "order-of-loyalty": "忠诚勋章",
    "order-of-outstanding-service-to-the-state": "国家卓越服务勋章",
    "royal-grand-collar-of-the-reign-of-his-majesty-king-norodom-sihamoni": "诺罗敦·西哈莫尼国王御世王家大项链章",
    "medal-of-national-merit": "国家功绩奖章",
    "sena-jayaseddh-medal": "塞纳·贾亚塞德奖章",
    "medal-of-national-defence": "国防奖章",
    "prince-virasundra-medal": "毗湿多罗王子奖章",
    "medal-for-the-royal-crusade-for-independence": "王家独立十字军纪念章",
    "national-independence-medal": "国家独立奖章",
    "sangkum-medal": "桑库姆奖章",
    "medal-of-the-crown": "王冠奖章",
    "medal-of-the-reign-of-king-norodom-i": "诺罗敦一世御世纪念章",
    "medal-of-the-reign-of-king-sisowath-i": "西索瓦一世御世纪念章",
    "medal-of-royal-remembrance": "王家纪念奖章",
    "medal-of-the-reign-of-king-sisowath-monivong": "西索瓦·莫尼旺御世纪念章",
    "medal-of-the-reign-of-king-norodom-sihanouk": "诺罗敦·西哈努克御世纪念章",
    "medal-of-the-reign-of-king-norodom-suramarit": "诺罗敦·苏拉玛里特御世纪念章",
    "cambodian-recognition-medal": "柬埔寨表彰奖章",
    "medal-of-sports-merit": "体育功绩奖章",
    "medal-of-improvement": "公共改善奖章",
    "medal-of-feminine-merit": "妇女功绩奖章",
    "medal-of-labor": "劳动奖章",
    "medal-for-the-construction-of-the-natonal-olympic-stadium": "国家奥林匹克体育场建设奖章",
    "medal-for-the-construction-of-the-sihanoukville-port": "西哈努克港建设奖章",
    "medal-for-the-construction-of-the-sihanoukville-railway": "西哈努克港铁路建设奖章",
    "medal-for-the-construction-of-hydroelectric-dams": "水电站建设奖章",
    "medal-for-the-construction-of-the-monivong-bridge": "莫尼旺桥建设奖章",
    "medal-for-the-construction-of-palaces": "宫殿建设奖章",
    "national-construction-medal": "国家建设奖章",
    "angkor-decoration": "吴哥勋章",
    "national-defence-decoration": "国防勋章",
    "victory-decoration": "胜利勋章",
    "issarak-combatants-decoration": "伊萨拉战士勋章",
    "labour-decoration": "劳动勋章",
    "7th-january-decoration": "一月七日勋章",
    "friendship-decoration": "友谊勋章",
    "labour-medal": "劳动奖章",
    "friendship-medal": "友谊奖章",
    "medal-of-national-construction": "国家建设奖章",
}

# Each tuple is suffix, display variant, source image numbers.  Images paired in one
# tuple are matching front/reverse views; separate tuples are distinct visible forms.
SPECIAL = {
    "royal-order-of-cambodia": [("class1-star", "一级星章", [1]), ("class3", "三级章", [2]), ("class4-french-ribbon", "四级章；法国式绶带", [3])],
    "royal-order-of-sahametrei": [("form-a", "挂章版型A", [1]), ("form-b", "挂章版型B", [2]), ("star", "星章", [3])],
    "order-of-the-queen": [("early-a", "早期挂章版型A", [1]), ("early-b", "早期挂章版型B", [2, 3]), ("current-i", "现行I型星章", [4]), ("current-ii", "现行II型挂章", [5])],
    "royal-order-of-sowathara": [("badge", "挂章；正背", [1, 2]), ("star", "星章；正背", [3, 4])],
    "royal-order-of-monisaraphon": [("star", "星章；正背", [1, 2]), ("badge-a", "挂章版型A", [3]), ("badge-b", "挂章版型B", [4])],
    "medal-of-national-merit": [("badge", "章饰", [1]), ("collar-a", "项链章版型A", [2]), ("collar-b", "项链章版型B", [3])],
    "medal-of-the-crown": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B", [3])],
    "medal-of-the-reign-of-king-norodom-i": [("gold", "金色版；正背", [1, 2]), ("silver", "银色版；正背", [3, 4]), ("bronze", "铜色版；正背", [5, 6])],
    "medal-of-the-reign-of-king-sisowath-i": [("medal", "章饰；正背", [1, 2])],
    "medal-of-royal-remembrance": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B；正背", [3, 4])],
    "medal-of-the-reign-of-king-sisowath-monivong": [("medal", "章饰；正背", [1, 2])],
    "medal-of-the-reign-of-king-norodom-sihanouk": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B；正背", [3, 4])],
    "medal-of-the-reign-of-king-norodom-suramarit": [("type-a", "版型A", [1]), ("type-b", "版型B；正背", [2, 3])],
    "medal-of-sports-merit": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B", [3]), ("type-c", "版型C", [4])],
    "medal-of-labor": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B", [3])],
    "angkor-decoration": [("type-a", "版型A", [1]), ("type-b", "版型B；正背", [2, 3])],
    "labour-decoration": [("grade-a", "图录所示级别A", [1]), ("grade-b", "图录所示级别B", [2]), ("grade-c", "图录所示级别C", [3])],
    "7th-january-decoration": [("type-a", "版型A", [1]), ("type-b", "版型B；正背", [2, 3])],
    "friendship-decoration": [("type-a", "版型A", [1]), ("type-b", "版型B；正背", [2, 3])],
}

EXCLUDE = {
    "royal-order-of-cambodia": [4],
    "royal-order-of-sahametrei": [4],
    "medal-of-the-reign-of-king-sisowath-i": [3],
    "medal-of-the-reign-of-king-sisowath-monivong": [3],
    "7th-january-decoration": [4],
}


def facts(source: dict) -> tuple[str, str]:
    slug = Path(source["object_url"]).stem
    page = ROOT / "sources/pages/wawards_cambodia" / f"{source['historical_polity']}__{slug}.html"
    body = page.read_text(encoding="utf-8", errors="replace")
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
    fact = re.search(r"(?:Order|Medal|Decoration) (?:was |is )?instituted(?: by [^.]+?|) (?:on |in )?([^.<]+)", text, re.I)
    if not fact:
        return source["page_title"], "设立时间待考"
    value = fact.group(1).strip()
    date_match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", value)
    if date_match:
        day, month, year = date_match.groups()
        months = {name: i for i, name in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
        return source["page_title"], f"{year}年{months.get(month, month)}月{int(day)}日设立"
    year_match = re.search(r"\b(18|19|20)\d{2}\b", value)
    return source["page_title"], f"{year_match.group(0)}年设立" if year_match else "设立时间待考"


def default_rows(slug: str, count: int):
    if count == 1:
        return [("main", "章饰", [1])]
    if count == 2:
        return [("main", "章饰；正背", [1, 2])]
    return [(f"form-{index}", f"图录所示版型{chr(64 + index)}", [index]) for index in range(1, count + 1)]


def build(polity: str, country_zh: str, volume_stem: str) -> tuple[int, int, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, used_hashes = [], [], set()
    excluded = []
    for source in [row for row in RAW if row["historical_polity"] == polity]:
        slug = Path(source["object_url"]).stem
        original, date_text = facts(source)
        source_images = {item["view_no"]: item for item in source["original_images"]}
        rows = SPECIAL.get(slug, default_rows(slug, len(source_images)))
        family = ("KHM" if polity == "kingdom" else "KAM") + "-AWARD-" + re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")
        for suffix, variant, picks in rows:
            record_id = f"{family}-{suffix.upper()}"
            views = []
            for order, image_no in enumerate(picks, 1):
                item = source_images[image_no]
                if item["sha256"] in used_hashes:
                    raise ValueError(f"duplicate selected payload: {slug}:{image_no}")
                used_hashes.add(item["sha256"])
                source_path = ROOT / item["local_path"]
                with Image.open(source_path) as decoded:
                    decoded.verify()
                relative = f"assets/images/wawards_cambodia/{polity}__{slug}_{suffix}_{image_no:02d}{source_path.suffix.lower()}"
                (ROOT / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, ROOT / relative)
                view_key = f"{record_id}-VIEW{order}"
                views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
                images.append({
                    "key": f"cambodia-wawards-{polity}-{slug}-{suffix}-{image_no:02d}",
                    "record_id": record_id,
                    "view_key": view_key,
                    "local_path": relative,
                    "source_page": source["object_url"],
                    "image_url": item["image_url"],
                    "artist": "World Awards reference catalogue",
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
                "country_zh": country_zh,
                "name": ZH[slug],
                "original": original,
                "date": date_text,
                "variant": variant,
                "views": views,
                "source_ids": [source["source_id"]],
                "image_kind": "object_photo",
                "html_eligible": True,
            })
        for image_no in EXCLUDE.get(slug, []):
            excluded.append({"source_id": source["source_id"], "image_no": image_no, "reason": "证书、章盒或局部细节，不作为完整章体行"})
    volume = ROOT / "data/volumes" / f"{volume_stem}.json"
    manifest = ROOT / "data/volumes" / f"{volume_stem}_manifest.json"
    volume.write_text(json.dumps({"as_of": "2026-09-28", "volume": country_zh, "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": [], "excluded_candidates": excluded}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(records), len({row["family"] for row in records}), len(images)


def main() -> None:
    kingdom = build("kingdom", "柬埔寨王国（1948–1970；1993–）", "cambodia_kingdom_wawards_variants")
    republic = build("peoples_republic", "柬埔寨人民共和国（1979–1989）", "kampuchea_peoples_republic_wawards_variants")
    print(json.dumps({"kingdom": {"rows": kingdom[0], "families": kingdom[1], "views": kingdom[2]}, "peoples_republic": {"rows": republic[0], "families": republic[1], "views": republic[2]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
