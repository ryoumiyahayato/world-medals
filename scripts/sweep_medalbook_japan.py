"""Sweep the complete public MedalBook Japan (excluding Manchukuo) catalogue."""

from pathlib import Path

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/japan/japan/"
sweep.SOURCE_SLUG = "japan"
sweep.SOURCE_SYSTEM = "MedalBook Japan catalogue"
sweep.COUNTRY_LABEL = "Japan"
sweep.INDEX_URLS = [
    sweep.BASE + "/asia/japan/japan",
    sweep.BASE + "/asia/japan/japan?page=2",
    sweep.BASE + "/asia/japan/japan/orders",
    sweep.BASE + "/asia/japan/japan/medals-decorations",
]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_japan"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_japan.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_japan_2026-09-27.json"


if __name__ == "__main__":
    sweep.main()
