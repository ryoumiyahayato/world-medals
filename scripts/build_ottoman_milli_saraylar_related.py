"""Extract complete Tanzimat medal faces from the official Milli Saraylar book."""
import hashlib
import json
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/books/milli_saraylar_osmanli_saltanatinin_sembolleri.pdf"
RAW_DIR = ROOT / "assets/raw/ottoman_milli_saraylar"
OUT_DIR = ROOT / "assets/images/ottoman_milli_saraylar"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# PDF page 97 / printed page 89, figures 5 and 5-a.
pdf = pdfium.PdfDocument(str(PDF))
full = pdf[96].render(scale=4.0).to_pil().convert("RGB")
raw_page = RAW_DIR / "osmanli_saltanatinin_sembolleri_pdf_page_97.png"
full.save(raw_page)

boxes = {
    "front": (1235, 1285, 1815, 1870),
    "reverse": (1235, 1890, 1815, 2460),
}
images = []
views = []
for side, box in boxes.items():
    destination = OUT_DIR / f"tanzimat_1850_{side}.png"
    crop = full.crop(box)
    crop.save(destination)
    key = f"OTT-MS-TANZIMAT-1850-{side.upper()}"
    views.append({"key": key, "label": "出版物实物照·正面" if side == "front" else "出版物实物照·背面"})
    images.append({
        "view_key": key,
        "local_path": destination.relative_to(ROOT).as_posix(),
        "source_id": "milli-saraylar-osmanli-saltanatinin-sembolleri-fig5",
        "source_page_url": "sources/books/milli_saraylar_osmanli_saltanatinin_sembolleri.pdf#page=97",
        "source_original_url": "sources/books/milli_saraylar_osmanli_saltanatinin_sembolleri.pdf#page=97",
        "source_pdf_page": 97,
        "printed_page": 89,
        "figure": "5" if side == "front" else "5-a",
        "crop_box_ltrb": list(box),
        "image_kind": "published_collection_photo",
        "license": "Milli Saraylar publication; local research use",
        "width": crop.width,
        "height": crop.height,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    })

record = {
    "id": "OTT-MS-REL-TANZIMAT-1850",
    "family": "OTT-REL-TANZIMAT-1850",
    "country_zh": "奥斯曼帝国",
    "name": "坦志麦特改革纪念章",
    "original": "Tanzimat Hatıra Madalyası / Tanzîmât-ı Hayriyye Madalyası",
    "date": "1850年制；1851年发行",
    "variant": "镀金青铜；100毫米；400.80克；Laurent-Joseph Hart制；完整正背面出版物实物照",
    "views": views,
    "source_ids": ["milli-saraylar-osmanli-saltanatinin-sembolleri-fig5", "salt-ANUDM00080", "tdv-madalya"],
    "image_kind": "published_collection_photo",
    "html_eligible": True,
}

(ROOT / "data/volumes/ottoman_milli_saraylar_related.json").write_text(
    json.dumps({"as_of": "2026-09-27", "volume": "奥斯曼帝国相关附编：Milli Saraylar", "records": [record]}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/ottoman_milli_saraylar_related_manifest.json").write_text(
    json.dumps({
        "as_of": "2026-09-27",
        "source_pdf": PDF.relative_to(ROOT).as_posix(),
        "source_pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "raw_page": raw_page.relative_to(ROOT).as_posix(),
        "images": images,
        "unpictured_candidates": [],
        "visual_check": "figures 5 and 5-a show complete circular front and reverse faces; no neighbouring object enters either crop",
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"record": record["id"], "views": len(views), "raw_page": str(raw_page.relative_to(ROOT))}, ensure_ascii=False))
