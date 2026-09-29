"""Normalize the pictured ODM Uzbekistan object and retain the directory differential."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medals_org_uzbekistan.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
ITEMS=json.loads((ROOT/'data/source_sweeps/medals_org_uzbekistan_2026-09-28.json').read_text(encoding='utf-8'))['items']
BY={(x['record_index'],x['image_index']):x for x in ITEMS if x.get('status')=='downloaded'}
OUT=ROOT/'assets/images/medals_org_uzbekistan';OUT.mkdir(parents=True,exist_ok=True)
raw=RAW[2];rid='UZB-ODM-002-JASORAT';views=[];images=[];used=set()
for n,image_index in enumerate((1,2),1):
 item=BY[(2,image_index)];ext=Path(item['local_path']).suffix.lower()
 if ext=='.gif' or item['height']<=70:raise ValueError('ribbon/non-object promoted')
 if item['sha256'] in used:raise ValueError('duplicate payload')
 used.add(item['sha256']);rel=f'assets/images/medals_org_uzbekistan/002_jasorat_{image_index:02d}{ext or ".jpg"}';shutil.copy2(ROOT/item['local_path'],ROOT/rel)
 key=f'{rid}-VIEW{n}';views.append({'key':key,'label':'完整正面' if n==1 else '完整背面'})
 images.append({'key':f'uzb-odm-002-jasorat-{image_index:02d}','record_id':rid,'view_key':key,'local_path':rel,'source_page':raw['page_url'],'image_url':item['url'],'artist':'ODM / medals.org.uk catalogue image','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
records=[{'id':rid,'family':'MENA7-JASORAT','country_zh':'乌兹别克斯坦','name':'勇气奖章','original':raw['original_name'],'date':'1994年5月5日设立','variant':'ODM 所示实物；完整正背面','views':views,'source_ids':[raw['source_id']],'image_kind':'object_photo','html_eligible':True}]
pending=[{'source_id':r['source_id'],'name':r['page_title'],'date':r.get('instituted_text') or '待考','page_url':r['page_url'],'status':'有记载未配完整章体图'} for i,r in enumerate(RAW) if i!=2]
(ROOT/'data/volumes/uzbekistan_medals_org_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'乌兹别克斯坦共和国 · ODM','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/uzbekistan_medals_org_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':pending,'excluded_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':1,'families':1,'views':2,'pending':len(pending)},ensure_ascii=False))
