"""Normalize all complete insignia images still downloadable from Kyrgyzstan's official awards portal."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/kyrgyz_awards_portal.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
STATE=json.loads((ROOT/'data/source_sweeps/kyrgyz_awards_portal_2026-09-28.json').read_text(encoding='utf-8'))
BY={x['url']:x for x in STATE['items']}
OUT=ROOT/'assets/images/kyrgyz_awards_portal';OUT.mkdir(parents=True,exist_ok=True)
# raw index,suffix,name,family,date,variant
E=[
 (16,'toktogul-prize','托克托古尔国家奖奖章','KGZ-MED-TOKTOGUL-STATE-PRIZE','设立日期待考','国家奖获奖者奖章'),
 (18,'courage','英勇奖章','KGZ-MED-ERDIK','1996年4月16日设立','官方门户所示版型'),
 (20,'military-service-1','优异军事服役奖章','KGZ-MED-MILITARY-SERVICE','1999年2月10日设立','一级；退出序列'),
 (21,'military-service-2','优异军事服役奖章','KGZ-MED-MILITARY-SERVICE','1999年2月10日设立','二级；退出序列'),
 (22,'charity','慈善奖章','KGZ-MED-CHARITY','2007年5月8日设立','退出序列'),
 (23,'labour-veteran','劳动老兵奖章','KGZ-MED-LABOUR-VETERAN','2007年5月8日设立','退出序列'),
]
records=[];images=[];used=set()
for idx,suffix,name,family,date,variant in E:
 raw=RAW[idx];url=raw['original_image_urls'][0];item=BY[url]
 if item['sha256'] in used:raise ValueError(f'duplicate payload {idx}')
 used.add(item['sha256']);src=ROOT/item['local_path'];ext=src.suffix.lower();rel=f'assets/images/kyrgyz_awards_portal/{idx:03d}_{suffix}{ext}';shutil.copy2(src,ROOT/rel)
 rid=f'KGZ-OFFICIAL-{idx:03d}-{suffix.upper()}';view=f'{rid}-VIEW1'
 records.append({'id':rid,'family':family,'country_zh':'吉尔吉斯共和国','name':name,'original':raw['original_name'],'date':date,'variant':variant,'views':[{'key':view,'label':'官方完整正面'}],'source_ids':[raw['source_id']],'image_kind':'official_object_photo','html_eligible':True})
 images.append({'key':f'kgz-official-{idx:03d}-{suffix}','record_id':rid,'view_key':view,'local_path':rel,'source_page':raw['page_url'],'image_url':url,'artist':'Kyrgyz Republic State Awards Portal','license':'Official portal image; retained for offline research catalogue with attribution','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
pending=[{'source_id':r['source_id'],'name':r['page_title'],'date':'待考','page_url':r['page_url'],'status':'官方目录有记录；原图链接当前不可取得'} for r in RAW if not r.get('local_image_path') and r['original_image_urls'] and r['original_image_urls'][0].rstrip('/')!= 'https://nagrada.srs.kg/Main_Photo/Awards']
(ROOT/'data/volumes/kyrgyzstan_official_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'吉尔吉斯共和国 · 国家奖励门户','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/kyrgyzstan_official_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':pending,'excluded_candidates':[{'kind':'duplicate_source_image','count':3,'reason':'相同通用荣誉称号徽章图在多个目录对象中重复，只保留可独立识别的候选记录'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images),'pending':len(pending)},ensure_ascii=False))
