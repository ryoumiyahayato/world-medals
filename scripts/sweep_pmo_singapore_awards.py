"""Exhaust the Singapore PMO Information on Medals directory and cache its official images."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.pmo.gov.sg"
INDEX = BASE + "/national-awards/information-on-medals/"
CACHE = ROOT / "sources/pages/pmo_singapore_awards"
RAW_DIR = ROOT / "assets/raw/pmo_singapore_awards"
OUT = ROOT / "data/raw_candidates/pmo_singapore_awards.jsonl"
STATE = ROOT / "data/source_sweeps/pmo_singapore_awards_2026-09-28.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36 world-medals-research"


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.links=[]; self.images=[]; self.text=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in {"script", "style", "svg"}: self.skip += 1
        if tag == "a" and attrs.get("href"): self.links.append(attrs["href"])
        if tag in {"img", "source"}:
            for key in ("src", "data-src", "srcset"):
                value=attrs.get(key, "") or ""
                if value: self.images.extend(part.strip().split()[0] for part in value.split(","))
    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg"} and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            value=re.sub(r"\s+", " ", html.unescape(data)).strip()
            if value: self.text.append(value)


def fetch(url: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url, headers={"User-Agent": UA, "Referer": INDEX, "Accept": "text/html,image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
            with urllib.request.urlopen(request, timeout=60) as response: return response.read()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise last


def parse(raw: bytes) -> Parser:
    parser=Parser(); parser.feed(raw.decode("utf-8", errors="replace")); return parser


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True); RAW_DIR.mkdir(parents=True, exist_ok=True)
    index_raw=fetch(INDEX); (CACHE / "index.html").write_bytes(index_raw)
    index_parser=parse(index_raw)
    pages=sorted({urllib.parse.urljoin(BASE, href) for href in index_parser.links if "/national-awards/information-on-medals/" in href and urllib.parse.urljoin(BASE, href).rstrip("/") != INDEX.rstrip("/")})
    rows=[]; images=[]; failures=[]
    for number, url in enumerate(pages, 1):
        slug=urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1]
        try:
            page_cache = CACHE / f"{slug}.html"
            raw = page_cache.read_bytes() if page_cache.is_file() and page_cache.stat().st_size > 10000 else fetch(url)
            page_cache.write_bytes(raw); parser=parse(raw)
            text=" ".join(parser.text)
            title=next((part for part in parser.text if part.lower().startswith("the ") and "(" in part), parser.text[0] if parser.text else slug.replace("-", " ").title()).split(" | ", 1)[0]
            image_urls=[]
            for value in parser.images:
                absolute=urllib.parse.urljoin(url, value)
                filename=urllib.parse.urlsplit(absolute).path.rsplit("/", 1)[-1].lower()
                if "isomer-user-content.by.gov.sg" in absolute and "medal" in filename and absolute not in image_urls: image_urls.append(absolute)
            local_images=[]
            for image_no, image_url in enumerate(image_urls, 1):
                data=fetch(image_url)
                with Image.open(BytesIO(data)) as decoded:
                    decoded.load(); width,height=decoded.size; fmt=decoded.format
                suffix={"JPEG":"jpg","PNG":"png","WEBP":"webp"}.get(fmt, "img")
                local=RAW_DIR / f"{slug}_{image_no:02d}.{suffix}"; local.write_bytes(data)
                item={"view_no": image_no, "image_url": image_url, "local_path": local.relative_to(ROOT).as_posix(), "width": width, "height": height, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                local_images.append(item); images.append(item | {"page_url": url, "title": title})
            dates=sorted({int(x) for x in re.findall(r"(?<!\d)(1[89]\d{2}|20\d{2})(?!\d)", text)})
            original_match=re.search(r"\(([^()]+)\)", title)
            rows.append({"source_id": f"pmo-singapore-{slug}", "page_title": title, "working_name_zh": "待归并", "name_original": original_match.group(1) if original_match else title, "name_en": title, "date_candidates": dates, "category": "national_award", "grade_material_clues": "见官方页面正文", "object_url": url, "image_page_url": url if local_images else None, "original_images": local_images, "notes": "Singapore Prime Minister's Office official Information on Medals page.", "status": "harvested"})
            time.sleep(0.1)
        except Exception as exc: failures.append({"url": url, "error": repr(exc)})
        print(f"processed {number}/{len(pages)}", flush=True)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in rows), encoding="utf-8")
    STATE.write_text(json.dumps({"as_of":"2026-09-28", "source_id":"pmo_singapore_awards", "source_name":"Singapore PMO — Information on Medals", "seed_url":INDEX, "status":"completed" if not failures and len(rows)==len(pages) else "partial", "directory_pages":1, "discovered_object_pages":len(pages), "processed_object_pages":len(rows), "downloaded_images":len(images), "failed_pages":failures, "candidate_file":OUT.relative_to(ROOT).as_posix(), "page_cache":CACHE.relative_to(ROOT).as_posix(), "image_cache":RAW_DIR.relative_to(ROOT).as_posix()}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"pages":len(rows), "images":len(images), "failures":len(failures)}, ensure_ascii=False))


if __name__ == "__main__": main()
