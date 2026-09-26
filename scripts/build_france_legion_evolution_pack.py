"""Crop the CC BY-SA 4.0 Commons Legion of Honour evolution plate by period."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "originals/legion_commons_pack1_2026-09-26/legion-evolution-5000.png"
out = ROOT / "assets/images/france_legion_evolution_pack1"
out.mkdir(parents=True, exist_ok=True)

names = [
    "first-empire",
    "bourbon-restoration",
    "july-monarchy",
    "second-republic",
    "second-empire",
    "third-republic",
    "fourth-fifth-republics",
]

with Image.open(source) as image:
    width, height = image.size
    for index, name in enumerate(names):
        left = round(width * index / len(names))
        right = round(width * (index + 1) / len(names))
        crop = image.crop((left, 0, right, height))
        crop.save(out / f"{name}.png", optimize=True)

