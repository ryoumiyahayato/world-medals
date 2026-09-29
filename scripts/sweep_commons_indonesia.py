"""Recursively sweep the Commons Indonesia award category tree."""
import sweep_commons_sudan as sweep
sweep.SCOPE_ID='indonesia'; sweep.SCOPE_LABEL='Indonesia'; sweep.AS_OF='2026-09-28'
sweep.START='Category:Orders, decorations and medals of Indonesia'
sweep.OUT=sweep.ROOT/'data/raw_candidates/commons_indonesia.jsonl'
sweep.SWEEP=sweep.ROOT/'data/source_sweeps/commons_indonesia_2026-09-28.json'
sweep.STATE=sweep.ROOT/'sources/cache/commons_indonesia_sweep_state.json'
sweep.RAW=sweep.ROOT/'assets/raw/commons_indonesia'; sweep.RAW.mkdir(parents=True,exist_ok=True)
if __name__=='__main__': sweep.main()
