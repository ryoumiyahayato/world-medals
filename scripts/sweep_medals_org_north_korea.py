"""Sweep the complete ODM / medals.org.uk North Korea directory."""

import sweep_medals_org_mongolia as sweep

sweep.SOURCE_SLUG = "north-korea"
sweep.SOURCE_LABEL = "North Korea"
sweep.INDEX = sweep.BASE + "/north-korea/north-korea-text.htm"
sweep.CACHE = sweep.ROOT / "sources/pages/medals_org_north_korea"
sweep.RAW_DIR = sweep.ROOT / "assets/raw/medals_org_north_korea"
sweep.CANDIDATES = sweep.ROOT / "data/raw_candidates/medals_org_north_korea.jsonl"
sweep.SWEEP = sweep.ROOT / "data/source_sweeps/medals_org_north_korea_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
