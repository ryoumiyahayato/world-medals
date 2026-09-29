"""Recursively sweep the complete ODM / medals.org.uk People's Republic of China directory."""

import sweep_medals_org_mongolia as sweep

sweep.SOURCE_SLUG = "china"
sweep.SOURCE_LABEL = "The People's Republic of China"
sweep.BASE = "https://medals.org.uk"
sweep.INDEX = sweep.BASE + "/china/prc/prc-text.htm"
sweep.PAGE_PATTERN = r"/china/prc/prc\d+\.htm$"
sweep.CACHE = sweep.ROOT / "sources/pages/medals_org_china"
sweep.RAW_DIR = sweep.ROOT / "assets/raw/medals_org_china"
sweep.CANDIDATES = sweep.ROOT / "data/raw_candidates/medals_org_china.jsonl"
sweep.SWEEP = sweep.ROOT / "data/source_sweeps/medals_org_china_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
