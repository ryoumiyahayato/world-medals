"""Publish reviewed Sudan variants from Spink 21001 lots 1326-1337."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/raw/sudan_spink21001"
DEST = ROOT / "assets/images/sudan_spink21001"
VOLUME = ROOT / "data/volumes/sudan_spink21001.json"
MANIFEST = ROOT / "data/volumes/sudan_spink21001_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(lot: int, key: str, filename: str, images: list[dict], crop=None, label="完整实物正面") -> dict:
    source = RAW / f"21001_{lot}_1.jpg"
    target = DEST / filename
    if crop:
        with Image.open(source) as image:
            image.crop(crop).save(target, quality=96)
    else:
        shutil.copy2(source, target)
    with Image.open(target) as image:
        width, height = image.size
        image.verify()
    images.append({
        "key": key,
        "record_id": key.rsplit("-VIEW-", 1)[0],
        "view_key": key,
        "local_path": target.relative_to(ROOT).as_posix(),
        "source_id": f"spink-21001-sudan-{lot}",
        "source_page": f"https://spink.com/lot/2100100{lot}",
        "source_original_url": f"https://d3ums4016ncdkp.cloudfront.net/auction/large/21001/21001_{lot}_1.jpg",
        "catalogue_pdf": "sources/books/spink/21001_lot_list.pdf",
        "catalogue_printed_page": 325 if lot <= 1329 else 326,
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": digest(target),
        "crop_box": list(crop) if crop else None,
        "visual_check": "complete award body and suspension retained",
    })
    return {"key": key, "label": label}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    images = []
    records = [
        {
            "id": "SDN-SPINK21001-1326-TWO-NILES-GRAND-OFFICER",
            "family": "MENA7-ORDER-OF-THE-TWO-NILES",
            "country_zh": "苏丹",
            "name": "两尼罗河勋章",
            "original": "Order of the Two Niles, Second Class / Grand Officer",
            "date": "1961年11月16日设立；图示约1961年后型",
            "variant": "二等／大官级；Spink & Son制造；60毫米颈章与92毫米星章；含微型章与襟章的完整套装",
            "views": [publish(1326, "SDN-SPINK21001-1326-TWO-NILES-GRAND-OFFICER-VIEW-1", "1326_grand_officer_set.jpg", images, label="完整套装正面")],
            "source_ids": ["spink-21001-sudan-1326"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
        {
            "id": "SDN-SPINK21001-1329-TWO-NILES-NECK-BADGE",
            "family": "MENA7-ORDER-OF-THE-TWO-NILES",
            "country_zh": "苏丹",
            "name": "两尼罗河勋章",
            "original": "Order of the Two Niles, neck badge",
            "date": "1961年11月16日设立",
            "variant": "颈章；47毫米；具体等级待考；完整实物正面",
            "views": [publish(1329, "SDN-SPINK21001-1329-TWO-NILES-NECK-BADGE-VIEW-1", "1329_two_niles_neck_badge.jpg", images)],
            "source_ids": ["spink-21001-sudan-1329"], "image_kind": "object_photo", "html_eligible": True,
        },
        {
            "id": "SDN-SPINK21001-1330-TWO-NILES-BREAST-BADGE",
            "family": "MENA7-ORDER-OF-THE-TWO-NILES",
            "country_zh": "苏丹",
            "name": "两尼罗河勋章",
            "original": "Order of the Two Niles, breast badge",
            "date": "1961年11月16日设立",
            "variant": "胸绶佩章；45毫米；犀牛悬饰；具体等级待考；完整实物正面",
            "views": [publish(1330, "SDN-SPINK21001-1330-TWO-NILES-BREAST-BADGE-VIEW-1", "1330_two_niles_breast_badge.jpg", images)],
            "source_ids": ["spink-21001-sudan-1330"], "image_kind": "object_photo", "html_eligible": True,
        },
        {
            "id": "SDN-SPINK21001-1331-REPUBLIC-FIRST-CLASS-STAR",
            "family": "MENA7-ORDER-OF-THE-REPUBLIC",
            "country_zh": "苏丹",
            "name": "苏丹共和国勋章",
            "original": "Order of the Republic, First Class Star",
            "date": "1961年11月16日设立",
            "variant": "一等星章；Spink & Son制造；98毫米；完整实物正面",
            "views": [publish(1331, "SDN-SPINK21001-1331-REPUBLIC-FIRST-CLASS-STAR-VIEW-1", "1331_republic_first_class_star.jpg", images)],
            "source_ids": ["spink-21001-sudan-1331"], "image_kind": "object_photo", "html_eligible": True,
            "supersedes_id": "SDN-MB-PENDING-ORDER-OF-THE-REPUBLIC-I-CLASS-BREAST-STAR",
        },
        {
            "id": "SDN-SPINK21001-1332-REPUBLIC-RHINO-NECK-BADGE",
            "family": "MENA7-ORDER-OF-THE-REPUBLIC",
            "country_zh": "苏丹",
            "name": "苏丹共和国勋章",
            "original": "Order of the Republic, neck badge",
            "date": "1961年11月16日设立；犀牛国徽型",
            "variant": "颈章；犀牛悬饰；88×60毫米；具体等级待考；完整实物正面",
            "views": [publish(1332, "SDN-SPINK21001-1332-REPUBLIC-RHINO-NECK-BADGE-VIEW-1", "1332_republic_rhino_neck_badge.jpg", images)],
            "source_ids": ["spink-21001-sudan-1332"], "image_kind": "object_photo", "html_eligible": True,
        },
        {
            "id": "SDN-SPINK21001-1334-CIVIL-ACCOMPLISHMENT-SPINK",
            "family": "MENA7-ORDER-OF-CIVIL-ACCOMPLISHMENT",
            "country_zh": "苏丹",
            "name": "苏丹民事成就勋章",
            "original": "Order of Civil Accomplishment, large breast badge",
            "date": "苏丹共和国时期",
            "variant": "大型星章式；Spink London制造；96×96毫米；完整实物正面",
            "views": [publish(1334, "SDN-SPINK21001-1334-CIVIL-ACCOMPLISHMENT-SPINK-VIEW-1", "1334_civil_accomplishment_spink.jpg", images)],
            "source_ids": ["spink-21001-sudan-1334"], "image_kind": "object_photo", "html_eligible": True,
            "supersedes_id": "MENA7-ORDER-OF-CIVIL-ACCOMPLISHMENT-F315C8EACA981751",
        },
        {
            "id": "SDN-SPINK21001-1335-REGIONAL-GOVERNMENT",
            "family": "MENA7-ORDER-OF-REGIONAL-GOVERNMENT",
            "country_zh": "苏丹",
            "name": "苏丹地方政府勋章",
            "original": "Order of Regional Government",
            "date": "苏丹共和国时期",
            "variant": "佩章；64毫米；原盒；完整实物正面",
            "views": [publish(1335, "SDN-SPINK21001-1335-REGIONAL-GOVERNMENT-VIEW-1", "1335_regional_government.jpg", images)],
            "source_ids": ["spink-21001-sudan-1335"], "image_kind": "object_photo", "html_eligible": True,
            "supersedes_id": "MENA7-ORDER-OF-REGIONAL-GOVERNMENT-66AD8F813B807E64",
        },
        {
            "id": "SDN-SPINK21001-1336-POLITICAL-ACCOMPLISHMENT",
            "family": "SDN-WAWARDS-ORDER-OF-POLITICAL-ACCOMPLISHMENT",
            "country_zh": "苏丹",
            "name": "政治成就勋章",
            "original": "Order of Political Accomplishment",
            "date": "1956年独立相关奖励体系",
            "variant": "镀金与镀银；40毫米；完整实物正面",
            "views": [publish(1336, "SDN-SPINK21001-1336-POLITICAL-ACCOMPLISHMENT-VIEW-1", "1336_political_accomplishment.jpg", images, (0, 0, 530, 931))],
            "source_ids": ["spink-21001-sudan-1336"], "image_kind": "object_photo", "html_eligible": True,
            "supersedes_id": "SDN-WAWARDS-ORDER-OF-POLITICAL-ACCOMPLISHMENT-01",
        },
        {
            "id": "SDN-SPINK21001-1336-PRODUCTION-50MM",
            "family": "MENA7-ORDER-OF-PRODUCTION-SUDAN",
            "country_zh": "苏丹",
            "name": "苏丹生产勋章",
            "original": "Order of Production",
            "date": "苏丹共和国时期",
            "variant": "镀金版；50毫米；具体等级待考；完整实物正面",
            "views": [publish(1336, "SDN-SPINK21001-1336-PRODUCTION-50MM-VIEW-1", "1336_production_50mm.jpg", images, (510, 0, 1100, 931))],
            "source_ids": ["spink-21001-sudan-1336"], "image_kind": "object_photo", "html_eligible": True,
        },
        {
            "id": "SDN-SPINK21001-1337-ALLIANCE",
            "family": "SDN-WAWARDS-ORDER-OF-THE-ALLIANCE",
            "country_zh": "苏丹",
            "name": "联盟勋章",
            "original": "Order of the Alliance",
            "date": "苏丹民主共和国时期",
            "variant": "单一等级；127×97毫米；完整实物正面",
            "views": [publish(1337, "SDN-SPINK21001-1337-ALLIANCE-VIEW-1", "1337_alliance.jpg", images)],
            "source_ids": ["spink-21001-sudan-1337"], "image_kind": "object_photo", "html_eligible": True,
        },
    ]
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹：Spink 21001拍品段", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27", "source": "Spink 21001, complete Sudan section, lots 1326-1337",
        "processed_lots": list(range(1326, 1338)),
        "omitted_as_same_grade_examples": [1327, 1328, 1333],
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"published {len(records)} Sudan Spink variant rows with {len(images)} complete views")


if __name__ == "__main__":
    main()
