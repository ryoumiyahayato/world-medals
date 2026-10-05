"""Fetch observed Commons object pages and original binaries, with a review gate."""
from pathlib import Path
from urllib.parse import quote,urlparse
import requests,json,hashlib,time,re
from bs4 import BeautifulSoup
from PIL import Image
R=Path(__file__).resolve().parents[1];C=R/'sources/cache/france_commons_completion';I=R/'assets/images/france_completion';I.mkdir(parents=True,exist_ok=True)
files=json.loads((R/'data/queues/france_commons_completion.json').read_text('utf-8'))['files']
selected=[]
exclude=re.compile(r'ribbon|ruban|diplôme|Dixmude|Eva Lallemant|Paul Delvaux|Tadashi|Louis Antoine|brevet',re.I)
categories=['douanes','eaux et forêts','engagement ultramarin','enseignement du premier degré','enseignement technique','Médaille de la famille','Médaille de la Fidélité française','French Liberation Medal','Ordre des Arts et des Lettres','Ordre du Brassard de Bordeaux']
for title,cats in files.items():
 if not exclude.search(title) and any(any(k in c for k in categories) for c in cats):selected.append((title,cats))
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0 (local historical catalog)';out=[]
for n,(title,cats) in enumerate(selected):
 key=hashlib.sha256(title.encode()).hexdigest()[:16];page=C/(key+'.html');row=dict(title=title,categories=cats,source_page='https://commons.wikimedia.org/wiki/'+quote(title.replace(' ','_'),safe=":()_"),accessed='2026-09-29')
 try:
  if not page.exists():
   r=s.get(row['source_page'],timeout=25)
   if r.status_code==429:raise InterruptedError('Rate limited; resume later')
   r.raise_for_status();page.write_bytes(r.content);time.sleep(15)
  soup=BeautifulSoup(page.read_bytes(),'html.parser');main=soup.select_one('#mw-content-text');row['source_text']=main.get_text(' ',strip=True)
  row['source_fields']={}
  for tr in soup.select('table.fileinfotpl-type-information tr'):
   cells=tr.find_all(['td','th'],recursive=False)
   if len(cells)>=2:row['source_fields'][cells[0].get_text(' ',strip=True)]=cells[1].get_text(' ',strip=True)
  row['license']=[x.get_text(' ',strip=True) for x in soup.select('.licensetpl_short')]
  row['license_urls']=[a['href'] for a in soup.select('a[href]') if 'creativecommons.org/' in a['href']]
  link=soup.select_one('.fullImageLink a');assert link,'Missing original link';row['original_url']=link['href']
  path=I/(key+Path(urlparse(link['href']).path).suffix.lower())
  if not path.exists():
   r=s.get(link['href'],timeout=35)
   if r.status_code==429:raise InterruptedError('Rate limited; resume later')
   r.raise_for_status();path.write_bytes(r.content);time.sleep(15)
  with Image.open(path) as im:im.load();row['width'],row['height']=im.size
  row.update(local_path=path.relative_to(R).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),status='decoded_pending_visual_review')
 except InterruptedError:
  (C/'download_interrupted.json').write_text(json.dumps({'next_title':title,'reason':'rate limit'},ensure_ascii=False),'utf-8');raise
 except Exception as e:row.update(status='failed',error=str(e))
 out.append(row);(C/'photos.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8');print(n+1,len(selected),row['status'],title,flush=True)

