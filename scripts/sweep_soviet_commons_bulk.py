"""Bulk sweep Wikimedia Commons categories for Soviet state awards.

This is a source-first sweep: category trees are enumerated before any award
record is normalized.  It intentionally records all visible category/file
members, including candidates that will later be excluded (ribbons,
certificates, portraits, recipient galleries).  No site HTML is touched.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sources" / "cache" / "commons_soviet_awards_api"
OUT = ROOT / "data" / "source_sweeps" / "soviet_commons_bulk_2026-09-28.json"
CACHE.mkdir(parents=True, exist_ok=True)

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "world-medals-research/1.0 (offline catalogue; contact unavailable)"}

ROOT_CATEGORIES = [
    "Category:Orders, decorations and medals of the Soviet Union",
    "Category:Orders of the Soviet Union",
    "Category:Medals of the Soviet Union",
    "Category:Military decorations of the Soviet Union",
    "Category:Campaign medals of the Soviet Union",
    "Category:Jubilee medals of the Soviet Union",
]

SKIP_SUBTREE = (
    "Recipients of",
    "Award certificates",
    "Ribbon bars",
    "ribbon bars",
    "Medals of the Soviet Union by material",
    "Medal groups of the Soviet Union",
    "School medals",
    "Academy of Sciences",
)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)[:180]


def cached_api(kind: str, key: str, params: dict[str, Any]) -> dict[str, Any]:
    f = CACHE / f"{kind}_{safe_name(key)}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    # Commons may return a short 429 window even with a conservative cadence;
    # honor Retry-After when present and back off instead of retrying rapidly.
    time.sleep(6.0)
    r = None
    for attempt in range(4):
        r = requests.get(API, params=params, headers=HEADERS, timeout=60)
        if r.status_code != 429:
            break
        delay = int(r.headers.get("Retry-After", "20"))
        delay = max(delay, 20 * (2**attempt))
        print(f"429 from Commons; waiting {delay}s before retry", flush=True)
        time.sleep(delay)
    assert r is not None
    r.raise_for_status()
    data = r.json()
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def category_members(title: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cont: dict[str, Any] = {}
    page = 1
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": title,
            "cmtype": "subcat|file",
            "cmlimit": "500",
            "format": "json",
            **cont,
        }
        data = cached_api("categorymembers", f"{title}_{page}", params)
        out.extend(data.get("query", {}).get("categorymembers", []))
        if "continue" not in data:
            break
        cont = data["continue"]
        page += 1
    return out


def main() -> None:
    pending = list(ROOT_CATEGORIES)
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    categories: list[dict[str, Any]] = []
    while pending:
        title = pending.pop(0)
        if title in seen:
            continue
        seen.add(title)
        members = category_members(title)
        row = {"category": title, "members": members, "status": "completed"}
        categories.append(row)
        for member in members:
            if member.get("ns") == 14:
                sub = member["title"]
                if not any(token in sub for token in SKIP_SUBTREE):
                    pending.append(sub)
            elif member.get("ns") == 6:
                records.append(
                    {
                        "category": title,
                        "file_title": member.get("title"),
                        "pageid": member.get("pageid"),
                        "ns": 6,
                    }
                )
    result = {
        "as_of": "2026-09-28",
        "sweep_id": "soviet_commons_bulk_2026-09-28",
        "scope": "Wikimedia Commons Soviet Union award category roots and recursively visible award subcategories; recipient/certificate/ribbon/material branches excluded from recursive source sweep",
        "roots": ROOT_CATEGORIES,
        "category_count": len(categories),
        "file_member_count": len(records),
        "categories": categories,
        "files": records,
        "access": {
            "method": "MediaWiki API categorymembers with cached responses and 1.5s pacing for uncached calls",
            "cache_dir": "sources/cache/commons_soviet_awards_api",
            "image_pages_not_yet_downloaded": True,
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"categories": len(categories), "files": len(records), "out": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
