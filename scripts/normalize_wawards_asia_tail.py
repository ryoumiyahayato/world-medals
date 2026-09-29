"""Normalize complete Hong Kong, Cyprus and Maldives country-index sweeps."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CONFIG={
"hong-kong":("HKG","香港特别行政区",{"grand-bauhinia-medal":"大紫荆勋章","bauhinia-star":"紫荆星章","medal-of-honour":"荣誉勋章","medal-for-bravery":"英勇勋章","hong-kong-plague-medal":"香港鼠疫奖章","police-medal-for-meritorious-service":"警察荣誉奖章","police-long-service-medal":"警察长期服务奖章","customs-and-excise-medal-for-distinguished-service":"海关卓越服务奖章","customs-and-excise-medal-for-meritorious-service":"海关荣誉奖章","customs-and-excise-long-service-medal":"海关长期服务奖章","civil-aid-service-long-service-medals":"民众安全服务队长期服务奖章"}),
"cyprus":("CYP","塞浦路斯共和国",{"order-of-makarios-iii":"马卡里奥斯三世勋章","order-of-merit-of-the-republic-of-cyprus":"塞浦路斯共和国功绩勋章","medal-of-eudokimos-diokesis":"优良行政奖章","police-medal-of-merit":"警察功绩奖章","police-service-medal":"警察服务奖章"}),
"maldives":("MDV","马尔代夫共和国",{"order-of-the-distinguished-leader":"杰出领袖勋章"})}
for scope,(prefix,country,names) in CONFIG.items():
 rows=[json.loads(x) for x in (ROOT/f"data/raw_candidates/wawards_{scope}.jsonl").read_text(encoding='utf-8').splitlines() if x.strip()];stem=scope.replace('-','_')+'_wawards_families';out=ROOT/f'assets/images/{stem}';out.mkdir(parents=True,exist_ok=True);records=[];images=[]
 for row in rows:
  slug=Path(urlparse(row['object_url']).path).stem;family=f"{prefix}-WA-{slug.upper().replace('-', '_')}";item=row['original_images'][1] if slug=='police-long-service-medal' else row['original_images'][0];src=ROOT/item['local_path'];rel=f"assets/images/{stem}/{slug}{src.suffix.lower()}";shutil.copy2(src,ROOT/rel)
  with Image.open(src) as im:w,h=im.size;im.verify()
  rid=family+'-REPRESENTATIVE';view=rid+'-VIEW1';date=(row.get('date_candidates') or ['日期待考'])[0]
  if date!='日期待考':date=f'{date}年设立／纪年'
  label='完整背面（区别图）' if slug=='police-long-service-medal' else '完整图样';variant='World Awards对象页所示完整背面；同系正面与警察荣誉奖章共用' if slug=='police-long-service-medal' else 'World Awards对象页所示完整章体；具体等级待考'
  records.append({'id':rid,'family':family,'country_zh':country,'name':names[slug],'original':row['page_title'],'date':date,'variant':variant,'views':[{'key':view,'label':label}],'source_ids':[row['source_id']],'image_kind':'catalogue_object_or_illustration','html_eligible':True})
  images.append({'key':rid.lower()+'-image','record_id':rid,'view_key':view,'local_path':rel,'source_page':row['object_url'],'image_url':item['image_url'],'license':'source-site research use; publication rights not asserted','dimensions':[w,h],'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'decoded':True,'visually_checked':True})
 (ROOT/f'data/volumes/{stem}.json').write_text(json.dumps({'as_of':'2026-09-28','volume':country,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/f'data/volumes/{stem}_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'scope':scope,'rows':len(records),'families':len(records),'views':len(images)},ensure_ascii=False))
