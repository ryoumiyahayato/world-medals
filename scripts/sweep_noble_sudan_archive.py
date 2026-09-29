"""Sweep the complete Noble Numismatics archive result set for ``Sudan``.

This is a source inventory pass.  It follows every result page, stores every
lot row as a raw candidate, and keeps British/Egyptian campaign material
separate from indigenous Sudanese orders during later normalization.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sources/pages/noble_sudan_archive"
OUTPUT = ROOT / "data/raw_candidates/noble_sudan_archive.jsonl"
SWEEP = ROOT / "data/source_sweeps/noble_sudan_archive_2026-09-27.json"
BASE = "https://www.noble.com.au"
HEADERS = {"User-Agent": "world-medals research catalogue/1.0"}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def fetch(url: str) -> tuple[bytes, str]:
    with urlopen(Request(url, headers=HEADERS), timeout=45) as response:
        raw = response.read()
    return raw, raw.decode("utf-8", errors="replace")


def clean(fragment: str) -> str:
    value = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    rows: dict[str, dict] = {}
    page = 1
    expected_total = None
    while True:
        url = f"{BASE}/auctions/archive/search?q=Sudan&c=51&p={page}"
        raw, text = fetch(url)
        atomic_text(CACHE / f"search_page_{page:03d}.html", text)
        summary = re.search(r"Showing lots\s+[\d,]+-[\d,]+\s+of\s+([\d,]+)", text)
        if summary:
            expected_total = int(summary.group(1).replace(",", ""))
        articles = re.findall(
            r'<article class="catalogue-lot-row">(.*?)</article>', text, re.S
        )
        if not articles:
            break
        for article in articles:
            lot_id = re.search(r'href="/auctions/lot/\?id=(\d+)"', article)
            lot_number = re.search(r'class="catalogue-lot-row__lot">\s*Lot\s+([^<]+)', article)
            sale = re.search(r'href="/auctions/sale/(\d+)"', article)
            desc = re.search(r'class="catalogue-lot-row__description">(.*?)</p>', article, re.S)
            image_urls = re.findall(r'(?:data-catalogue-preview-src(?:-\d+)?|src)="([^"]*catalogue-images[^"]+)"', article)
            if not lot_id:
                continue
            identifier = lot_id.group(1)
            description = clean(desc.group(1)) if desc else ""
            native_terms = re.compile(
                r"Order of (?:the )?(?:Republic|Two Niles|Duty|Sport|Palm|Civil|Political)|"
                r"Good Accomplishment|Political Merit|Conscientious Work|Sudan Republic",
                re.I,
            )
            rows[identifier] = {
                "source": "Noble Numismatics",
                "source_id": f"noble-archive-lot-{identifier}",
                "source_scope": "Noble archive search: Sudan, Orders Decorations & Medals",
                "sale": int(sale.group(1)) if sale else None,
                "lot": clean(lot_number.group(1)) if lot_number else "",
                "title": description[:240],
                "description": description,
                "object_url": f"{BASE}/auctions/lot/?id={identifier}",
                "image_original_urls": sorted({urljoin(BASE, html.unescape(item)) for item in image_urls}),
                "classification_hint": "native_sudan_award_candidate" if native_terms.search(description) else "sudan_campaign_or_other_candidate",
                "search_page": page,
                "search_page_sha256": hashlib.sha256(raw).hexdigest(),
                "accessed": str(date.today()),
                "status": "RAW_CANDIDATE_PENDING_NORMALIZATION",
            }
        if f"Page {page} of" not in text or "pagination__link--next" not in text:
            break
        page += 1
        time.sleep(0.2)

    ordered = sorted(rows.values(), key=lambda row: (-int(row["sale"] or 0), int(re.sub(r"\D", "", row["lot"]) or 0)))
    atomic_text(OUTPUT, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ordered))
    native = [row for row in ordered if row["classification_hint"] == "native_sudan_award_candidate"]
    atomic_text(SWEEP, json.dumps({
        "as_of": str(date.today()),
        "source_id": "noble_sudan_archive",
        "status": "completed_current_archive_search_result_set",
        "query": "Sudan",
        "category": "Orders, Decorations & Medals",
        "pages_processed": page,
        "expected_result_count": expected_total,
        "raw_candidates": len(ordered),
        "native_sudan_award_candidates": len(native),
        "results_with_images": sum(bool(row["image_original_urls"]) for row in ordered),
        "raw_candidate_path": OUTPUT.relative_to(ROOT).as_posix(),
        "notes": "Every visible page in the bounded search result was processed. Campaign medals, foreign recipient groups and indigenous Sudanese awards remain distinct normalization classes.",
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"swept {len(ordered)} Noble Sudan results across {page} pages; {len(native)} native-award candidates")
    for row in native:
        print(row["source_id"], row["sale"], row["lot"], row["description"][:220])


if __name__ == "__main__":
    main()
