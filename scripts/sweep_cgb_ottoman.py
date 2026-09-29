"""Sweep CGB's current Ottoman search result set into a reusable local cache.

This is a source sweep, not an ingestion script: it records every returned
result, fetches every medal/object page in scope, and leaves family/variant
normalization to a later batch.
"""

from __future__ import annotations

import hashlib
import html
import http.cookiejar
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sources" / "pages" / "cgb_ottoman"
RAW = ROOT / "data" / "raw_candidates" / "cgb_ottoman.jsonl"
REPORT = ROOT / "data" / "source_sweeps" / "cgb_ottoman_current.json"
BASE = "https://www.cgb.fr/"
QUERIES = [
    "OTTOMAN",
    "TURQUIE MEDAILLE",
    "ABDUL MEDJID MEDAILLE",
    "ORDRE MEDJIDIE",
    "ORDRE OSMANIE",
]
UA = "Mozilla/5.0 world-medals-research/1.0"


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def request(opener, url: str, data: bytes | None = None) -> bytes:
    error = None
    for attempt in range(3):
        try:
            req = Request(url, data=data, headers={"User-Agent": UA})
            with opener.open(req, timeout=35) as response:
                return response.read()
        except Exception as exc:
            error = exc
            time.sleep(1.5 * (attempt + 1))
    raise error  # type: ignore[misc]


def field(text: str, label: str) -> str | None:
    pattern = (
        rf"<span>\s*{re.escape(label)}\s*:\s*</span>"
        rf"\s*<span[^>]*>\s*(.*?)\s*</span>"
    )
    match = re.search(pattern, text, re.I)
    return clean(match.group(1)) if match else None


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request(opener, BASE)
    results_by_id = {}
    query_counts = {}
    for query in QUERIES:
        payload = urlencode(
            {
                "data": query,
                "page": "1",
                "enstock": "false",
                "titre": "false",
                "exact": "false",
                "reinit": "true",
            }
        ).encode()
        search_bytes = request(opener, urljoin(BASE, "ajax/js_recherche.php"), payload)
        slug = re.sub(r"[^a-z0-9]+", "_", query.lower()).strip("_")
        (CACHE / f"search_{slug}_page1.json").write_bytes(search_bytes)
        message = json.loads(search_bytes.decode("utf-8")).get("message", "")
        query_items = []
        for match in re.finditer(
            r"<div class='bloc[^']*' id='(?P<id>[a-z]+_[0-9]+)' "
            r"data-lien='(?P<href>[^']+)'.*?"
            r"<div class='titre_objet'>(?P<title>.*?)</div>",
            message,
            re.I | re.S,
        ):
            item = match.groupdict()
            item["title"] = clean(item["title"])
            item["url"] = urljoin(BASE, item.pop("href"))
            query_items.append(item)
            results_by_id[item["id"]] = item
        query_counts[query] = len(query_items)
    results = list(results_by_id.values())

    # CGB's global search includes coins, jetons and banknotes.  Every medal
    # result (fme_) is fetched; other departments remain in the audit record.
    candidates = [item for item in results if item["id"].startswith("fme_")]
    rows = []
    failures = []
    for index, item in enumerate(candidates, 1):
        item_id = item["id"]
        try:
            cache_file = CACHE / f"{item_id}.html"
            if cache_file.exists() and cache_file.stat().st_size > 5000:
                page_bytes = cache_file.read_bytes()
            else:
                page_bytes = request(opener, item["url"])
                cache_file.write_bytes(page_bytes)
            page = page_bytes.decode("utf-8", errors="replace")
            page_text = clean(page)
            image_match = re.search(
                rf"//images3\.cgb\.fr/images/medaille/{re.escape(item_id)}\.jpg",
                page,
                re.I,
            )
            title = item["title"]
            formal_scope = bool(
                re.search(
                    r"^TURQUIE\s+-\s+(?:EMPIRE OTTOMAN|SULTAN ABDOUL)|"
                    r"ORDRE (?:DE |DU )?(?:MEDJIDIE|L.OSMANI)",
                    title,
                    re.I,
                )
            )
            related_scope = not formal_scope and bool(
                re.search(r"OTTOMAN|TURQUIE|ABDUL|ABDÜL|CONSTANTINOPLE", title, re.I)
            )
            rows.append(
                {
                    "source_id": f"cgb-{item_id}",
                    "source_system": "CGB global archive search — OTTOMAN",
                    "page_title": title,
                    "working_name_zh": "待归并",
                    "original_name": title,
                    "english_name": None,
                    "date_candidates": [field(page, "Date")] if field(page, "Date") else [],
                    "category": "award_or_medal_object" if formal_scope else "ottoman_related_medal" if related_scope else "search_false_positive",
                    "grade_material_clues": {
                        "type": field(page, "Type"),
                        "metal": field(page, "Métal"),
                        "diameter": field(page, "Diamètre"),
                        "weight": field(page, "Poids"),
                    },
                    "page_url": item["url"],
                    "image_page_url": item["url"],
                    "original_image_urls": [
                        f"https://images3.cgb.fr/images/medaille/{item_id}.jpg"
                    ]
                    if image_match
                    else [],
                    "notes": page_text[:900],
                    "status": "RAW_CANDIDATE" if formal_scope else "RELATED_CANDIDATE" if related_scope else "OUT_OF_SCOPE_SEARCH_HIT",
                    "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
                }
            )
        except Exception as exc:  # keep sweep moving and preserve exact gap
            failures.append({"id": item_id, "url": item["url"], "error": str(exc)})
        if index % 10 == 0:
            time.sleep(0.5)

    with RAW.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    in_scope_rows = [row for row in rows if row["status"] == "RAW_CANDIDATE"]
    related_rows = [row for row in rows if row["status"] == "RELATED_CANDIDATE"]
    report = {
        "as_of": str(date.today()),
        "source_id": "cgb_ottoman_current",
        "source_name": "CGB global archive search",
        "queries": QUERIES,
        "query_result_counts": query_counts,
        "status": "complete_current_query" if not failures else "partial_item_failures",
        "search_pages": 1,
        "all_results": len(results),
        "medal_department_results": len(candidates),
        "item_pages_fetched": len(rows),
        "item_pages_failed": len(failures),
        "ottoman_scope_candidates": len(in_scope_rows),
        "ottoman_related_candidates": len(related_rows),
        "false_positive_medal_pages": len(rows) - len(in_scope_rows) - len(related_rows),
        "pagination_note": "The current AJAX result returned the full result set in one response.",
        "raw_candidate_file": str(RAW.relative_to(ROOT)).replace("\\", "/"),
        "cache_directory": str(CACHE.relative_to(ROOT)).replace("\\", "/"),
        "failures": failures,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
