"""Build contact sheets for the already-cached MedalBook Sudan object images."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/review/sudan_medalbook_contact_sheets"
OUT.mkdir(parents=True, exist_ok=True)

rows = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_sudan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
items = []
for row in rows:
    for index, rel in enumerate(row.get("local_raw_images", []), 1):
        path = ROOT / rel
        if path.is_file():
            items.append((row["page_title"], index, path))

font = ImageFont.load_default()
for sheet_no, start in enumerate(range(0, len(items), 20), 1):
    page = Image.new("RGB", (1600, 2000), "#ece8df")
    draw = ImageDraw.Draw(page)
    for slot, (title, index, path) in enumerate(items[start:start + 20]):
        col, line = slot % 4, slot // 4
        x, y = 20 + col * 395, 20 + line * 395
        try:
            with Image.open(path) as src:
                image = src.convert("RGB")
                image.thumbnail((355, 310))
            page.paste(image, (x + (355 - image.width) // 2, y))
            draw.multiline_text((x, y + 318), f"{start + slot + 1}. {title}\nview {index}", fill="black", font=font, spacing=3)
        except Exception as exc:
            draw.text((x, y), f"decode error: {exc}", fill="red", font=font)
    page.save(OUT / f"sheet_{sheet_no:02d}.jpg", quality=90)

print(json.dumps({"images": len(items), "sheets": (len(items) + 19) // 20, "output": str(OUT)}, ensure_ascii=False))
