"""Render selected ITU catalogue pages and assemble lightweight contact sheets."""

from pathlib import Path
import argparse

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "sources" / "books" / "itu_ottoman_medals_catalogue.pdf"
OUT_DIR = ROOT / "tmp" / "pdfs" / "itu_scan"


def render_page(pdf: pdfium.PdfDocument, page_no: int, scale: float) -> Path:
    destination = OUT_DIR / f"page-{page_no:03d}.jpg"
    if not destination.exists():
        bitmap = pdf[page_no - 1].render(scale=scale)
        bitmap.to_pil().convert("RGB").save(destination, quality=88)
    return destination


def make_contact(paths: list[Path], columns: int = 5) -> Path:
    thumbs = []
    for path in paths:
        with Image.open(path) as image:
            preview = image.convert("RGB")
            preview.thumbnail((380, 520))
            thumbs.append((path, preview.copy()))
    cell_w, cell_h = 400, 560
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (path, preview) in enumerate(thumbs):
        x = (index % columns) * cell_w
        y = (index // columns) * cell_h
        draw.text((x + 6, y + 5), path.stem, fill="black")
        sheet.paste(preview, (x + (cell_w - preview.width) // 2, y + 30))
    output = OUT_DIR / f"contact_{paths[0].stem}_{paths[-1].stem}.jpg"
    sheet.save(output, quality=90)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("--chunk", type=int, default=20)
    parser.add_argument("--scale", type=float, default=1.25)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(PDF_PATH))
    pages = [render_page(pdf, number, args.scale) for number in range(args.start, args.end + 1)]
    for offset in range(0, len(pages), args.chunk):
        print(make_contact(pages[offset : offset + args.chunk]))


if __name__ == "__main__":
    main()
