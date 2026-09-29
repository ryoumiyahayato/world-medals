"""Sweep the complete public MedalBook Manchukuo catalogue."""

import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = "/asia/japan/manchukuo/"
sweep.SOURCE_SLUG = "manchukuo"
sweep.SOURCE_SYSTEM = "MedalBook Manchukuo catalogue"
sweep.COUNTRY_LABEL = "Manchukuo"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/japan/manchukuo",
    sweep.BASE + "/asia/japan/manchukuo/orders",
    sweep.BASE + "/asia/japan/manchukuo/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_manchukuo"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_manchukuo.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_manchukuo_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
