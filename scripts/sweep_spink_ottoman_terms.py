"""Sweep a bounded union of Ottoman award terminology in the Spink archive."""

from __future__ import annotations

import html
import json
import math
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "sources/pages/spink_ottoman_terms"
RAW = ROOT / "data/raw_candidates/spink_ottoman_terms.jsonl"
REPORT = ROOT / "data/source_sweeps/spink_ottoman_terms_2026-09-27.json"
BASE = "https://www.spink.com"
UA = "Mozilla/5.0 (compatible; world-medals research cache/1.0)"

# Terms are deliberately bounded and recorded.  They cover English catalogue
# variants used for the major Ottoman orders and medals rather than asserting
# that every possible Spink wording has been exhausted.
QUERIES = [
    "Medjidie",
    "Médjidié",
    "Osmanieh",
    "Ottoman medal",
    "Turkey",
    "Turkish medal",
    "Turkish War Medal",
    "Turkey Order",
    "Turkish Order",
    "Gallipoli Star",
    "Ottoman War Medal",
    "Turkish Crimea Medal",
    "Imtiyaz",
    "Iftikhar",
    "Liyakat",
    "Liakat",
    "Shefkat",
]

AWARD_TERMS = re.compile(
    r"\b(order|medal|medals|decoration|decorations|badge|star|insignia|imtiaz|imtiyaz|iftihar|"
    r"medjid|osmani|charity|shefkat|crimea|gallipoli|liyakat|liakat)\b",
    re.I,
)
EXCLUDE_TERMS = re.compile(
    r"\b(coin|coins|kurush|piastre|para|sultani|banknote|banknotes|state notes|currency|stamp|stamps)\b",
    re.I,
)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def fetch(url: str, target: Path) -> str:
    if target.is_file() and target.stat().st_size > 500:
        return target.read_text(encoding="utf-8", errors="replace")
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return data.decode("utf-8", errors="replace")


def clean(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def total_items(text: str) -> int:
    match = re.search(r'Showing <b>[^<]+</b> of <b>(\d+)</b> items', text, re.I)
    return int(match.group(1)) if match else 0


def listing_items(text: str) -> list[dict]:
    items = []
    for block in re.split(r'(?=<div data-key=")', text):
        key_match = re.match(r'<div data-key="([^"]+)"', block)
        if not key_match:
            continue
        lot_match = re.search(r'href="/lot/(\d+)"', block)
        title_match = re.search(r'class="title"[^>]*>(.*?)</a>', block, flags=re.I | re.S)
        description_match = re.search(r'class="description"[^>]*>(.*?)</div>', block, flags=re.I | re.S)
        items.append({
            "result_key": key_match.group(1),
            "lot_path_id": lot_match.group(1) if lot_match else None,
            "title": clean(title_match.group(1)) if title_match else "Unavailable archived result",
            "listing_description": clean(description_match.group(1)) if description_match else clean(block)[:1000],
        })
    return items


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    by_key: dict[str, dict] = {}
    query_stats = []
    for query in QUERIES:
        query_slug = slug(query)
        first_url = f"{BASE}/archive/index?" + urllib.parse.urlencode({
            "AuctionLotSearch[look_in]": "archive",
            "AuctionLotSearch[keyword]": query,
            "page": 1,
        })
        first = fetch(first_url, PAGES / f"{query_slug}_1.html")
        total = total_items(first)
        if not total:
            # Spink omits the normal summary wrapper for some one-result pages.
            total = len(listing_items(first))
        pages = max(1, math.ceil(total / 20)) if total else 1
        parsed = []
        for page in range(1, pages + 1):
            if page == 1:
                text = first
            else:
                url = f"{BASE}/archive/index?" + urllib.parse.urlencode({
                    "AuctionLotSearch[look_in]": "archive",
                    "AuctionLotSearch[keyword]": query,
                    "page": page,
                })
                text = fetch(url, PAGES / f"{query_slug}_{page}.html")
                time.sleep(1)
            parsed.extend(listing_items(text))
        if len(parsed) != total:
            raise RuntimeError(f"{query}: expected {total} results, parsed {len(parsed)}")
        query_stats.append({"query": query, "result_count": total, "pages_processed": pages})
        for item in parsed:
            existing = by_key.setdefault(item["result_key"], item)
            existing.setdefault("matched_queries", []).append(query)
        time.sleep(1)

    candidates = []
    for item in by_key.values():
        haystack = f'{item["title"]} {item["listing_description"]}'
        award_candidate = bool(AWARD_TERMS.search(haystack)) and not bool(EXCLUDE_TERMS.search(haystack))
        item_id = item["lot_path_id"] or f'result-{item["result_key"]}'
        row = {
            "source_id": f'spink-terms-{item_id}',
            "source_system": "Spink archive Ottoman terminology sweep",
            "matched_queries": sorted(set(item["matched_queries"])),
            "page_title": item["title"],
            "page_url": f'{BASE}/lot/{item["lot_path_id"]}' if item["lot_path_id"] else None,
            "listing_description": item["listing_description"],
            "category": "award_candidate" if award_candidate else "non_award_result",
            "image_original_urls": [],
            "access_date": str(date.today()),
        }
        if award_candidate and item["lot_path_id"]:
            detail_path = PAGES / f'lot_{item["lot_path_id"]}.html'
            detail = fetch(row["page_url"], detail_path)
            row["image_original_urls"] = sorted(set(re.findall(
                r'https://d3ums4016ncdkp\.cloudfront\.net/auction/large/[^"\']+?\.jpg', detail, flags=re.I
            )))
            description_match = re.search(r'<div class="description">(.*?)</div>', detail, flags=re.I | re.S)
            if description_match:
                row["object_description"] = clean(description_match.group(1))
            row["cache_file"] = detail_path.relative_to(ROOT).as_posix()
            time.sleep(1)
        elif award_candidate:
            row["status"] = "ARCHIVE_RESULT_WITHOUT_ACCESSIBLE_LOT_LINK"
        candidates.append(row)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
    award_rows = [row for row in candidates if row["category"] == "award_candidate"]
    REPORT.write_text(json.dumps({
        "as_of": str(date.today()),
        "source_id": "spink-ottoman-terminology-union",
        "source_title": "Spink Lots Archive: Ottoman award terminology union",
        "queries": query_stats,
        "status": "complete_current_bounded_query_union",
        "deduplicated_results_processed": len(candidates),
        "award_candidate_lot_pages_processed": len(award_rows),
        "award_candidate_image_urls": sum(len(row["image_original_urls"]) for row in award_rows),
        "non_award_results_retained_for_audit": len(candidates) - len(award_rows),
        "candidate_file": RAW.relative_to(ROOT).as_posix(),
        "notes": [
            "Every current result page for every recorded query was processed.",
            "The union is deduplicated by Spink result key before object-page retrieval.",
            "Coins, currency and stamps remain in the raw audit file but are not catalogue candidates.",
            "This closes the recorded terminology set, not every conceivable spelling in the whole Spink archive.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Spink terminology union: {len(candidates)} results, {len(award_rows)} award candidates")


if __name__ == "__main__":
    main()
