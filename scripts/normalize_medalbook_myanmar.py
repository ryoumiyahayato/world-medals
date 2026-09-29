from __future__ import annotations
import json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medalbook_myanmar.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
SWEEP=json.loads((ROOT/'data/source_sweeps/medalbook_myanmar_images_2026-09-28.json').read_text(encoding='utf-8'))
OUT_DIR=ROOT/'assets/images/medalbook_myanmar'
ROWS={
154:('缅甸联邦与社会主义共和国（1948–1988）','MMR-STAR-REVOLUTION','革命之星勋章','三级星章；正背','1953年设立；至1986年仍有授予',[1,3]),
155:('贡榜王朝（1752–1885）','BUR-KONBAUNG-TSALWE','萨尔维勋饰','肩带式金质勋饰；正背','1784年已有授予规章',[2,1]),
}

def main():
 OUT_DIR.mkdir(parents=True,exist_ok=True); items={(x['record_index'],x['image_index']):x for x in SWEEP['items'] if x['status']=='downloaded'}; records=[]; images=[]; hashes=set()
 for index,(country,family,name,variant,date,picks) in ROWS.items():
  src=RAW[index]; rid=f'{family}-MEDALBOOK-{index:03d}'; views=[]
  for n,image_no in enumerate(picks,1):
   item=items[(index,image_no)]; sp=ROOT/item['local_path']
   if item['sha256'] in hashes: raise ValueError(f'duplicate selected payload {index}:{image_no}')
   hashes.add(item['sha256'])
   with Image.open(sp) as im: im.verify()
   rel=f'assets/images/medalbook_myanmar/{index:03d}_{image_no:02d}{sp.suffix.lower()}'; shutil.copy2(sp,ROOT/rel); vk=f'{rid}-VIEW{n}'
   views.append({'key':vk,'label':'完整正面' if n==1 else '完整背面'})
   images.append({'key':f'myanmar-medalbook-{index:03d}-{image_no:02d}','record_id':rid,'view_key':vk,'local_path':rel,'source_page':src['page_url'],'image_url':item['url'],'artist':'MedalBook catalogue object photograph','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
  records.append({'id':rid,'family':family,'country_zh':country,'name':name,'original':src['page_title'],'date':date,'variant':variant,'views':views,'source_ids':[src['source_id']],'image_kind':'object_photo','html_eligible':True})
 (ROOT/'data/volumes/myanmar_medalbook_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'缅甸诸历史授予主体','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'data/volumes/myanmar_medalbook_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[{'record_index':113,'name':'Prototype Military Award','reason':'source does not identify an instituted award; prototype retained only as a raw research candidate'},{'count':164,'reason':'catalogue pages without a public object image remain in raw candidates'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))
if __name__=='__main__': main()
