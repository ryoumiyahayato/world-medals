"""Recursively sweep the complete ODM / medals.org.uk India directory."""
import sweep_medals_org_mongolia as sweep

sweep.SOURCE_SLUG = "india"
sweep.SOURCE_LABEL = "India"
sweep.BASE = "https://www.medals.org.uk"
sweep.INDEX = sweep.BASE + "/india/india-text.htm"
sweep.PAGE_PATTERN = r"/india/india\d+\.htm$"
sweep.CACHE = sweep.ROOT / "sources/pages/medals_org_india"
sweep.RAW_DIR = sweep.ROOT / "assets/raw/medals_org_india"
sweep.CANDIDATES = sweep.ROOT / "data/raw_candidates/medals_org_india.jsonl"
sweep.SWEEP = sweep.ROOT / "data/source_sweeps/medals_org_india_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
