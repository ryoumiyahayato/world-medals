"""Sweep the complete public MedalBook Thailand catalogue into raw candidates."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.medalbook.com"
COUNTRY_PREFIX = "/asia/thailand/"
SOURCE_SLUG = "thailand"
SOURCE_SYSTEM = "MedalBook Thailand catalogue"
COUNTRY_LABEL = "Thailand"
AS_OF = "2026-09-27"
INDEX_URLS = [
    BASE + "/asia/thailand-1",
    BASE + "/asia/thailand-1?page=2",
    BASE + "/asia/thailand/orders",
    BASE + "/asia/thailand/medals-decorations",
]
CACHE = ROOT / "sources/pages/medalbook_thailand"
OUT = ROOT / "data/raw_candidates/medalbook_thailand.jsonl"
STATE = ROOT / "data/source_sweeps/medalbook_thailand_2026-09-27.json"
UA = "world-medals research catalogue/1.0"


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[str] = []
        self.meta: dict[str, str] = {}
        self.text: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): v or "" for k, v in attrs}
        if tag in {"script", "style", "svg"}:
            self.skip += 1
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if tag in {"img", "source"}:
            for key in ("src", "data-src", "srcset"):
                value = attr.get(key, "")
                if value:
                    self.images.extend(x.strip().split(" ")[0] for x in value.split(","))
        if tag == "meta":
            key = attr.get("property") or attr.get("name")
            if key and attr.get("content"):
                self.meta[key.lower()] = html.unescape(attr["content"]).strip()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            value = re.sub(r"\s+", " ", html.unescape(data)).strip()
            if value:
                self.text.append(value)


def cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".html")


def fetch(url: str) -> str:
    path = cache_path(url)
    if path.exists() and path.stat().st_size:
        return path.read_text(encoding="utf-8", errors="replace")
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read()
    text = raw.decode("utf-8", errors="replace")
    path.write_text(text, encoding="utf-8")
    time.sleep(0.15)
    return text


def parse(text: str) -> Parser:
    parser = Parser()
    parser.feed(text)
    return parser


def item_link(href: str) -> str | None:
    url = urllib.parse.urljoin(BASE, href)
    parsed = urllib.parse.urlsplit(url)
    if parsed.netloc != "www.medalbook.com" or not parsed.path.startswith(COUNTRY_PREFIX):
        return None
    parts = parsed.path[len(COUNTRY_PREFIX):].strip("/").split("/")
    if len(parts) < 3:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    links: set[str] = set()
    index_counts: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    for url in INDEX_URLS:
        try:
            parser = parse(fetch(url))
            found = {x for href in parser.links if (x := item_link(href))}
            links.update(found)
            index_counts[url] = len(found)
        except Exception as exc:
            failures.append({"url": url, "error": repr(exc)})
    rows = []

    def process_item(url: str):
        try:
            parser = parse(fetch(url))
            title = parser.meta.get("og:title", "").strip() or urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("-", " ")
            description = parser.meta.get("og:description", "").strip()
            body = re.sub(r"\s+", " ", " ".join(parser.text))
            image_urls = sorted({
                urllib.parse.urljoin(BASE, value)
                for value in parser.images
                if "/attachments/" in value and re.search(r"\.(?:jpe?g|png)(?:\?|$)", value, re.I)
            })
            parts = urllib.parse.urlsplit(url).path[len(COUNTRY_PREFIX):].strip("/").split("/")
            dates = sorted({int(x) for x in re.findall(r"(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)", title + " " + description + " " + body[:4000])})
            return ({
                "source_id": f"medalbook-{SOURCE_SLUG}-" + hashlib.sha1(url.encode()).hexdigest()[:16],
                "source_system": SOURCE_SYSTEM,
                "page_title": title,
                "working_name_zh": "待译",
                "original_name": title,
                "english_name": title,
                "aliases": [],
                "date_candidates": dates,
                "category": parts[0],
                "family_hint": parts[1].replace("-", " "),
                "grade_material_clues": title,
                "page_url": url,
                "image_page_url": url if image_urls else None,
                "original_image_urls": image_urls,
                "notes": description or "来源页未提供摘要；缓存正文已保留。",
                "status": "RAW_CANDIDATE",
                "cache_file": cache_path(url).relative_to(ROOT).as_posix(),
            }, None)
        except Exception as exc:
            return (None, {"url": url, "error": repr(exc)})

    ordered_links = sorted(links)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_item, url): url for url in ordered_links}
        for number, future in enumerate(as_completed(futures), 1):
            row, failure = future.result()
            if row is not None:
                rows.append(row)
            if failure is not None:
                failures.append(failure)
            if number % 25 == 0:
                print(f"processed {number}/{len(links)}", flush=True)
    rows.sort(key=lambda row: row["page_url"])
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    status = "completed" if not failures and len(index_counts) == len(INDEX_URLS) and len(rows) == len(links) else "partial"
    STATE.write_text(json.dumps({
        "as_of": AS_OF,
        "source_id": f"medalbook_{SOURCE_SLUG}",
        "source_name": f"MedalBook — {COUNTRY_LABEL} complete public catalogue",
        "seed_url": INDEX_URLS[0],
        "status": status,
        "planned_index_pages": len(INDEX_URLS),
        "processed_index_pages": len(index_counts),
        "index_page_candidate_counts": index_counts,
        "discovered_item_pages": len(links),
        "processed_item_pages": len(rows),
        "item_pages_with_images": sum(bool(row["original_image_urls"]) for row in rows),
        "original_image_urls": sum(len(row["original_image_urls"]) for row in rows),
        "failed_pages": failures,
        "remaining_pages": max(0, len(links) - len(rows)),
        "raw_candidate_file": OUT.relative_to(ROOT).as_posix(),
        "cache_directory": CACHE.relative_to(ROOT).as_posix(),
        "completion_rule": f"Every configured index/category page and every discovered {COUNTRY_LABEL} object/version page were fetched.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "items": len(rows), "images": sum(len(row["original_image_urls"]) for row in rows), "failures": len(failures)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
