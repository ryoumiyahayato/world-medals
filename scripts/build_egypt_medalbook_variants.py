from __future__ import annotations

import hashlib
import json
import pathlib
import shutil

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_egypt.jsonl"
IMAGE_MANIFEST = ROOT / "data/source_sweeps/medalbook_egypt_images_2026-09-27.json"
OUT_DIR = ROOT / "assets/images/egypt_medalbook"
VOLUME = ROOT / "data/volumes/egypt_medalbook_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_medalbook_variants_manifest.json"


# record index: family id, Chinese name, date, Chinese variant, selected full views
ROWS = {
    82: ("EGY-COLLAR-OF-FOUAD-I", "福阿德一世项链勋饰", "1936—1954年", "项链；完整正面", [4]),
    86: ("EGY-ORDER-OF-AGRICULTURE", "农业勋章", "1932—1954年", "一等指挥官级；完整正面", [4, 5]),
    90: ("EGY-ORDER-OF-ARTS-AND-SCIENCES", "艺术与科学勋章", "1953年设立", "指挥官级；完整正反面", [8, 2]),
    91: ("EGY-ORDER-OF-ARTS-AND-SCIENCES", "艺术与科学勋章", "1953年设立", "军官级；完整正反面", [8, 6]),
    92: ("EGY-ORDER-OF-CULTURE", "文化勋章", "1932—1953年", "一等指挥官级；完整正反面", [5, 3]),
    94: ("EGY-ORDER-OF-CULTURE", "文化勋章", "1932—1953年", "二等军官级；完整正反面", [5, 6]),
    98: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1915—1953年型", "第一型三等；完整正面", [1]),
    99: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1915—1953年型", "第一型最高等绶章；完整正面", [1]),
    100: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1915—1953年型", "第一型最高等星章；完整正反面", [4, 1]),
    101: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1953年后型", "第二型一等；完整正反面", [2, 1]),
    103: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1953年后型", "第二型二等；完整正面", [1]),
    104: ("MENA7-ORDER-OF-THE-VIRTUES", "阿尔卡迈勒勋章（美德勋章）", "1953年后型", "第二型三等；完整正反面", [1, 2]),
    119: ("MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "1955—1965年", "一等大十字绶章；完整正反面", [1, 3]),
    120: ("MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "1955—1965年", "一等大十字星章；完整正反面", [1, 2]),
    121: ("MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "1955—1965年", "二等星章；完整正反面", [1, 3]),
    123: ("MENA7-ORDER-OF-INDEPENDENCE-EGYPT", "埃及独立勋章", "1955—1965年", "二等军官级；完整正反面", [1, 5]),
    127: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1953—1972年型", "第一型指挥官级；完整正反面", [2, 4]),
    128: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1953—1972年型", "第一型大绶章；完整正反面", [1, 2]),
    129: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1953—1972年型", "第一型大绶星章；完整正反面", [1, 2]),
    130: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1953—1972年型", "第一型大官级绶章；完整正反面", [2, 3]),
    131: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1953—1972年型", "第一型大官级星章；完整正反面", [2, 1]),
    134: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型指挥官级；完整正反面", [4, 5]),
    135: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型大绶章；完整正反面", [3, 1]),
    136: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型大绶星章；完整正反面", [1, 2]),
    137: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型大官级绶章；完整正反面", [2, 4]),
    138: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型大官级星章；完整正反面", [1, 2]),
    139: ("MENA7-ORDER-OF-MERIT-EGYPT", "埃及功绩勋章", "1972年后型", "第二型骑士级；完整正反面", [6, 7]),
    148: ("EGY-ORDER-OF-SPORTS", "体育勋章", "1954年设立", "二等章；完整正反面", [5, 4]),
    149: ("EGY-ORDER-OF-SPORTS", "体育勋章", "1954年设立", "一等指挥官级；完整正反面", [2, 4]),
    150: ("EGY-ORDER-OF-SPORTS", "体育勋章", "1954年设立", "三等骑士级；完整正反面", [1, 4]),
    152: ("EGY-MILITARY-STAR-OF-KING-FOUAD-I", "福阿德一世国王军事星章", "1919年设立；1922年改称", "奖章；完整正反面", [5, 6]),
    153: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型指挥官级；完整正反面", [3, 5]),
    154: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型大绶章；完整正反面", [4, 3]),
    155: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型大绶星章；完整正反面", [4, 5]),
    156: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型大官级绶章；完整正反面", [3, 1]),
    157: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型大官级星章；完整正反面", [5, 2]),
    158: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1915—1926年型", "第一型骑士级；完整正反面", [2, 5]),
    162: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型指挥官级；完整正面", [2]),
    163: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型大绶章；完整正反面", [3, 4]),
    164: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型大绶星章；完整正反面", [5, 2]),
    165: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型大官级绶章；完整正面", [3]),
    166: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型大官级星章；完整正面", [1]),
    168: ("MENA7-ORDER-OF-THE-NILE", "尼罗河勋章", "1926—1953年型", "第二型军官级；完整正反面", [4, 3]),
    170: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型指挥官级；完整正反面", [3, 2]),
    171: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型大绶章；完整正反面", [1, 3]),
    172: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型大绶星章；完整正反面", [3, 4]),
    173: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型大官级绶章；完整正反面", [2, 4]),
    174: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型大官级星章；完整正反面", [2, 1]),
    175: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型骑士级；完整正反面", [3, 5]),
    176: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1953—1972年型", "第一型军官级；完整正反面", [3, 2]),
    178: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1972年后型", "第二型指挥官级；完整正反面", [3, 4]),
    179: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1972年后型", "第二型大绶章；完整正反面", [4, 5]),
    180: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1972年后型", "第二型大绶星章；完整正反面", [3, 6]),
    181: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1972年后型", "第二型大官级绶章；完整正反面", [2, 1]),
    182: ("MENA7-ORDER-OF-THE-REPUBLIC-EGYPT", "埃及共和国勋章", "1972年后型", "第二型大官级星章；完整正反面", [3, 2]),
    185: ("EGY-ORDER-OF-THE-SINAI-STAR", "西奈之星勋章", "1972年设立", "一等；完整正反面", [7, 8]),
    186: ("EGY-ORDER-OF-THE-SINAI-STAR", "西奈之星勋章", "1972年设立", "二等；完整正面", [1]),
    188: ("EGY-ORDER-OF-TRADE-AND-INDUSTRY", "工商勋章", "1932—1954年", "第一型一等指挥官级；完整正反面", [3, 7]),
    193: ("EGY-ORDER-OF-TRADE-AND-INDUSTRY", "工商勋章", "1932—1954年", "第二型二等军官级；完整正反面", [5, 6]),
    194: ("EGY-UNION-ORDER-UAR", "阿拉伯联合共和国联合勋章", "1958—1961年", "章；完整正反面", [1, 3]),
}

# MedalBook reuses the exact same object photographs under these incompatible
# grade labels.  Keep the unambiguous counterpart and do not repeat or guess.
for _ambiguous_duplicate in (94, 130, 173):
    ROWS.pop(_ambiguous_duplicate)


def main() -> None:
    raw_records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    image_items = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["items"]
    lookup = {(x["record_index"], x["image_index"]): x for x in image_items}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, used_hashes = [], [], set()
    for index, (family, name, date, variant, selections) in ROWS.items():
        raw = raw_records[index]
        record_id = f"EGY-MB-{index:03d}"
        views = []
        for order, image_index in enumerate(selections, 1):
            item = lookup[(index, image_index)]
            source = ROOT / item["local_path"]
            suffix = source.suffix.lower()
            target = OUT_DIR / f"{index:03d}_{image_index:02d}{suffix}"
            shutil.copy2(source, target)
            sha = hashlib.sha256(target.read_bytes()).hexdigest()
            if sha in used_hashes:
                raise RuntimeError(f"duplicate selected image payload: {index}/{image_index}")
            used_hashes.add(sha)
            with Image.open(target) as im:
                dimensions = list(im.size)
                im.verify()
            view_key = f"EGY-MB-{index:03d}-V{order}"
            label = "完整正面" if order == 1 else "完整背面"
            views.append({"key": view_key, "label": label})
            images.append({
                "key": f"egypt-medalbook-{index:03d}-{image_index:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": raw["page_url"],
                "image_url": item["url"],
                "artist": "MedalBook catalogue object image",
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
            "country_zh": "埃及",
            "name": name,
            "original": raw["page_title"],
            "date": date,
            "variant": variant,
            "views": views,
            "source_ids": [raw["source_id"]],
            "image_kind": "object_photo",
            "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 · MedalBook 等级与版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "images": len(images), "families": len({r['family'] for r in records})}, ensure_ascii=False))


if __name__ == "__main__":
    main()
