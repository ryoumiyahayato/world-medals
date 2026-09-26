"""Retry missing MENA Commons review images through Special:Redirect/file."""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEEP = "--deep" in sys.argv
LIMIT = int(next((arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--limit=")), "80"))
INPUT = ROOT / "data/normalized_drafts" / ("mena_core_deep_round7_candidates.json" if DEEP else "mena_bulk_round7_candidates.json")
OUTDIR = ROOT / "assets/raw" / ("mena_core_deep_round7_review" if DEEP else "mena_round7_review")
UA = "world-medals-local-research/1.0 (offline catalogue; Commons file redirect)"

records = json.loads(INPUT.read_text(encoding="utf-8"))["records"]
OUTDIR.mkdir(parents=True, exist_ok=True)
missing = [row for row in records if not (OUTDIR / f"{row['candidate_id']}.png").is_file()]
done = []
failed = []
for row in missing[:LIMIT]:
    name = row["file_title"][5:]
    url = "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + urllib.parse.quote(name, safe="") + "?width=640"
    target = OUTDIR / f"{row['candidate_id']}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = response.read()
        with Image.open(io.BytesIO(payload)) as source:
            source.load()
            image = source.convert("RGBA" if source.mode in ("RGBA", "LA") else "RGB")
            image.save(target, "PNG", optimize=True)
        done.append(row["candidate_id"])
    except Exception as exc:
        failed.append({"candidate_id": row["candidate_id"], "file_title": row["file_title"], "error": f"{type(exc).__name__}: {exc}"})
    time.sleep(0.75)

checkpoint = ROOT / "data/checkpoints" / ("commons_core_deep_redirect_retry_2026-09-26.json" if DEEP else "commons_mena_redirect_retry_2026-09-26.json")
checkpoint.write_text(json.dumps({"attempted": min(LIMIT, len(missing)), "downloaded": len(done), "failed": failed, "remaining_before_run": len(missing)}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"deep": DEEP, "attempted": min(LIMIT, len(missing)), "downloaded": len(done), "failed": len(failed)}, ensure_ascii=False))
