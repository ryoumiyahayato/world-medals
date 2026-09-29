"""Sweep the complete Malaysian federal honours directory embedded in official page popups."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.istiadat.gov.my/darjah-kebesaran-persekutuan/darjah-darjah-kebesaran-bintang-bintang-pingat-pingat-persekutuan/"
CACHE = ROOT / "sources/pages/istiadat_malaysia_federal"
RAW_DIR = ROOT / "assets/raw/istiadat_malaysia_federal"
OUT = ROOT / "data/raw_candidates/istiadat_malaysia_federal.jsonl"
STATE = ROOT / "data/source_sweeps/istiadat_malaysia_federal_2026-09-28.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 world-medals-research"


def fetch(url: str, referer: str = URL) -> bytes:
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise last


def plain(fragment: str) -> str:
    value = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    page_path = CACHE / "federal_awards.html"
    raw = page_path.read_bytes() if page_path.is_file() and page_path.stat().st_size > 100000 else fetch(URL)
    page_path.write_bytes(raw)
    source = raw.decode("utf-8", errors="replace")
    popups = list(re.finditer(r'<div id="pum-(\d+)".*?(?=<div id="pum-|\Z)', source, re.S))
    rows, failures = [], []
    seen_urls = set()
    for popup in popups:
        popup_id, block = popup.group(1), popup.group(0)
        content_match = re.search(r'<div class="pum-content popmake-content">(.*?)(?:<button|</div>\s*</div>\s*</div>)', block, re.S)
        content = content_match.group(1) if content_match else block
        name_match = re.search(r"<strong>(.*?)</strong>", content, re.S)
        image_urls = re.findall(r'https://www\.istiadat\.gov\.my/wp-content/uploads/2021/01/[^\s"<]+?\.png', content)
        image_urls = [u for u in image_urls if not re.search(r"-\d+x\d+\.png$", u)]
        if not name_match or not image_urls:
            continue
        name = plain(name_match.group(1)).replace("\xa0", " ")
        image_url = image_urls[-1]
        if image_url in seen_urls:
            continue
        seen_urls.add(image_url)
        text = plain(content)
        dates = sorted({int(year) for year in re.findall(r"(?<!\d)(18\d{2}|19\d{2}|20\d{2})(?!\d)", text)})
        abbreviation = ""
        abbr_match = re.search(r"\(([A-Z](?:\.?[A-Z0-9])+\.?)\)", name)
        if abbr_match:
            abbreviation = abbr_match.group(1)
        try:
            data = fetch(image_url)
            with Image.open(BytesIO(data)) as decoded:
                decoded.load()
                width, height, fmt = decoded.width, decoded.height, decoded.format
            suffix = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}.get(fmt, "img")
            local = RAW_DIR / f"{popup_id}_{re.sub(r'[^a-z0-9]+', '_', abbreviation.lower()).strip('_') or 'award'}.{suffix}"
            local.write_bytes(data)
            image = {"image_url": image_url, "local_path": local.relative_to(ROOT).as_posix(), "width": width, "height": height, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            rows.append({
                "source_id": f"istiadat-malaysia-federal-{popup_id}",
                "page_title": name,
                "working_name_zh": "待归并",
                "name_original": name,
                "name_en": None,
                "date_candidates": dates,
                "category": "federal_honour",
                "grade_material_clues": text,
                "object_url": URL + f"#pum-{popup_id}",
                "image_page_url": URL,
                "original_images": [image],
                "notes": "Official Malaysian Prime Minister's Department ceremonial and international conference division directory.",
                "status": "harvested",
            })
        except Exception as exc:
            failures.append({"popup_id": popup_id, "name": name, "image_url": image_url, "error": repr(exc)})
        print(f"processed {len(rows) + len(failures)}/{len(seen_urls)} {name}", flush=True)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    STATE.write_text(json.dumps({
        "as_of": "2026-09-28",
        "source_id": "istiadat_malaysia_federal",
        "source_name": "Bahagian Istiadat dan Urusetia Persidangan Antarabangsa — Federal Honours",
        "seed_url": URL,
        "status": "completed" if not failures else "partial",
        "directory_pages": 1,
        "embedded_popups_seen": len(popups),
        "award_popups_processed": len(rows),
        "downloaded_images": len(rows),
        "failed_images": failures,
        "candidate_file": OUT.relative_to(ROOT).as_posix(),
        "page_cache": CACHE.relative_to(ROOT).as_posix(),
        "image_cache": RAW_DIR.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"popups": len(popups), "awards": len(rows), "images": len(rows), "failures": len(failures)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
