"""Build the first visually verified Sudan pack from the completed Wawards sweep."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "data/image_harvest/wawards_sudan_all_images.json"
OUT_DIR = ROOT / "assets/images/sudan_wawards_pack1"
VOLUME = ROOT / "data/volumes/sudan_wawards_pack1.json"
MANIFEST = ROOT / "data/volumes/sudan_wawards_pack1_manifest.json"

# Titles not represented by an independent family in the current Sudan volume.
AWARDS = {
    "Collar of Honour": ("荣誉项圈", "قلادة الشرف / Collar of Honour", "苏丹共和国时期；制度日期待考", "国家元首级项圈；完整项圈套装及配套星章"),
    "Defence Force Distinguished Service Decoration": ("苏丹防卫军杰出服务装饰章", "Defence Force Distinguished Service Decoration", "1933年11月4日设立", "防卫军杰出服务章；同一版型正反面"),
    "Defence Force General Service Medal": ("苏丹防卫军一般服务奖章", "Defence Force General Service Medal", "1933年11月4日设立；1940—1941年意军作战亦有授予", "战役／一般服务奖章；同一版型正反面"),
    "Defence Force Native Officer's Decoration": ("苏丹防卫军本地军官长期服务章", "Defence Force Native Officer's Decoration", "1933年11月4日设立", "本地军官十八年长期功绩服务章；完整正面"),
    "Medal of Bravery": ("勇敢奖章", "نوط الشجاعة / Medal of Bravery", "苏丹共和国时期；制度日期待考", "两级制；图示等级待考；完整正面"),
    "Medal of Duty": ("职责奖章", "نوط الواجب / Medal of Duty", "苏丹共和国时期；制度日期待考", "三级制；图示等级待考；同一版型正反面"),
    "Medal of Educational Hierarchy": ("教育体系奖章", "نوط السلم التعليمي / Medal of Educational Hierarchy", "民主共和国时期；制度日期待考", "三级制；图示等级待考；同一版型正反面"),
    "Medal of Evacuation": ("撤军纪念奖章", "نوط الجلاء / Medal of Evacuation", "1950年代独立前后；制度日期待考", "外国军队撤离纪念授予型；完整正面"),
    "Medal of Independence": ("独立奖章", "نوط الإستقلال / Medal of Independence", "1956年独立纪念授予型", "授予独立宣布日在役武装部队人员；同一版型正反面"),
    "Medal of Long and Distinguished Service": ("长期杰出服务奖章", "نوط الخدمة الطويلة الممتازة / Medal of Long and Distinguished Service", "苏丹共和国时期；制度日期待考", "士官与士兵长期杰出服务型；图示军种绶带版；完整正面"),
    "Order of Bravery": ("勇敢勋章", "وسام الشجاعة / Order of Bravery", "苏丹共和国时期；制度日期待考", "授予军官及同等身份公民的非凡英勇功绩型；完整正面"),
    "Order of Military Accomplishment": ("军事成就勋章", "وسام الإنجاز العسكري / Order of Military Accomplishment", "苏丹共和国时期；制度日期待考", "授予军事单位／机构的成就型；同一版型正反面"),
    "Order of National Unity": ("民族团结勋章", "وسام الوحدة الوطنية / Order of National Unity", "五月革命时期；制度日期待考", "军民国家团结功绩授予型；完整正面"),
    "Order of Persistence": ("坚毅勋章", "وسام الصمود / Order of Persistence", "苏丹共和国时期；制度日期待考", "武装、安全、警察、监狱及消防系统英勇坚毅授予型；同一版型正反面"),
    "Order of Political Accomplishment": ("政治成就勋章", "Order of Political Accomplishment", "苏丹共和国时期；制度日期待考", "政治独立与议会功绩授予型；完整正面"),
    "Order of Science and the Arts": ("科学与艺术勋章", "وسام العلم والآداب والفنون / Order of Science and the Arts", "苏丹共和国时期；制度日期待考", "两级制；图示等级待考；完整正面"),
    "Order of the Alliance": ("联盟勋章", "وسام التحالف / Order of the Alliance", "苏丹共和国时期；制度日期待考", "民主、社会主义与民族团结功绩授予型；完整正面"),
    "Order of the Constitution": ("宪法勋章", "وسام الدستور / Order of the Constitution", "1973年宪法纪念授予型", "授予首届人民议会议长及议员；同一版型正反面"),
    "Order of the Revolution": ("革命勋章", "وسام الثورة / Order of the Revolution", "1969年5月25日革命纪念授予型", "革命功绩授予型；同一版型正反面"),
    "Order of Victory": ("胜利勋章", "وسام النصر / Order of Victory", "苏丹共和国时期；制度日期待考", "武装部队、警察及监狱系统保卫革命授予型；同一版型正反面"),
    "Police and Prison Service Medal for Gallantry": ("警察与监狱服务英勇奖章", "Police and Prison Service Medal for Gallantry", "1948年12月15日设立", "警察与监狱人员英勇授予型；同一版型正反面"),
    "Police and Prison Service Medal for Meritorious Service": ("警察与监狱功绩服务奖章", "Police and Prison Service Medal for Meritorious Service", "1948年12月15日设立", "警察与监狱人员功绩服务型；同一版型正反面"),
    "Sash of Honour": ("荣誉绶带勋饰", "وشاح الشرف / Sash of Honour", "苏丹共和国时期；制度日期待考", "限额荣誉绶带；完整绶带套装及配套星章"),
    "Star of Civil Accomplishment": ("民事成就星章", "Star of Civil Accomplishment", "苏丹共和国时期；制度日期待考", "民事建设与发展功绩授予型；完整正面"),
    "Star of Military Accomplishment": ("军事成就星章", "نجمة الإنجاز العسكرية / Star of Military Accomplishment", "苏丹共和国时期；制度日期待考", "授予武装部队建设与发展功绩人员；完整正面"),
}


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    harvested = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    by_title: dict[str, list[dict]] = {}
    for image in harvested:
        by_title.setdefault(image["page_title"], []).append(image)

    records = []
    manifest = []
    for title, (name, original, date, variant) in AWARDS.items():
        source_images = sorted(by_title.get(title, []), key=lambda item: item["ordinal"])
        if not source_images:
            raise RuntimeError(f"No decoded source image for {title}")
        family = f"SDN-WAWARDS-{slug(title)}"
        record_id = family + "-01"
        views = []
        for index, source in enumerate(source_images, 1):
            source_path = ROOT / source["local_path"]
            suffix = source_path.suffix.lower()
            target = OUT_DIR / f"{slug(title).lower()}-{index:02d}{suffix}"
            shutil.copyfile(source_path, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{family}-V{index}"
            if title in {"Collar of Honour", "Sash of Honour"}:
                label = "完整套装" if index == 1 else "配套星章"
            elif len(source_images) == 2:
                label = "完整正面" if index == 1 else "完整反面"
            else:
                label = "完整正面" if index == 1 else f"补充视图{index}"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"wawards-sudan-{slug(title).lower()}-{index:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": source["page_url"], "image_url": source["image_url"],
                "artist": "Wawards / source collection", "license": "Rights status not stated; retained for offline research catalogue",
                "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "苏丹", "name": name,
            "original": original, "date": date, "variant": variant, "views": views,
            "source_ids": [source_images[0]["source_id"]], "image_kind": "object_photo", "html_eligible": True,
        })

    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹 Wawards 完整图批次1", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} Sudan families, {len(manifest)} complete local views")


if __name__ == "__main__":
    main()
