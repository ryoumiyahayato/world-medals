"""Download Commons review thumbnails and render contact sheets for the round-7 bulk pack."""
from __future__ import annotations

import io
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEEP = "--deep" in sys.argv
INPUT = ROOT / "data/normalized_drafts" / ("mena_core_deep_round7_candidates.json" if DEEP else "mena_bulk_round7_candidates.json")
OUTDIR = ROOT / "assets/raw" / ("mena_core_deep_round7_review" if DEEP else "mena_round7_review")
SHEETDIR = ROOT / "data/review" / ("mena_core_deep_round7_contact_sheets" if DEEP else "mena_round7_contact_sheets")
MANIFEST = ROOT / "data/image_harvest" / ("mena_core_deep_round7_review_manifest.json" if DEEP else "mena_round7_review_manifest.json")
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-local-research/1.0 (offline catalogue)"

def request_json(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError

data = json.loads(INPUT.read_text(encoding="utf-8"))
records = data["records"]
OUTDIR.mkdir(parents=True, exist_ok=True)
SHEETDIR.mkdir(parents=True, exist_ok=True)
by_title = {row["file_title"]: row for row in records}
failures = []

def download_row(row: dict, pages: dict) -> tuple[dict, str | None]:
    target = OUTDIR / f"{row['candidate_id']}.png"
    try:
        info = pages[row["file_title"]]["imageinfo"][0]
        url = info.get("thumburl") or info["url"]
        if not target.is_file():
            payload = fetch(url)
            with Image.open(io.BytesIO(payload)) as image:
                image.load()
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")
                image.save(target, "PNG", optimize=True)
        with Image.open(target) as image:
            image.verify()
        with Image.open(target) as image:
            width, height = image.size
        row["review_thumb_url"] = url
        row["review_local_path"] = str(target.relative_to(ROOT)).replace("\\", "/")
        row["review_width"], row["review_height"] = width, height
        return row, None
    except Exception as exc:
        return row, f"{type(exc).__name__}: {exc}"

for start in range(0, len(records), 20):
    batch = records[start:start + 20]
    response = request_json({"action": "query", "prop": "imageinfo", "titles": "|".join(row["file_title"] for row in batch),
                             "iiprop": "url|size|mime", "iiurlwidth": 320})
    pages = {page.get("title"): page for page in response.get("query", {}).get("pages", [])}
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(download_row, row, pages) for row in batch]
        for job in as_completed(jobs):
            row, error = job.result()
            if error:
                failures.append({"candidate_id": row["candidate_id"], "file_title": row["file_title"], "error": error})
    time.sleep(3)
    print(f"review thumbnails {min(start + 20, len(records))}/{len(records)}", flush=True)

font = ImageFont.load_default()
valid = [row for row in records if row.get("review_local_path")]
per_sheet = 20
for sheet_no in range(math.ceil(len(valid) / per_sheet)):
    subset = valid[sheet_no * per_sheet:(sheet_no + 1) * per_sheet]
    sheet = Image.new("RGB", (1600, 5 * 330), "white")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(subset):
        col, line = index % 4, index // 4
        x, y = col * 400, line * 330
        with Image.open(ROOT / row["review_local_path"]) as source:
            source = source.convert("RGBA")
            preview = ImageOps.contain(source, (360, 245))
            bg = Image.new("RGBA", preview.size, "white")
            bg.alpha_composite(preview)
            sheet.paste(bg.convert("RGB"), (x + (400 - preview.width) // 2, y + 4))
        title = row["file_title"][5:]
        if len(title) > 48:
            title = title[:45] + "..."
        draw.text((x + 8, y + 255), f"{row['candidate_id']} | {row['country_zh']}", fill="black", font=font)
        draw.text((x + 8, y + 274), title, fill="black", font=font)
        draw.text((x + 8, y + 293), row["family_hint"][:52], fill="#444444", font=font)
    path = SHEETDIR / f"sheet_{sheet_no + 1:02d}.jpg"
    sheet.save(path, quality=88)

MANIFEST.parent.mkdir(parents=True, exist_ok=True)
MANIFEST.write_text(json.dumps({"as_of": "2026-09-26", "records": records, "failures": failures,
                                "contact_sheets": [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted(SHEETDIR.glob("sheet_*.jpg"))]},
                               ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"downloaded": len(valid), "failed": len(failures), "sheets": math.ceil(len(valid) / per_sheet)}, ensure_ascii=False))
