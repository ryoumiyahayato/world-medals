"""Build the 1854 Hart Triple Alliance commemorative medal as related material."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "raw" / "ottoman_cng_triple_alliance" / "3970802.jpg"
ASSETS = ROOT / "assets" / "images" / "ottoman_cng_triple_alliance"
VOLUME = ROOT / "data" / "volumes" / "ottoman_cng_triple_alliance_related.json"
MANIFEST = ROOT / "data" / "volumes" / "ottoman_cng_triple_alliance_related_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with Image.open(RAW) as source:
        width, height = source.size
        # The CNG original is a purpose-made two-side composite with a narrow
        # white gutter. Each crop retains the complete circular medal edge.
        boxes = {
            "FRONT": (0, 0, width // 2, height),
            "BACK": (width // 2, 0, width, height),
        }
        views, images = [], []
        for side, box in boxes.items():
            destination = ASSETS / f"hart_triple_alliance_1854_{side.lower()}.jpg"
            source.crop(box).save(destination, quality=96)
            with Image.open(destination) as cropped:
                crop_width, crop_height = cropped.size
                cropped.verify()
            key = f"OTT-CNG-HART-1854-{side}"
            views.append({"key": key, "label": "正面完整实物照" if side == "FRONT" else "背面完整实物照"})
            images.append({
                "view_key": key,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "source_id": "cng-eauction-397-lot-802",
                "download_status": "cropped_from_source_two-side_composite_and_decoded",
                "source_page_url": "https://www.cngcoins.com/Coin.aspx?CoinID=336564",
                "source_original_url": "https://www.cngcoins.com/photos/enlarged/3970802.jpg",
                "license": "CNG auction archive image; local research use",
                "width": crop_width,
                "height": crop_height,
                "sha256": digest(destination),
                "side": side.lower(),
                "crop_box": list(box),
                "raw_composite": RAW.relative_to(ROOT).as_posix(),
                "visual_check": "完整圆章边缘均保留；两面来自CNG同一拍品合图",
            })
    record = {
        "id": "OTT-CNG-HART-TRIPLE-ALLIANCE-1854",
        "family": "OTT-TRIPLE-ALLIANCE",
        "country_zh": "奥斯曼帝国",
        "name": "三国联盟与克里米亚战争胜利纪念章（黑海与多瑙河纪念章）",
        "original": "The Triple Alliance and Victory in the Crimean War / La Mer Noire et le Danube seront libres",
        "date": "1854",
        "variant": "L. Hart制；铜质；67毫米；207.7克；Dogan 6539；CNG 397拍卖第802号；完整正背面",
        "views": views,
        "source_ids": ["cng-eauction-397-lot-802", "tdv-madalya"],
        "image_kind": "object_photo",
        "html_eligible": True,
    }
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国相关纪念章：1854年三国联盟与克里米亚战争胜利",
        "records": [record],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Classical Numismatic Group, eAuction 397, lot 802",
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote 1 related record and 2 complete object-side crops")


if __name__ == "__main__":
    main()
