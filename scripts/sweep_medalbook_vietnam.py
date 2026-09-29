"""Sweep the complete public MedalBook Vietnam catalogue across all four historical periods."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/vietnam/"
sweep.SOURCE_SLUG = "vietnam"
sweep.SOURCE_SYSTEM = "MedalBook Vietnam catalogue"
sweep.COUNTRY_LABEL = "Vietnam historical polities"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/vietnam-1",
    sweep.BASE + "/asia/vietnam-1?page=2",
    sweep.BASE + "/asia/vietnam-1?page=3",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_vietnam"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_vietnam.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_vietnam_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
