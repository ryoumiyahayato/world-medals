"""Cache complete visible country trees and their linked originals, resumably.

Raw candidates only: every photograph still needs curator approval before HTML.
"""
from pathlib import Path
from urllib.parse import urljoin,urlsplit
import json,hashlib,time,requests,re,sys
from bs4 import BeautifulSoup
from PIL import Image
R=Path(__file__).resolve().parents[1]
C=R/'sources/cache/east_south_africa_bulk';O=R/'data/raw_candidates/east_south_africa_bulk';I=R/'assets/raw/east_south_africa_bulk'
for p in (C,O,I):p.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers['User-Agent']='world-medals-research/1.0 (offline research; cached incremental requests)'
known={}
for p in (R/'data/raw_candidates/minimum_east_south_africa').glob('*.json'):
 row=json.loads(p.read_text(encoding='utf-8'))
 if row.get('directory_cache'):known[row['directory']]=R/row['directory_cache']
 if row.get('object_cache'):known[row['object_page']]=R/row['object_cache']
 for i in row.get('images',[]):known[i['url']]=R/i['path']
def fetch(url,target):
 if url in known and known[url].exists():return known[url]
 if not target.exists():
  r=s.get(url,timeout=20);r.raise_for_status();target.write_bytes(r.content);time.sleep(1)
 return target
for country in sys.argv[1:]:
 queue=['https://wawards.org/'+country+'.html'];seen=set();failures=[];pages=0;images=0
 while queue:
  url=queue.pop(0)
  if url in seen:continue
  seen.add(url);key=hashlib.sha256(url.encode()).hexdigest()[:16];out=O/(country+'-'+key+'.json')
  try:
   cache=fetch(url,C/(country+'-'+key+'.html'));soup=BeautifulSoup(cache.read_bytes(),'html.parser')
   linked=[]
   for a in soup.select('a[href]'):
    href=urlsplit(urljoin(url,a['href'])).path
    href=re.sub(r'^/(en|ru)/','/',href)
    if href.startswith('/'+country+'/') and href.endswith('.html'):
     linked.append('https://wawards.org'+href)
   queue.extend(x for x in dict.fromkeys(linked) if x not in seen)
   if out.exists():
    prior=json.loads(out.read_text(encoding='utf-8'));pages+=1;images+=len(prior.get('images',[]));continue
   title=soup.find('h1') or soup.find('title')
   row=dict(source_id='WAW-BULK-'+country.upper()+'-'+key,title=title.get_text(' ',strip=True) if title else url,source_page=url,accessed='2026-09-29',cache=cache.relative_to(R).as_posix(),source_text=soup.get_text(' ',strip=True),linked_pages=linked,images=[],status='candidate_unreviewed')
   urls=list(dict.fromkeys(urljoin(url,a['href']) for a in soup.select('a[href]') if a['href'].startswith('/images/'+country+'/') and re.search(r'\.(jpg|jpeg|png|webp)$',a['href'],re.I)))
   for iu in urls:
    try:
     ikey=hashlib.sha256(iu.encode()).hexdigest()[:20];ip=fetch(iu,I/(country+'-'+ikey+Path(iu).suffix))
     with Image.open(ip) as im:im.load();w,h=im.size
     row['images'].append(dict(url=iu,local_path=ip.relative_to(R).as_posix(),width=w,height=h,sha256=hashlib.sha256(ip.read_bytes()).hexdigest(),review_status='pending',license='Copyright source owners; local research only, no public redistribution permission inferred'))
    except Exception as e:row.setdefault('image_failures',[]).append(dict(url=iu,error=str(e)))
   out.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');pages+=1;images+=len(row['images'])
   print(country,pages,row['title'],len(row['images']),flush=True)
  except Exception as e:failures.append(dict(url=url,error=str(e)));print(country,'FAILED',url,str(e),flush=True)
  checkpoint=dict(as_of='2026-09-29',country=country,status='partial' if queue or failures else 'completed_visible_tree',pages=pages,downloaded_images=images,remaining_urls=queue,failures=failures,boundary='Same-country HTML paths reachable from country index; no off-country gallery or unrelated navigation')
  (C/(country+'-checkpoint.json')).write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
 image_failures=[]
 for candidate in O.glob(country+'-*.json'):
  image_failures.extend(json.loads(candidate.read_text(encoding='utf-8')).get('image_failures',[]))
 checkpoint=dict(as_of='2026-09-29',country=country,status='partial' if failures or image_failures else 'completed_visible_tree',pages=pages,downloaded_images=images,remaining_urls=[],failures=failures,image_failures=image_failures,boundary='Same-country HTML paths reachable from country index; completion refers to raw discovery, not reviewed atlas inclusion')
 (C/(country+'-checkpoint.json')).write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
 print('COUNTRY FINISHED',country,pages,images,'failures',len(failures),flush=True)
