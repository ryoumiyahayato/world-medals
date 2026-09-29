from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_brunei.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR = ROOT / "assets/images/wawards_brunei"

ZH = {
    "royal-family-order-of-the-crown-of-brunei": "文莱王冠王家家族勋章",
    "most-illustrious-islamic-religious-order": "至显赫伊斯兰宗教勋章",
    "most-illustrious-order-of-splendid-valour": "至显赫英勇勋章",
    "most-esteemed-family-order": "至尊王家家族勋章",
    "most-exalted-order-of-famous-valour": "至高卓著英勇勋章",
    "most-gallant-order-of-the-hero-of-the-state-of-brunei": "文莱国家英雄至勇勋章",
    "most-blessed-order-of-loyalty": "至福忠诚勋章",
    "most-distinguished-order-of-merit": "至卓越功绩勋章",
    "most-honourable-order-of-the-crown": "至尊王冠勋章",
    "sultan-omar-ali-saifuddin-medal": "苏丹奥马尔·阿里·赛义夫丁奖章",
    "sultan-hassanal-bolkiah-medal": "苏丹哈桑纳尔·博尔基亚奖章",
    "faithful-and-meritorious-service-medal": "忠诚功绩服务奖章",
    "most-faithful-order-of-gallantry": "至忠英勇勋章",
    "meritorious-service-medal": "功绩服务奖章",
    "government-office-medal": "政府服务奖章",
    "medal-for-service-to-the-state": "国家服务奖章",
    "medal-of-the-proclamation-of-independence": "独立宣告奖章",
    "campaign-medal": "战役奖章",
    "long-service-medal": "长期服务奖章",
    "star-of-supreme-gallantry": "最高英勇星章",
    "warrior-soldier-star": "勇士星章",
    "inauguration-medal": "就职奖章",
    "armed-forces-general-service-medal": "武装部队一般服务奖章",
    "armed-forces-silver-jubilee-medal": "武装部队银禧奖章",
    "distinguished-warrior-star": "卓越勇士星章",
    "armed-forces-golden-jubilee-medal": "武装部队金禧奖章",
    "sultan-ahmad-tajuddin-medal": "苏丹艾哈迈德·塔朱丁奖章",
    "omar-ali-saifuddin-coronation-medal": "奥马尔·阿里·赛义夫丁加冕奖章",
    "sultan-hassanal-bolkiah-coronation-medal": "苏丹哈桑纳尔·博尔基亚加冕奖章",
    "armed-forces-60th-anniversary-medal": "武装部队六十周年奖章",
    "police-long-service-medal": "警察长期服务奖章",
    "police-medal-for-the-royal-proclamation": "警察王室宣告奖章",
    "silver-jubilee-medal": "苏丹登基银禧奖章",
    "golden-jubilee-medal": "苏丹登基金禧奖章",
    "national-day-silver-jubilee-medal": "国庆银禧奖章",
    "police-golden-jubilee-medal": "警察金禧奖章",
    "gurkha-reserve-unit-medal": "廓尔喀后备部队奖章",
    "royal-malay-regiment-long-service-and-good-conduct-medal": "王家马来团长期服务与品行优良奖章",
    "police-service-medal": "警察服务奖章",
}

# Deliberate split after visual review of all six contact sheets. Each tuple is
# (stable suffix, public variant label, source image numbers). Images grouped in
# one tuple are matching obverse/reverse views; separate tuples are distinct
# visible insignia or materially different forms.
SPECIAL = {
    "royal-family-order-of-the-crown-of-brunei": [("collar", "项链章", [1]), ("sash-badge", "绶章", [2]), ("star", "星章", [3])],
    "most-illustrious-islamic-religious-order": [("sash-badge", "绶章", [1]), ("star", "星章", [2])],
    "most-illustrious-order-of-splendid-valour": [("badge", "挂章", [1]), ("star", "星章", [2])],
    "most-esteemed-family-order": [("class1-collar", "一级项链章", [2]), ("class1-sash", "一级绶章", [3]), ("class1-star", "一级星章", [4]), ("class2-sash", "二级绶章", [5]), ("class2-star", "二级星章", [6])],
    "most-exalted-order-of-famous-valour": [("badge", "挂章", [1]), ("star", "星章", [2])],
    "most-gallant-order-of-the-hero-of-the-state-of-brunei": [("collar", "项链章", [1]), ("upper-star", "高级星章", [2]), ("upper-badge", "高级挂章", [3]), ("lower-badge", "低级挂章", [4]), ("lower-star", "低级星章", [5])],
    "most-blessed-order-of-loyalty": [("badge-a", "挂章版型A", [1]), ("star-a", "星章版型A", [2]), ("collar", "项链章", [3]), ("sash-badge", "绶章", [4]), ("star-b", "星章版型B", [5]), ("badge-b", "挂章版型B", [6]), ("badge-c", "挂章版型C", [7])],
    "most-distinguished-order-of-merit": [("collar", "项链章", [1]), ("badge-a", "挂章版型A", [2]), ("star-a", "星章版型A", [3]), ("badge-b", "挂章版型B；正背", [4, 5]), ("star-b", "星章版型B", [6]), ("star-c", "星章版型C", [7])],
    "most-honourable-order-of-the-crown": [("collar", "项链章", [1]), ("sash-badge", "绶章", [2]), ("star", "星章", [3])],
    "sultan-hassanal-bolkiah-medal": [("gold", "金色级", [1]), ("silver", "银色级", [2])],
    "most-faithful-order-of-gallantry": [("insignia-a", "章饰版型A", [1]), ("insignia-b", "章饰版型B", [2]), ("badge", "挂章", [3])],
    "meritorious-service-medal": [("type-a", "版型A；正背", [1, 2]), ("type-b", "版型B；正背", [3, 4])],
    "armed-forces-general-service-medal": [("type-a", "版型A", [1]), ("type-b", "版型B", [2]), ("type-c", "版型C", [3]), ("type-d", "版型D；正背", [4, 5])],
    "sultan-hassanal-bolkiah-coronation-medal": [("gold", "金色级；正背", [1, 2]), ("silver", "银色级", [3])],
    "armed-forces-60th-anniversary-medal": [("medal", "章饰；正背", [1, 3])],
}

