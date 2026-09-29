"""Sweep the complete public MedalBook Brunei catalogue into raw candidates."""

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/brunei/"
sweep.SOURCE_SLUG = "brunei"
sweep.SOURCE_SYSTEM = "MedalBook Brunei catalogue"
sweep.COUNTRY_LABEL = "Brunei"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/brunei-1",
    sweep.BASE + "/asia/brunei/orders",
    sweep.BASE + "/asia/brunei/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_brunei"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_brunei.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_brunei_2026-09-28.json"


if __name__ == "__main__":
    sweep.main()
