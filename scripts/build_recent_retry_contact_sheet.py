"""Render the images added by the Commons redirect retry for rapid review."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
cutoff = datetime.now().timestamp() - 20 * 60
catalogue = {}
for name in ("mena_bulk_round7_candidates.json", "mena_core_deep_round7_candidates.json"):
    for row in json.loads((ROOT / "data/normalized_drafts" / name).read_text(encoding="utf-8"))["records"]:
        catalogue[row["candidate_id"]] = row
items = []
for folder in (ROOT / "assets/raw/mena_round7_review", ROOT / "assets/raw/mena_core_deep_round7_review"):
    for path in folder.glob("*.png"):
        if path.stat().st_mtime >= cutoff and path.stem in catalogue:
            items.append((path, catalogue[path.stem]))
items.sort(key=lambda x: x[0].name)
font = ImageFont.load_default()
sheet = Image.new("RGB", (1600, ((len(items) + 3) // 4) * 380), "white")
draw = ImageDraw.Draw(sheet)
for index, (path, row) in enumerate(items):
    x, y = (index % 4) * 400, (index // 4) * 380
    with Image.open(path) as source:
        preview = ImageOps.contain(source.convert("RGB"), (370, 285))
    sheet.paste(preview, (x + (380 - preview.width) // 2, y))
    label = row["file_title"][5:]
    draw.multiline_text((x + 8, y + 292), f"{path.stem}\n{row['country_zh']} | {label[:58]}\n{row['family_hint'][:58]}", fill="black", font=font, spacing=2)
out = ROOT / "data/review/commons_redirect_retry_contact_sheet.jpg"
sheet.save(out, quality=90)
print(json.dumps({"images": len(items), "output": str(out)}, ensure_ascii=False))
