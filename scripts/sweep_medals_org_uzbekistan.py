"""Recursively sweep the complete ODM / medals.org.uk Uzbekistan directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG="uzbekistan";sweep.SOURCE_LABEL="Uzbekistan";sweep.BASE="https://www.medals.org.uk";sweep.INDEX=sweep.BASE+"/uzbekistan/uzbekistan-text.htm";sweep.PAGE_PATTERN=r"/uzbekistan/uzbekistan\d+\.htm$";sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_uzbekistan";sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_uzbekistan";sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_uzbekistan.jsonl";sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_uzbekistan_2026-09-28.json"
if __name__=="__main__":sweep.main()
