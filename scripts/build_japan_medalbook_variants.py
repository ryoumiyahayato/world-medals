from __future__ import annotations

import hashlib
import json
import pathlib
import shutil

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_japan.jsonl"
IMAGE_MANIFEST = ROOT / "data/source_sweeps/medalbook_japan_images_2026-09-28.json"
OUT_DIR = ROOT / "assets/images/japan_medalbook"
VOLUME = ROOT / "data/volumes/japan_medalbook_variants.json"
MANIFEST = ROOT / "data/volumes/japan_medalbook_variants_manifest.json"


SELECTIONS = {
    1:[1],2:[1,2],3:[1,4],4:[2,1],6:[1,2],7:[1,2],8:[1,3],9:[2,1],
    14:[1],15:[1,2],35:[2,4],37:[1],38:[1,2],40:[1,2],42:[1,3],43:[4,6],
    44:[1,2],46:[2,4],48:[1,2],51:[4,3],53:[1,2],57:[1],58:[1,2],59:[2,4],
    61:[1,3],62:[2,1],65:[2,1],69:[1],70:[1],71:[2,4],72:[5,2],73:[1],
    74:[6,7],75:[1],78:[1],79:[1,2],80:[3,4],81:[3,2],82:[2,1],83:[1,3],
    84:[4,7],85:[2],86:[4,3],87:[1],88:[3,5],89:[1],90:[5,4],91:[5],
    92:[2],93:[1,4],94:[1,2],95:[2,3],96:[4,2],98:[1],99:[1,2],100:[1,4],
    101:[2,1],102:[1],103:[4,3],104:[4,1],105:[2,1],106:[2,4],107:[5,6],
    108:[3,2],109:[2,1],110:[1,3],111:[4,3],112:[1,2],113:[1,3],114:[2,1],
    115:[1,2],116:[3,4],
}

# These pictured pages are useful adjacent material, not Japanese state awards.
# The second-class Golden Kite star is also excluded because its entire image set
# is byte-for-byte identical to the first-class page; the surviving row is
# explicitly described as the I/II-class shared star insignia.
EXCLUDED = {10, 11, 41, 49, 50, 63, 76}
HISTORICAL_DRAWINGS = {57, 69, 98}

