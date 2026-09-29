"""Sweep the complete public MedalBook Laos catalogue into raw candidates."""

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/laos/"
sweep.SOURCE_SLUG = "laos"
sweep.SOURCE_SYSTEM = "MedalBook Laos catalogue"
sweep.COUNTRY_LABEL = "Laos"
sweep.AS_OF = "2026-09-28"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/laos-1",
    sweep.BASE + "/asia/laos/kingdom-of-laos",
    sweep.BASE + "/asia/laos/peoples-democratic-republic-of-laos",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_laos"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_laos.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_laos_2026-09-28.json"


if __name__ == "__main__":
    sweep.main()
