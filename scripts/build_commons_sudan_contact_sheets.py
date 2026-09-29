"""Render review sheets for downloaded Sudan Commons object candidates."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/image_harvest/commons_sudan_full_body_retry.json"
OUT = ROOT / "data/review/commons_sudan_contact_sheets"
OUT.mkdir(parents=True, exist_ok=True)

items = [x for x in json.loads(SOURCE.read_text(encoding="utf-8"))["pending"] if x.get("status") == "DOWNLOADED"]
font = ImageFont.load_default()
for sheet_no, start in enumerate(range(0, len(items), 9), 1):
    sheet = Image.new("RGB", (1800, 1800), "#eeeae1")
    draw = ImageDraw.Draw(sheet)
    for slot, item in enumerate(items[start:start + 9]):
        col, row = slot % 3, slot // 3
        x, y = 25 + col * 590, 25 + row * 590
        path = ROOT / item["local_path"]
        with Image.open(path) as source:
            preview = ImageOps.contain(source.convert("RGBA"), (540, 470))
            background = Image.new("RGBA", preview.size, "white")
            background.alpha_composite(preview)
            preview = background.convert("RGB")
        sheet.paste(preview, (x + (540 - preview.width) // 2, y))
        label = f"{start + slot + 1}. {item['page_title']}\n{item['width']}×{item['height']} · {item['categories'][0]}"
        draw.multiline_text((x, y + 485), label, fill="black", font=font, spacing=3)
    sheet.save(OUT / f"sheet_{sheet_no:02d}.jpg", quality=92)

print(json.dumps({"images": len(items), "sheets": (len(items) + 8) // 9, "output": str(OUT)}, ensure_ascii=False))
