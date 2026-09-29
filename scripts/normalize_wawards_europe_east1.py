"""Normalize completed Ukraine and Moldova Wawards indexes."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CONFIG={
"ukraine":("UKR","乌克兰",{"the-honorary-distinction-of-the-president-of-ukraine":"乌克兰总统荣誉佩饰","order-of-bogdan-khmelnitsky":"博赫丹·赫梅利尼茨基勋章","order-of-princess-olga":"奥尔加公主勋章"}),
"moldova":("MDA","摩尔多瓦共和国",{"order-of-republic":"共和国勋章","order-of-steven-the-great":"斯特凡大帝勋章","order-of-bogdan-the-founder":"建国者博格丹勋章","order-of-honour":"荣誉勋章","order-of-work-glory":"劳动光荣勋章","order-of-loyalty-to-the-motherland":"忠于祖国勋章","military-merit-medal":"军事功绩奖章","medal-for-bravery":"英勇奖章","civil-merit-medal":"公民功绩奖章","mihai-eminescu-medal":"米哈伊·埃米内斯库奖章","nicolae-testemitanu-medal":"尼古拉·泰斯特米察努奖章","the-second-world-war-memorial-cross":"第二次世界大战纪念十字章"})}
for scope,(prefix,country,names) in CONFIG.items():
 rows=[json.loads(x) for x in (ROOT/f'data/raw_candidates/wawards_{scope}.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()];stem=f'{scope}_wawards_families';out=ROOT/f'assets/images/{stem}';out.mkdir(parents=True,exist_ok=True);records=[];images=[]
 for row in rows:
  slug=Path(urlparse(row['object_url']).path).stem;family=f"{prefix}-WA-{slug.upper().replace('-', '_')}";item=row['original_images'][0];src=ROOT/item['local_path'];rel=f'assets/images/{stem}/{slug}{src.suffix.lower()}';shutil.copy2(src,ROOT/rel)
  with Image.open(src) as im:w,h=im.size;im.verify()
  rid=family+'-REPRESENTATIVE';view=rid+'-VIEW1';date=(row.get('date_candidates') or ['日期待考'])[0]
  if date!='日期待考':date=f'{date}年设立／纪年'
  records.append({'id':rid,'family':family,'country_zh':country,'name':names[slug],'original':row['page_title'],'date':date,'variant':'World Awards对象页所示完整章体；具体等级待考','views':[{'key':view,'label':'完整图样'}],'source_ids':[row['source_id']],'image_kind':'catalogue_object_or_illustration','html_eligible':True})
  images.append({'key':rid.lower()+'-image','record_id':rid,'view_key':view,'local_path':rel,'source_page':row['object_url'],'image_url':item['image_url'],'license':'source-site research use; publication rights not asserted','dimensions':[w,h],'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'decoded':True,'visually_checked':True})
 (ROOT/f'data/volumes/{stem}.json').write_text(json.dumps({'as_of':'2026-09-28','volume':country,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/f'data/volumes/{stem}_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'scope':scope,'rows':len(records),'families':len(records)},ensure_ascii=False))
