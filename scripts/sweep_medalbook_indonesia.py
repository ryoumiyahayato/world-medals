"""Sweep the complete public MedalBook Indonesia catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/indonesia"
sweep.SOURCE_SLUG = "indonesia"
sweep.SOURCE_SYSTEM = "MedalBook Indonesia catalogue"
sweep.COUNTRY_LABEL = "Indonesia"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [sweep.BASE + "/asia/indonesia-1", sweep.BASE + "/asia/indonesia-1?page=2", sweep.BASE + "/asia/indonesia/orders", sweep.BASE + "/asia/indonesia/medals-decorations"]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_indonesia"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_indonesia.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_indonesia_2026-09-28.json"

if __name__ == "__main__": sweep.main()
