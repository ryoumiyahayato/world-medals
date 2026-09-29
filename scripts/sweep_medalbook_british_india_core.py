"""Sweep complete MedalBook family pages for core British Indian awards."""
from __future__ import annotations

import urllib.parse
import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/europe/united-kingdom/"
sweep.SOURCE_SLUG = "british-india-core"
sweep.SOURCE_SYSTEM = "MedalBook British India core award families"
sweep.COUNTRY_LABEL = "British India central and imperial awards"
sweep.AS_OF = "2026-09-28"

PATHS = [
    "/europe/united-kingdom/orders/the-most-exalted-order-of-the-star-of-india",
    "/europe/united-kingdom/orders/the-most-eminent-order-of-the-indian-empire",
    "/europe/united-kingdom/orders/the-imperial-order-of-the-crown-of-india",
    "/europe/united-kingdom/medals-decorations/gallantry-decorations/order-of-british-india",
    "/europe/united-kingdom/medals-decorations/gallantry-decorations/indian-order-of-merit",
    "/europe/united-kingdom/medals-decorations/indian-order-of-merit",
    "/europe/united-kingdom/medals-decorations/gallantry-decorations/indian-distinguished-service-medal",
    "/europe/united-kingdom/medals-decorations/gallantry-decorations/indian-police-medal",
    "/europe/united-kingdom/medals-decorations/gallantry-decorations/kaisar-i-hind-medal",
]
sweep.INDEX_URLS = [sweep.BASE + path for path in PATHS]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_british_india_core"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_british_india_core.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_british_india_core_2026-09-28.json"

ALLOWED = tuple(path.rstrip("/") + "/" for path in PATHS)

def core_item_link(href: str) -> str | None:
    url = urllib.parse.urljoin(sweep.BASE, href)
    parsed = urllib.parse.urlsplit(url)
    if parsed.netloc != "www.medalbook.com":
        return None
    if not parsed.path.startswith(ALLOWED):
        return None
    # Parent family pages are seeds, never object records.
    if parsed.path.rstrip("/") in {path.rstrip("/") for path in PATHS}:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))

sweep.item_link = core_item_link

if __name__ == "__main__":
    sweep.main()
