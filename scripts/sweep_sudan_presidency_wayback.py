"""Sweep the complete award sidebar from the archived Sudan Presidency site."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "sources/pages/sudan_presidency_wayback"
RAW_IMAGES = ROOT / "assets/raw/sudan_presidency_wayback"
RAW = ROOT / "data/raw_candidates/sudan_presidency_wayback.jsonl"
REPORT = ROOT / "data/source_sweeps/sudan_presidency_wayback_2026-09-27.json"
TIMESTAMP = "20230313013209"
ORIGIN = "https://www.presidency.gov.sd"
WAYBACK = f"https://web.archive.org/web/{TIMESTAMP}"
SEED_SLUG = "Medal-science-literature-arts-Gold"
UA = "Mozilla/5.0 (compatible; world-medals research cache/1.0)"


def fetch(url: str, target: Path) -> bytes:
    if target.is_file() and target.stat().st_size > 500:
        return target.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return data


def clean(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    RAW_IMAGES.mkdir(parents=True, exist_ok=True)
    seed_url = f"{WAYBACK}/{ORIGIN}/medals-decorations/{SEED_SLUG}"
    seed_bytes = fetch(seed_url, PAGES / f"{SEED_SLUG}.html")
    seed = seed_bytes.decode("utf-8", errors="replace")
    slugs = []
    for match in re.finditer(r'href="(?:https://web\.archive\.org)?/web/\d+/https?://www\.presidency\.gov\.sd/medals-decorations/([^"?#]+)"', seed, re.I):
        value = urllib.parse.unquote(match.group(1)).strip("/")
        if value and value.lower() not in {s.lower() for s in slugs}:
            slugs.append(value)
    if SEED_SLUG.lower() not in {s.lower() for s in slugs}:
        slugs.append(SEED_SLUG)
    if len(slugs) < 20:
        raise RuntimeError(f"Only {len(slugs)} award slugs parsed from the official sidebar")

    rows = []
    failures = []
    for index, slug in enumerate(slugs, 1):
        page_url = f"{WAYBACK}/{ORIGIN}/medals-decorations/{slug}"
        page_path = PAGES / f"{slug}.html"
        try:
            page_data = fetch(page_url, page_path)
            text = page_data.decode("utf-8", errors="replace")
            title_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
            title = clean(title_match.group(1)) if title_match else slug
            image_matches = re.findall(
                r'(?:src|href)="(?:https://web\.archive\.org)?/web/\d+im_/https?://www\.presidency\.gov\.sd/(img/nodes/big/[^"?]+)"',
                text,
                re.I,
            )
            image_rel = image_matches[0] if image_matches else None
            image_url = f"{WAYBACK}im_/{ORIGIN}/{image_rel}" if image_rel else None
            local_path = None
            dimensions = None
            sha256 = None
            if image_url:
                suffix = Path(urllib.parse.urlparse(image_rel).path).suffix.lower() or ".img"
                image_path = RAW_IMAGES / f"{slug}{suffix}"
                image_bytes = fetch(image_url, image_path)
                with Image.open(image_path) as im:
                    im.verify()
                with Image.open(image_path) as im:
                    dimensions = [im.width, im.height]
                local_path = image_path.relative_to(ROOT).as_posix()
                sha256 = hashlib.sha256(image_bytes).hexdigest()
            body_match = re.search(r"<h1[^>]*>.*?</h1>(.*?)(?:<div[^>]+class=\"(?:sidebar|block)|<h2|<footer)", text, re.I | re.S)
            description = clean(body_match.group(1))[:3000] if body_match else ""
            rows.append({
                "source_id": f"sudan-presidency-{slug.lower()}",
                "source_system": "Sudan Presidency medals and decorations (Wayback capture)",
                "page_title_ar": title,
                "working_name": slug,
                "page_url": page_url,
                "original_page_url": f"{ORIGIN}/medals-decorations/{slug}",
                "image_original_url": f"{ORIGIN}/{image_rel}" if image_rel else None,
                "image_archive_url": image_url,
                "local_raw_image": local_path,
                "image_dimensions": dimensions,
                "image_sha256": sha256,
                "description_ar": description,
                "status": "OFFICIAL_IMAGE_CACHED" if local_path else "OFFICIAL_TEXT_NO_IMAGE",
                "cache_file": page_path.relative_to(ROOT).as_posix(),
                "access_date": str(date.today()),
            })
        except Exception as exc:
            failures.append({"slug": slug, "url": page_url, "error": repr(exc)})
        if index < len(slugs):
            time.sleep(1.5)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    REPORT.write_text(json.dumps({
        "as_of": str(date.today()),
        "source_id": "sudan-presidency-wayback-awards",
        "source_title": "Sudan Presidency — medals and decorations archived official directory",
        "capture_timestamp": TIMESTAMP,
        "status": "complete_current_visible_sidebar" if not failures else "partial_with_failures",
        "sidebar_award_links_discovered": len(slugs),
        "award_pages_processed": len(rows),
        "official_images_downloaded_and_decoded": sum(bool(row["local_raw_image"]) for row in rows),
        "failures": failures,
        "candidate_file": RAW.relative_to(ROOT).as_posix(),
        "notes": [
            "Every unique award link exposed by the archived official award-page sidebar was visited.",
            "Original archived node images were downloaded and decoded; site chrome images were excluded.",
            "The official site rights notice is retained: images are cached for catalogue research and are not represented as openly licensed.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sudan Presidency: {len(slugs)} links, {len(rows)} pages, {sum(bool(r['local_raw_image']) for r in rows)} images, {len(failures)} failures")


if __name__ == "__main__":
    main()
