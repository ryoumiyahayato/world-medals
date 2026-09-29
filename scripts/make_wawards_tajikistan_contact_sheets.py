from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "assets/raw/wawards_tajikistan"
OUTPUT = ROOT / "sources/pages/wawards_tajikistan/contact_sheets"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in INPUT.iterdir() if p.is_file())
    font = ImageFont.load_default()
    cols, rows = 4, 5
    cell_w, cell_h = 320, 360
    for sheet_no, offset in enumerate(range(0, len(paths), cols * rows), 1):
        batch = paths[offset : offset + cols * rows]
        sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(batch):
            with Image.open(path) as source:
                image = source.convert("RGB")
            image.thumbnail((cell_w - 24, cell_h - 58), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + (cell_w - image.width) // 2
            y = (index // cols) * cell_h + 8
            sheet.paste(image, (x, y))
            draw.text(((index % cols) * cell_w + 8, (index // cols) * cell_h + cell_h - 44), path.name, fill="black", font=font)
        sheet.save(OUTPUT / f"all_{sheet_no:02d}.jpg", quality=90)
    print(f"images={len(paths)} sheets={(len(paths) + cols * rows - 1) // (cols * rows)}")


if __name__ == "__main__":
    main()
