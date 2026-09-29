"""Sweep the complete public MedalBook Philippines catalogue."""

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/philippines"
sweep.SOURCE_SLUG = "philippines"
sweep.SOURCE_SYSTEM = "MedalBook Philippines catalogue"
sweep.COUNTRY_LABEL = "Philippines"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/philippines-1",
    sweep.BASE + "/asia/philippines-1?page=2",
    sweep.BASE + "/asia/philippines/orders",
    sweep.BASE + "/asia/philippines/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_philippines"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_philippines.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_philippines_2026-09-28.json"


if __name__ == "__main__": sweep.main()
