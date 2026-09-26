from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[1]
src = root / "tmp/pdfs/spain_boe2025_extracted"
out_dir = root / "tmp/pdfs/spain_boe2025_contact_sheets"
out_dir.mkdir(parents=True, exist_ok=True)
files = sorted(src.glob("*.png"))
cell_w, cell_h, cols, per_sheet = 300, 390, 4, 24
for sheet_no, start in enumerate(range(0, len(files), per_sheet), 1):
    batch = files[start : start + per_sheet]
    rows = (len(batch) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(batch):
        with Image.open(path) as image:
            preview = ImageOps.contain(image.convert("RGB"), (cell_w - 18, cell_h - 58))
        x0 = (i % cols) * cell_w
        y0 = (i // cols) * cell_h
        sheet.paste(preview, (x0 + (cell_w - preview.width) // 2, y0 + 5))
        draw.text((x0 + 7, y0 + cell_h - 48), path.stem, fill="black")
    target = out_dir / f"sheet_{sheet_no:02d}.jpg"
    sheet.save(target, quality=92)
    print(target)
