from __future__ import annotations

from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf"
OUT = ROOT / "tmp/pdfs/spain_boe2025_extracted"
PAGES = list(range(126, 151)) + list(range(201, 220)) + [225, 233, 235, 236, 237]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(PDF)
    count = 0
    for page_number in PAGES:
        page = reader.pages[page_number - 1]
        for image_index, image_file in enumerate(page.images):
            image = image_file.image
            if image.mode == "CMYK":
                image = image.convert("RGB")
            elif image.mode not in {"RGB", "RGBA", "L"}:
                image = image.convert("RGBA")
            target = OUT / f"page_{page_number:03d}_image_{image_index:02d}.png"
            image.save(target, optimize=True)
            count += 1
    print(f"extracted {count} images to {OUT}")


if __name__ == "__main__":
    main()
