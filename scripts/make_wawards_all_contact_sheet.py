"""Make a review sheet of every image in a Wawards raw candidate file."""
import json
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
scope, output = sys.argv[1], sys.argv[2]
rows = [json.loads(x) for x in (ROOT / f"data/raw_candidates/wawards_{scope}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
cols, cw, ch = 6, 260, 250
items = []
for row in rows:
    for n, item in enumerate(row.get("original_images", []), 1):
        items.append((row["page_title"], n, ROOT / item["local_path"]))
canvas = Image.new("RGB", (cols * cw, max(1, (len(items) + cols - 1) // cols) * ch), "white")
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
for index, (title, n, path) in enumerate(items):
    x, y = (index % cols) * cw, (index // cols) * ch
    with Image.open(path) as source:
        image = source.convert("RGB")
    image.thumbnail((cw - 12, 198))
    canvas.paste(image, (x + (cw - image.width) // 2, y + 4 + (198 - image.height) // 2))
    label = f"{index+1:03d} {n}: {title}"
    draw.multiline_text((x + 4, y + 204), "\n".join(textwrap.wrap(label, 35)[:2]), fill="black", font=font, spacing=2)
    draw.rectangle((x, y, x + cw - 1, y + ch - 1), outline="#999")
out = ROOT / output
out.parent.mkdir(parents=True, exist_ok=True)
canvas.save(out, quality=86)
print(out)
