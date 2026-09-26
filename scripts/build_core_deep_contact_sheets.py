"""Build contact sheets from already cached deep-review thumbnails."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / "data/normalized_drafts/mena_core_deep_round7_candidates.json").read_text(encoding="utf-8"))["records"]
source = ROOT / "assets/raw/mena_core_deep_round7_review"
outdir = ROOT / "data/review/mena_core_deep_round7_contact_sheets"
outdir.mkdir(parents=True, exist_ok=True)
records = [r for r in records if (source / f"{r['candidate_id']}.png").is_file()]
font = ImageFont.load_default()
for number in range(math.ceil(len(records) / 20)):
    subset = records[number * 20:(number + 1) * 20]
    sheet = Image.new("RGB", (1600, 1650), "white"); draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(subset):
        col, line = index % 4, index // 4; x, y = col * 400, line * 330
        with Image.open(source / f"{row['candidate_id']}.png") as im:
            preview = ImageOps.contain(im.convert("RGBA"), (360, 245)); bg = Image.new("RGBA", preview.size, "white"); bg.alpha_composite(preview)
            sheet.paste(bg.convert("RGB"), (x + (400 - preview.width) // 2, y + 4))
        title = row["file_title"][5:]
        draw.text((x + 8, y + 255), f"{row['candidate_id']} | {row['country_zh']}", fill="black", font=font)
        draw.text((x + 8, y + 274), (title[:45] + "...") if len(title) > 48 else title, fill="black", font=font)
        draw.text((x + 8, y + 293), row["family_hint"][:52], fill="#444", font=font)
    sheet.save(outdir / f"sheet_{number + 1:02d}.jpg", quality=88)
print(json.dumps({"cached": len(records), "sheets": math.ceil(len(records) / 20)}))
