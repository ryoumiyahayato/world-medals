"""Sweep the complete public MedalBook North Korea catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/korea/north-korea/"
sweep.SOURCE_SLUG = "north_korea"
sweep.SOURCE_SYSTEM = "MedalBook North Korea catalogue"
sweep.COUNTRY_LABEL = "North Korea"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/korea/north-korea-1",
    sweep.BASE + "/asia/korea/north-korea/orders",
    sweep.BASE + "/asia/korea/north-korea/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_north_korea"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_north_korea.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_north_korea_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
