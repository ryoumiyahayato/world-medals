"""Build a contact sheet from the official images referenced by the completed PMO sweep."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/pmo_singapore_awards.jsonl"
OUTPUT = ROOT / "sources/pages/pmo_singapore_awards/contact_sheets"


def main() -> None:
    rows=[json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    items=[(row["page_title"], ROOT / image["local_path"]) for row in rows for image in row["original_images"]]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cols, cell_w, cell_h = 4, 320, 360
    sheet=Image.new("RGB", (cols*cell_w, 5*cell_h), "white"); draw=ImageDraw.Draw(sheet); font=ImageFont.load_default()
    for index,(title,path) in enumerate(items):
        with Image.open(path) as source: image=source.convert("RGB")
        image.thumbnail((cell_w-24, cell_h-74), Image.Resampling.LANCZOS)
        x=(index%cols)*cell_w+(cell_w-image.width)//2; y=(index//cols)*cell_h+8
        sheet.paste(image,(x,y)); draw.text(((index%cols)*cell_w+8,(index//cols)*cell_h+cell_h-58),title[:48],fill="black",font=font)
    sheet.save(OUTPUT / "all_01.jpg", quality=90)
    print(f"images={len(items)} sheets=1")


if __name__ == "__main__": main()
