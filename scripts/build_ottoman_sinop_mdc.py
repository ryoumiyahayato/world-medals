"""Register the verified 1853 Sinope medal obverse/reverse from MDC lot 1439."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "data/volumes/ottoman_sinop_mdc.json"
MANIFEST = ROOT / "data/volumes/ottoman_sinop_mdc_manifest.json"
FILES = [
    ("FRONT", "正面完整实物图", ROOT / "assets/images/ottoman_sinop_mdc/sinop_lot1439_front.jpg", "https://bidkit.ams3.digitaloceanspaces.com/167/imgMed/10/1439a00.jpg"),
    ("BACK", "背面完整实物图", ROOT / "assets/images/ottoman_sinop_mdc/sinop_lot1439.jpg", "https://bidkit.ams3.digitaloceanspaces.com/167/imgMed/10/1439r00.jpg"),
]


def main() -> None:
    views, images = [], []
    for side, label, path, url in FILES:
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        key = f"OTT-MDC-SINOP-1853-{side}"
        views.append({"key": key, "label": label})
        images.append({
            "view_key": key,
            "local_path": path.relative_to(ROOT).as_posix(),
            "source_id": "mdc-auction10-lot1439",
            "download_status": "downloaded_and_decoded",
            "source_page_url": "https://mdc.bidinside.com/de/lot/12721/turquie-abdlmecid-ier-ou-abdul-mejid-/",
            "source_original_url": url,
            "license": "MDC/BidKit auction photograph; local research use only",
            "width": width,
            "height": height,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "side": side.lower(),
        })
    record = {
        "id": "OTT-MDC-SINOP-1853-BRONZE",
        "family": "OTT-SINOP-1853",
        "country_zh": "奥斯曼帝国",
        "name": "锡诺普战役纪念奖章",
        "original": "Sinop Muharebesi Hatıra Madalyası / Médaille de la bataille de Sinope",
        "date": "1853年制；1854年实际设立",
        "variant": "布鲁塞尔Hart制；青铜；68毫米；正背完整；MDC拍卖第10场拍品1439",
        "views": views,
        "source_ids": ["mdc-auction10-lot1439", "salt-anudm00083", "tdv-madalya"],
        "image_kind": "object_photo",
        "html_eligible": True,
    }
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：锡诺普奖章来源差集",
        "records": [record],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "MDC Monnaies de Collection, Auction 10, lot 1439",
        "source_page": "https://mdc.bidinside.com/de/lot/12721/turquie-abdlmecid-ier-ou-abdul-mejid-/",
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote 1 record and 2 complete object photographs")


if __name__ == "__main__":
    main()
