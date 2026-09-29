"""Publish reviewed Sudan variants from Noble Numismatics archive lots."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/raw/sudan_noble/sale109_lot4550_4248.jpg"
DEST = ROOT / "assets/images/sudan_noble/sale109_lot4550_two_niles_iv.jpg"
VOLUME = ROOT / "data/volumes/sudan_noble_variants.json"
MANIFEST = ROOT / "data/volumes/sudan_noble_variants_manifest.json"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DEST)
    with Image.open(DEST) as image:
        width, height = image.size
        image.verify()
    record_id = "SDN-NOBLE-S109-4550-TWO-NILES-IV"
    view_key = record_id + "-VIEW-1"
    record = {
        "id": record_id,
        "family": "MENA7-ORDER-OF-THE-TWO-NILES",
        "country_zh": "苏丹",
        "name": "两尼罗河勋章",
        "original": "Order of the Two Niles, 4th Class",
        "date": "1961年11月16日设立；2015年拍卖记录",
        "variant": "四等军官级胸章；银质、鎏金及珐琅；55毫米；短绶带；完整实物正面",
        "views": [{"key": view_key, "label": "四等胸章完整正面"}],
        "source_ids": ["noble-sale109-lot4550"],
        "image_kind": "object_photo",
        "html_eligible": True,
        "supersedes_id": "SDN-MB-PENDING-ORDER-OF-THE-TWO-NILES-OFFICER",
    }
    image = {
        "key": view_key,
        "record_id": record_id,
        "view_key": view_key,
        "local_path": DEST.relative_to(ROOT).as_posix(),
        "source_id": "noble-sale109-lot4550",
        "source_page": "https://www.noble.com.au/auctions/lot/?id=298128",
        "source_original_url": "https://www.noble.com.au/catalogue-images/sales/s109/large/4248.jpg",
        "image_kind": "object_photo",
        "width": width,
        "height": height,
        "sha256": hashlib.sha256(DEST.read_bytes()).hexdigest(),
        "visual_check": "complete front, suspension and short ribbon visible; no reverse supplied by source",
        "rights_note": "Noble Numismatics auction archive photograph; retained for offline research catalogue use subject to source terms",
    }
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹：Noble拍卖档案", "records": [record]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "source": "Noble Numismatics Sale 109", "images": [image]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("published Noble Sale 109 lot 4550: Two Niles IV Class")


if __name__ == "__main__":
    main()
