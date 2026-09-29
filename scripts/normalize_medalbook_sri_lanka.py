"""Preserve the exhausted MedalBook Sri Lanka differential as unpictured candidates."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
raw=[json.loads(x) for x in (ROOT/'data/raw_candidates/medalbook_sri_lanka.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def date_text(r):
 values=r.get('date_candidates') or []
 return '／'.join(str(x) for x in values) if values else '待考'
pending=[{'source_id':r['source_id'],'name':r.get('page_title') or r.get('original_name'),'date':date_text(r),'page_url':r['page_url'],'status':'有记载未配完整章体图'} for r in raw]
(ROOT/'data/volumes/sri_lanka_medalbook_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'斯里兰卡／锡兰 · MedalBook','records':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/sri_lanka_medalbook_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':[],'unpictured_candidates':pending,'excluded_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':0,'unpictured_candidates':len(pending)},ensure_ascii=False))
