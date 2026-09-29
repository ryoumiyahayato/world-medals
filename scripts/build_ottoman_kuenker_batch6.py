"""Build the final formal-award delta from Kuenker Auction 299, pages 233-238."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "tmp/pdfs/kuenker299_embedded"
ASSETS = ROOT / "assets/images/ottoman_kuenker299_batch6"
VOLUME = ROOT / "data/volumes/ottoman_kuenker299_batch6.json"
MANIFEST = ROOT / "data/volumes/ottoman_kuenker299_batch6_manifest.json"

LOTS = [
    (7382, 233, 9, 8, "OTT-CANAKKALE-AGRICULTURE-1918", "恰纳卡莱农业展览奖章", "Çanakkale Zirâat Sergisi Madalyası", "1918", "青铜级；重度佩戴；无环无绶带"),
    (7406, 238, 5, 4, "OTT-WILHELM-II-VISIT-1917", "德皇威廉二世访问君士坦丁堡纪念章", "Alman Mülâkat Madalyası", "1917", "官方银级；64.8毫米；非佩戴式；边缘铭文"),
]


def extracted(page: int, index: int) -> Path:
    matches = sorted((EXTRACTED / f"page_{page:03d}").glob(f"{index:02d}_*"))
    if len(matches) != 1:
        raise RuntimeError((page, index, matches))
    return matches[0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    records, images = [], []
    for lot, page, front_index, back_index, family, name, original, date, variant in LOTS:
        record_id = f"OK299-{lot}"
        views = []
        for side, label, index in (
            ("FRONT", "正面完整实物图", front_index),
            ("BACK", "背面完整实物图", back_index),
        ):
            src = extracted(page, index)
            dst = ASSETS / f"lot_{lot}_{side.lower()}{src.suffix.lower()}"
            shutil.copy2(src, dst)
            with Image.open(dst) as image:
                width, height = image.size
                image.verify()
            key = f"{record_id}-{side}"
            views.append({"key": key, "label": label})
            images.append({
                "view_key": key,
                "local_path": dst.relative_to(ROOT).as_posix(),
                "source_id": f"kuenker299-lot-{lot}",
                "download_status": "extracted_and_decoded",
                "source_page_url": f"https://kuenker.s3.eu-central-1.amazonaws.com/media/31/1d/22/1736866624/299_kuenker-katalog_web.pdf#page={page}",
                "source_original_url": f"embedded image in Kuenker Auction 299 PDF, page {page}, image {index}",
                "license": "Kuenker Auction 299 catalogue photograph; local research use only",
                "width": width,
                "height": height,
                "sha256": digest(dst),
                "pdf_page": page,
                "lot": lot,
                "side": side.lower(),
            })
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": "奥斯曼帝国",
            "name": name,
            "original": original,
            "date": date,
            "variant": f"{variant}；Künker 299图录实物照 · 2017",
            "views": views,
            "source_ids": [f"kuenker299-lot-{lot}"],
            "image_kind": "object_photo",
            "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：Künker 299专题拍卖差集第六批",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Künker Auction 299, The Ottoman Collection Part 2",
        "source_pdf": "sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf",
        "pages_processed": sorted({item[1] for item in LOTS}),
        "lots_ingested": [item[0] for item in LOTS],
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} records and {len(images)} images")


if __name__ == "__main__":
    main()
