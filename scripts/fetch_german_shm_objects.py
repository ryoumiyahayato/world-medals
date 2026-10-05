from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import requests,time,json,hashlib
R=Path(__file__).resolve().parents[1];C=R/'sources/cache/german_shm_20260929';I=R/'assets/images/german_completion'
selected=json.loads((R/'data/staging/german_completion/shm_selected.json').read_text('utf-8'))
items={x['id']:x for x in json.loads((C/'candidates.json').read_text('utf-8'))};out=json.loads((C/'objects.json').read_text('utf-8')) if (C/'objects.json').exists() else []
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0'
def get(u,p):
 if p.exists():return p.read_bytes()
 r=s.get(u,timeout=40);r.raise_for_status();p.write_bytes(r.content);time.sleep(4);return r.content
for spec in selected:
 if any(o['id']==spec['id'] for o in out):continue
 x=items[spec['id']];p=C/(x['id']+'.html');row=dict(spec,metadata=x,source_page=x['url'],images=[])
 try:
  soup=BeautifulSoup(get(x['url'],p),'html.parser');row['source_text']=soup.get_text(' ',strip=True)
  urls=list(dict.fromkeys(a['href'] for a in soup.select('a[href]') if a.get_text(' ',strip=True)=='Ladda ner media' and 'media.samlingar.shm.se/item/' in a['href']))
  for u in urls:
   key=u.rsplit('/',1)[-1];dest=I/('shm-'+key+'.jpg');get(u,dest)
   with Image.open(dest) as im:im.load();w,h=im.size
   row['images'].append(dict(original_url=u,local_path=dest.relative_to(R).as_posix(),width=w,height=h,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),status='decoded_pending_review'))
  row['status']='downloaded_pending_review'
 except Exception as e:row['status']='partial';row['error']=str(e)
 out.append(row);(C/'objects.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8');print(spec['id'],row['status'],len(row['images']),flush=True)