MEDALS = {
    1:("JPN-MEIJI-FORMOSA-EXPEDITION", "台湾出兵从军牌", "1874—1875年", "日本 · 明治时期"),
    2:("JPN-MEIJI-SINO-JAPANESE-WAR-CAMPAIGN-MEDAL", "明治二十七八年从军记章", "1894—1895年", "日本 · 明治时期"),
    3:("JPN-BOXER-WAR-MEDAL", "北清事变从军记章", "1900—1901年", "日本 · 明治时期"),
    4:("JPN-RUSSO-JAPANESE-WAR-MEDAL", "明治三十七八年从军记章", "1904—1905年", "日本 · 明治时期"),
    6:("JPN-WWI-CAMPAIGN-MEDAL", "大正三年至九年战役从军记章", "1914—1920年", "日本 · 大正时期"),
    7:("JPN-CHINA-INCIDENT-1931", "昭和六年至九年事变从军记章", "1931—1934年", "日本 · 昭和时期"),
    8:("JPN-CHINA-INCIDENT-1937", "支那事变从军记章", "1937—1945年", "日本 · 昭和时期"),
    9:("JPN-IMPERIAL-PALACE-DOUBLE-BRIDGE-VISIT", "帝国宫殿二重桥参观纪念章", "1937年", "日本 · 昭和时期"),
    14:("JPN-IMPERIAL-SILVER-WEDDING", "明治天皇银婚纪念章", "1894年", "日本 · 明治时期"),
    15:("JPN-2600-NATIONAL-ANNIVERSARY", "纪元二千六百年纪念章", "1940年", "日本 · 昭和时期"),
    35:("JPN-CHINA-INCIDENT-COMMEMORATIVE", "支那事变纪念章", "1942年", "日本 · 昭和时期"),
    37:("JPN-CROWN-PRINCE-KOREA-VOYAGE", "皇太子韩国行启纪念章", "1907—1909年", "日本 · 明治时期"),
    38:("JPN-TAISHO-FIRST-NATIONAL-CENSUS-MEDAL", "第一回国势调查纪念章", "1920—1921年", "日本 · 大正时期"),
    40:("JPN-CONSTITUTION-PROMULGATION", "帝国宪法发布纪念章", "1889年", "日本 · 明治时期"),
    42:("JPN-IMPERIAL-FLYING-ASSOCIATION-MERIT", "帝国飞行协会有功章", "1929年", "日本 · 昭和时期"),
    43:("JPN-SEA-DISASTER-RESCUE-MERIT", "帝国海难救济会有功章", "设立日期待考", "日本 · 大正时期"),
    44:("JPN-SEA-DISASTER-RESCUE-MERIT", "帝国海难救济会有功章", "设立日期待考", "日本 · 大正时期"),
    46:("JPN-HORSE-ADMINISTRATION-BUREAU", "马政局奖章", "1915年", "日本 · 大正时期"),
    48:("JPN-HORSE-ADMINISTRATION-BUREAU", "马政局奖章", "1915年", "日本 · 大正时期"),
    51:("JPN-KOREA-ANNEXATION-MEDAL", "韩国并合纪念章", "1910—1912年", "日本 · 明治时期"),
    53:("JPN-MEDAL-OF-HONOUR", "褒章", "1881年设立", "日本 · 明治时期"),
    57:("JPN-RED-CROSS-MEMBERSHIP", "日本红十字会会员章", "1888年后", "日本 · 明治时期"),
    58:("JPN-RED-CROSS-MEMBERSHIP", "日本红十字会会员章", "1888年后", "日本 · 明治时期"),
    59:("JPN-RED-CROSS-RUSSO-JAPANESE-WAR", "日本红十字会日俄战争纪念章", "1904—1905年", "日本 · 明治时期"),
    61:("JPN-SHOWA-ENTHRONEMENT", "昭和大礼纪念章", "1928年", "日本 · 昭和时期"),
    62:("JPN-TAISHO-ENTHRONEMENT-MEDAL", "大正大礼纪念章", "1915年", "日本 · 大正时期"),
    65:("JPN-WWI-VICTORY-MEDAL", "第一次世界大战战捷纪念章", "1920年", "日本 · 大正时期"),
}

ORDER_FAMILIES = [
    ("Order of the Chrysanthemum", "JPN-ORDER-CHRYSANTHEMUM", "菊花章", "1876／1888年设立", "日本 · 明治时期"),
    ("Order of the Golden Kite", "JPN-ORDER-GOLDEN-KITE", "金鵄勋章", "1890年正式制定；1947年废止", "日本 · 明治时期"),
    ("Order of the Paulownia Flowers", "JPN-ORDER-PAULOWNIA", "桐花大绶章", "2003年独立设置", "日本 · 现代"),
    ("Order of the Rising Sun", "JPN-ORDER-RISING-SUN", "旭日章", "1875年设立", "日本 · 明治时期"),
    ("Order of the Sacred Crown", "JPN-ORDER-SACRED-CROWN", "宝冠章", "1888年设立", "日本 · 明治时期"),
    ("Order of the Sacred Treasure", "JPN-ORDER-SACRED-TREASURE", "瑞宝章", "1888年设立", "日本 · 明治时期"),
    ("Red Cross Order of Merit", "JPN-RED-CROSS-ORDER-MERIT", "日本红十字会有功章", "1888年后；一等1956年设置", "日本 · 现代"),
]


def order_identity(title: str) -> tuple[str, str, str, str]:
    for prefix, family, name, date, period in ORDER_FAMILIES:
        if title.startswith(prefix):
            return family, name, date, period
    raise ValueError(title)