EXCLUDE = {
    "most-esteemed-family-order": [1],
    "most-distinguished-order-of-merit": [8],
    "sultan-omar-ali-saifuddin-medal": [3],
    "sultan-hassanal-bolkiah-medal": [3],
    "faithful-and-meritorious-service-medal": [3],
    "meritorious-service-medal": [5],
    "campaign-medal": [3],
    "long-service-medal": [3],
    "armed-forces-general-service-medal": [6, 7],
    "armed-forces-golden-jubilee-medal": [3],
    "sultan-hassanal-bolkiah-coronation-medal": [4],
    "police-long-service-medal": [3],
    "silver-jubilee-medal": [3],
    "police-golden-jubilee-medal": [3],
    "royal-malay-regiment-long-service-and-good-conduct-medal": [3],
    "armed-forces-60th-anniversary-medal": [2],
}


def date_text(slug: str) -> str:
    body = (ROOT / "sources/pages/wawards_brunei" / f"brunei__{slug}.html").read_text(encoding="utf-8", errors="replace")
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
    match = re.search(r"(?:Order|Medal|Decoration) (?:was |is )?instituted([^.<]+)", text, re.I)
    if not match:
        return "设立时间待考"
    value = match.group(1).strip()
    first_year = re.search(r"\b(?:18|19|20)\d{2}\b", value)
    if not first_year:
        return "设立时间待考"
    value = value[: first_year.end()]
    full = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", value)
    if full:
        day, month, year = full.groups()
        months = {name: i for i, name in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
        return f"{year}年{months.get(month, month)}月{int(day)}日设立"
    month_year = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+((?:18|19|20)\d{2})", value, re.I)
    if month_year:
        month, year = month_year.groups()
        months = {name: i for i, name in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
        proper = month[:1].upper() + month[1:].lower()
        return f"{year}年{months.get(proper, proper)}月设立"
    return f"{first_year.group(0)}年设立"


def default_rows(slug: str, count: int) -> list[tuple[str, str, list[int]]]:
    excluded = set(EXCLUDE.get(slug, []))
    usable = [number for number in range(1, count + 1) if number not in excluded]
    if len(usable) == 1:
        return [("main", "章饰", usable)]
    if len(usable) == 2:
        return [("main", "章饰；正背", usable)]
    return [(f"form-{index}", f"图录所示版型{chr(64 + index)}", [number]) for index, number in enumerate(usable, 1)]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, excluded, used_hashes = [], [], [], set()
    for source in RAW:
        slug = Path(source["object_url"]).stem
        by_no = {item["view_no"]: item for item in source["original_images"]}
        rows = SPECIAL.get(slug, default_rows(slug, len(by_no)))
        family = "BRN-AWARD-" + re.sub(r"[^A-Z0-9]+", "-", slug.upper()).strip("-")
        for suffix, variant, picks in rows:
            record_id = f"{family}-{suffix.upper()}"
            views = []
            for order, image_no in enumerate(picks, 1):
                item = by_no[image_no]
                if item["sha256"] in used_hashes:
                    raise ValueError(f"duplicate selected payload: {slug}:{image_no}")
                used_hashes.add(item["sha256"])
                source_path = ROOT / item["local_path"]
                with Image.open(source_path) as decoded:
                    decoded.verify()
                relative = f"assets/images/wawards_brunei/{slug}_{suffix}_{image_no:02d}{source_path.suffix.lower()}"
                shutil.copy2(source_path, ROOT / relative)
                view_key = f"{record_id}-VIEW{order}"
                views.append({"key": view_key, "label": "完整正面" if order == 1 else "完整背面"})
                images.append({
                    "key": f"brunei-wawards-{slug}-{suffix}-{image_no:02d}", "record_id": record_id,
                    "view_key": view_key, "local_path": relative, "source_page": source["object_url"],
                    "image_url": item["image_url"], "artist": "World Awards reference catalogue",
                    "license": "Source terms apply; retained for offline research catalogue",
                    "dimensions": [item["width"], item["height"]], "bytes": source_path.stat().st_size,
                    "sha256": item["sha256"], "decoded": True, "visually_checked": True,
                })
            records.append({
                "id": record_id, "family": family, "country_zh": "文莱达鲁萨兰国",
                "name": ZH[slug], "original": source["page_title"], "date": date_text(slug),
                "variant": variant, "views": views, "source_ids": [source["source_id"]],
                "image_kind": "object_photo", "html_eligible": True,
            })
        for image_no in EXCLUDE.get(slug, []):
            excluded.append({"source_id": source["source_id"], "image_no": image_no, "reason": "证书、说明册、章盒或冗余套装总览，不作为单独完整章体行"})

    volume = ROOT / "data/volumes/brunei_wawards_variants.json"
    manifest = ROOT / "data/volumes/brunei_wawards_variants_manifest.json"
    volume.write_text(json.dumps({"as_of": "2026-09-28", "volume": "文莱达鲁萨兰国", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.write_text(json.dumps({"as_of": "2026-09-28", "images": images, "unpictured_candidates": [], "excluded_candidates": excluded}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(records), "families": len({row['family'] for row in records}), "views": len(images), "excluded": len(excluded)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
