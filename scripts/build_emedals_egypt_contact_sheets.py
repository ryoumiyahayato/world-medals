"""Build review-only contact sheets for selected eMedals Egypt products."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "data/image_harvest/emedals_egypt_catalog.json"
RAW_CANDIDATES = ROOT / "data/raw_candidates/emedals_egypt_catalog.jsonl"
OUT = ROOT / "sources/pages/emedals_egypt/contact_sheets"
SELECTED = {1, 2, 3, 8, 14, 45, 47, 58, 64, 69, 79}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = json.loads(HARVEST.read_text(encoding="utf-8"))["images"]
    by_product: dict[int, list[dict]] = {}
    for item in images:
        by_product.setdefault(item["product_id"], []).append(item)
    candidates = [json.loads(line) for line in RAW_CANDIDATES.read_text(encoding="utf-8").splitlines() if line.strip()]
    products = [(item["source_position"], item["source_product_id"], item["page_title"]) for item in candidates]
    for position, product_id, title in products:
        if position not in SELECTED:
            continue
        items = sorted(by_product[product_id], key=lambda item: item["ordinal"])
        cell_w, cell_h, header = 260, 300, 82
        columns = min(4, len(items))
        rows = (len(items) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cell_w, header + rows * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((10, 8), f"#{position} {title[:120]}", fill="black")
        for index, item in enumerate(items):
            with Image.open(ROOT / item["local_path"]) as source:
                rendered = ImageOps.contain(source.convert("RGB"), (cell_w - 20, cell_h - 45))
            x = (index % columns) * cell_w + (cell_w - rendered.width) // 2
            y = header + (index // columns) * cell_h + 24
            sheet.paste(rendered, (x, y))
            draw.text(((index % columns) * cell_w + 8, header + (index // columns) * cell_h + 5), f"view {item['ordinal']} {item['dimensions'][0]}x{item['dimensions'][1]}", fill="black")
        sheet.save(OUT / f"{position:03d}_{product_id}.jpg", quality=90)
    print(f"built {len(list(OUT.glob('*.jpg')))} eMedals Egypt review sheets")


if __name__ == "__main__":
    main()
