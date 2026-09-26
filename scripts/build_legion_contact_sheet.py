from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[1]
src = root / "sources/cache/france_samlhoc_legion_honour/images"
out = root / "tmp/france_samlhoc_legion_honour_contact_sheet.jpg"
files = sorted(p for p in src.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
cell_w, cell_h, cols = 320, 360, 4
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(files):
    with Image.open(path) as image:
        image = image.convert("RGB")
        preview = ImageOps.contain(image, (cell_w - 20, cell_h - 55))
    x = (i % cols) * cell_w + (cell_w - preview.width) // 2
    y = (i // cols) * cell_h + 5
    sheet.paste(preview, (x, y))
    draw.text(((i % cols) * cell_w + 8, (i // cols) * cell_h + cell_h - 45), f"{i+1:02d} {path.name[:38]}", fill="black")
out.parent.mkdir(parents=True, exist_ok=True)
sheet.save(out, quality=92)
print(out)
