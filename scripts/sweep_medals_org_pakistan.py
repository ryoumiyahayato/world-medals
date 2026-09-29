"""Recursively sweep the complete ODM / medals.org.uk Pakistan directory."""
import sweep_medals_org_mongolia as sweep

sweep.SOURCE_SLUG = "pakistan"
sweep.SOURCE_LABEL = "Pakistan"
sweep.BASE = "https://www.medals.org.uk"
sweep.INDEX = sweep.BASE + "/pakistan/pakistan-text.htm"
sweep.PAGE_PATTERN = r"/pakistan/pakistan\d+\.htm$"
sweep.RECURSIVE = True
sweep.CACHE = sweep.ROOT / "sources/pages/medals_org_pakistan"
sweep.RAW_DIR = sweep.ROOT / "assets/raw/medals_org_pakistan"
sweep.CANDIDATES = sweep.ROOT / "data/raw_candidates/medals_org_pakistan.jsonl"
sweep.SWEEP = sweep.ROOT / "data/source_sweeps/medals_org_pakistan_2026-09-28.json"

if __name__ == "__main__":
    sweep.main()
