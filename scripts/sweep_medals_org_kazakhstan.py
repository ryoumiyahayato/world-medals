"""Recursively sweep the complete ODM / medals.org.uk Kazakhstan directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG="kazakhstan";sweep.SOURCE_LABEL="Kazakhstan";sweep.BASE="https://www.medals.org.uk";sweep.INDEX=sweep.BASE+"/kazakhstan/kazakhstan-text.htm";sweep.PAGE_PATTERN=r"/kazakhstan/kazakhstan\d+\.htm$";sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/"sources/pages/medals_org_kazakhstan";sweep.RAW_DIR=sweep.ROOT/"assets/raw/medals_org_kazakhstan";sweep.CANDIDATES=sweep.ROOT/"data/raw_candidates/medals_org_kazakhstan.jsonl";sweep.SWEEP=sweep.ROOT/"data/source_sweeps/medals_org_kazakhstan_2026-09-28.json"
if __name__=="__main__":sweep.main()
