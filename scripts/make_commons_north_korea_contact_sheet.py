"""Build a contact sheet from currently cached Commons North Korea rasters."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ROWS = [json.loads(line) for line in (ROOT / "data/raw_candidates/commons_north_korea.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
ITEMS = [row for row in ROWS if row.get("local_raw_image")]
OUT = ROOT / "sources/pages/commons_north_korea/contact_sheets/cached_01.jpg"

columns, cell_w, cell_h = 3, 420, 340
rows = (len(ITEMS) + columns - 1) // columns
canvas = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
draw, font = ImageDraw.Draw(canvas), ImageFont.load_default()
for n, item in enumerate(ITEMS):
    x, y = (n % columns) * cell_w, (n // columns) * cell_h
    with Image.open(ROOT / item["local_raw_image"]) as im:
        im = im.convert("RGB"); im.thumbnail((cell_w - 20, 260))
        canvas.paste(im, (x + (cell_w - im.width) // 2, y + 5 + (260 - im.height) // 2))
    title = item["file_title"].removeprefix("File:")
    draw.multiline_text((x + 6, y + 270), "\n".join(textwrap.wrap(title, width=54)[:4]), fill="black", font=font, spacing=2)
    draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#999999")
OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, quality=88)
print(OUT)
