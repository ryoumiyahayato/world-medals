"""Recursively sweep the complete ODM / medals.org.uk Tajikistan directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG='tajikistan';sweep.SOURCE_LABEL='Tajikistan';sweep.BASE='https://www.medals.org.uk';sweep.INDEX=sweep.BASE+'/tajikistan/tajikistan-text.htm';sweep.PAGE_PATTERN=r'/tajikistan/tajikistan\d+\.htm$';sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/'sources/pages/medals_org_tajikistan';sweep.RAW_DIR=sweep.ROOT/'assets/raw/medals_org_tajikistan';sweep.CANDIDATES=sweep.ROOT/'data/raw_candidates/medals_org_tajikistan.jsonl';sweep.SWEEP=sweep.ROOT/'data/source_sweeps/medals_org_tajikistan_2026-09-28.json'
if __name__=='__main__':sweep.main()
