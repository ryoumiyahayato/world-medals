"""Normalize the confirmed OMSA Egypt appendix difference set without inventing images."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/omsa_egypt_awards_appendix.jsonl"
VOLUME = ROOT / "data/volumes/egypt_omsa_unpictured_pack1.json"
MANIFEST = ROOT / "data/volumes/egypt_omsa_unpictured_pack1_manifest.json"
CONFLICT = ROOT / "data/conflicts/egypt_omsa_uncertain_dynastic_2026-09-27.json"

NEW = {
    "EGY-OMSA-BRAVERY": ("EGY-OMSA-BRAVERY-MEDAL", "勇敢奖章"),
    "EGY-OMSA-FILAHA": ("EGY-OMSA-ORDER-FILAHA", "法拉哈勋章"),
    "EGY-OMSA-GRACE-FAVOUR": ("EGY-OMSA-GRACE-FAVOUR-MEDAL", "恩典奖章"),
    "EGY-OMSA-CIVIL-COURTS-50TH": ("EGY-OMSA-CIVIL-COURTS-50TH", "民事法院五十周年纪念奖章"),
    "EGY-OMSA-MALARIA": ("EGY-OMSA-MALARIA-MEDAL", "疟疾奖章"),
    "EGY-OMSA-CHOLERA": ("EGY-OMSA-CHOLERA-MEDAL", "霍乱奖章"),
    "EGY-OMSA-JANUARY-26": ("EGY-OMSA-JANUARY-26-MEDAL", "一月二十六日奖章"),
    "EGY-OMSA-FUAD-LIFE-SAVING": ("EGY-OMSA-FUAD-LIFE-SAVING", "福阿德国王救生奖章"),
    "EGY-OMSA-FAROUK-BODYGUARD": ("EGY-OMSA-FAROUK-BODYGUARD", "法鲁克国王卫队纪念奖章"),
    "EGY-OMSA-KAMAL-AL-DIN-HUSSEIN": ("EGY-OMSA-KAMAL-AL-DIN-HUSSEIN", "卡迈勒丁·侯赛因亲王奖章"),
}
UNCERTAIN = {"EGY-OMSA-CROWN-EGYPT", "EGY-OMSA-IBRAHIM-PASHA", "EGY-OMSA-PARLIAMENTARY"}

PICTURED = {
    "EGY-OMSA-BRAVERY": {
        "date": "1913年5月10日设立；1914年12月19日停授",
        "variant": "银质奖章；浅蓝绶带；完整正反面；低清参考",
        "views": [
            {"key": "EGY-OMSA-BRAVERY-1913-V1", "label": "完整正面"},
            {"key": "EGY-OMSA-BRAVERY-1913-V2", "label": "完整反面"},
        ],
        "source_ids": ["omsa_egypt_awards_appendix", "medals_org_egypt_kingdom"],
        "image_kind": "object_photo",
    },
    "EGY-OMSA-GRACE-FAVOUR": {
        "date": "1928/29年实物；OMSA目录列1923年",
        "variant": "金质一等（35年以上服务）；福阿德一世版；L. Rosen & Co.（开罗）；正反面；历史拍卖图录插图·2019",
        "views": [
            {"key": "EGY-OMSA-GRACE-FAVOUR-GOLD-FUAD-V1", "label": "完整正面"},
            {"key": "EGY-OMSA-GRACE-FAVOUR-GOLD-FUAD-V2", "label": "完整反面"},
        ],
        "source_ids": ["omsa_egypt_awards_appendix", "heritage_auction_3075_2019"],
        "image_kind": "historical_auction_catalogue_illustration",
    },
    "EGY-OMSA-CHOLERA": {
        "date": "1947年",
        "variant": "镀金铜章；无皇冠悬挂版；35毫米；Fox／Fuchs（开罗）制；正反面；历史图录插图·2005",
        "views": [
            {"key": "EGY-OMSA-CHOLERA-1947-V1", "label": "完整正面"},
            {"key": "EGY-OMSA-CHOLERA-1947-V2", "label": "完整反面"},
        ],
        "source_ids": ["omsa_egypt_awards_appendix", "omsa_egypt_malaria_cholera_2005"],
        "image_kind": "historical_journal_illustration",
    },
    "EGY-OMSA-MALARIA": {
        "date": "1945年",
        "variant": "镀金章；红釉皇冠悬挂版；淡绿／白双色绶带及顶栏；正反面为不同实物型制参考",
        "views": [
            {"key": "EGY-OMSA-MALARIA-1945-CROWN-V1", "label": "完整正面（Spink拍品）"},
            {"key": "EGY-OMSA-MALARIA-1945-CROWN-V2", "label": "完整反面（JOMSA不同实物）"},
        ],
        "source_ids": ["omsa_egypt_awards_appendix", "spink_24003_egypt_health_medals", "omsa_egypt_malaria_cholera_2005"],
        "image_kind": "object_photo_and_historical_journal_reference",
    },
}

PICTURED_IMAGES = [
    {
        "key": "egypt-medals-org-bravery-1913-obverse",
        "record_id": "EGY-OMSA-BRAVERY-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-BRAVERY-1913-V1",
        "local_path": "assets/images/egypt_medals_org/bravery_1913_obverse.jpg",
        "source_page": "https://medals.org.uk/egypt/egypt-kingdom/egypt-kingdom016.htm",
        "image_url": "https://medals.org.uk/egypt/egypt-kingdom/images/egypt-kingdom016-01.jpg",
        "artist": "Medals of the World",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [162, 250],
        "bytes": 13452,
        "sha256": "170501d8214db78fe3a3c3a8d9dd5567d2ced1fc7ab73fb8ace1729ef87b14c1",
        "decoded": True,
        "visually_checked": True,
    },
    {
        "key": "egypt-medals-org-bravery-1913-reverse",
        "record_id": "EGY-OMSA-BRAVERY-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-BRAVERY-1913-V2",
        "local_path": "assets/images/egypt_medals_org/bravery_1913_reverse.jpg",
        "source_page": "https://medals.org.uk/egypt/egypt-kingdom/egypt-kingdom016.htm",
        "image_url": "https://medals.org.uk/egypt/egypt-kingdom/images/egypt-kingdom016-02.jpg",
        "artist": "Medals of the World",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [167, 250],
        "bytes": 11297,
        "sha256": "182775cb2cf4c757e4571718f6af8867286ddea6acf02fe5d082c05f9d45e044",
        "decoded": True,
        "visually_checked": True,
    },
    {
        "key": "egypt-heritage-3075-grace-favour-front",
        "record_id": "EGY-OMSA-GRACE-FAVOUR-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-GRACE-FAVOUR-GOLD-FUAD-V1",
        "local_path": "assets/images/egypt_heritage_3075/grace_favour_fuad_gold_front.jpg",
        "source_page": "sources/books/heritage_auction_3075_2019.pdf#page=88",
        "image_url": "embedded image R2474.jp2 on PDF page 88",
        "artist": "Heritage Auctions catalogue 3075, lot 32149",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [250, 246],
        "bytes": 23831,
        "sha256": "5967e72712d3ad6e161076d10aa47bc45920ab9550746668cb9e67773cdf868e",
        "decoded": True,
        "visually_checked": True,
    },
    {
        "key": "egypt-heritage-3075-grace-favour-reverse",
        "record_id": "EGY-OMSA-GRACE-FAVOUR-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-GRACE-FAVOUR-GOLD-FUAD-V2",
        "local_path": "assets/images/egypt_heritage_3075/grace_favour_fuad_gold_reverse.jpg",
        "source_page": "sources/books/heritage_auction_3075_2019.pdf#page=88",
        "image_url": "embedded image R2476.jp2 on PDF page 88",
        "artist": "Heritage Auctions catalogue 3075, lot 32149",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [250, 247],
        "bytes": 32894,
        "sha256": "62ab46a1668c8d9f8bb083bd6d303e0684ae1935bf30838a5ac69c9aa11b0dca",
        "decoded": True,
        "visually_checked": True,
    },
    {
        "key": "egypt-omsa-cholera-1947-front",
        "record_id": "EGY-OMSA-CHOLERA-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-CHOLERA-1947-V1",
        "local_path": "assets/images/egypt_omsa_malaria_cholera/cholera_1947_front.png",
        "source_page": "sources/books/omsa_egypt_malaria_cholera_2005.pdf#page=1",
        "image_url": "crop from JOMSA Vol. 56 No. 2, printed p.35, Figure 3",
        "artist": "JOMSA / source collection",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [545, 710],
        "bytes": 685702,
        "sha256": "4629da1f58fa2a22b0f8b599a50501b25184e8869c49ab4a1d666f4629e06347",
        "decoded": True,
        "visually_checked": True,
        "crop_box": [1115, 120, 1660, 830],
        "source_scan": "sources/pages/omsa_egypt_malaria_cholera_2005/page_1.png",
    },
    {
        "key": "egypt-omsa-cholera-1947-reverse",
        "record_id": "EGY-OMSA-CHOLERA-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-CHOLERA-1947-V2",
        "local_path": "assets/images/egypt_omsa_malaria_cholera/cholera_1947_reverse.png",
        "source_page": "sources/books/omsa_egypt_malaria_cholera_2005.pdf#page=1",
        "image_url": "crop from JOMSA Vol. 56 No. 2, printed p.35, Figure 4",
        "artist": "JOMSA / source collection",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [545, 715],
        "bytes": 692036,
        "sha256": "938c424cd1555eef6e81ff572e17687395bc9ea980e2e94e106246a150ae17c6",
        "decoded": True,
        "visually_checked": True,
        "crop_box": [1115, 875, 1660, 1590],
        "source_scan": "sources/pages/omsa_egypt_malaria_cholera_2005/page_1.png",
    },
    {
        "key": "egypt-spink-malaria-1945-red-crown-front",
        "record_id": "EGY-OMSA-MALARIA-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-MALARIA-1945-CROWN-V1",
        "local_path": "assets/images/egypt_omsa_malaria_cholera/malaria_1945_red_crown_front.jpg",
        "source_page": "https://spink.com/lot/24003000347",
        "image_url": "https://d3ums4016ncdkp.cloudfront.net/auction/large/24003/24003_347_1.jpg",
        "artist": "Spink & Son, auction 24003 lot 347",
        "license": "All rights reserved; retained for offline research catalogue",
        "dimensions": [245, 567],
        "bytes": 52307,
        "sha256": "b591a0ef9e847a7242b98142066eac008bfe81f26db915bdcf2b4ae652fb1e99",
        "decoded": True,
        "visually_checked": True,
        "crop_box": [45, 0, 290, 567],
        "source_scan": "assets/raw/egypt_spink_24003/24003_347_1.jpg",
    },
    {
        "key": "egypt-omsa-malaria-1945-crown-reverse",
        "record_id": "EGY-OMSA-MALARIA-MEDAL-PENDING-01",
        "view_key": "EGY-OMSA-MALARIA-1945-CROWN-V2",
        "local_path": "assets/images/egypt_omsa_malaria_cholera/malaria_1945_crown_reverse.png",
        "source_page": "sources/books/omsa_egypt_malaria_cholera_2005.pdf#page=1",
        "image_url": "crop from JOMSA Vol. 56 No. 2, printed p.35, Figure 2",
        "artist": "JOMSA / source collection",
        "license": "Rights status not stated; retained for offline research catalogue",
        "dimensions": [510, 1185],
        "bytes": 798504,
        "sha256": "6d08406e22f22ebc842f617af4ead891d3b67ad9a1dd03ba895e9903f4cd270f",
        "decoded": True,
        "visually_checked": True,
        "crop_box": [250, 85, 760, 1270],
        "source_scan": "sources/pages/omsa_egypt_malaria_cholera_2005/page_1.png",
    },
]


def main() -> None:
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_key = {row["candidate_key"]: row for row in rows}
    records = []
    for key, (family, name) in NEW.items():
        row = by_key[key]
        dates = row.get("date_candidates") or []
        date = "、".join(str(x) for x in dates) + "年" if dates else "日期待考"
        clues = "、".join(row.get("grades_or_classes") or []) or "版型待考"
        record = {
            "id": f"{family}-PENDING-01", "family": family, "country_zh": "埃及",
            "name": name, "original": row["page_title"], "date": date,
            "variant": f"{clues}；有目录文字记录，暂缺完整图片", "views": [],
            "source_ids": [row["source_id"]], "image_kind": "unpictured_record", "html_eligible": True,
        }
        if key in PICTURED:
            record.update(PICTURED[key])
            record["html_eligible"] = True
        records.append(record)
    conflicts = []
    for key in sorted(UNCERTAIN):
        row = by_key[key]
        conflicts.append({
            "candidate_key": key, "title": row["page_title"], "status": "INSUFFICIENT_TO_NORMALIZE",
            "reason": row.get("uncertainty_note") or "The appendix names only an award group and does not identify a discrete award.",
            "source_id": row["source_id"], "source_url": row["source_url"],
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 OMSA 差集（待配图）", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": PICTURED_IMAGES}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CONFLICT.write_text(json.dumps({"as_of": "2026-09-27", "scope": "Egypt OMSA appendix candidates not suitable for formal normalization", "items": conflicts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pictured = sum(bool(record["views"]) for record in records)
    print(f"built {len(records)} source-backed Egyptian families ({pictured} pictured, {len(records)-pictured} unpictured); retained {len(conflicts)} uncertain/group candidates")


if __name__ == "__main__":
    main()
