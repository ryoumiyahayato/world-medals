"""Persist the inaccessible MedalBook Uzbekistan source without inventing candidates."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'data/volumes/uzbekistan_medalbook_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'乌兹别克斯坦共和国 · MedalBook','records':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/uzbekistan_medalbook_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':[],'unpictured_candidates':[],'excluded_candidates':[{'kind':'source_unavailable','reason':'Configured country index returned HTTP 404; no object candidates inferred.'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':0,'unpictured_candidates':0},ensure_ascii=False))