def variant_zh(title: str, index: int) -> str:
    if index == 74:
        return "一／二等共用星章；完整正反面"
    tail = title.split(",", 1)[1].strip() if "," in title else "章"
    replacements = {
        "Grand Cordon Breast Star":"大绶副章／星章", "Grand Cordon Badge":"大绶正章",
        "Small Chain Badge":"小链章饰", "Collar Badge":"颈饰章饰", "Collar":"颈饰",
        "I Class Breast Star":"一等星章", "II Class Breast Star":"二等星章",
        "I Class Sash Badge":"一等大绶正章", "III Class Neck Badge":"三等颈章",
        "IV Class Badge":"四等章饰", "V Class Badge":"五等章饰",
        "VI Class Badge":"六等章饰", "VII Class Silver Badge":"七等银质章饰",
        "I Class":"一等", "II Class":"二等", "III Class":"三等", "IV Class":"四等",
        "V Class":"五等", "VI Class":"六等", "VII Class":"七等", "VIII Class":"八等",
        "Badge":"章饰", "Star":"星章",
    }
    result = replacements.get(tail, tail)
    if index in HISTORICAL_DRAWINGS:
        return result + "；历史图录插图"
    return result + ("；完整正反面" if len(SELECTIONS[index]) > 1 else "；完整正面")


def medal_variant(title: str, index: int) -> str:
    clues = {
        14:"银质版", 43:"一等", 44:"二等", 46:"一等；马匹颈挂奖章",
        48:"三等；马匹颈挂奖章", 53:"具体绶色／种类待考", 57:"特别会员金质版",
        58:"特别会员银质版",
    }
    prefix = clues.get(index, "奖章")
    if index in HISTORICAL_DRAWINGS:
        return prefix + "；历史图录插图"
    return prefix + ("；完整正反面" if len(SELECTIONS[index]) > 1 or index == 1 else "；完整正面")


def main() -> None:
    raw_records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    image_items = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["items"]
    lookup = {(x["record_index"], x["image_index"]): x for x in image_items}
    pictured = {x["record_index"] for x in image_items}
    assert set(SELECTIONS) == pictured - EXCLUDED
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, used_hashes = [], [], set()
    for index in sorted(SELECTIONS):
        raw = raw_records[index]
        title = raw["page_title"]
        if index in MEDALS:
            family, name, date, period = MEDALS[index]
            variant = medal_variant(title, index)
        else:
            family, name, date, period = order_identity(title)
            variant = variant_zh(title, index)
        record_id = f"JPN-MB-{index:03d}"
        views = []
        for order, image_index in enumerate(SELECTIONS[index], 1):
            item = lookup[(index, image_index)]
            source = ROOT / item["local_path"]
            target = OUT_DIR / f"{index:03d}_{image_index:02d}{source.suffix.lower()}"
            shutil.copy2(source, target)
            sha = hashlib.sha256(target.read_bytes()).hexdigest()
            if sha in used_hashes:
                raise RuntimeError(f"duplicate selected image payload: {index}/{image_index}")
            used_hashes.add(sha)
            with Image.open(target) as im:
                dimensions = list(im.size)
                im.verify()
            view_key = f"JPN-MB-{index:03d}-V{order}"
            label = "历史图录插图" if index in HISTORICAL_DRAWINGS else ("完整正面" if order == 1 else "完整背面")
            views.append({"key": view_key, "label": label})
            images.append({
                "key": f"japan-medalbook-{index:03d}-{image_index:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": raw["page_url"],
                "image_url": item["url"],
                "artist": "MedalBook catalogue historical plate" if index in HISTORICAL_DRAWINGS else "MedalBook catalogue object image",
                "license": "Source terms apply; retained for offline research catalogue",
                "dimensions": dimensions,
                "bytes": target.stat().st_size,
                "sha256": sha,
                "decoded": True,
                "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": period, "name": name,
            "original": title, "date": date, "variant": variant, "views": views,
            "source_ids": [raw["source_id"]],
            "image_kind": "historical_catalogue_illustration" if index in HISTORICAL_DRAWINGS else "object_photo",
            "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of":"2026-09-28", "volume":"日本 · MedalBook 勋奖章等级与版型", "records":records}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of":"2026-09-28", "images":images}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    by_period = {p:sum(r["country_zh"] == p for r in records) for p in sorted({r["country_zh"] for r in records})}
    print(json.dumps({"records":len(records), "images":len(images), "families":len({r['family'] for r in records}), "by_period":by_period}, ensure_ascii=False))


if __name__ == "__main__":
    main()
