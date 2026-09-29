from __future__ import annotations

import json
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/source_sweeps/medalbook_thailand_images_2026-09-27.json"
OUT = ROOT / "sources/pages/medalbook_thailand/contact_sheets"


def make_sheet(items: list[dict], name: str) -> None:
    columns, cell_w, cell_h = 4, 330, 300
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw, font = ImageDraw.Draw(canvas), ImageFont.load_default()
    for n, item in enumerate(items):
        x, y = (n % columns) * cell_w, (n // columns) * cell_h
        with Image.open(ROOT / item["local_path"]) as im:
            im = im.convert("RGB")
            im.thumbnail((cell_w - 20, 225))
            canvas.paste(im, (x + (cell_w - im.width) // 2, y + 5 + (225 - im.height) // 2))
        title = f'{item["record_index"]:03d}/{item["image_index"]:02d} {item["title"]}'
        draw.multiline_text((x + 6, y + 235), "\n".join(textwrap.wrap(title, width=43)[:4]), fill="black", font=font, spacing=2)
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#999999")
    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT / name, quality=88)


def main() -> None:
    items = [
        item for item in json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]
        if item.get("status") == "downloaded" and item.get("local_path")
    ]
    for offset in range(0, len(items), 24):
        make_sheet(items[offset:offset + 24], f"all_{offset // 24 + 1:02d}.jpg")


if __name__ == "__main__":
    main()
