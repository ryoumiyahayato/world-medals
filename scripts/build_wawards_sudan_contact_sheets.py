"""Render contact sheets for the cached Wawards Sudan source sweep."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/image_harvest/wawards_sudan_all_images.json"
OUT = ROOT / "data/review/wawards_sudan_contact_sheets"
OUT.mkdir(parents=True, exist_ok=True)

items = json.loads(SOURCE.read_text(encoding="utf-8"))["images"]
font = ImageFont.load_default()
for sheet_no, start in enumerate(range(0, len(items), 12), 1):
    sheet = Image.new("RGB", (1800, 1800), "#eeeae1")
    draw = ImageDraw.Draw(sheet)
    for slot, item in enumerate(items[start:start + 12]):
        col, row = slot % 3, slot // 3
        x, y = 25 + col * 590, 25 + row * 440
        path = ROOT / item["local_path"]
        with Image.open(path) as source:
            preview = ImageOps.contain(source.convert("RGB"), (540, 350))
        sheet.paste(preview, (x + (540 - preview.width) // 2, y))
        label = f"{start + slot + 1}. {item['page_title']}\nview {item['ordinal']} · {item['dimensions'][0]}×{item['dimensions'][1]}"
        draw.multiline_text((x, y + 360), label, fill="black", font=font, spacing=3)
    sheet.save(OUT / f"sheet_{sheet_no:02d}.jpg", quality=92)

print(json.dumps({"images": len(items), "sheets": (len(items) + 11) // 12, "output": str(OUT)}, ensure_ascii=False))
