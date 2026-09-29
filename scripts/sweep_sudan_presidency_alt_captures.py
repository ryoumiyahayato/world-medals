"""Try alternate Wayback snapshots for Sudan Presidency award pages lacking images."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE_RAW = ROOT / "data/raw_candidates/sudan_presidency_wayback.jsonl"
PAGES = ROOT / "sources/pages/sudan_presidency_alt"
RAW_IMAGES = ROOT / "assets/raw/sudan_presidency_alt"
OUT = ROOT / "data/raw_candidates/sudan_presidency_alt_captures.jsonl"
REPORT = ROOT / "data/source_sweeps/sudan_presidency_alt_captures_2026-09-27.json"
ORIGIN = "https://www.presidency.gov.sd"
TIMESTAMPS = [
    "20180101000000",
    "20190101000000",
    "20200101000000",
    "20210101000000",
    "20220101000000",
    "20230101000000",
    "20240101000000",
]
UA = "Mozilla/5.0 (compatible; world-medals research cache/1.0)"


def get(url: str, timeout: int = 35) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), response.geturl()


def image_relative(html: str) -> str | None:
    patterns = [
        r'(?:src|href)="(?:https://web\.archive\.org)?/web/\d+(?:im_)?/https?://www\.presidency\.gov\.sd/(img/nodes/big/[^"?]+)',
        r'(?:src|href)="https?://www\.presidency\.gov\.sd/(img/nodes/big/[^"?]+)',
        r'(?:src|href)="/(img/nodes/big/[^"?]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return urllib.parse.unquote(match.group(1))
    return None


def capture_timestamp(url: str) -> str | None:
    match = re.search(r"/web/(\d{14})", url)
    return match.group(1) if match else None


def capture_matches_slug(url: str, slug: str) -> bool:
    decoded = urllib.parse.unquote(url).lower()
    return f"/medals-decorations/{slug.lower()}" in decoded


def main() -> None:
    rows = [json.loads(line) for line in BASE_RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    pending = [row for row in rows if not row.get("local_raw_image")]
    PAGES.mkdir(parents=True, exist_ok=True)
    RAW_IMAGES.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    attempts: list[dict] = []

    for row in pending:
        slug = row["working_name"]
        original = f"{ORIGIN}/medals-decorations/{slug}"
        found = None
        seen_final: set[str] = set()
        for requested in TIMESTAMPS:
            page_url = f"https://web.archive.org/web/{requested}id_/{original}"
            try:
                data, final_url = get(page_url)
                actual = capture_timestamp(final_url) or requested
                if not capture_matches_slug(final_url, slug):
                    attempts.append({
                        "slug": slug,
                        "requested": requested,
                        "actual": actual,
                        "status": "REDIRECTED_OFF_SCOPE",
                        "final_url": final_url,
                    })
                    continue
                identity = f"{actual}:{hashlib.sha256(data).hexdigest()}"
                if identity in seen_final:
                    attempts.append({"slug": slug, "requested": requested, "actual": actual, "status": "DUPLICATE_CAPTURE"})
                    continue
                seen_final.add(identity)
                page_path = PAGES / f"{slug}_{actual}.html"
                page_path.write_bytes(data)
                text = data.decode("utf-8", errors="replace")
                image_rel = image_relative(text)
                attempts.append({
                    "slug": slug,
                    "requested": requested,
                    "actual": actual,
                    "status": "IMAGE_REFERENCE_FOUND" if image_rel else "NO_IMAGE_REFERENCE",
                    "cache_file": page_path.relative_to(ROOT).as_posix(),
                })
                if not image_rel:
                    continue
                suffix = Path(urllib.parse.urlparse(image_rel).path).suffix.lower() or ".img"
                image_url = f"https://web.archive.org/web/{actual}im_/{ORIGIN}/{image_rel}"
                image_data, image_final_url = get(image_url)
                image_path = RAW_IMAGES / f"{slug}_{actual}{suffix}"
                image_path.write_bytes(image_data)
                with Image.open(image_path) as image:
                    image.verify()
                with Image.open(image_path) as image:
                    dimensions = [image.width, image.height]
                found = {
                    "source_id": f"sudan-presidency-alt-{slug.lower()}-{actual}",
                    "source_system": "Sudan Presidency medals and decorations (alternate Wayback capture)",
                    "working_name": slug,
                    "original_page_url": original,
                    "requested_timestamp": requested,
                    "capture_timestamp": actual,
                    "page_archive_url": final_url,
                    "image_original_url": f"{ORIGIN}/{image_rel}",
                    "image_archive_url": image_final_url,
                    "local_raw_image": image_path.relative_to(ROOT).as_posix(),
                    "image_dimensions": dimensions,
                    "image_sha256": hashlib.sha256(image_data).hexdigest(),
                    "cache_file": page_path.relative_to(ROOT).as_posix(),
                    "status": "OFFICIAL_ALT_IMAGE_CACHED",
                    "access_date": str(date.today()),
                }
                break
            except Exception as error:
                attempts.append({"slug": slug, "requested": requested, "status": "ERROR", "error": repr(error)})
            finally:
                time.sleep(0.5)
        if found:
            results.append(found)

    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in results), encoding="utf-8")
    REPORT.write_text(json.dumps({
        "as_of": str(date.today()),
        "source_id": "sudan-presidency-wayback-alternate-captures",
        "status": "complete_bounded_timestamp_probe",
        "pending_slugs_checked": len(pending),
        "requested_timestamps": TIMESTAMPS,
        "attempts": len(attempts),
        "alternate_official_images_recovered": len(results),
        "recovered_slugs": [row["working_name"] for row in results],
        "candidate_file": OUT.relative_to(ROOT).as_posix(),
        "attempt_log": attempts,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alternate Sudan Presidency captures: {len(pending)} slugs, {len(attempts)} attempts, {len(results)} images")


if __name__ == "__main__":
    main()
