"""Normalize pictured objects from the completed ODM Kazakhstan directory."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medals_org_kazakhstan.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
ITEMS=json.loads((ROOT/'data/source_sweeps/medals_org_kazakhstan_2026-09-28.json').read_text(encoding='utf-8'))['items']
BY={(x['record_index'],x['image_index']):x for x in ITEMS if x.get('status')=='downloaded'}
OUT=ROOT/'assets/images/medals_org_kazakhstan';OUT.mkdir(parents=True,exist_ok=True)
# index,suffix,name,family,date,variant,[(image,label)]
E=[
 (0,'people-hero','人民英雄金星章','KAZ-TITLE-PEOPLES-HERO','1993年设立','金星章',[(2,'完整正面')]),
 (1,'golden-eagle','金鹰勋章','KAZ-ORD-GOLDEN-EAGLE','1995年设立','章饰与星章',[(2,'章饰完整正面'),(3,'星章完整正面')]),
 (2,'fatherland','祖国勋章','KAZ-ORD-OTAN','1995年设立','章饰',[(1,'完整正面')]),
 (4,'glory-1-badge','光荣勋章','KAZ-ORD-DANK','1993年设立','一级章饰',[(1,'完整正面')]),
 (4,'glory-1-star','光荣勋章','KAZ-ORD-DANK','1993年设立','一级星章',[(2,'完整正面')]),
 (4,'glory-2','光荣勋章','KAZ-ORD-DANK','1993年设立','二级',[(3,'完整正面')]),
 (5,'valour-1','英勇勋章','KAZ-ORD-AIBYN','1995年设立','一级',[(1,'完整正面')]),
 (5,'valour-2','英勇勋章','KAZ-ORD-AIBYN','1995年设立','二级',[(2,'完整正面')]),
 (5,'valour-3','英勇勋章','KAZ-ORD-AIBYN','1995年设立','三级',[(3,'完整正面')]),
 (6,'nobility','高尚勋章','KAZ-ORD-PARASAT','1995年设立','章饰',[(1,'完整正面')]),
 (7,'friendship','友谊勋章','KAZ-ORD-DOSTYK','1995年设立','章饰',[(1,'完整正面')]),
]
records=[];images=[];used=set()
for idx,suffix,name,family,date,variant,picks in E:
 raw=RAW[idx];rid=f'KAZ-ODM-{idx:03d}-{suffix.upper()}';views=[]
 for n,(image_index,label) in enumerate(picks,1):
  item=BY[(idx,image_index)];ext=Path(item['local_path']).suffix.lower()
  if ext=='.gif' or item['height']<=70:raise ValueError(f'ribbon/non-object promoted {idx}:{image_index}')
  if item['sha256'] in used:raise ValueError(f'duplicate payload {idx}:{image_index}')
  used.add(item['sha256']);rel=f'assets/images/medals_org_kazakhstan/{idx:03d}_{suffix}_{image_index:02d}{ext or ".jpg"}';shutil.copy2(ROOT/item['local_path'],ROOT/rel)
  key=f'{rid}-VIEW{n}';views.append({'key':key,'label':label})
  images.append({'key':f'kaz-odm-{idx:03d}-{suffix}-{image_index:02d}','record_id':rid,'view_key':key,'local_path':rel,'source_page':raw['page_url'],'image_url':item['url'],'artist':'ODM / medals.org.uk catalogue image','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
 records.append({'id':rid,'family':family,'country_zh':'哈萨克斯坦共和国','name':name,'original':raw['original_name'],'date':date,'variant':variant,'views':views,'source_ids':[raw['source_id']],'image_kind':'object_photo','html_eligible':True})
pending=[]
for idx,raw in enumerate(RAW):
 object_items=[x for x in ITEMS if x['record_index']==idx and Path(x['local_path']).suffix.lower()!='.gif' and x['height']>70]
 if not object_items:pending.append({'source_id':raw['source_id'],'name':raw['page_title'],'date':raw.get('instituted_text') or '待考','page_url':raw['page_url'],'status':'有记载未配完整章体图'})
(ROOT/'data/volumes/kazakhstan_medals_org_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'哈萨克斯坦共和国 · ODM','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/kazakhstan_medals_org_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':pending,'excluded_candidates':[{'kind':'ribbon_only','count':2,'reason':'绶带图不作为章体图示'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images),'pending':len(pending)},ensure_ascii=False))
