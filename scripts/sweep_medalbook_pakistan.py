"""Sweep the complete public MedalBook Pakistan orders/medals catalogue."""
from __future__ import annotations

import urllib.parse
import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/pakistan/"
sweep.SOURCE_SLUG = "pakistan"
sweep.SOURCE_SYSTEM = "MedalBook Pakistan catalogue"
sweep.COUNTRY_LABEL = "Pakistan"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [sweep.BASE + "/asia/pakistan-1", sweep.BASE + "/asia/pakistan-1?page=2"]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_pakistan"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_pakistan.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_pakistan_2026-09-28.json"

def award_item_link(href: str) -> str | None:
    url = urllib.parse.urljoin(sweep.BASE, href)
    parsed = urllib.parse.urlsplit(url)
    prefixes = ("/asia/pakistan/orders/", "/asia/pakistan/medals-decorations/")
    if parsed.netloc != "www.medalbook.com" or not parsed.path.startswith(prefixes):
        return None
    parts = parsed.path[len(sweep.COUNTRY_PREFIX):].strip("/").split("/")
    if len(parts) < 3:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))

sweep.item_link = award_item_link

if __name__ == "__main__":
    sweep.main()
