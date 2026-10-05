"""Object-page and original-image closed loop for selected candidates; not publication approval."""
from pathlib import Path
import requests,json,hashlib,time
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];sid='emedals_austria_imperial_20261005'
rows=[json.loads(l) for l in (R/'data/raw_candidates'/f'{sid}.jsonl').read_text('utf-8').splitlines()]
chosen={'9490202919189','9486246936853','8522061873429','9575620313365','8521757819157','9515819434261'}
out=[];D=R/'assets/raw'/sid;D.mkdir(parents=True,exist_ok=True)
session=requests.Session()
for row in rows:
 if row['object_id'] not in chosen:continue
 p=R/'sources/pages'/sid/(row['object_id']+'.html')
 if not p.exists():
  response=session.get(row['object_page'],timeout=40);response.raise_for_status();p.write_bytes(response.content);time.sleep(.7)
 image_records=[]
 for n,im in enumerate(row['images']):
  f=D/(row['object_id']+'-'+str(n+1)+'.jpg')
  if not f.exists():
   response=session.get(im['image_url'],timeout=40);response.raise_for_status();f.write_bytes(response.content);time.sleep(.3)
  with Image.open(f) as pic:dimensions=list(pic.size);pic.verify()
  image_records.append(dict(im,local_path=f.relative_to(R).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),dimensions=dimensions,decoded=True,status='visual_review_pending',publication_eligible=False))
 out.append(dict(row,images=image_records,object_html=p.relative_to(R).as_posix()))
 print(row['object_id'],len(image_records),flush=True)
stage=R/'data/staging'/sid;stage.mkdir(parents=True,exist_ok=True)
(stage/'review_candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
canvas=Image.new('RGB',(1200,len(out)*190),'white');draw=ImageDraw.Draw(canvas)
for y,row in enumerate(out):
 draw.text((8,y*190+2),row['object_id']+' '+row['page_title'][:100],fill='black')
 for x,im in enumerate(row['images'][:7]):
  with Image.open(R/im['local_path']) as pic:tile=ImageOps.contain(pic.convert('RGB'),(165,155));canvas.paste(tile,(x*170+5,y*190+25))
canvas.save(stage/'contact.jpg')
print('contact',stage/'contact.jpg')
