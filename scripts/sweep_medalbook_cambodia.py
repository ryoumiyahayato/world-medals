"""Sweep the complete public MedalBook Cambodia catalogue into raw candidates."""

from pathlib import Path

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/cambodia/"
sweep.SOURCE_SLUG = "cambodia"
sweep.SOURCE_SYSTEM = "MedalBook Cambodia catalogue"
sweep.COUNTRY_LABEL = "Cambodia"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/cambodia-1",
    sweep.BASE + "/asia/cambodia-1?page=2",
    sweep.BASE + "/asia/cambodia/cambodia-french-protectorate-1863-1948",
    sweep.BASE + "/asia/cambodia/kingdom-of-cambodia-1948-1970",
    sweep.BASE + "/asia/cambodia/peoples-republic-of-kampuchea-1979-1989",
    sweep.BASE + "/asia/cambodia/kingdom-of-cambodia-1993-date",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_cambodia"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_cambodia.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_cambodia_2026-09-28.json"


if __name__ == "__main__":
    sweep.main()
