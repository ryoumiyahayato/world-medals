"""Recursively sweep the public MedalBook Ottoman catalogue into raw candidates.

This is intentionally a source-ingestion pass: it records the catalogue's own
labels and URLs without attempting award-family normalization.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.medalbook.com"
PATH = "/europe-east/turkey/ottoman-empire-1299-1922"
INDEX_URLS = (
    [BASE + PATH]
    + [BASE + PATH + f"?page={n}" for n in range(2, 5)]
    + [BASE + PATH + "/badges-3", BASE + PATH + "/insignia-4"]
)
CACHE = ROOT / "sources" / "pages" / "medalbook_ottoman"
OUT = ROOT / "data" / "raw_candidates" / "medalbook_ottoman.jsonl"
STATE = ROOT / "data" / "source_sweeps" / "medalbook_ottoman.json"
UA = "world-medals research catalogue/1.0"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[str] = []
        self.meta: dict[str, str] = {}
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): v or "" for k, v in attrs}
        if tag in {"script", "style", "svg"}:
            self._skip += 1
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
        if tag in {"script", "style", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
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
    with urllib.request.urlopen(request, timeout=35) as response:
        raw = response.read()
    text = raw.decode("utf-8", errors="replace")
    path.write_text(text, encoding="utf-8")
    time.sleep(0.18)
    return text


def parse(text: str) -> PageParser:
    parser = PageParser()
    parser.feed(text)
    return parser


def normalize_link(href: str) -> str | None:
    url = urllib.parse.urljoin(BASE, href)
    parsed = urllib.parse.urlsplit(url)
    accepted = (
        parsed.path.startswith(PATH + "/"),
        parsed.path.startswith("/europe-east/turkey/orders/"),
        parsed.path.startswith("/europe-east/turkey/medals-decorations/"),
        parsed.path.startswith("/europe-east/turkey/badges-3/"),
        parsed.path.startswith("/europe-east/turkey/insignia-4/"),
        parsed.path.startswith("/europe-east/turkey/badges-insignia/"),
    )
    if parsed.netloc != "www.medalbook.com" or not any(accepted):
        return None
    if parsed.path.startswith("/europe-east/turkey/badges-insignia/"):
        remainder = parsed.path[len("/europe-east/turkey/badges-insignia/") :].strip("/")
        if "/" not in remainder:  # family/category landing page, not an object page
            return None
    if parsed.path.rstrip("/") in {
        PATH + "/orders",
        PATH + "/medals-decorations",
        PATH + "/badges-3",
        PATH + "/insignia-4",
    }:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def category_for(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    rest = path[len(PATH) + 1 :] if path.startswith(PATH + "/") else path[len("/europe-east/turkey/") :]
    return rest.split("/", 1)[0] if rest else "unknown"


def family_hint_for(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    rest = path[len(PATH) + 1 :] if path.startswith(PATH + "/") else path[len("/europe-east/turkey/") :]
    parts = rest.split("/")
    return parts[1].replace("-", " ") if len(parts) > 1 else "待核"


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    links: set[str] = set()
    index_counts: dict[str, int] = {}
    failures: list[dict[str, str]] = []

    for url in INDEX_URLS:
        try:
            parser = parse(fetch(url))
            found = {x for href in parser.links if (x := normalize_link(href))}
            links.update(found)
            index_counts[url] = len(found)
        except Exception as exc:  # preserve exact sweep gaps
            failures.append({"url": url, "error": repr(exc)})

    rows: list[dict[str, object]] = []
    for number, url in enumerate(sorted(links), 1):
        try:
            parser = parse(fetch(url))
            title = parser.meta.get("og:title", "").strip() or urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("-", " ")
            description = parser.meta.get("og:description", "").strip()
            body = " ".join(parser.text)
            body = re.sub(r"\s+", " ", body)
            image_urls = sorted({
                urllib.parse.urljoin(BASE, item)
                for item in parser.images
                if "/attachments/" in item and re.search(r"\.(?:jpe?g|png)(?:\?|$)", item, re.I)
            })
            dates = sorted({int(x) for x in re.findall(r"(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)", title + " " + description)})
            category = category_for(url)
            family_hint = family_hint_for(url)
            rows.append({
                "source_id": "medalbook-ottoman-" + hashlib.sha1(url.encode()).hexdigest()[:16],
                "source_system": "MedalBook Ottoman Empire catalogue",
                "page_title": title,
                "working_name_zh": "待译",
                "original_name": title,
                "english_name": title,
                "aliases": [],
                "date_candidates": dates,
                "category": category,
                "family_hint": family_hint,
                "grade_material_clues": title,
                "page_url": url,
                "image_page_url": url if image_urls else None,
                "original_image_urls": image_urls,
                "notes": description or "来源页未提供可用摘要；待归并时按缓存正文提取。",
                "status": "RAW_CANDIDATE",
                "cache_file": str(cache_path(url).relative_to(ROOT)).replace("\\", "/"),
            })
        except Exception as exc:
            failures.append({"url": url, "error": repr(exc)})
        if number % 25 == 0:
            print(f"processed {number}/{len(links)}")

    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    status = "complete" if not failures and len(INDEX_URLS) == len(index_counts) else "partial"
    STATE.write_text(json.dumps({
        "source_id": "medalbook_ottoman",
        "source_name": "MedalBook — Ottoman Empire (1299–1922)",
        "seed_url": INDEX_URLS[0],
        "status": status,
        "planned_index_pages": len(INDEX_URLS),
        "processed_index_pages": len(index_counts),
        "index_page_candidate_counts": index_counts,
        "discovered_item_pages": len(links),
        "processed_item_pages": len(rows),
        "failed_pages": failures,
        "remaining_pages": max(0, len(links) - len(rows)),
        "raw_candidate_file": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "cache_directory": str(CACHE.relative_to(ROOT)).replace("\\", "/"),
        "completion_rule": "All four award pages, the badge and insignia category pages, and every discovered Ottoman item page were fetched.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "items": len(rows), "failures": len(failures)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
