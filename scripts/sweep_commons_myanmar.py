"""Recursively sweep the Commons Myanmar/Burma award category tree."""
import sweep_commons_sudan as sweep
sweep.SCOPE_ID='myanmar'; sweep.SCOPE_LABEL='Myanmar/Burma'; sweep.AS_OF='2026-09-28'
sweep.START='Category:Orders, decorations and medals of Myanmar'
sweep.OUT=sweep.ROOT/'data/raw_candidates/commons_myanmar.jsonl'
sweep.SWEEP=sweep.ROOT/'data/source_sweeps/commons_myanmar_2026-09-28.json'
sweep.STATE=sweep.ROOT/'sources/cache/commons_myanmar_sweep_state.json'
sweep.RAW=sweep.ROOT/'assets/raw/commons_myanmar'; sweep.RAW.mkdir(parents=True,exist_ok=True)
if __name__=='__main__': sweep.main()
