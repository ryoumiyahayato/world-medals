from __future__ import annotations

import hashlib
import json
import pathlib
import shutil

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_thailand.jsonl"
IMAGE_MANIFEST = ROOT / "data/source_sweeps/medalbook_thailand_images_2026-09-27.json"
OUT_DIR = ROOT / "assets/images/thailand_medalbook"
VOLUME = ROOT / "data/volumes/thailand_medalbook_variants.json"
MANIFEST = ROOT / "data/volumes/thailand_medalbook_variants_manifest.json"


# record index: family id, Chinese name, date, exact pictured variant, selected views
ROWS = {
    1: ("THA-BUDDHA-2500", "佛历二千五百年纪念奖章", "1957年", "奖章；完整正反面", [2, 1]),
    2: ("THA-BORDER-SERVICE", "边境服务奖章", "1955年设立", "奖章；完整正反面", [2, 1]),
    9: ("THA-CHAKRA-MALA", "查克拉玛拉奖章", "1905年设立", "奖章；完整正反面", [2, 1]),
    10: ("THA-CHAKRABARTI-MALA", "查克拉巴蒂玛拉奖章", "1912年设立", "奖章；完整正反面", [2, 4]),
    13: ("THA-JUBILEE-COMMEMORATIVE", "登基银禧纪念奖章", "1971年", "奖章；完整正反面", [2, 4]),
    14: ("THA-CROWN-PRINCE-INVESTITURE", "哇集拉隆功王储册立纪念奖章", "1972年", "奖章；完整正反面", [3, 4]),
    15: ("THA-RAMA-V-EUROPE-VISIT", "拉玛五世欧洲访问纪念奖章", "1897／1907年", "奖章；完整正反面", [1, 2]),
    16: ("THA-ROYAL-STATE-VISIT-US-EUROPE", "国王访美及访欧纪念奖章", "1960—1961年", "奖章；完整正反面", [1, 2]),
    20: ("THA-PRINCESS-SIRINDHORN-ELEVATION", "诗琳通公主晋封纪念奖章", "1977年", "奖章；完整正反面", [2, 3]),
    23: ("THA-RAMA-IX-CORONATION", "拉玛九世加冕纪念奖章", "1950年", "银质奖章；完整正反面", [2, 5]),
    24: ("THA-RAMA-VII-MEDAL", "拉玛七世奖章", "1926年", "银质奖章；完整正反面", [1, 2]),
    29: ("THA-DUSHID-MALA", "杜西迪玛拉奖章", "1882年设立", "二等；完整正反面", [2, 1]),
    33: ("THA-FREEMEN-SAFEGUARDING", "自由民保卫奖章", "1969年设立", "二等；完整正反面", [4, 2]),
    34: ("THA-GREAT-WAR-VICTORY", "第一次世界大战胜利奖章", "1918—1921年", "奖章；完整正反面", [1, 2]),
    36: ("THA-CONSTITUTION-SAFEGUARDING", "保卫宪法奖章", "1932年后", "奖章；完整正反面", [1, 3]),
    42: ("THA-RAJARUCHI", "拉乍鲁吉奖章", "1897年设立", "奖章；完整正反面", [1, 2]),
    45: ("THA-RED-CROSS-APPRECIATION", "红十字表彰奖章", "设立日期待考", "一等金质版；完整正反面", [2, 1]),
    46: ("THA-RED-CROSS-APPRECIATION", "红十字表彰奖章", "设立日期待考", "二等银质版；完整正反面", [3, 2]),
    55: ("THA-ROYAL-CIPHER", "王室徽号奖章", "2020年设立", "一等；完整正反面", [2, 1]),
    69: ("THA-CHULA-CHOM-KLAO", "朱拉朱姆告勋章", "1873年设立", "特等大绶章星章；完整正面", [1]),
    70: ("THA-CHULA-CHOM-KLAO", "朱拉朱姆告勋章", "1873年设立", "特等大绶章项链；完整套件与章饰", [1, 3]),
    72: ("THA-CHULA-CHOM-KLAO", "朱拉朱姆告勋章", "1873年设立", "一等大十字星章；完整正反面", [3, 1]),
    73: ("THA-CHULA-CHOM-KLAO", "朱拉朱姆告勋章", "1873年设立", "一等大十字绶章；完整正反面", [3, 1]),
    75: ("THA-CHULA-CHOM-KLAO", "朱拉朱姆告勋章", "1873年设立", "四等军官级；完整正面", [1]),
    83: ("THA-ORDER-OF-RAMA", "拉玛勋章", "1918年设立", "一等大指挥官级；完整正面", [1]),
    88: ("THA-CROWN", "泰王冠勋章", "1869年设立", "一等大十字星章；完整正反面", [4, 3]),
    89: ("THA-CROWN", "泰王冠勋章", "1869—1948年型", "第一型三等指挥官级；完整正反面", [1, 2]),
    90: ("THA-CROWN", "泰王冠勋章", "1869—1948年型", "第一型二等大指挥官星章；完整正面", [1]),
    91: ("THA-CROWN", "泰王冠勋章", "1869—1948年型", "第一型二等大指挥官绶章；完整正反面", [1, 3]),
    94: ("THA-CROWN", "泰王冠勋章", "1869—1948年型", "第一型一等大十字绶章；完整正面", [4]),
    96: ("THA-CROWN", "泰王冠勋章", "1869—1948年型", "第一型六等金质奖章；完整正反面", [2, 4]),
    99: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型二等大指挥官星章；完整正反面", [2, 4]),
    100: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型二等大指挥官绶章；完整正反面", [3, 2]),
    101: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型特等大绶星章；完整正反面", [2, 1]),
    102: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型特等大绶章章饰；完整正反面", [1, 3]),
    103: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型一等大十字星章；完整正反面", [2, 1]),
    104: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型一等大十字套件；完整实物合图", [1]),
    105: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型三等骑士指挥官级；完整正反面", [1, 2]),
    106: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型五等骑士级；完整正反面", [2, 1]),
    107: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型六等金质奖章；完整正面", [1]),
    108: ("THA-CROWN", "泰王冠勋章", "1948年后型", "第二型七等银质奖章；完整正反面", [2, 1]),
    111: ("THA-DIREKGUNABHORN", "迪雷古那蓬勋章", "1991年设立", "四等同袍级；完整正面", [1]),
    119: ("THA-NINE-GEMS", "九宝石勋章", "1851年设立", "章饰；完整正面", [2]),
    120: ("THA-NINE-GEMS", "九宝石勋章", "1851年设立", "骑士戒指；完整实物", [1]),
    121: ("THA-NINE-GEMS", "九宝石勋章", "1851年设立", "佩挂式星章；完整正面", [1]),
    122: ("THA-WHITE-ELEPHANT", "白象勋章", "1861年设立", "二等大指挥官星章；完整正反面", [1, 3]),
    125: ("THA-WHITE-ELEPHANT", "白象勋章", "1861—1869年型", "第一型二等星章；完整正面", [1]),
    127: ("THA-WHITE-ELEPHANT", "白象勋章", "1861—1873年型", "第二型一等章饰；历史图录插图", [1]),
    128: ("THA-WHITE-ELEPHANT", "白象勋章", "1861—1873年型", "第二型二等章饰；历史图录插图", [1]),
    132: ("THA-WHITE-ELEPHANT", "白象勋章", "1861—1873年型", "第二型三等指挥官级；完整正反面", [1, 2]),
    134: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型三等指挥官级；完整正反面", [2, 5]),
    135: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型二等大指挥官级；完整正反面", [1, 3]),
    136: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型特等大绶章；历史图录插图", [1]),
    137: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型特等大绶星章；完整正反面", [2, 1]),
    138: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型一等大十字星章；完整正反面", [3, 1]),
    139: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型一等大十字绶章；完整正反面", [1, 2]),
    140: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型五等骑士级；完整正面", [1]),
    143: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型七等银质奖章；完整正反面", [2, 3]),
    144: ("THA-WHITE-ELEPHANT", "白象勋章", "1873—1941年型", "第三型四等军官级；完整正面", [1]),
    146: ("THA-RATANA-VARABHORN", "拉达纳瓦拉蓬功绩勋章", "1911年设立", "章饰；历史图录插图", [1]),
    148: ("THA-ROYAL-HOUSE-CHAKRI", "却克里王室勋章", "1884年设立", "星章；完整正面", [1]),
    149: ("THA-ROYAL-HOUSE-CHAKRI", "却克里王室勋章", "1884年设立", "项链；完整实物", [1]),
    150: ("THA-ROYAL-HOUSE-CHAKRI", "却克里王室勋章", "1884年设立", "佩章；完整正面", [1]),
}

