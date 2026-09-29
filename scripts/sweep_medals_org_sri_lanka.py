"""Recursively sweep the complete ODM / medals.org.uk Sri Lanka directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG="sri_lanka";sweep.SOURCE_LABEL="Sri Lanka";sweep.BASE="https://www.medals.org.uk";sweep.INDEX=sweep.BASE+"/sri-lanka/sri-lanka-text.htm";sweep.PAGE_PATTERN=r"/sri-lanka/sri-lanka\d+\.htm$";sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_sri_lanka";sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_sri_lanka";sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_sri_lanka.jsonl";sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_sri_lanka_2026-09-28.json"
if __name__=="__main__":sweep.main()
