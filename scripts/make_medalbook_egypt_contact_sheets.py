from __future__ import annotations

import json
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/source_sweeps/medalbook_egypt_images_2026-09-27.json"
OUT = ROOT / "sources/pages/medalbook_egypt/contact_sheets"


def make_sheet(items: list[dict], name: str, columns: int = 4) -> None:
    cell_w, cell_h = 330, 300
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for n, item in enumerate(items):
        x, y = (n % columns) * cell_w, (n // columns) * cell_h
        path = ROOT / item["local_path"]
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((cell_w - 20, 225))
            px = x + (cell_w - im.width) // 2
            py = y + 5 + (225 - im.height) // 2
            canvas.paste(im, (px, py))
        title = f'{item["record_index"]:03d}/{item["image_index"]:02d} {item["title"]}'
        lines = textwrap.wrap(title, width=43)[:4]
        draw.multiline_text((x + 6, y + 235), "\n".join(lines), fill="black", font=font, spacing=2)
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#999999")
    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT / name, quality=88)


def main() -> None:
    items = json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]
    firsts = [x for x in items if x["image_index"] == 1]
    for offset in range(0, len(firsts), 20):
        make_sheet(firsts[offset:offset + 20], f"overview_{offset // 20 + 1}.jpg")
    groups = {
        "virtues_independence.jpg": range(98, 124),
        "merit.jpg": range(127, 140),
        "nile.jpg": range(153, 169),
        "republic.jpg": range(170, 183),
        "other_orders.jpg": list(range(82, 98)) + list(range(148, 153)) + list(range(185, 195)),
    }
    for name, indices in groups.items():
        selected = [x for x in items if x["record_index"] in indices]
        for offset in range(0, len(selected), 24):
            stem = pathlib.Path(name).stem
            make_sheet(selected[offset:offset + 24], f"{stem}_{offset // 24 + 1}.jpg")


if __name__ == "__main__":
    main()
