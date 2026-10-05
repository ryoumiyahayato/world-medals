import json,time,hashlib
from pathlib import Path
from PIL import Image
import requests
R=Path(__file__).resolve().parents[1];S=R/'data/staging/france_identify_20260930';D=R/'assets/raw/france_identify_20260930';D.mkdir(exist_ok=True)
raw=[json.loads(s) for s in (R/'data/raw_candidates/france_identify_20260930.jsonl').read_text('utf-8').splitlines() if s]
dest=S/'image_manifest.json';items=json.loads(dest.read_text('utf-8')) if dest.exists() else []
known={x['image_url']:x for x in items};probe=json.loads((S/'download_probe.json').read_text('utf-8'));session=requests.Session();session.headers.update({'User-Agent':'WorldMedalsResearch/1.0','Accept':'image/jpeg,image/png,image/*;q=0.9,*/*;q=0.5'})
for row in raw:
 for im in row['content_images']:
  u=im['url']
  if u in known:continue
  key=hashlib.sha256(u.encode()).hexdigest()[:16];ext=Path(u.split('?')[0]).suffix.lower();p=D/(key+ext)
  try:
   if u==probe['original_url']:p=R/probe['local_path']
   elif not p.exists():
    res=session.get(u,timeout=25);res.raise_for_status();p.write_bytes(res.content);time.sleep(1)
   with Image.open(p) as pic:pic.load();w,h=pic.size
   x=dict(image_url=u,object_page=row['object_page'],title=row['page_title'],local_path=p.relative_to(R).as_posix(),width=w,height=h,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='decoded_pending_visual_review',credit='IdentifyMedals / Yisela Alvarez Trentini',permission='Publisher permits reuse with attribution and watermark retained; upstream third-party rights not individually established. Local research edition only.',permission_url='https://www.identifymedals.com/about-images-from-identifymedals-com/')
  except Exception as e:x=dict(image_url=u,object_page=row['object_page'],title=row['page_title'],status='failed',error=str(e))
  items.append(x);known[u]=x;dest.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n','utf-8')
  if len(items)%10==0:print('images',len(items),flush=True)
print('finished',len(items))
