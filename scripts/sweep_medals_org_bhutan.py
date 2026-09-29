"""Recursively sweep the complete ODM / medals.org.uk Bhutan directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG="bhutan"; sweep.SOURCE_LABEL="Bhutan"; sweep.BASE="https://www.medals.org.uk"; sweep.INDEX=sweep.BASE+"/bhutan/bhutan-text.htm"; sweep.PAGE_PATTERN=r"/bhutan/bhutan\d+\.htm$"; sweep.RECURSIVE=True
sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_bhutan"; sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_bhutan"; sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_bhutan.jsonl"; sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_bhutan_2026-09-28.json"
if __name__=="__main__": sweep.main()
