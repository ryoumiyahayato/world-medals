"""Promote visually reviewed Sudan Commons grade/variant images into the catalogue."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/image_harvest/commons_sudan_full_body_retry.json"
MENA = ROOT / "data/volumes/mena_round7_2026-09-26.json"
WAWARDS = ROOT / "data/volumes/sudan_wawards_pack1.json"
OUT = ROOT / "data/volumes/sudan_commons_variants.json"
MANIFEST = ROOT / "data/volumes/sudan_commons_variants_manifest.json"
DEST = ROOT / "assets/images/sudan_commons_variants"

REPLACEMENTS = [
    ("MENA7-MEDAL-FOR-GALLANTRY-7CC54D027FD2C886", "Medal For Gallantry-removebg-preview.png", "Medal For Gallantry back-removebg-preview.png", "图示版型；完整正背面"),
    ("MENA7-MEDAL-FOR-MERIT-135AA0D3E9C4685F", "Medal For Merit I Class-removebg-preview.png", "Medal For Merit I Class back-removebg-preview.png", "一等；完整正背面"),
    ("MENA7-MEDAL-FOR-MERIT-2236C96A483E7B5E", "Medal For Merit III Class-removebg-preview.png", "Medal For Merit III Class back-removebg-preview.png", "三等；完整正背面"),
    ("MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC-A9B7F78A1898", "Jadara Bronze front part of Order of Merit of the Sudanese Republic.png", "Jadara Bronze back part of Order of Merit of the Sudanese Republic.png", "三等；铜质／铜色版；完整正背面"),
    ("MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC-C7EED759BFC1", "Jadara Gold front part of Order of Merit of the Sudanese Republic.jpg", "Jadara Gold back part of Order of Merit of the Sudanese Republic.png", "一等；银鎏金／金色版；完整正背面"),
    ("MENA7-ORDER-OF-DISTINCTION-SUDAN-8119C2006F68", "Order of Distinction (Sudan), class I.png", None, "一等；完整实物正面"),
    ("MENA7-PRISON-LONG-AND-DISTINGUISHED-SERVICE-MEDAL-666541F2E76E5753", "Prison Long And Distinguished Service Medal-removebg-preview.png", "Prison Long And Distinguished Service Medal back-removebg-preview.png", "监狱版；完整正背面"),
    ("MENA7-ORDER-OF-PRODUCTION-SUDAN-83C824242AD5", "Production Bronze part of Order of Merit of the Sudanese Republic.png", None, "铜质／铜色版；完整实物正面"),
    ("MENA7-QUEEN-S-SUDAN-MEDAL-6F8B2E605E2F", "Queen s Sudan Medal In Silver-removebg-preview.png", "Queen s Sudan Medal In Silver back-removebg-preview.png", "银质版；完整正背面"),
]

NEW = [
    ("SDN-COMMONS-DISTINCTION-CLASS-III", "MENA7-ORDER-OF-DISTINCTION-SUDAN", "苏丹卓越勋章", "Order of Distinction (Sudan) Class III", "1961年11月16日设立", "三等；完整实物正面", "Order of Distinction (Sudan) Class III.png"),
    ("SDN-COMMONS-DISTINCTION-BOW", "MENA7-ORDER-OF-DISTINCTION-SUDAN", "苏丹卓越勋章", "Order of Distinction (Sudan)", "1961年11月16日设立", "蝶结绶佩带型；具体等级待考；完整实物正面", "Order of Distinction (Sudan).png"),
    ("SDN-COMMONS-DISTINCTION-STAR", "MENA7-ORDER-OF-DISTINCTION-SUDAN", "苏丹卓越勋章", "Order of Distinction Sudan", "1961年11月16日设立", "星章式；具体等级待考；完整实物正面", "Order of Distinction Sudan-removebg-preview.png"),
    ("SDN-COMMONS-LOYAL-SON-MINIATURE", "MENA7-ORDER-OF-LOYAL-SON-OF-SUDAN", "苏丹忠诚之子勋章", "Miniature Order of Loyal Son of Sudan", "苏丹共和国时期", "微型章；完整实物正面", "Miniature+Order+of+Loyal+Son+of+Sudan+3-removebg-preview.png"),
    ("SDN-COMMONS-MILITARY-ACCOMPLISHMENT-ALT", "SDN-WAWARDS-ORDER-OF-MILITARY-ACCOMPLISHMENT", "军事成就勋章", "Order of Military Accomplishment Sudan", "苏丹共和国时期", "八芒星式另一图式；完整实物正面", "Order of Military Accomplishment Sudan-removebg-preview.png"),
    ("SDN-COMMONS-TWO-NILES-1961-1969-SET", "MENA7-ORDER-OF-THE-TWO-NILES", "两尼罗河勋章", "Order of the Two Niles grand cross insignias (Sudan 1961-1969)", "1961—1969年型", "大十字级套装；历史实物陈列图", "Order of the Two Niles grand cross insignias (Sudan 1961-1969) - Tallinn Museum of Orders.jpg"),
    ("SDN-COMMONS-PRODUCTION-GOLD", "MENA7-ORDER-OF-PRODUCTION-SUDAN", "苏丹生产勋章", "Production Gold part of Order of Merit of the Sudanese Republic", "苏丹共和国时期", "金质／金色版；完整实物正面", "Production Gold part of Order of Merit of the Sudanese Republic.png"),
    ("SDN-COMMONS-PRODUCTION-SILVER", "MENA7-ORDER-OF-PRODUCTION-SUDAN", "苏丹生产勋章", "Production Silver part of Order of Merit of the Sudanese Republic", "苏丹共和国时期", "银质／银色版；完整实物正面", "Production Silver part of Order of Merit of the Sudanese Republic.png"),
    ("SDN-COMMONS-QUEENS-SUDAN-BRONZE", "MENA7-QUEEN-S-SUDAN-MEDAL", "女王苏丹奖章", "Queen's Sudan Medal in Bronze", "1899年设立", "铜质版；完整正背面", "Queen s Sudan Medal In Bronze-removebg-preview.png", None, "Queen s Sudan Medal In Bronze back-removebg-preview.png"),
    ("SDN-COMMONS-SCIENCE-ARTS-GOLD", "SDN-WAWARDS-ORDER-OF-SCIENCE-AND-THE-ARTS", "科学、文学与艺术勋章", "Order of Science, Literature and the Arts in Gold", "苏丹共和国时期", "金质／金色版；完整实物正面", "Science gold part of Order of Merit of the Sudanese Republic.png", "SDN-MB-PENDING-ORDER-OF-SCIENCE-LITERATURE-AND-THE-ARTS-IN-GOLD"),
    ("SDN-COMMONS-SCIENCE-ARTS-SILVER", "SDN-WAWARDS-ORDER-OF-SCIENCE-AND-THE-ARTS", "科学、文学与艺术勋章", "Order of Science, Literature and the Arts in Silver", "苏丹共和国时期", "银质／银色版；完整实物正面", "Science silver part of Order of Merit of the Sudanese Republic.png", "SDN-MB-PENDING-ORDER-OF-SCIENCE-LITERATURE-AND-THE-ARTS-IN-SILVER"),
    ("SDN-COMMONS-ORDER-MERIT-ALT-BRONZE", "MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC", "苏丹共和国功绩勋章", "Sudan Order of Merit Bronze", "1961年11月16日设立", "三等；铜质；另一图式；完整实物正面", "Sudan Order of Merit Bronze.png"),
    ("SDN-COMMONS-ORDER-MERIT-ALT-GOLD", "MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC", "苏丹共和国功绩勋章", "Sudan Order of Merit Gold", "1961年11月16日设立", "一等；银鎏金／金色；另一图式；完整实物正面", "Sudan Order of Merit Gold front.png"),
    ("SDN-COMMONS-ORDER-MERIT-ALT-SILVER", "MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC", "苏丹共和国功绩勋章", "Sudan Order of Merit Silver", "1961年11月16日设立", "二等；银质／银色；另一图式；完整实物正面", "Sudan Order of Merit Silver.png"),
    ("SDN-COMMONS-ORDER-MERIT-ALT-BICOLOUR", "MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC", "苏丹共和国功绩勋章", "Sudan Order of Merit", "苏丹共和国时期", "双色珐琅异型；具体等级待考；完整实物正面", "Sudan Order of Merit.png"),
    ("SDN-COMMONS-REPUBLIC-II-C-BADGE", "MENA7-ORDER-OF-THE-REPUBLIC", "苏丹共和国勋章", "Sudan Order of the Republic II Class Badge", "苏丹共和国时期", "二等；蝶结绶挂章；完整实物正面", "Sudan+Order+of+Republic+II+C+Badge+ME-removebg-preview.png"),
    ("SDN-COMMONS-MEDAL-OF-DUTY-UNRESOLVED", "SDN-MB-ORDER-OF-DUTY", "苏丹义务奖章", "Medal of Duty", "苏丹共和国时期", "三等；铜质；三条白纹绿绶；完整实物正面", "Medal of Duty Sudan-removebg-preview.png"),
    ("SDN-COMMONS-POLICE-PRISON-MERITORIOUS-SERVICE", "SDN-MB-MERITORIOUS-SERVICE-MEDAL", "警察与监狱服务功绩奖章", "Police and Prison Service Medal for Meritorious Service", "1948年12月15日设立", "警察与监狱服务版；完整实物正背面", "Police and Prison Service Medal for Meritorious Service-removebg-previe.png", "SDN-MB-PENDING-MEDAL-FOR-MERITORIOUS-SERVICE", "Police and Prison Service Medal for Meritorious Service-removebg-preview.png"),
]

OFFICIAL_AUGMENTS = [
    ("SDN-COMMONS-UPGRADE-MENA7-MEDAL-FOR-GALLANTRY-7CC54D027FD2C886", "SDN-PRESIDENCY-COURAGE-OFFICIAL", "官方图式（等级待考）", "courage_official.png", "medal-courage"),
    ("SDN-COMMONS-UPGRADE-MENA7-MEDAL-FOR-MERIT-135AA0D3E9C4685F", "SDN-PRESIDENCY-MERIT-I-FRONT-OFFICIAL", "一等官方图式·正面", "merit_class1_front_official.png", "medal-merit"),
    ("SDN-COMMONS-UPGRADE-MENA7-MEDAL-FOR-MERIT-135AA0D3E9C4685F", "SDN-PRESIDENCY-MERIT-I-REVERSE-OFFICIAL", "一等官方图式·反面", "merit_class1_reverse_official.png", "medal-merit2"),
    ("SDN-COMMONS-UPGRADE-MENA7-MEDAL-FOR-MERIT-135AA0D3E9C4685F", "SDN-PRESIDENCY-MERIT-I-GOLD-FRONT-OFFICIAL", "一等金色官方图式·正面", "merit_class1_gold_front_official.jpg", "medal-merit-goldf"),
    ("SDN-COMMONS-UPGRADE-MENA7-MEDAL-FOR-MERIT-135AA0D3E9C4685F", "SDN-PRESIDENCY-MERIT-I-GOLD-REVERSE-OFFICIAL", "一等金色官方图式·反面", "merit_class1_gold_reverse_official.png", "medal-merit-goldb"),
    ("SDN-COMMONS-UPGRADE-MENA7-ORDER-OF-PRODUCTION-SUDAN-83C824242AD5", "SDN-PRESIDENCY-PRODUCTION-BRONZE-OFFICIAL", "官方图式", "production_bronze_official.png", "medal-production"),
    ("SDN-COMMONS-PRODUCTION-GOLD", "SDN-PRESIDENCY-PRODUCTION-GOLD-OFFICIAL", "官方图式", "production_gold_official.png", "medal-production-gold"),
    ("SDN-COMMONS-PRODUCTION-SILVER", "SDN-PRESIDENCY-PRODUCTION-SILVER-OFFICIAL", "官方图式", "production_silver_official.png", "medal-production-silver"),
    ("SDN-COMMONS-SCIENCE-ARTS-GOLD", "SDN-PRESIDENCY-SCIENCE-ARTS-GOLD-OFFICIAL", "官方图式", "science_arts_gold_official.png", "Medal-science-literature-arts-Gold"),
    ("SDN-COMMONS-SCIENCE-ARTS-SILVER", "SDN-PRESIDENCY-SCIENCE-ARTS-SILVER-OFFICIAL", "官方图式", "science_arts_silver_official.png", "Medal-science-literature-arts-silver"),
]


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def main() -> None:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))["pending"]
    by_title = {x["page_title"]: x for x in queue if x.get("status") == "DOWNLOADED"}
    existing = {r["id"]: r for path in (MENA, WAWARDS) for r in json.loads(path.read_text(encoding="utf-8"))["records"]}
    records, images = [], []
    DEST.mkdir(parents=True, exist_ok=True)

    def views(record_id: str, titles: list[str]) -> list[dict]:
        result = []
        for index, title in enumerate(titles, 1):
            item = by_title.get(title)
            if not item:
                raise RuntimeError(f"Required reviewed image not downloaded: {title}")
            key = f"{record_id}-VIEW-{index}"
            label = "完整正面" if index == 1 else "完整反面"
            source_path = ROOT / item["local_path"]
            suffix = source_path.suffix.lower()
            published = DEST / f"{slug(record_id).lower()}-{index}{suffix}"
            shutil.copyfile(source_path, published)
            result.append({"key": key, "label": label})
            images.append({
                "key": key, "record_id": record_id, "view_key": key,
                "local_path": published.relative_to(ROOT).as_posix(), "source_page": item["page_url"],
                "source_file_title": item["file_title"], "image_kind": "object_photo",
            })
        return result

    for old_id, front, back, variant in REPLACEMENTS:
        old = existing[old_id]
        record_id = "SDN-COMMONS-UPGRADE-" + slug(old_id)
        record = {
            **{k: v for k, v in old.items() if k not in {"id", "views", "variant", "source_ids"}},
            "id": record_id, "variant": variant, "views": views(record_id, [front] + ([back] if back else [])),
            "source_ids": [by_title[front]["source_id"]] + ([by_title[back]["source_id"]] if back else []),
            "image_kind": "object_photo", "html_eligible": True, "supersedes_id": old_id,
        }
        if old_id.startswith("MENA7-PRISON-LONG-AND-DISTINGUISHED-SERVICE-MEDAL-"):
            record["family"] = "MENA7-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL-FOR-POLICE"
            record["name"] = "长期服务与良好品行奖章"
        records.append(record)

    for spec in NEW:
        record_id, family, name, original, date, variant, title = spec[:7]
        supersedes_id = spec[7] if len(spec) > 7 else None
        back = spec[8] if len(spec) > 8 else None
        row = {
            "id": record_id, "family": family, "country_zh": "苏丹", "name": name,
            "original": original, "date": date, "variant": variant,
            "views": views(record_id, [title] + ([back] if back else [])),
            "source_ids": [by_title[title]["source_id"]] + ([by_title[back]["source_id"]] if back else []),
            "image_kind": "object_photo", "html_eligible": True,
        }
        if supersedes_id:
            row["supersedes_id"] = supersedes_id
        records.append(row)

    by_record_id = {record["id"]: record for record in records}
    for record_id, key, label, filename, page_slug in OFFICIAL_AUGMENTS:
        record = by_record_id[record_id]
        record["views"].append({"key": key, "label": label})
        record["variant"] += "＋官方图式" if "官方图式" not in record["variant"] else ""
        images.append({
            "key": key, "record_id": record_id, "view_key": key,
            "local_path": f"assets/images/sudan_presidency_official/{filename}",
            "source_page": f"https://www.presidency.gov.sd/medals-decorations/{page_slug}",
            "source_file_title": f"Sudan Presidency official diagram: {page_slug}",
            "image_kind": "official_diagram",
        })

    OUT.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹 Commons 等级与版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} Sudan Commons variant rows with {len(images)} complete views; replaced {len(REPLACEMENTS)} older rows")


if __name__ == "__main__":
    main()
