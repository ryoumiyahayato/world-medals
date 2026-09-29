"""Sweep the complete public MedalBook Malaysia federal and state catalogue."""

import sweep_medalbook_thailand as sweep


sweep.COUNTRY_PREFIX = "/asia/malaysia"
sweep.SOURCE_SLUG = "malaysia"
sweep.SOURCE_SYSTEM = "MedalBook Malaysia federal and state catalogue"
sweep.COUNTRY_LABEL = "Malaysia"
sweep.AS_OF = "2026-09-28"
sections = [
    "federal-awards", "federal-territories", "malacca", "penang", "sabah", "sarawak",
    "sultanate-of-johor", "sultanate-of-kedah-9", "sultanate-of-kelantan",
    "sultanate-of-negeri-sembilan", "sultanate-of-pahang-11", "sultanate-of-perak-12",
    "sultanate-of-perlis", "sultanate-of-selangor", "sultanate-of-terengganu",
]
sweep.INDEX_URLS = [sweep.BASE + "/asia/malaysia-1"] + [sweep.BASE + f"/asia/malaysia-1?page={page}" for page in range(2, 9)] + [sweep.BASE + ("/asia/malaysia-1/" if section in {"sultanate-of-kedah-9", "sultanate-of-pahang-11", "sultanate-of-perak-12"} else "/asia/malaysia/") + section for section in sections]
sweep.CACHE = sweep.ROOT / "sources/pages/medalbook_malaysia"
sweep.OUT = sweep.ROOT / "data/raw_candidates/medalbook_malaysia.jsonl"
sweep.STATE = sweep.ROOT / "data/source_sweeps/medalbook_malaysia_2026-09-28.json"


if __name__ == "__main__": sweep.main()
