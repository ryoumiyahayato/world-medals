"""Register AlifArt lot 76 as a documented Tasvir-i Hümayun object photograph."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "assets/raw/ottoman_tasvir_humayun"
IMAGE_DIR = ROOT / "assets/images/ottoman_tasvir_humayun"
ORIGINAL_DIR = ROOT / "originals/ottoman_tasvir_humayun"
SOURCE_FILE = RAW_DIR / "alifart_2022_lot76_1.jpg"
IMAGE_FILE = IMAGE_DIR / "alifart_2022_lot76_front.jpg"
ORIGINAL_FILE = ORIGINAL_DIR / "alifart_2022_lot76_front.jpg"
VOLUME = ROOT / "data/volumes/ottoman_tasvir_humayun.json"
MANIFEST = ROOT / "data/volumes/ottoman_tasvir_humayun_manifest.json"
SOURCE_PAGE = "https://www.alifart.com/tasvr-humayun-280571/"
SOURCE_IMAGE = "https://www.alifart.com/pictures/product/3255-76.jpg"


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_FILE, IMAGE_FILE)
    shutil.copy2(SOURCE_FILE, ORIGINAL_FILE)
    with Image.open(IMAGE_FILE) as image:
        width, height = image.size
        image.verify()
    view_key = "OTT-ALIFART-TASVIR-HUMAYUN-MAHMUD-II-FRONT"
    record = {
        "id": "OTT-ALIFART-TASVIR-HUMAYUN-MAHMUD-II",
        "family": "OTT-TASVIR-HUMAYUN",
        "country_zh": "奥斯曼帝国",
        "name": "御容勋章",
        "original": "Tasvir-i Hümâyûn Nişanı / Order of the Imperial Portrait",
        "date": "马哈茂德二世时期，约1832年设立；本件19世纪",
        "variant": "马哈茂德二世御容；象牙油彩珐琅；金银及约4克拉玫瑰式钻石框；框为后配时期风格；8×7厘米；AlifArt 2022年第76号；完整正面低清参考",
        "views": [{"key": view_key, "label": "正面完整实物图"}],
        "source_ids": ["alifart-2022-12-17-lot76", "medalbook-ottoman-f77211854f5ca905"],
        "image_kind": "object_photo",
        "html_eligible": True,
    }
    image_entry = {
        "view_key": view_key,
        "local_path": IMAGE_FILE.relative_to(ROOT).as_posix(),
        "original_local_path": ORIGINAL_FILE.relative_to(ROOT).as_posix(),
        "source_id": "alifart-2022-12-17-lot76",
        "download_status": "downloaded_and_decoded",
        "source_page_url": SOURCE_PAGE,
        "source_original_url": SOURCE_IMAGE,
        "license": "AlifArt auction photograph; rights reserved; local research use only",
        "width": width,
        "height": height,
        "sha256": hashlib.sha256(IMAGE_FILE.read_bytes()).hexdigest(),
        "side": "front",
    }
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：御容勋章来源差集",
        "records": [record],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "AlifArt, 17 December 2022 auction, lot 76",
        "source_page": SOURCE_PAGE,
        "images": [image_entry],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote 1 record and 1 complete object photograph ({width}x{height})")


if __name__ == "__main__":
    main()
