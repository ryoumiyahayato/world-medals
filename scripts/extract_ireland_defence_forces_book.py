from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/books/ireland_defence_forces_medals_2010.pdf"
OUT = ROOT / "sources/pages/ireland_defence_forces_medals_2010"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(PDF)
    pages: list[dict[str, object]] = []
    chunks: list[str] = []
    for number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        chunks.append(f"\n\n===== PDF PAGE {number} =====\n{text}")
        pages.append(
            {
                "pdf_page": number,
                "text": text,
                "embedded_image_count": len(list(page.images)),
            }
        )
    (OUT / "full_text.txt").write_text("".join(chunks), encoding="utf-8")
    (OUT / "page_text.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"pages": len(pages), "output": str(OUT)}, ensure_ascii=False))


def make_contact_sheets() -> None:
    image_paths = sorted(
        OUT.glob("page-*.jpg"), key=lambda path: int(path.stem.split("-")[-1])
    )
    sheet_dir = ROOT / "data/image_harvest/ireland_defence_forces_medals_2010"
    sheet_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    thumb_w, thumb_h, label_h = 260, 368, 20
    for offset in range(0, len(image_paths), 12):
        batch = image_paths[offset : offset + 12]
        sheet = Image.new("RGB", (thumb_w * 4, (thumb_h + label_h) * 3), "white")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(batch):
            page_number = int(path.stem.split("-")[-1])
            image = Image.open(path).convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8), Image.Resampling.LANCZOS)
            col, row = index % 4, index // 4
            x = col * thumb_w + (thumb_w - image.width) // 2
            y = row * (thumb_h + label_h) + label_h
            sheet.paste(image, (x, y))
            draw.text((col * thumb_w + 6, row * (thumb_h + label_h) + 4), f"PDF p.{page_number}", fill="black", font=font)
        first = int(batch[0].stem.split("-")[-1])
        last = int(batch[-1].stem.split("-")[-1])
        sheet.save(sheet_dir / f"pages-{first:03d}-{last:03d}.jpg", quality=90)
    print(json.dumps({"contact_sheets": (len(image_paths) + 11) // 12}, ensure_ascii=False))


if __name__ == "__main__":
    main()
    make_contact_sheets()
