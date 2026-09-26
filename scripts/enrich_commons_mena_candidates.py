"""Batch-resolve Commons file metadata and licence for MENA sweep candidates."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEEP = "--deep" in sys.argv
INPUT = ROOT / "data" / "raw_candidates" / ("commons_core_deep_2026-09-26.jsonl" if DEEP else "commons_mena_category_sweep_2026-09-26.jsonl")
OUTPUT = ROOT / "data" / "raw_candidates" / ("commons_core_deep_enriched_2026-09-26.jsonl" if DEEP else "commons_mena_enriched_2026-09-26.jsonl")
CHECKPOINT = ROOT / "data" / "checkpoints" / ("commons_core_deep_enrichment_2026-09-26.json" if DEEP else "commons_mena_enrichment_2026-09-26.json")
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-local-research/1.0 (offline catalogue)"


def request_json(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = json.load(response)
            time.sleep(1.2)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def clean(meta: dict, key: str) -> str | None:
    value = meta.get(key, {}).get("value")
    return value if value not in (None, "") else None


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_title = {row["file_title"]: row for row in rows}
    if OUTPUT.is_file():
        for old in (json.loads(line) for line in OUTPUT.read_text(encoding="utf-8").splitlines() if line.strip()):
            if old.get("file_title") in by_title and old.get("original_url"):
                by_title[old["file_title"]].update(old)
    titles = sorted(by_title)
    pending = [title for title in titles if not by_title[title].get("original_url")]
    resolved = len(titles) - len(pending)
    failures: list[dict] = []
    batch_size = 20
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        try:
            data = request_json({
                "action": "query",
                "prop": "imageinfo",
                "titles": "|".join(batch),
                "iiprop": "url|size|mime|mediatype|sha1|timestamp|extmetadata",
                "iiextmetadatafilter": "ObjectName|ImageDescription|DateTimeOriginal|Artist|Credit|License|LicenseShortName|UsageTerms|Categories",
                "iiextmetadatalanguage": "en",
            })
        except Exception as exc:
            failures.append({"start": start, "count": len(batch), "error": f"{type(exc).__name__}: {exc}"})
            continue
        for page in data.get("query", {}).get("pages", []):
            title = page.get("title")
            if title not in by_title or not page.get("imageinfo"):
                continue
            info = page["imageinfo"][0]
            meta = info.get("extmetadata", {})
            row = by_title[title]
            row.update({
                "pageid": page.get("pageid"),
                "original_url": info.get("url"),
                "width": info.get("width"),
                "height": info.get("height"),
                "size_bytes": info.get("size"),
                "mime": info.get("mime"),
                "mediatype": info.get("mediatype"),
                "sha1": info.get("sha1"),
                "timestamp": info.get("timestamp"),
                "object_name": clean(meta, "ObjectName"),
                "image_description": clean(meta, "ImageDescription"),
                "date_time_original": clean(meta, "DateTimeOriginal"),
                "artist": clean(meta, "Artist"),
                "credit": clean(meta, "Credit"),
                "license": clean(meta, "License"),
                "license_short_name": clean(meta, "LicenseShortName"),
                "usage_terms": clean(meta, "UsageTerms"),
                "commons_categories": clean(meta, "Categories"),
            })
            resolved += 1
        OUTPUT.write_text("".join(json.dumps(by_title[t], ensure_ascii=False) + "\n" for t in titles), encoding="utf-8")
        print(f"resolved pending batch {start + 1}-{min(start + batch_size, len(pending))}: total {resolved}", flush=True)
    summary = {
        "as_of": "2026-09-26",
        "input_rows": len(rows),
        "metadata_resolved": resolved,
        "metadata_unresolved": len(rows) - resolved,
        "batch_failures": failures,
        "output": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
    }
    CHECKPOINT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
