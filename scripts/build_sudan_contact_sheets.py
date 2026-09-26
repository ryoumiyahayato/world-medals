from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_sudan.jsonl"
OUT = ROOT / "tmp/sudan_medalbook_contact_sheets"
OUT.mkdir(parents=True, exist_ok=True)

items: list[tuple[Path, str, str]] = []
for line in RAW.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    for index, relative in enumerate(row.get("local_raw_images") or [], 1):
        items.append((ROOT / relative, row.get("page_title", ""), f"{row.get('source_id')}:{index}"))

font = ImageFont.load_default()
cell_w, cell_h = 320, 270
cols, rows_per_page = 4, 5
per_page = cols * rows_per_page
manifest = []

for page_index in range((len(items) + per_page - 1) // per_page):
    canvas = Image.new("RGB", (cell_w * cols, cell_h * rows_per_page), "white")
    draw = ImageDraw.Draw(canvas)
    for slot, (path, title, item_id) in enumerate(items[page_index * per_page : (page_index + 1) * per_page]):
        x = (slot % cols) * cell_w
        y = (slot // cols) * cell_h
        try:
            with Image.open(path) as source:
                source = source.convert("RGB")
                source.thumbnail((cell_w - 20, cell_h - 62))
                px = x + (cell_w - source.width) // 2
                py = y + 8
                canvas.paste(source, (px, py))
        except Exception as exc:
            draw.text((x + 8, y + 8), f"DECODE ERROR: {exc}", fill="red", font=font)
        label = title if len(title) <= 46 else title[:43] + "..."
        draw.text((x + 6, y + cell_h - 48), label, fill="black", font=font)
        draw.text((x + 6, y + cell_h - 30), path.name, fill="#555", font=font)
        manifest.append({"sheet": page_index + 1, "slot": slot + 1, "file": str(path.relative_to(ROOT)).replace("\\", "/"), "title": title, "item_id": item_id})
    out_path = OUT / f"sheet_{page_index + 1:02d}.jpg"
    canvas.save(out_path, quality=90)

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"images": len(items), "sheets": (len(items) + per_page - 1) // per_page, "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
