"""Extract the Ferahi Medal front/reverse from ITU catalogue plate 1.A-1.B."""
import hashlib
import json
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/books/itu_ottoman_medals_catalogue.pdf"
RAW_DIR = ROOT / "assets/raw/ottoman_itu_ferahi"
OUT_DIR = ROOT / "assets/images/ottoman_itu_ferahi"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# PDF page 29 is printed catalogue page 20 and contains figure 1.A-1.B.
pdf = pdfium.PdfDocument(str(PDF))
page = pdf[28]
full = page.render(scale=4.0).to_pil().convert("RGB")
raw_page = RAW_DIR / "itu_catalogue_pdf_page_29.png"
full.save(raw_page)

# Boxes preserve each complete rectangular medal face, including both loops.
boxes = {
    "front": (360, 250, 1140, 825),
    "reverse": (1160, 245, 1940, 825),
}
images = []
views = []
for side, box in boxes.items():
    destination = OUT_DIR / f"ferahi_1730_{side}.png"
    crop = full.crop(box)
    crop.save(destination)
    key = f"OTT-ITU-FERAHI-1730-{side.upper()}"
    views.append({"key": key, "label": f"历史图录插图·正面" if side == "front" else "历史图录插图·背面"})
    images.append({
        "view_key": key,
        "local_path": destination.relative_to(ROOT).as_posix(),
        "source_id": "itu-ottoman-medals-catalogue-plate-1",
        "source_page_url": "sources/books/itu_ottoman_medals_catalogue.pdf#page=29",
        "source_original_url": "sources/books/itu_ottoman_medals_catalogue.pdf#page=29",
        "source_pdf_page": 29,
        "printed_page": 20,
        "figure": "Şekil 1.A-1.B",
        "crop_box_ltrb": list(box),
        "image_kind": "historical_catalogue_illustration",
        "license": "ITU thesis/catalogue scan; local research use",
        "width": crop.width,
        "height": crop.height,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    })

record = {
    "id": "OTT-ITU-FERAHI-1730",
    "family": "OTT-FERAHI",
    "country_zh": "奥斯曼帝国",
    "name": "费拉希奖章",
    "original": "Ferahî Madalyası",
    "date": "1730（回历1143）",
    "variant": "金质；37.98克；44×65毫米；馆藏号18687；历史图录插图·图1A／1B",
    "views": views,
    "source_ids": ["itu-ottoman-medals-catalogue-plate-1", "tdv-madalya", "nigde-academic-ottoman"],
    "image_kind": "historical_catalogue_illustration",
    "html_eligible": True,
}

(ROOT / "data/volumes/ottoman_itu_ferahi.json").write_text(
    json.dumps({"as_of": "2026-09-27", "volume": "奥斯曼帝国：费拉希奖章", "records": [record]}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/ottoman_itu_ferahi_manifest.json").write_text(
    json.dumps({
        "as_of": "2026-09-27",
        "source_pdf": PDF.relative_to(ROOT).as_posix(),
        "source_pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "raw_page": raw_page.relative_to(ROOT).as_posix(),
        "images": images,
        "unpictured_candidates": [],
        "visual_check": "figure 1.A-1.B contains complete front and reverse rectangular medal faces; both suspension loops retained",
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"record": record["id"], "views": len(views), "raw_page": str(raw_page.relative_to(ROOT))}, ensure_ascii=False))
