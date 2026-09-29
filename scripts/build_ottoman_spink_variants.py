"""Build notable Ottoman order variants from individually verified Spink lots."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "raw" / "ottoman_spink_variants"
ASSETS = ROOT / "assets" / "images" / "ottoman_spink_variants"
VOLUME = ROOT / "data" / "volumes" / "ottoman_spink_variants.json"
MANIFEST = ROOT / "data" / "volumes" / "ottoman_spink_variants_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    images: list[dict] = []

    diamond_raw = RAW / "19002_882_1.jpg"
    diamond_views = []
    with Image.open(diamond_raw) as source:
        width, height = source.size
        boxes = {"FRONT": (0, 0, width // 2, height), "BACK": (width // 2, 0, width, height)}
        for side, box in boxes.items():
            destination = ASSETS / f"medjidie_diamond_star_{side.lower()}.jpg"
            source.crop(box).save(destination, quality=96)
            with Image.open(destination) as decoded:
                crop_width, crop_height = decoded.size
                decoded.verify()
            key = f"OTT-SPINK19002-882-{side}"
            diamond_views.append({"key": key, "label": "正面完整实物照" if side == "FRONT" else "背面完整实物照"})
            images.append({
                "view_key": key,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "source_id": "spink-19002-lot-882",
                "source_page_url": "https://spink.com/lot/19002000882",
                "source_original_url": "https://d3ums4016ncdkp.cloudfront.net/auction/large/19002/19002_882_1.jpg",
                "download_status": "cropped_from_source_two-side_composite_and_decoded",
                "license": "Spink auction archive image; local research use",
                "width": crop_width,
                "height": crop_height,
                "sha256": digest(destination),
                "side": side.lower(),
                "crop_box": list(box),
                "raw_composite": diamond_raw.relative_to(ROOT).as_posix(),
                "visual_check": "星章轮廓及全部镶钻结构完整；两面来自同一拍品合图",
            })

    osmanieh_raw = RAW / "20003_1550_1.jpg"
    osmanieh_destination = ASSETS / "osmanieh_first_class_set.jpg"
    shutil.copy2(osmanieh_raw, osmanieh_destination)
    with Image.open(osmanieh_destination) as decoded:
        width, height = decoded.size
        decoded.verify()
    images.append({
        "view_key": "OTT-SPINK20003-1550-SET",
        "local_path": osmanieh_destination.relative_to(ROOT).as_posix(),
        "source_id": "spink-20003-lot-1550",
        "source_page_url": "https://spink.com/lot/20003001550",
        "source_original_url": "https://d3ums4016ncdkp.cloudfront.net/auction/large/20003/20003_1550_1.jpg",
        "download_status": "downloaded_original_and_decoded",
        "license": "Spink auction archive image; local research use",
        "width": width,
        "height": height,
        "sha256": digest(osmanieh_destination),
        "side": "front_set",
        "visual_check": "一等全套星章、绶章、悬挂结构及大绶均完整入画",
    })

    records = [
        {
            "id": "OTT-SPINK19002-882",
            "family": "OTT-MEDJ",
            "country_zh": "奥斯曼帝国",
            "name": "梅吉迪耶勋章",
            "original": "Order of the Medjidie",
            "date": "1852年设立；该件制作期待考",
            "variant": "镶钻胸星；99毫米；银、鎏银与金质背托；约镶553颗旧式切割及玫瑰切割钻石；完整正背面；Spink 19002第882号拍品",
            "views": diamond_views,
            "source_ids": ["spink-19002-lot-882"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
        {
            "id": "OTT-SPINK20003-1550",
            "family": "OTT-OSM",
            "country_zh": "奥斯曼帝国",
            "name": "奥斯曼勋章",
            "original": "Order of Osmanieh / Osmanlı Nişanı",
            "date": "1862年设立；该件制作期待考",
            "variant": "一等全套：大绶章82×65毫米、胸星92毫米；银、鎏银与珐琅；完整套装实物照；Spink 20003第1550号拍品",
            "views": [{"key": "OTT-SPINK20003-1550-SET", "label": "一等全套完整实物照"}],
            "source_ids": ["spink-20003-lot-1550"],
            "image_kind": "object_photo",
            "html_eligible": True,
        },
    ]
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：Spink重要勋章版型补充",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Spink verified individual lot pages",
        "processed_lots": ["19002-882", "20003-1550"],
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} notable variant rows and {len(images)} complete local images")


if __name__ == "__main__":
    main()
