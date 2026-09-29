"""Normalize pictured objects from the completed ODM Sri Lanka directory."""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medals_org_sri_lanka.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
ITEMS=json.loads((ROOT/'data/source_sweeps/medals_org_sri_lanka_2026-09-28.json').read_text(encoding='utf-8'))['items']
BY={(x['record_index'],x['image_index']):x for x in ITEMS if x.get('status')=='downloaded'}
OUT=ROOT/'assets/images/medals_org_sri_lanka'; OUT.mkdir(parents=True,exist_ok=True)

# index, suffix, Chinese name, family, date, variant, image indices
E=[
 (0,'supreme-heroism','最高英勇勋章','LKA-DEC-PARAMA-WEERA-VIBHUSHANAYA','1971年设立','章饰',[2,3]),
 (9,'meritorious-service','武装部队功绩服务奖章','LKA-MED-ARMED-FORCES-MERITORIOUS-SERVICE','1981年设立','奖章',[1,2]),
 (14,'civil-war-service','内战服役奖章','LKA-MED-CIVIL-WAR-SERVICE','1983年设立；适用服役期1977—2010年','奖章',[1,2]),
 (16,'independence-50','独立五十周年纪念章','LKA-MED-INDEPENDENCE-50','1998年设立','纪念章',[2,3]),
 (17,'air-force-50','斯里兰卡空军五十周年纪念章','LKA-MED-AIR-FORCE-50','2001年设立','空军纪念章',[1,2]),
 (18,'son-nation','国家之子奖章','LKA-MED-DESHA-PUTHRA-SAMMANAYA','1972年设立','负伤／殉职奖章',[1,2]),
]
records=[];images=[];used=set()
for idx,suffix,name,family,date,variant,picks in E:
 raw=RAW[idx];rid=f'LKA-ODM-{idx:03d}-{suffix.upper()}';views=[]
 for n,image_index in enumerate(picks,1):
  item=BY[(idx,image_index)]; ext=Path(item['local_path']).suffix.lower()
  if ext=='.gif' or item['height']<=70: raise ValueError(f'ribbon/non-object promoted {idx}:{image_index}')
  if item['sha256'] in used: raise ValueError(f'duplicate payload {idx}:{image_index}')
  used.add(item['sha256']); rel=f'assets/images/medals_org_sri_lanka/{idx:03d}_{suffix}_{image_index:02d}{ext or ".jpg"}';shutil.copy2(ROOT/item['local_path'],ROOT/rel)
  key=f'{rid}-VIEW{n}';views.append({'key':key,'label':'完整正面' if n==1 else '完整背面'})
  images.append({'key':f'lka-odm-{idx:03d}-{suffix}-{image_index:02d}','record_id':rid,'view_key':key,'local_path':rel,'source_page':raw['page_url'],'image_url':item['url'],'artist':'ODM / medals.org.uk catalogue image','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
 records.append({'id':rid,'family':family,'country_zh':'斯里兰卡民主社会主义共和国','name':name,'original':raw['original_name'],'date':date,'variant':variant,'views':views,'source_ids':[raw['source_id']],'image_kind':'object_photo','html_eligible':True})
pending=[]
for idx,raw in enumerate(RAW):
 object_items=[x for x in ITEMS if x['record_index']==idx and Path(x['local_path']).suffix.lower()!='.gif' and x['height']>70]
 if not object_items: pending.append({'source_id':raw['source_id'],'name':raw['page_title'],'date':raw.get('instituted_text') or '待考','page_url':raw['page_url'],'status':'有记载未配完整章体图'})
(ROOT/'data/volumes/sri_lanka_medals_org_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'斯里兰卡 · ODM','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/sri_lanka_medals_org_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':pending,'excluded_candidates':[{'kind':'ribbon_only','count':3,'reason':'绶带图不作为章体图示'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images),'pending':len(pending)},ensure_ascii=False))
