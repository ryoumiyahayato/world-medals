from __future__ import annotations
import json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/'data/raw_candidates/medalbook_indonesia.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
SWEEP=json.loads((ROOT/'data/source_sweeps/medalbook_indonesia_images_2026-09-28.json').read_text(encoding='utf-8'))
OUT_DIR=ROOT/'assets/images/medalbook_indonesia'
ROWS={
17:('IDN-COMBAT-COMMUNISM','反共产主义战斗奖章','章饰；正背','九三〇事件后授予',[1,2]),
18:('IDN-FAITHFUL-SERVICE','军队忠诚服务奖章','十六年服役型；正背','1958年设立',[1,2]),
19:('IDN-FAITHFUL-SERVICE','军队忠诚服务奖章','二十四年服役型；正背','1958年设立',[1,2]),
31:('IDN-OPERATIONAL-SERVICE','军事行动服务奖章','西伊里安1969年型；正背','1969年版',[1,2]),
32:('IDN-MILITARY-SERVICE-EAST-TIMOR','东帝汶军事服务奖章','章饰；正背','1970年版',[1,3]),
41:('IDN-POLICE-HONOUR-STAR','警察荣誉星章','三级；正背','设立时间待考',[1,2]),
42:('IDN-POLICE-PRESIDENTIAL-COMMENDATION','警察总统嘉奖奖章','章饰；正背','设立时间待考',[1,3]),
93:('IDN-STAR-MAHAPUTERA','马哈普特拉星章','五级；正背','1959年设立',[4,3]),
97:('IDN-STAR-REPUBLIC','印度尼西亚共和国星章','二级星章；正背','设立时间待考',[2,1]),
}

def main():
 OUT_DIR.mkdir(parents=True,exist_ok=True); items={(x['record_index'],x['image_index']):x for x in SWEEP['items'] if x['status']=='downloaded'}; records=[]; images=[]; hashes=set()
 for index,(family,name,variant,date,picks) in ROWS.items():
  src=RAW[index]; rid=f'{family}-MEDALBOOK-{index:03d}'; views=[]
  for n,image_no in enumerate(picks,1):
   item=items[(index,image_no)]; sp=ROOT/item['local_path']
   if item['sha256'] in hashes: raise ValueError(f'duplicate selected payload {index}:{image_no}')
   hashes.add(item['sha256'])
   with Image.open(sp) as im: im.verify()
   rel=f'assets/images/medalbook_indonesia/{index:03d}_{image_no:02d}{sp.suffix.lower()}'; shutil.copy2(sp,ROOT/rel); vk=f'{rid}-VIEW{n}'
   views.append({'key':vk,'label':'完整正面' if n==1 else '完整背面'})
   images.append({'key':f'indonesia-medalbook-{index:03d}-{image_no:02d}','record_id':rid,'view_key':vk,'local_path':rel,'source_page':src['page_url'],'image_url':item['url'],'artist':'MedalBook catalogue object photograph','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
  records.append({'id':rid,'family':family,'country_zh':'印度尼西亚共和国','name':name,'original':src['page_title'],'date':date,'variant':variant,'views':views,'source_ids':[src['source_id']],'image_kind':'object_photo','html_eligible':True})
 (ROOT/'data/volumes/indonesia_medalbook_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'印度尼西亚共和国','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'data/volumes/indonesia_medalbook_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[{'count':92,'reason':'catalogue pages without a public object image remain in raw candidates'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))
if __name__=='__main__': main()
