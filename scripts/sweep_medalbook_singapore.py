"""Sweep the complete public MedalBook Singapore catalogue into raw candidates."""

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/singapore/"
sweep.SOURCE_SLUG = "singapore"
sweep.SOURCE_SYSTEM = "MedalBook Singapore catalogue"
sweep.COUNTRY_LABEL = "Singapore"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/singapore-1",
    sweep.BASE + "/asia/singapore/orders",
    sweep.BASE + "/asia/singapore/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_singapore"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_singapore.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_singapore_2026-09-28.json"


if __name__ == "__main__":
    sweep.main()
