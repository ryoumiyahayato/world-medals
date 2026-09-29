from __future__ import annotations

import concurrent.futures
import hashlib
import json
import mimetypes
import pathlib
import re
import time
import urllib.parse
import urllib.request

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw_candidates/medalbook_egypt.jsonl"
OUT_DIR = ROOT / "assets/raw/medalbook_egypt"
MANIFEST = ROOT / "data/source_sweeps/medalbook_egypt_images_2026-09-27.json"


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:80] or "item"


def extension(url: str, content_type: str) -> str:
    suffix = pathlib.Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    return guessed if guessed in {".jpg", ".png", ".webp", ".gif", ".tif", ".tiff"} else ".jpg"


def fetch(job: dict) -> dict:
    url = job["url"]
    base = f'{job["record_index"]:03d}_{slug(job["title"])}_{job["image_index"]:02d}'
    cached = list(OUT_DIR.glob(base + ".*"))
    if cached:
        path = cached[0]
        try:
            data = path.read_bytes()
            with Image.open(path) as im:
                width, height = im.size
                fmt = im.format
            return {
                **job,
                "status": "downloaded",
                "local_path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "width": width,
                "height": height,
                "format": fmt,
                "sha256": hashlib.sha256(data).hexdigest(),
                "cached": True,
            }
        except Exception:
            pass
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 world-medals research archive"})
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read()
                ctype = response.headers.get("Content-Type", "")
            path = OUT_DIR / (base + extension(url, ctype))
            path.write_bytes(data)
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                width, height = im.size
                fmt = im.format
            return {
                **job,
                "status": "downloaded",
                "local_path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "width": width,
                "height": height,
                "format": fmt,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        except Exception as exc:
            if attempt == 2:
                return {**job, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            time.sleep(1.5 * (attempt + 1))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    jobs = []
    for record_index, record in enumerate(records):
        for image_index, url in enumerate(record.get("original_image_urls", []), 1):
            jobs.append({
                "record_index": record_index,
                "image_index": image_index,
                "title": record["page_title"],
                "page_url": record["page_url"],
                "url": url,
            })
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for future in concurrent.futures.as_completed([pool.submit(fetch, job) for job in jobs]):
            results.append(future.result())
            if len(results) % 40 == 0:
                print(f"downloaded/attempted: {len(results)}/{len(jobs)}")
    results.sort(key=lambda x: (x["record_index"], x["image_index"]))
    payload = {
        "source_id": "medalbook_egypt_images",
        "as_of": "2026-09-27",
        "boundary": "All original image URLs exposed by the completed 195-page MedalBook Egypt sweep",
        "planned_images": len(jobs),
        "downloaded": sum(x["status"] == "downloaded" for x in results),
        "failed": sum(x["status"] == "failed" for x in results),
        "items": results,
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("planned_images", "downloaded", "failed")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
