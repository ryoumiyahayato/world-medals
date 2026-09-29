"""Publish reviewed Sudan variants from Noonans auction archive."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/raw/sudan_noonans"
DEST = ROOT / "assets/images/sudan_noonans"
VOLUME = ROOT / "data/volumes/sudan_noonans_variants.json"
MANIFEST = ROOT / "data/volumes/sudan_noonans_variants_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    views = []
    images = []
    source_urls = [
        "https://media.noonans.co.uk/database_images/Cataloguing%20System/Internet%20-%20Lots%20%28Images%29/279894/Internet%20Image%201_w500h500.jpg",
        "https://media.noonans.co.uk/database_images/Cataloguing%20System/Internet%20-%20Lots%20%28Images%29/279894/Internet%20Image%202_w500h500.jpg",
    ]
    for number, label in ((1, "完整实物正面"), (2, "完整实物背面")):
        source = RAW / f"279894_{number}_w500.jpg"
        target = DEST / f"sdf_long_service_good_conduct_{number}.jpg"
        shutil.copy2(source, target)
        with Image.open(target) as image:
            width, height = image.size
            image.verify()
        key = f"SDN-NOONANS-203194-SDF-LSGC-VIEW-{number}"
        views.append({"key": key, "label": label})
        images.append({
            "key": key,
            "record_id": "SDN-NOONANS-203194-SDF-LSGC",
            "view_key": key,
            "local_path": target.relative_to(ROOT).as_posix(),
            "source_id": "noonans-226-lot-428",
            "source_page": "https://www.noonans.co.uk/archive/past-catalogues/226/catalogue/203194/",
            "source_original_url": source_urls[number - 1],
            "image_kind": "object_photo",
            "width": width,
            "height": height,
            "sha256": digest(target),
            "visual_check": "complete medal and suspension retained",
            "rights_note": "Noonans archive image; retained for research catalogue use subject to source terms",
        })
    records.append({
        "id": "SDN-NOONANS-203194-SDF-LSGC",
        "family": "SDN-MB-SDF-LONG-SERVICE-GOOD-CONDUCT",
        "country_zh": "苏丹",
        "name": "苏丹防卫军长期服务与良好品行奖章",
        "original": "Sudan Defence Force Long Service and Good Conduct Medal",
        "date": "1933年11月4日设立",
        "variant": "铜质；无绶带实物；完整正反面；低清参考",
        "views": views,
        "source_ids": ["noonans-226-lot-428", "medalbook-sudan-020f567da416bb19"],
        "image_kind": "object_photo",
        "html_eligible": True,
        "supersedes_id": "SDN-MB-PENDING-SUDAN-DEFENCE-FORCE-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL",
    })

    pdf_source = ROOT / "sources/books/noonans/page_168_images/Im697.jpg"
    pdf_target = DEST / "anglo_egyptian_police_distinguished_service_lot647.jpg"
    shutil.copy2(pdf_source, pdf_target)
    with Image.open(pdf_target) as image:
        width, height = image.size
        image.verify()
    pdf_key = "SDN-NOONANS-2010-09-16-LOT647-VIEW-1"
    records.append({
        "id": "SDN-NOONANS-2010-09-16-LOT647",
        "family": "SDN-MB-POLICE-DISTINGUISHED-SERVICE",
        "country_zh": "苏丹",
        "name": "英埃苏丹警察杰出服务奖章",
        "original": "Anglo-Egyptian Sudan Police Distinguished Service Medal",
        "date": "英埃苏丹时期（1899—1955）",
        "variant": "银质；无名；佩挂状态；完整正面；历史拍卖图录·2010；低清参考",
        "views": [{"key": pdf_key, "label": "完整实物正面"}],
        "source_ids": ["noonans-2010-09-16-lot-647", "medalbook-sudan-c5295eba36deb910"],
        "image_kind": "object_photo",
        "html_eligible": True,
        "supersedes_id": "SDN-MB-PENDING-POLICE-DISTINGUISHED-SERVICE-MEDAL",
    })
    images.append({
        "key": pdf_key,
        "record_id": "SDN-NOONANS-2010-09-16-LOT647",
        "view_key": pdf_key,
        "local_path": pdf_target.relative_to(ROOT).as_posix(),
        "source_id": "noonans-2010-09-16-lot-647",
        "source_page": "https://www.noonans.co.uk/media/auction_catalogues/Medals%2016%20Sep%2010.pdf",
        "source_original_url": "https://www.noonans.co.uk/media/auction_catalogues/Medals%2016%20Sep%2010.pdf#page=168",
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": digest(pdf_target),
        "visual_check": "complete medal obverse and suspension retained; embedded catalogue photograph for lot 647",
        "rights_note": "Noonans historical auction catalogue image; retained for research catalogue use subject to source terms",
    })

    bar_source = RAW / "275916_1_w500.jpg"
    bar_target = DEST / "police_prison_gallantry_second_award_bar.jpg"
    shutil.copy2(bar_source, bar_target)
    with Image.open(bar_target) as image:
        width, height = image.size
        image.verify()
    bar_key = "SDN-NOONANS-199216-POLICE-PRISON-GALLANTRY-BAR-VIEW-1"
    records.append({
        "id": "SDN-NOONANS-199216-POLICE-PRISON-GALLANTRY-BAR",
        "family": "SDN-WAWARDS-POLICE-AND-PRISON-SERVICE-MEDAL-FOR-GALLANTRY",
        "country_zh": "苏丹",
        "name": "警察与监狱服务英勇奖章",
        "original": "Sudan Police and Prison Service Gallantry Medal",
        "date": "1948年设立",
        "variant": "银质；第二次授予横条；佩挂状态；同一实物正反面合图；低清参考",
        "views": [{"key": bar_key, "label": "完整实物正反面"}],
        "source_ids": ["noonans-woodliffe-lot-89", "wawards-sudan-a1a90d59f33d6a1dd484"],
        "image_kind": "object_photo",
        "html_eligible": True,
    })
    images.append({
        "key": bar_key,
        "record_id": "SDN-NOONANS-199216-POLICE-PRISON-GALLANTRY-BAR",
        "view_key": bar_key,
        "local_path": bar_target.relative_to(ROOT).as_posix(),
        "source_id": "noonans-woodliffe-lot-89",
        "source_page": "https://www.noonans.co.uk/archive/special-collections/2/199216/",
        "source_original_url": "https://media.noonans.co.uk/database_images/Cataloguing%20System/Internet%20-%20Lots%20%28Images%29/275916/Internet%20Image%201_w500h500.jpg",
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": digest(bar_target),
        "visual_check": "complete mounted medal shown from both faces; second-award bar retained",
        "rights_note": "Noonans archive image; retained for research catalogue use subject to source terms",
    })

    merit_source = RAW / "275915_1_w500.jpg"
    merit_target = DEST / "police_prison_meritorious_second_award_bar.jpg"
    shutil.copy2(merit_source, merit_target)
    with Image.open(merit_target) as image:
        width, height = image.size
        image.verify()
    merit_key = "SDN-NOONANS-199215-POLICE-PRISON-MERITORIOUS-BAR-VIEW-1"
    records.append({
        "id": "SDN-NOONANS-199215-POLICE-PRISON-MERITORIOUS-BAR",
        "family": "SDN-WAWARDS-POLICE-AND-PRISON-SERVICE-MEDAL-FOR-MERITORIOUS-SERVICE",
        "country_zh": "苏丹",
        "name": "警察与监狱功绩服务奖章",
        "original": "Sudan Police and Prison Service Meritorious Service Medal",
        "date": "1948年设立",
        "variant": "银质；第二次授予横条；佩挂状态；同一实物正反面合图；低清参考",
        "views": [{"key": merit_key, "label": "完整实物正反面"}],
        "source_ids": ["noonans-woodliffe-lot-88", "wawards-sudan-7b07898b9fbd0b114486"],
        "image_kind": "object_photo",
        "html_eligible": True,
    })
    images.append({
        "key": merit_key,
        "record_id": "SDN-NOONANS-199215-POLICE-PRISON-MERITORIOUS-BAR",
        "view_key": merit_key,
        "local_path": merit_target.relative_to(ROOT).as_posix(),
        "source_id": "noonans-woodliffe-lot-88",
        "source_page": "https://www.noonans.co.uk/archive/special-collections/2/199215/",
        "source_original_url": "https://media.noonans.co.uk/database_images/Cataloguing%20System/Internet%20-%20Lots%20%28Images%29/275915/Internet%20Image%201_w500h500.jpg",
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": digest(merit_target),
        "visual_check": "complete mounted medal shown from both faces; second-award bar retained",
        "rights_note": "Noonans archive image; retained for research catalogue use subject to source terms",
    })

    officer_source = RAW / "275914_1_w500.jpg"
    officer_target = DEST / "sdf_native_officers_named_wrong_ribbon.jpg"
    shutil.copy2(officer_source, officer_target)
    with Image.open(officer_target) as image:
        width, height = image.size
        image.verify()
    officer_key = "SDN-NOONANS-199214-SDF-NATIVE-OFFICERS-VIEW-1"
    records.append({
        "id": "SDN-NOONANS-199214-SDF-NATIVE-OFFICERS",
        "family": "SDN-WAWARDS-DEFENCE-FORCE-NATIVE-OFFICER-S-DECORATION",
        "country_zh": "苏丹",
        "name": "苏丹防卫军本地军官长期服务章",
        "original": "Sudan Defence Forces Native Officers’ Decoration",
        "date": "1933年11月4日设立",
        "variant": "银质；阿拉伯文边铭；具名实物；配带非原绶带；同一实物正反面合图；低清参考",
        "views": [{"key": officer_key, "label": "完整实物正反面"}],
        "source_ids": ["noonans-woodliffe-lot-87"],
        "image_kind": "object_photo",
        "html_eligible": True,
    })
    images.append({
        "key": officer_key,
        "record_id": "SDN-NOONANS-199214-SDF-NATIVE-OFFICERS",
        "view_key": officer_key,
        "local_path": officer_target.relative_to(ROOT).as_posix(),
        "source_id": "noonans-woodliffe-lot-87",
        "source_page": "https://www.noonans.co.uk/archive/special-collections/2/199214/",
        "source_original_url": "https://media.noonans.co.uk/database_images/Cataloguing%20System/Internet%20-%20Lots%20%28Images%29/275914/Internet%20Image%201_w500h500.jpg",
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": digest(officer_target),
        "visual_check": "complete named medal shown from both faces; auction description explicitly identifies the incorrect ribbon",
        "rights_note": "Noonans archive image; retained for research catalogue use subject to source terms",
    })

    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹：Noonans拍卖档案", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "source": "Noonans Sudan auction archive and historical catalogues", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"published {len(records)} Sudan Noonans variant rows with {len(images)} complete local images")


if __name__ == "__main__":
    main()
