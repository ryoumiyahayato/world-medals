"""Recursively sweep the complete ODM / medals.org.uk Kyrgyzstan directory."""
import sweep_medals_org_mongolia as sweep
sweep.SOURCE_SLUG='kyrgyzstan';sweep.SOURCE_LABEL='Kyrgyzstan';sweep.BASE='https://www.medals.org.uk';sweep.INDEX=sweep.BASE+'/kyrgyzstan/kyrgyzstan-text.htm';sweep.PAGE_PATTERN=r'/kyrgyzstan/kyrgyzstan\d+\.htm$';sweep.RECURSIVE=True;sweep.CACHE=sweep.ROOT/'sources/pages/medals_org_kyrgyzstan';sweep.RAW_DIR=sweep.ROOT/'assets/raw/medals_org_kyrgyzstan';sweep.CANDIDATES=sweep.ROOT/'data/raw_candidates/medals_org_kyrgyzstan.jsonl';sweep.SWEEP=sweep.ROOT/'data/source_sweeps/medals_org_kyrgyzstan_2026-09-28.json'
if __name__=='__main__':sweep.main()
