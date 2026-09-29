"""Sweep the complete public MedalBook India catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/india/"
sweep.SOURCE_SLUG = "india"
sweep.SOURCE_SYSTEM = "MedalBook India catalogue"
sweep.COUNTRY_LABEL = "India and historical Indian polities"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/india-1",
    *[sweep.BASE + f"/asia/india-1?page={page}" for page in range(2, 9)],
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_india"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_india.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_india_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
