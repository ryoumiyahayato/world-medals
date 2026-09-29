"""Sweep every current Spink archive result for the query 'Ottoman Empire'."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "sources/pages/spink_ottoman_archive"
RAW = ROOT / "data/raw_candidates/spink_ottoman_archive.jsonl"
REPORT = ROOT / "data/source_sweeps/spink_ottoman_archive_complete_2026-09-27.json"
BASE = "https://www.spink.com"
QUERY = "Ottoman Empire"
UA = "Mozilla/5.0 (compatible; world-medals research cache/1.0)"

AWARD_TERMS = re.compile(
    r"\b(order|medal|medals|decoration|decorations|badge|star|insignia|imtiaz|iftihar|medjid|osmani|charity|shefkat|crimea|gallipoli)\b",
    re.I,
)
EXCLUDE_TERMS = re.compile(
    r"\b(coin|coins|kurush|piastre|para|sultani|banknote|banknotes|state notes|currency|stamp|stamps)\b",
    re.I,
)


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
    all_items: list[dict] = []
    for page in range(1, 6):
        params = urllib.parse.urlencode({
            "AuctionLotSearch[look_in]": "archive",
            "AuctionLotSearch[keyword]": QUERY,
            "page": page,
        })
        url = f"{BASE}/archive/index?{params}"
        text = fetch(url, PAGES / f"results_{page}.html")
        items = listing_items(text)
        if not items:
            raise RuntimeError(f"No Spink results parsed from page {page}")
        all_items.extend(items)
        if page < 5:
            time.sleep(2)

    unique = {item["result_key"]: item for item in all_items}
    if len(unique) != 83:
        raise RuntimeError(f"Expected the current 83 Spink results, parsed {len(unique)}")

    candidates = []
    for item in unique.values():
        haystack = f'{item["title"]} {item["listing_description"]}'
        award_candidate = bool(AWARD_TERMS.search(haystack)) and not bool(EXCLUDE_TERMS.search(haystack))
        item_id = item["lot_path_id"] or f'result-{item["result_key"]}'
        row = {
            "source_id": f'spink-archive-{item_id}',
            "source_system": "Spink archive search: Ottoman Empire",
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
            time.sleep(2)
        elif award_candidate:
            row["status"] = "ARCHIVE_RESULT_WITHOUT_ACCESSIBLE_LOT_LINK"
        candidates.append(row)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
    award_rows = [row for row in candidates if row["category"] == "award_candidate"]
    REPORT.write_text(json.dumps({
        "as_of": str(date.today()),
        "source_id": "spink-ottoman-archive-query",
        "source_title": "Spink Lots Archive search: Ottoman Empire",
        "query": QUERY,
        "status": "complete_current_result_set",
        "result_pages_processed": 5,
        "all_results_processed": len(candidates),
        "award_candidate_lot_pages_processed": len(award_rows),
        "award_candidate_image_urls": sum(len(row["image_original_urls"]) for row in award_rows),
        "non_award_results_retained_for_audit": len(candidates) - len(award_rows),
        "candidate_file": RAW.relative_to(ROOT).as_posix(),
        "notes": [
            "Every current result page and every award-candidate lot page was cached.",
            "Coins, banknotes, stamps and currency lots remain in the raw audit file as non-award results and are not catalogue candidates.",
            "The query is a reproducible bounded source sweep, not a claim that all possible Spink wording variants have been exhausted.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Spink Ottoman archive: {len(candidates)} results, {len(award_rows)} award candidates, {sum(len(r['image_original_urls']) for r in award_rows)} large images")


if __name__ == "__main__":
    main()
