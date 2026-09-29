"""Normalize the complete pictured ODM Kyrgyzstan directory."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medals_org_kyrgyzstan.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
ITEMS=json.loads((ROOT/'data/source_sweeps/medals_org_kyrgyzstan_2026-09-28.json').read_text(encoding='utf-8'))['items']
BY={(x['record_index'],x['image_index']):x for x in ITEMS if x.get('status')=='downloaded'}
OUT=ROOT/'assets/images/medals_org_kyrgyzstan';OUT.mkdir(parents=True,exist_ok=True)
# index,suffix,name,family,date,variant,[(image,label)]
E=[
 (0,'hero','吉尔吉斯共和国英雄','KGZ-TITLE-HERO','1996年4月16日设立','“白隼”特别标志',[(1,'完整正面'),(2,'完整背面')]),
 (1,'manas-1','玛纳斯勋章','KGZ-ORD-MANAS','1996年4月16日设立','一级',[(1,'完整正面')]),
 (1,'manas-2','玛纳斯勋章','KGZ-ORD-MANAS','1996年4月16日设立','二级',[(2,'完整正面')]),
 (1,'manas-3','玛纳斯勋章','KGZ-ORD-MANAS','1996年4月16日设立','三级',[(3,'完整正面')]),
 (2,'kurmanjan-datka','库尔曼詹·达特卡勋章','KGZ-ORD-KURMANJAN-DATKA','2016年11月26日设立','章饰',[(1,'完整正面')]),
 (3,'danaker','丹纳克尔（和平缔造者）勋章','KGZ-ORD-DANAKER','1999年11月12日设立','章饰',[(1,'完整正面')]),
 (4,'glory-order','荣耀勋章','KGZ-ORD-DANK','2017年8月18日设立','章饰',[(1,'完整正面')]),
 (5,'friendship','友谊勋章','KGZ-ORD-DOSTUK','2017年8月18日设立','章饰',[(1,'完整正面')]),
 (6,'mother-heroine','英雄母亲勋章','KGZ-ORD-MOTHER-HEROINE','1996年4月16日设立','章饰',[(1,'完整正面'),(2,'完整背面')]),
 # ODM page 8 is superseded by the higher-resolution official portal image.
 (8,'glory-medal','荣耀奖章','KGZ-MED-DANK','1996年4月16日设立','奖章',[(1,'完整正面')]),
 (9,'mother-glory','母亲荣耀奖章','KGZ-MED-MOTHER-GLORY','1996年4月16日设立','奖章',[(1,'完整正面')]),
 (10,'people-title-badge','第一类“人民”荣誉称号徽章','KGZ-BADGE-PEOPLES-HONORARY-TITLE','2017年6月28日设立','荣誉称号徽章',[(1,'完整正面')]),
 (11,'merit-title-badge','“功勋”荣誉称号徽章','KGZ-BADGE-MERIT-HONORARY-TITLE','2017年6月28日设立','荣誉称号徽章',[(1,'完整正面')]),
]
records=[];images=[];used=set()
for idx,suffix,name,family,date,variant,picks in E:
 raw=RAW[idx];rid=f'KGZ-ODM-{idx:03d}-{suffix.upper()}';views=[]
 for n,(image_index,label) in enumerate(picks,1):
  item=BY[(idx,image_index)];ext=Path(item['local_path']).suffix.lower()
  if ext=='.gif' or item['height']<=70:raise ValueError(f'ribbon/non-object promoted {idx}:{image_index}')
  if item['sha256'] in used:raise ValueError(f'duplicate payload {idx}:{image_index}')
  used.add(item['sha256']);rel=f'assets/images/medals_org_kyrgyzstan/{idx:03d}_{suffix}_{image_index:02d}{ext or ".jpg"}';shutil.copy2(ROOT/item['local_path'],ROOT/rel)
  key=f'{rid}-VIEW{n}';views.append({'key':key,'label':label})
  images.append({'key':f'kgz-odm-{idx:03d}-{suffix}-{image_index:02d}','record_id':rid,'view_key':key,'local_path':rel,'source_page':raw['page_url'],'image_url':item['url'],'artist':'ODM / medals.org.uk catalogue image','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
 records.append({'id':rid,'family':family,'country_zh':'吉尔吉斯共和国','name':name,'original':raw['original_name'],'date':date,'variant':variant,'views':views,'source_ids':[raw['source_id']],'image_kind':'object_photo','html_eligible':True})
(ROOT/'data/volumes/kyrgyzstan_medals_org_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'吉尔吉斯共和国 · ODM','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/kyrgyzstan_medals_org_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[{'source_id':RAW[7]['source_id'],'name':RAW[7]['page_title'],'reason':'同型图由官方国家奖励门户更高分辨率原图替代'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))
