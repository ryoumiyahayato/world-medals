"""Crop the complete Tayyare Medal obverse/reverse from ITU catalogue plate 117."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_PAGE = ROOT / "assets/raw/ottoman_itu_tayyare/page_133.png"
ASSETS = ROOT / "assets/images/ottoman_itu_tayyare"
VOLUME = ROOT / "data/volumes/ottoman_itu_tayyare.json"
MANIFEST = ROOT / "data/volumes/ottoman_itu_tayyare_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with Image.open(RAW_PAGE) as page:
        width, height = page.size
        boxes = {
            "FRONT": (round(width * .195), round(height * .705), round(width * .462), round(height * .900)),
            "BACK": (round(width * .475), round(height * .705), round(width * .790), round(height * .900)),
        }
        images, views = [], []
        for side, box in boxes.items():
            dst = ASSETS / f"tayyare_silver_{side.lower()}.png"
            page.crop(box).save(dst, optimize=True)
            with Image.open(dst) as cropped:
                crop_width, crop_height = cropped.size
                cropped.verify()
            key = f"OTT-ITU-TAYYARE-SILVER-{side}"
            views.append({"key": key, "label": "正面历史图录插图" if side == "FRONT" else "背面历史图录插图"})
            images.append({
                "view_key": key,
                "local_path": dst.relative_to(ROOT).as_posix(),
                "source_id": "itu-ottoman-medals-catalogue-plate-117",
                "download_status": "cropped_from_decoded_300dpi_page",
                "source_page_url": "https://polen.itu.edu.tr/bitstreams/eead0879-ff92-4fb0-a8e6-c92181d5aa65/download#page=133",
                "source_original_url": "sources/books/itu_ottoman_medals_catalogue.pdf#page=133",
                "license": "Istanbul Technical University repository scan; local research use; preserve source page",
                "width": crop_width,
                "height": crop_height,
                "sha256": digest(dst),
                "pdf_page": 133,
                "printed_page": 124,
                "plate": "Şekil 117.A-117.B",
                "crop_box": list(box),
                "raw_page": RAW_PAGE.relative_to(ROOT).as_posix(),
                "side": side.lower(),
            })
    record = {
        "id": "OTT-ITU-TAYYARE-SILVER",
        "family": "OTT-AVIATION-1914",
        "country_zh": "奥斯曼帝国",
        "name": "航空奖章（伊斯坦布尔—开罗飞行奖章）",
        "original": "Tayyare Madalyası / İstanbul Kahire Hava Seyahati Madalyası",
        "date": "1914；穆罕默德五世时期",
        "variant": "银质；30毫米；馆藏号18899；历史图录插图 · 图版117",
        "views": views,
        "source_ids": ["itu-ottoman-medals-catalogue-plate-117", "tdv-madalya"],
        "image_kind": "historical_catalogue_illustration",
        "html_eligible": True,
    }
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：伊斯坦布尔技术大学馆藏目录差集",
        "records": [record],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "ITU collection catalogue, catalogue no. 123, plate 117.A-117.B",
        "source_pdf": "sources/books/itu_ottoman_medals_catalogue.pdf",
        "source_page_preserved": RAW_PAGE.relative_to(ROOT).as_posix(),
        "pages_processed": [133],
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote 1 record and 2 historical-catalogue image crops")


if __name__ == "__main__":
    main()
