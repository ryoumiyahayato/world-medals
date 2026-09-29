"""Sweep the complete public MedalBook Myanmar/Burma catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/myanmar"
sweep.SOURCE_SLUG = "myanmar"
sweep.SOURCE_SYSTEM = "MedalBook Myanmar/Burma catalogue"
sweep.COUNTRY_LABEL = "Myanmar/Burma"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [sweep.BASE + "/asia/myanmar/"] + [sweep.BASE + f"/asia/myanmar-1?page={p}" for p in (2,3)] + [sweep.BASE + "/asia/myanmar/orders", sweep.BASE + "/asia/myanmar/medals-decorations"]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_myanmar"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_myanmar.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_myanmar_2026-09-28.json"

if __name__ == "__main__": sweep.main()
