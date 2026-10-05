"""Bounded Commons museum collection sweep; cache every page and stop on rate limits."""
from pathlib import Path
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
from PIL import Image
import requests,time,json,hashlib,re
R=Path(__file__).resolve().parents[1];C=R/'sources/cache/german_commons_20260929';I=R/'assets/images/german_completion';C.mkdir(parents=True,exist_ok=True);I.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0 (local historical catalog)'
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def fetch(url,path):
 if path.exists():return path.read_bytes()
 r=s.get(url,timeout=45)
 if r.status_code==429:raise InterruptedError('HTTP429: stopped, resume after cooldown')
 r.raise_for_status();path.write_bytes(r.content);time.sleep(8);return r.content
start='https://commons.wikimedia.org/wiki/Category:Collections_of_the_Tallinn_Museum_of_Orders_of_Knighthood'
url=start;files={};pages=[]
while url:
 key=hashlib.sha256(url.encode()).hexdigest()[:16];soup=BeautifulSoup(fetch(url,C/(key+'.html')),'html.parser');pages.append(url)
 for a in soup.select('.gallerytext a[href]'):
  if '/wiki/File:' in a['href']:files[urljoin(url,a['href'])]=a.get('title') or a.get_text(' ',strip=True)
 nxt=next((a for a in soup.select('a[href]') if a.get_text(' ',strip=True)=='next page'),None);url=urljoin(url,nxt['href']) if nxt else None
 save(C/'museum_index.json',dict(pages=pages,files=files,status='scanning' if url else 'complete'))
pattern=re.compile(r'Baden|Brunswick|Saxony|Saxon|Wurttemberg|Württemberg|Hesse|Hessen|Hanover|Hannover|Mecklenburg|Anhalt|Lippe|Waldeck|Oldenburg|Nassau|Schwarzburg|Bremen|Hamburg|Lubeck|Lübeck|Germany|German Empire',re.I)
selected={u:t for u,t in files.items() if pattern.search(t)}
save(C/'selected.json',selected)
out=[];prior=C/'photos.json'
if prior.exists():out=json.loads(prior.read_text('utf-8'))
done={x['source_page'] for x in out if x.get('status')=='decoded_pending_visual_review'}
for n,(u,t) in enumerate(selected.items()):
 if u in done:continue
 key=hashlib.sha256(u.encode()).hexdigest()[:16];row=dict(title=t,source_page=u,accessed='2026-09-29',source_collection=start)
 try:
  soup=BeautifulSoup(fetch(u,C/(key+'.html')),'html.parser');row['source_fields']={}
  for tr in soup.select('table.fileinfotpl-type-information tr'):
   cells=tr.find_all(['td','th'],recursive=False)
   if len(cells)>=2:row['source_fields'][cells[0].get_text(' ',strip=True)]=cells[1].get_text(' ',strip=True)
  row['license']=[x.get_text(' ',strip=True) for x in soup.select('.licensetpl_short')]
  row['license_urls']=[a['href'] for a in soup.select('.licensetpl a[href]') if 'creativecommons.org/' in a['href']]
  a=soup.select_one('.fullImageLink a');assert a,'No original';row['original_url']=a['href'];path=I/(key+Path(urlparse(a['href']).path).suffix.lower())
  fetch(a['href'],path)
  with Image.open(path) as im:im.load();row['width'],row['height']=im.size
  row.update(local_path=path.relative_to(R).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),status='decoded_pending_visual_review')
 except InterruptedError as e:
  save(C/'checkpoint.json',dict(status='partial_rate_limited',next_page=u,completed=len(done),planned=len(selected),reason=str(e)));raise
 except Exception as e:row.update(status='failed',error=str(e))
 out=[x for x in out if x['source_page']!=u]+[row];save(prior,out);print(n+1,len(selected),row['status'],t,flush=True)
save(C/'checkpoint.json',dict(status='completed_selected_german_objects',planned=len(selected),completed=sum(x['status']=='decoded_pending_visual_review' for x in out),collection_pages=len(pages),collection_file_pages=len(files)))
