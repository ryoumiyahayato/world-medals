"""Recover rate-limited Commons North Korea files through API-provided 1200px thumbnails."""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_JSONL = ROOT / "data/raw_candidates/commons_north_korea.jsonl"
SWEEP = ROOT / "data/source_sweeps/commons_north_korea_2026-09-28.json"
OUT = ROOT / "assets/raw/commons_north_korea"
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-research/1.0 (offline catalogue; paced Commons thumbnail recovery)"


def api(titles: list[str]) -> dict[str, dict]:
    params = {
        "format": "json", "formatversion": 2, "action": "query", "prop": "imageinfo",
        "titles": "|".join(titles), "iiprop": "url|size|mime|sha1", "iiurlwidth": 1200,
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)
    return {page["title"]: (page.get("imageinfo") or [{}])[0] for page in data["query"]["pages"]}


def main() -> None:
    rows = [json.loads(line) for line in RAW_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Reconcile any file written before an interrupted run and checkpoint it
    # before making another network request.
    for row in rows:
        if not row.get("likely_object") or row.get("local_raw_image"):
            continue
        stem = hashlib.sha256(row["file_title"].encode("utf-8")).hexdigest()[:16]
        matches = list(OUT.glob(stem + ".*"))
        if not matches:
            continue
        path = matches[0]
        try:
            with Image.open(path) as im:
                width, height, fmt = *im.size, im.format
                im.verify()
            row.update({"local_raw_image": path.relative_to(ROOT).as_posix(), "download_representation": "Commons cached raster reconciled after interrupted recovery", "cached_width": width, "cached_height": height, "cached_format": fmt})
        except Exception:
            path.unlink(missing_ok=True)
    RAW_JSONL.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    if os.environ.get("COMMONS_RECONCILE_ONLY") == "1":
        print(json.dumps({"cached_total": sum(bool(row.get('local_raw_image')) for row in rows), "mode": "reconcile_only"}, ensure_ascii=False))
        return
    wanted = [r["file_title"] for r in rows if r.get("likely_object") and not r.get("local_raw_image")]
    details: dict[str, dict] = {}
    for offset in range(0, len(wanted), 25):
        details.update(api(wanted[offset:offset + 25]))
        time.sleep(2.0)
    recovered, failures = 0, []
    for n, row in enumerate(rows, 1):
        if not row.get("likely_object") or row.get("local_raw_image"):
            continue
        info = details.get(row["file_title"], {})
        url = info.get("thumburl") or info.get("url")
        if not url:
            failures.append({"title": row["file_title"], "error": "No API thumbnail URL"})
            continue
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
            ext = ".jpg"
        path = OUT / (hashlib.sha256(row["file_title"].encode("utf-8")).hexdigest()[:16] + ext)
        error = None
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=90) as response:
                    path.write_bytes(response.read())
                with Image.open(path) as im:
                    width, height, fmt = *im.size, im.format
                    im.verify()
                row.update({
                    "local_raw_image": path.relative_to(ROOT).as_posix(), "download_url_used": url,
                    "download_representation": "Commons API 1200px thumbnail after original endpoint rate limit",
                    "cached_width": width, "cached_height": height, "cached_format": fmt,
                })
                recovered += 1
                RAW_JSONL.write_text("".join(json.dumps(candidate, ensure_ascii=False) + "\n" for candidate in rows), encoding="utf-8")
                error = None
                break
            except urllib.error.HTTPError as exc:
                error = f"HTTP {exc.code}"
                path.unlink(missing_ok=True)
                if exc.code == 429:
                    time.sleep(12 * (attempt + 1))
                else:
                    break
            except Exception as exc:
                error = repr(exc)
                path.unlink(missing_ok=True)
                break
        if error:
            failures.append({"title": row["file_title"], "url": url, "error": error})
        time.sleep(1.25)
        if n % 25 == 0:
            print(f"processed row {n}/{len(rows)} recovered={recovered} failures={len(failures)}", flush=True)

    RAW_JSONL.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    sweep["thumbnail_recovery"] = {
        "attempted": len(wanted), "recovered": recovered, "failures": failures,
        "method": "API-provided 1200px thumbnails, paced after original endpoint 429 responses",
    }
    sweep["raster_files_cached"] = sum(bool(row.get("local_raw_image")) for row in rows)
    if not failures:
        sweep["status"] = "complete_with_thumbnail_recovery"
    SWEEP.write_text(json.dumps(sweep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempted": len(wanted), "recovered": recovered, "failures": len(failures), "cached_total": sweep["raster_files_cached"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
