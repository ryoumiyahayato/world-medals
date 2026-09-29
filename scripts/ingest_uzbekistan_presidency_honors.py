"""Ingest every award card on the Uzbekistan Presidency honours page (two cards)."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
AS_OF='2026-09-28'
PAGE='https://president.uz/ru/pages/view/honors'
OUT=ROOT/'assets/images/uzbekistan_presidency';OUT.mkdir(parents=True,exist_ok=True)
cards=[
 {'slug':'mehnat-shuhrati','name':'劳动荣誉勋章','original':'Mehnat shuhrati','family':'UZB-ORD-MEHNAT-SHUHRATI','date':'1995年8月31日设立','variant':'总统府官方展示版','raw':'assets/raw/uzbekistan_presidency/mehnat_shuhrati.png','url':'https://president.uz/uploads/ddd7ebfa-d939-55c8-4764-ccbeea65295f_media_8253.png','summary':'授予在经济与文化发展、人民福祉提升以及维护和平稳定方面具有卓越劳动功绩的公民。'},
 {'slug':'fidokorona-xizmatlari-uchun','name':'无私服务勋章','original':'Fidokorona xizmatlari uchun','family':'UZB-ORD-FIDOKORONA-XIZMATLARI-UCHUN','date':'设立日期待考','variant':'总统府官方展示版','raw':'assets/raw/uzbekistan_presidency/fidokorona_xizmatlari_uchun.png','url':'https://president.uz/uploads/863a7ae6-347a-30f0-2cd9-3053aa5e5b3d_media_8254.png','summary':'授予为国家发展、国防安全、社会和平稳定作出重大贡献并体现无私服务的公民与军人。'},
]
records=[];images=[];raw_rows=[];items=[]
for i,c in enumerate(cards,1):
 src=ROOT/c['raw'];dst=OUT/f"{i:02d}_{c['slug']}.png";shutil.copy2(src,dst)
 with Image.open(dst) as im: dims=list(im.size);im.verify()
 data=dst.read_bytes();sha=hashlib.sha256(data).hexdigest();rid=f"UZB-PRES-{i:03d}-{c['slug'].upper()}";view=f'{rid}-VIEW1';sid=f"uzbekistan-presidency-{c['slug']}"
 rel=dst.relative_to(ROOT).as_posix()
 records.append({'id':rid,'family':c['family'],'country_zh':'乌兹别克斯坦','name':c['name'],'original':c['original'],'date':c['date'],'variant':c['variant'],'views':[{'key':view,'label':'官方完整正面'}],'source_ids':[sid],'image_kind':'official_object_photo','html_eligible':True})
 images.append({'key':f"uzb-pres-{i:03d}-{c['slug']}",'record_id':rid,'view_key':view,'local_path':rel,'source_page':PAGE,'image_url':c['url'],'artist':'Official website of the President of the Republic of Uzbekistan','license':'Official site states all rights reserved; retained for offline research catalogue with attribution','dimensions':dims,'bytes':len(data),'sha256':sha,'decoded':True,'visually_checked':True})
 raw_rows.append({'source_id':sid,'source_system':'President of Uzbekistan — State honours','page_title':c['original'],'working_name_zh':c['name'],'original_name':c['original'],'english_name':c['original'],'aliases':[],'date_candidates':[1995] if i==1 else [],'category':'state-order','family_hint':c['family'],'grade_material_clues':c['variant'],'page_url':PAGE,'image_page_url':PAGE,'original_image_urls':[c['url']],'notes':c['summary'],'status':'NORMALIZED'})
 items.append({'record_index':i-1,'image_index':1,'url':c['url'],'local_path':c['raw'],'status':'downloaded','width':dims[0],'height':dims[1],'bytes':len(data),'sha256':sha})
(ROOT/'data/raw_candidates/uzbekistan_presidency_honors.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in raw_rows),encoding='utf-8')
(ROOT/'data/source_sweeps/uzbekistan_presidency_honors_2026-09-28.json').write_text(json.dumps({'as_of':AS_OF,'source_id':'uzbekistan_presidency_state_honours','source_name':'President of Uzbekistan — State honours','seed_url':PAGE,'status':'completed','planned_pages':1,'processed_pages':1,'award_cards':2,'downloaded_images':2,'failed_images':0,'items':items,'completion_rule':'Every award card and linked image on the page was processed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/uzbekistan_presidency_variants.json').write_text(json.dumps({'as_of':AS_OF,'volume':'乌兹别克斯坦共和国 · 总统府国家奖励','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/uzbekistan_presidency_variants_manifest.json').write_text(json.dumps({'as_of':AS_OF,'images':images,'unpictured_candidates':[],'excluded_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'sources/pages/uzbekistan_presidency_honors_2026-09-28.txt').write_text('Source page: '+PAGE+'\nAccessed: '+AS_OF+'\nComplete visible award-card boundary: 2/2.\n\n'+''.join(f"{c['original']}\n{c['summary']}\nImage: {c['url']}\n\n" for c in cards),encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))
