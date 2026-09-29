"""Build Ottoman variant rows from the complete Turkey section of Spink 21001."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "raw" / "ottoman_spink21001"
ASSETS = ROOT / "assets" / "images" / "ottoman_spink21001"
VOLUME = ROOT / "data" / "volumes" / "ottoman_spink21001.json"
MANIFEST = ROOT / "data" / "volumes" / "ottoman_spink21001_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_full_image(lot: int, view_key: str, filename: str, label: str, images: list[dict]) -> dict:
    source = RAW / f"21001_{lot}_1.jpg"
    destination = ASSETS / filename
    shutil.copy2(source, destination)
    with Image.open(destination) as decoded:
        width, height = decoded.size
        decoded.verify()
    images.append({
        "view_key": view_key,
        "local_path": destination.relative_to(ROOT).as_posix(),
        "source_id": f"spink-21001-lot-{lot}",
        "source_page_url": f"https://spink.com/lot/2100100{lot}",
        "source_original_url": f"https://d3ums4016ncdkp.cloudfront.net/auction/large/21001/21001_{lot}_1.jpg",
        "download_status": "downloaded_original_and_decoded",
        "license": "Spink auction archive image; local research use",
        "width": width,
        "height": height,
        "sha256": digest(destination),
        "side": "front",
        "visual_check": "完整绶带、悬挂结构与章体均在画面内",
    })
    return {"key": view_key, "label": label}


def add_pair(lot: int, prefix: str, base_name: str, images: list[dict]) -> list[dict]:
    source_path = RAW / f"21001_{lot}_1.jpg"
    views = []
    with Image.open(source_path) as source:
        width, height = source.size
        boxes = {
            "FRONT": (0, 0, width // 2, height),
            "BACK": (width // 2, 0, width, height),
        }
        for side, box in boxes.items():
            destination = ASSETS / f"{base_name}_{side.lower()}.jpg"
            source.crop(box).save(destination, quality=96)
            with Image.open(destination) as decoded:
                crop_width, crop_height = decoded.size
                decoded.verify()
            view_key = f"{prefix}-{side}"
            views.append({"key": view_key, "label": "正面完整实物照" if side == "FRONT" else "背面完整实物照"})
            images.append({
                "view_key": view_key,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "source_id": f"spink-21001-lot-{lot}",
                "source_page_url": f"https://spink.com/lot/2100100{lot}",
                "source_original_url": f"https://d3ums4016ncdkp.cloudfront.net/auction/large/21001/21001_{lot}_1.jpg",
                "download_status": "cropped_from_source_two-side_composite_and_decoded",
                "license": "Spink auction archive image; local research use",
                "width": crop_width,
                "height": crop_height,
                "sha256": digest(destination),
                "side": side.lower(),
                "crop_box": list(box),
                "raw_composite": source_path.relative_to(ROOT).as_posix(),
                "visual_check": "章体、吊环及绶带完整；两面来自同一拍品合图",
            })
    return views


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    images: list[dict] = []
    medjidie_view = add_full_image(
        1381, "OTT-SPINK21001-1381-FRONT", "medjidie_named_97th_regiment_front.jpg",
        "正面完整实物照", images,
    )
    records = [
        {
            "id": "OTT-SPINK21001-1381",
            "family": "OTT-MEDJ",
            "country_zh": "奥斯曼帝国",
            "name": "梅吉迪耶勋章",
            "original": "Order of the Medjidie / Mecidiye Nişanı",
            "date": "1852年设立；拍品年代待考",
            "variant": "佩章；银质、金质中心及珐琅；背刻“F.A. 97th Regt.”；Spink 21001第1381号拍品",
            "views": [medjidie_view],
            "source_ids": ["spink-21001-lot-1381"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
        {
            "id": "OTT-SPINK21001-1382",
            "family": "OTT-IMTIYAZ-MEDAL",
            "country_zh": "奥斯曼帝国",
            "name": "优异与勇敢奖章",
            "original": "İmtiyaz Madalyası / Loyalty and Bravery Medal",
            "date": "1882年设立；该件授予期约20世纪初",
            "variant": "银质；36毫米；背面具名铭文，授予苏丹名誉侍从A'amr Farooq；完整正背面；Spink 21001第1382号拍品",
            "views": add_pair(1382, "OTT-SPINK21001-1382", "imtiyaz_named_farooq", images),
            "source_ids": ["spink-21001-lot-1382"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
        {
            "id": "OTT-SPINK21001-1384",
            "family": "OTT-YEMEN-1892",
            "country_zh": "奥斯曼帝国",
            "name": "第二次也门战役奖章",
            "original": "Yemen Campaign Medal / Cedid Yemen Madalyası",
            "date": "章面纪年1273/1310（约1892–1893）；Spink归为1892年型",
            "variant": "第一版；双纪年并列；24毫米；完整正背面；Spink 21001第1384号拍品",
            "views": add_pair(1384, "OTT-SPINK21001-1384", "yemen_1892_type1", images),
            "source_ids": ["spink-21001-lot-1384"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
        {
            "id": "OTT-SPINK21001-1385",
            "family": "OTT-YEMEN-1892",
            "country_zh": "奥斯曼帝国",
            "name": "第二次也门战役奖章",
            "original": "Yemen Campaign Medal / Cedid Yemen Madalyası",
            "date": "章面纪年1273/1310（约1892–1893）；Spink归为1892年型",
            "variant": "第二版；双纪年上下排列；24毫米；原装佩戴悬挂；完整正背面；Spink 21001第1385号拍品",
            "views": add_pair(1385, "OTT-SPINK21001-1385", "yemen_1892_type2", images),
            "source_ids": ["spink-21001-lot-1385"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
    ]
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：Spink 21001 土耳其拍品段",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Spink auction 21001, complete Turkey/Ottoman section, lots 1381–1385",
        "processed_lots": [1381, 1382, 1383, 1384, 1385],
        "omitted_as_redundant": {
            "1383": "Kars and Danube front-only group image; both families already have stronger complete front/back coverage",
        },
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} variant rows and {len(images)} complete local images")


if __name__ == "__main__":
    main()
