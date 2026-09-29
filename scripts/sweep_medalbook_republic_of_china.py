"""Sweep the complete public MedalBook Republic of China catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/china/republic-of-china-1912-date/"
sweep.SOURCE_SLUG = "republic_of_china"
sweep.SOURCE_SYSTEM = "MedalBook Republic of China catalogue"
sweep.COUNTRY_LABEL = "Republic of China (1912-date)"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/china/republic-of-china-1912-date",
    sweep.BASE + "/asia/china/republic-of-china-1912-date/orders",
    sweep.BASE + "/asia/china/republic-of-china-1912-date/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_republic_of_china"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_republic_of_china.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_republic_of_china_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
