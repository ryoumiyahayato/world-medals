import hashlib,json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'assets/images/portugal_orders_fast_2026-09-28'
items=[
('agri_industrial','prt-k-agri-industrial-gc-badge.jpg','葡萄牙王国','农业与工业功绩勋章','Order of Agricultural and Industrial Merit','1893','大十字挂章'),
('avis','prt-k-avis-gc-badge.jpg','葡萄牙王国','阿维斯勋章','Order of Avis','历史设立；本版待考','大十字挂章，王国版'),
('christ','prt-k-christ-gc-star.jpg','葡萄牙王国','基督勋章','Order of Christ','1319；本版待考','大十字星章，王国版'),
('amelia_overseas','prt-k-queen-amelia-overseas-gold.jpg','葡萄牙王国','阿梅莉亚王后海外战役奖章','Queen Amélia Overseas Campaigns Medal','1902','金质级'),
('amelia_overseas','prt-k-queen-amelia-overseas-silver.jpg','葡萄牙王国','阿梅莉亚王后海外战役奖章','Queen Amélia Overseas Campaigns Medal','1902','银质级'),
('tower_sword','prt-k-torre-espada-gc-star.jpg','葡萄牙王国','塔与剑勋章','Order of the Tower and Sword','1808；本版待考','大十字星章，王国版'),
('vilavicosa','prt-k-vilavicosa-gc-badge.jpg','葡萄牙王国','维拉维索萨圣母无玷始胎勋章','Order of the Immaculate Conception of Vila Viçosa','1818','大十字挂章'),
('avis','prt-r-avis-gc-badge.jpg','葡萄牙共和国','阿维斯勋章','Military Order of Avis','历史设立；本版待考','大十字挂章，共和国版'),
('christ','prt-r-christ-gc-badge.jpg','葡萄牙共和国','基督勋章','Military Order of Christ','1319；本版待考','大十字挂章，共和国版'),
('entrepreneurial_merit','prt-r-entrepreneurial-merit-gc-star.jpg','葡萄牙共和国','企业功绩勋章','Order of Entrepreneurial Merit','待考','大十字星章'),
('liberty','prt-r-liberty-gc-star.jpg','葡萄牙共和国','自由勋章','Order of Liberty','1976','大十字星章'),
('liberty','prt-r-liberty-grand-officer-badge.jpg','葡萄牙共和国','自由勋章','Order of Liberty','1976','大军官级挂章'),
('merit','prt-r-merit-gc-badge.jpg','葡萄牙共和国','功绩勋章','Order of Merit','1929','大十字挂章'),
('military_bravery','prt-r-military-bravery-cross.jpg','葡萄牙共和国','军事英勇十字章','Military Bravery Cross','待考','十字章'),
('navy_cross','prt-r-navy-cross-class-4.jpg','葡萄牙共和国','海军十字章','Navy Cross','待考','四级'),
('prince_henry','prt-r-prince-henry-gc-badge.jpg','葡萄牙共和国','航海家亨利王子勋章','Order of Prince Henry','1960','大十字挂章'),
('prince_henry','prt-r-prince-henry-gc-star.jpg','葡萄牙共和国','航海家亨利王子勋章','Order of Prince Henry','1960','大十字星章'),
('public_instruction','prt-r-public-instruction-commander-star.jpg','葡萄牙共和国','公共教育勋章','Order of Public Instruction','1927','指挥官级星章'),
('santiago','prt-r-santiago-gc-star.jpg','葡萄牙共和国','圣地亚哥宝剑勋章','Military Order of Saint James of the Sword','历史设立；本版待考','大十字星章，共和国版'),
('tower_sword','prt-r-torre-espada-gc-badge.jpg','葡萄牙共和国','塔与剑勋章','Order of the Tower and Sword','1808；本版待考','大十字挂章，共和国版')]
records=[];images=[]; seen={}
for n,(family,file,country,name,original,date,variant) in enumerate(items,1):
 p=IMG/file; data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
 with Image.open(p) as im: dims=list(im.size); im.verify()
 fkey=family.upper(); idx=seen.get(family,0)+1; seen[family]=idx
 rid=f'PRT-ODM-{fkey}-V{idx:02d}'; view=f'{rid}-VIEW1'
 records.append({'id':rid,'family':f'PRT-ODM-{fkey}','country_zh':country,'name':name,'original':original,'date':date,'variant':variant+'；完整正面；低清参考','views':[{'key':view,'label':'完整正面'}],'source_ids':['medalsorg-portugal-master'],'image_kind':'complete_object_low_resolution','html_eligible':True})
 images.append({'key':f'prt-odm-{n:02d}-image','record_id':rid,'view_key':view,'local_path':str(p.relative_to(ROOT)).replace('\\','/'),'source_page':'https://www.medals.org.uk/portugal/portugal-text.htm','image_url':'source object page image','license':'source-site research use; publication rights not asserted','dimensions':dims,'bytes':len(data),'sha256':sha,'decoded':True,'visually_checked':True})
(ROOT/'data/volumes/portugal_medals_org_fast_2026-09-28.json').write_text(json.dumps({'as_of':'2026-09-29','volume':'portugal_medals_org_fast_2026-09-28','records':records},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/volumes/portugal_medals_org_fast_2026-09-28_manifest.json').write_text(json.dumps({'as_of':'2026-09-29','volume':'portugal_medals_org_fast_2026-09-28','images':images},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(records),len({r['family'] for r in records}),len(images),len({x['sha256'] for x in images}))
