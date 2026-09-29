"""Sweep the complete public MedalBook South Korea catalogue for an official-list differential."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/korea/south-korea/"
sweep.SOURCE_SLUG = "south_korea"
sweep.SOURCE_SYSTEM = "MedalBook South Korea catalogue"
sweep.COUNTRY_LABEL = "South Korea"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/korea/south-korea-1",
    sweep.BASE + "/asia/korea/south-korea/orders",
    sweep.BASE + "/asia/korea/south-korea/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_south_korea"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_south_korea.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_south_korea_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
