"""Recursively sweep the complete ODM / medals.org.uk Bangladesh directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG="bangladesh";sweep.SOURCE_LABEL="Bangladesh";sweep.BASE="https://www.medals.org.uk";sweep.INDEX=sweep.BASE+"/bangladesh/bangladesh-text.htm";sweep.PAGE_PATTERN=r"/bangladesh/bangladesh\d+\.htm$";sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_bangladesh";sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_bangladesh";sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_bangladesh.jsonl";sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_bangladesh_2026-09-28.json"
if __name__=="__main__":sweep.main()
