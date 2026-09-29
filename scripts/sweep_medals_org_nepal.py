"""Recursively sweep the complete ODM / medals.org.uk Nepal directory."""
import sweep_medals_org_mongolia as sweep

sweep.SOURCE_SLUG="nepal"
sweep.SOURCE_LABEL="Nepal"
sweep.BASE="https://www.medals.org.uk"
sweep.INDEX=sweep.BASE+"/nepal/nepal-text.htm"
sweep.PAGE_PATTERN=r"/nepal/nepal\d+\.htm$"
sweep.RECURSIVE=True
sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_nepal"
sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_nepal"
sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_nepal.jsonl"
sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_nepal_2026-09-28.json"
if __name__=="__main__": sweep.main()
