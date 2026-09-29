"""Normalize visually checked Commons Indonesia objects and official illustrations."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ROWS=[json.loads(x) for x in (ROOT/'data/raw_candidates/commons_indonesia.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
BY={x['source_id']:x for x in ROWS}; OUT=ROOT/'assets/images/commons_indonesia'; OUT.mkdir(parents=True,exist_ok=True)
SELECTED=[
('commons-indonesia-0003','IDN-STAR-GUERRILLA-COMMONS','IDN-STAR-GUERRILLA','游击星章','1958年设立','博物馆藏实物；完整正面','object_photo'),
('commons-indonesia-0020','IDN-STAR-MAHAPUTERA-COMMONS','IDN-STAR-MAHAPUTERA','马哈普特拉星章','1959年设立','等级待考；博物馆藏实物正面','object_photo'),
('commons-indonesia-0133','IDN-STAR-REPUBLIC-I-OFFICIAL','IDN-STAR-REPUBLIC','印度尼西亚共和国星章','1959年设立','一级（Adipurna）；官方图式','official_illustration'),
('commons-indonesia-0132','IDN-STAR-REPUBLIC-II-OFFICIAL','IDN-STAR-REPUBLIC','印度尼西亚共和国星章','1959年设立','二级（Adipradana）；官方图式','official_illustration'),
('commons-indonesia-0138','IDN-STAR-REPUBLIC-III-OFFICIAL','IDN-STAR-REPUBLIC','印度尼西亚共和国星章','1959年设立','三级（Utama）；官方图式','official_illustration'),
('commons-indonesia-0136','IDN-STAR-REPUBLIC-IV-OFFICIAL','IDN-STAR-REPUBLIC','印度尼西亚共和国星章','1959年设立','四级（Pratama）；官方图式','official_illustration'),
('commons-indonesia-0134','IDN-STAR-REPUBLIC-V-OFFICIAL','IDN-STAR-REPUBLIC','印度尼西亚共和国星章','1959年设立','五级（Nararya）；官方图式','official_illustration'),
('commons-indonesia-0062','IDN-KARYA-SATYA-XX-OFFICIAL','IDN-KARYA-SATYA','忠诚工作奖章','1994年现行三档制','二十年服务；银质章；图式','illustration'),
('commons-indonesia-0063','IDN-KARYA-SATYA-XXX-OFFICIAL','IDN-KARYA-SATYA','忠诚工作奖章','1994年现行三档制','三十年服务；金色章；图式','illustration'),
]

MULTIVIEW=[
(['commons-indonesia-0081','commons-indonesia-0082'], 'IDN-SATYALANCANA-BHAKTI-AM806910', 'IDN-SATYALANCANA-BHAKTI', '奉献奖章', '1958年设立', '负伤功绩型；奥克兰战争纪念博物馆藏实物；正背'),
(['commons-indonesia-0084','commons-indonesia-0085'], 'IDN-SEWINDU-ANGKATAN-PERANG-AM806911', 'IDN-SEWINDU-ANGKATAN-PERANG', '武装部队八年纪念星章', '1954年设立；1959年改称星章', '武装部队八年服役型；奥克兰战争纪念博物馆藏实物；正背'),
(['commons-indonesia-0105','commons-indonesia-0106'], 'IDN-FAITHFUL-SERVICE-VIII-AM806919', 'IDN-FAITHFUL-SERVICE', '军队忠诚服务奖章', '1958年设立', '八年服役型；奥克兰战争纪念博物馆藏实物；正背'),
]
records=[]; images=[]
for sid,rid,family,name,date,variant,kind in SELECTED:
 row=BY[sid]; src=ROOT/row['local_raw_image']; rel=f'assets/images/commons_indonesia/{sid.rsplit("-",1)[-1]}{src.suffix.lower()}'; shutil.copy2(src,ROOT/rel)
 with Image.open(src) as im: width,height=im.size; im.verify()
 digest=hashlib.sha256(src.read_bytes()).hexdigest(); vk=rid+'-VIEW1'
 label={'object_photo':'完整正面','official_illustration':'完整官方图式','illustration':'完整图式'}[kind]
 records.append({'id':rid,'family':family,'country_zh':'印度尼西亚共和国','name':name,'original':row['file_title'].removeprefix('File:'),'date':date,'variant':variant,'views':[{'key':vk,'label':label}],'source_ids':[sid],'image_kind':kind,'html_eligible':True})
 images.append({'key':rid.lower()+'-image','record_id':rid,'view_key':vk,'local_path':rel,'source_page':row['page_url'],'image_url':row['original_image_url'],'artist':row.get('artist'),'license':row.get('license'),'dimensions':[width,height],'bytes':src.stat().st_size,'sha256':digest,'decoded':True,'visually_checked':True})
for sids,rid,family,name,date,variant in MULTIVIEW:
 views=[]
 for n,sid in enumerate(sids,1):
  row=BY[sid]; src=ROOT/row['local_raw_image']; rel=f'assets/images/commons_indonesia/{sid.rsplit("-",1)[-1]}{src.suffix.lower()}'; shutil.copy2(src,ROOT/rel)
  with Image.open(src) as im: width,height=im.size; im.verify()
  digest=hashlib.sha256(src.read_bytes()).hexdigest(); vk=f'{rid}-VIEW{n}'; label='完整正面' if n==1 else '完整背面'; views.append({'key':vk,'label':label})
  images.append({'key':rid.lower()+f'-image-{n}','record_id':rid,'view_key':vk,'local_path':rel,'source_page':row['page_url'],'image_url':row['original_image_url'],'artist':row.get('artist'),'license':row.get('license'),'dimensions':[width,height],'bytes':src.stat().st_size,'sha256':digest,'decoded':True,'visually_checked':True})
 records.append({'id':rid,'family':family,'country_zh':'印度尼西亚共和国','name':name,'original':BY[sids[0]]['description'],'date':date,'variant':variant,'views':views,'source_ids':sids,'image_kind':'object_photo','html_eligible':True})
(ROOT/'data/volumes/indonesia_commons_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'印度尼西亚共和国','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/indonesia_commons_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[{'source_id':'commons-indonesia-0055','name':'Bintang Sri Nugraha I Class illustration','reason':'non-official modern reconstruction; stronger source required before formal inclusion'},{'source_id':'commons-indonesia-0059','name':'GANEFO bronze sports medal','reason':'sports-event medal retained for related-awards research, not the formal state volume'},{'source_id':'commons-indonesia-0108','name':'Indonesia of my Dream Contest 2010 Medal','reason':'contest medal retained for related-awards research, not the formal state volume'},{'source_id':'commons-myanmar-0062','name':'Order of Thudhamma Thingaha illustration','reason':'user-drawn sample under CC BY 3.0; retained as discovery evidence but not described as an official or historical illustration'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))