HISTORICAL_DRAWINGS = {127, 128, 136, 146}


def main() -> None:
    raw_records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    image_items = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["items"]
    lookup = {(x["record_index"], x["image_index"]): x for x in image_items}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, used_hashes = [], [], set()
    for index, (family, name, date, variant, selections) in ROWS.items():
        raw = raw_records[index]
        record_id = f"THA-MB-{index:03d}"
        views = []
        for order, image_index in enumerate(selections, 1):
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
            view_key = f"THA-MB-{index:03d}-V{order}"
            if index in HISTORICAL_DRAWINGS:
                label = "历史图录插图"
            else:
                label = "完整正面" if order == 1 else "完整背面"
            views.append({"key": view_key, "label": label})
            images.append({
                "key": f"thailand-medalbook-{index:03d}-{image_index:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": raw["page_url"],
                "image_url": item["url"],
                "artist": "MedalBook catalogue object image" if index not in HISTORICAL_DRAWINGS else "MedalBook catalogue historical plate",
                "license": "Source terms apply; retained for offline research catalogue",
                "dimensions": dimensions,
                "bytes": target.stat().st_size,
                "sha256": sha,
                "decoded": True,
                "visually_checked": True,
            })
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": "泰国",
            "name": name,
            "original": raw["page_title"],
            "date": date,
            "variant": variant,
            "views": views,
            "source_ids": [raw["source_id"]],
            "image_kind": "historical_catalogue_illustration" if index in HISTORICAL_DRAWINGS else "object_photo",
            "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "泰国 · MedalBook 勋奖章等级与版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "images": len(images), "families": len({r['family'] for r in records}), "historical_drawings": len(HISTORICAL_DRAWINGS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
