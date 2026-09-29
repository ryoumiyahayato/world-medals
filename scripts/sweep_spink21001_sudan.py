"""Sweep the complete Sudan lot segment (1326-1337) of Spink auction 21001."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/raw/sudan_spink21001"
RAW = ROOT / "data/raw_candidates/spink21001_sudan.jsonl"
REPORT = ROOT / "data/source_sweeps/spink21001_sudan_2026-09-27.json"
UA = "Mozilla/5.0 (compatible; world-medals research cache/1.0)"

LOTS = {
    1326: "Order of the Two Niles, Second Class set, Spink & Son, 60 mm badge and 92 mm star",
    1327: "Order of the Two Niles, Second Class set, Spink & Son, 94 mm badge and star",
    1328: "Order of the Two Niles, Second Class set, Spink & Son, cased",
    1329: "Order of the Two Niles, neck badge, 47 mm",
    1330: "Order of the Two Niles, badge, 45 mm",
    1331: "Order of the Republic, First Class star, Spink & Son, 98 mm",
    1332: "Order of the Republic, neck badge with rhinoceros suspension, 88 x 60 mm",
    1333: "Order of Civil Accomplishment, 96 mm",
    1334: "Order of Civil Accomplishment, large breast badge, Spink, 96 x 96 mm",
    1335: "Order of Regional Government, badge, 64 mm",
    1336: "Order of Production and Order of Political Accomplishment group",
    1337: "Order of the Alliance, single class, 127 x 97 mm",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    rows = []
    for lot, title in LOTS.items():
        image_url = f"https://d3ums4016ncdkp.cloudfront.net/auction/large/21001/21001_{lot}_1.jpg"
        target = DEST / f"21001_{lot}_1.jpg"
        status = "DOWNLOAD_FAILED"
        error = None
        width = height = None
        if not target.exists():
            try:
                request = urllib.request.Request(image_url, headers={"User-Agent": UA})
                with urllib.request.urlopen(request, timeout=45) as response:
                    target.write_bytes(response.read())
                time.sleep(1)
            except Exception as exc:
                target.unlink(missing_ok=True)
                error = str(exc)
        if target.exists():
            try:
                with Image.open(target) as image:
                    width, height = image.size
                    image.verify()
                status = "ORIGINAL_IMAGE_CACHED"
            except Exception as exc:
                error = f"decode failed: {exc}"
                target.unlink(missing_ok=True)
        rows.append({
            "source_id": f"spink-21001-sudan-{lot}",
            "source_system": "Spink auction 21001 Sudan segment",
            "lot": lot,
            "page_title": title,
            "page_url": f"https://spink.com/lot/2100100{lot}",
            "catalogue_pdf": "sources/books/spink/21001_lot_list.pdf",
            "catalogue_printed_page": 325 if lot <= 1329 else 326,
            "image_original_url": image_url,
            "local_raw_image": target.relative_to(ROOT).as_posix() if target.exists() else None,
            "image_dimensions": [width, height] if width else None,
            "image_sha256": digest(target) if target.exists() else None,
            "status": status,
            "error": error,
            "access_date": str(date.today()),
        })
    RAW.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    successes = [row for row in rows if row["status"] == "ORIGINAL_IMAGE_CACHED"]
    REPORT.write_text(json.dumps({
        "as_of": str(date.today()),
        "source_id": "spink-21001-sudan-section",
        "source_title": "Spink 21001, complete Sudan section",
        "source_url": "https://storage.spink.com/source/Docs/21001_Lot_List.pdf",
        "processed_scope": "Printed pages 325-326, lots 1326-1337 inclusive",
        "status": "section_complete",
        "lots_processed": list(LOTS),
        "candidate_rows": len(rows),
        "original_images_downloaded_and_decoded": len(successes),
        "failed_image_lots": [row["lot"] for row in rows if row["status"] != "ORIGINAL_IMAGE_CACHED"],
        "candidate_file": RAW.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Spink 21001 Sudan: {len(rows)} lots processed, {len(successes)} original images cached")


if __name__ == "__main__":
    main()
