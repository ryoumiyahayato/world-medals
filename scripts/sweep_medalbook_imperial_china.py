"""Sweep the complete public MedalBook Imperial China catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/china/imperial-china-1796-1912/"
sweep.SOURCE_SLUG = "imperial_china"
sweep.SOURCE_SYSTEM = "MedalBook Imperial China catalogue"
sweep.COUNTRY_LABEL = "Imperial China (1796-1912)"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/china/imperial-china-1796-1912",
    sweep.BASE + "/asia/china/imperial-china-1796-1912/orders",
    sweep.BASE + "/asia/china/imperial-china-1796-1912/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_imperial_china"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_imperial_china.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_imperial_china_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
