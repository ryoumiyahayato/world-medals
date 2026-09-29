"""Recursively sweep the Commons North Korea award category tree once."""

import sweep_commons_sudan as sweep

sweep.SCOPE_ID = "north-korea"
sweep.SCOPE_LABEL = "North Korea"
sweep.AS_OF = "2026-09-28"
sweep.START = "Category:Orders, decorations and medals of North Korea"
sweep.OUT = sweep.ROOT / "data/raw_candidates/commons_north_korea.jsonl"
sweep.SWEEP = sweep.ROOT / "data/source_sweeps/commons_north_korea_2026-09-28.json"
sweep.STATE = sweep.ROOT / "sources/cache/commons_north_korea_sweep_state.json"
sweep.RAW = sweep.ROOT / "assets/raw/commons_north_korea"
sweep.RAW.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    sweep.main()
