"""Bounded, cached sweep of the France directory's visible object pages."""
import json,time,hashlib
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];S=R/'data/staging/france_identify_20260930';C=R/'sources/cache/france_identify_20260930';O=C/'objects';O.mkdir(exist_ok=True)
seed=json.loads((S/'root_directory_seed.json').read_text('utf-8'))
session=requests.Session();session.headers.update({'User-Agent':'WorldMedalsResearch/1.0','Accept':'text/html,application/xhtml+xml;q=0.9,*/*;q=0.5'})
raw=[];failed=[]
def save():
 (R/'data/raw_candidates/france_identify_20260930.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in raw)+'\n','utf-8')
 (S/'discovery.json').write_text(json.dumps(dict(planned=len(seed),read=len(raw),failed=failed,remaining=[x['url'] for x in seed if x['url'] not in {y['object_page'] for y in raw}],directories=6,visible_pagination_links=0,scope='France landing and five visible period catalogues; all h2/h3 medal cards including related-country references',objects=seed),ensure_ascii=False,indent=2),'utf-8')
save()
for i,item in enumerate(seed):
 u=item['url'];p=O/(hashlib.sha256(u.encode()).hexdigest()[:16]+'.html')
 try:
  if not p.exists():
   resp=session.get(u,timeout=25);resp.raise_for_status();p.write_bytes(resp.content);time.sleep(1)
  soup=BeautifulSoup(p.read_bytes(),'html.parser');title=soup.find('h1');title=title.get_text(' ',strip=True) if title else item['title']
  # Elementor post content is separate from related-medal grids and adverts.
  blocks=soup.select('.elementor-widget-theme-post-content,.entry-content')
  body='\n'.join(b.get_text(' ',strip=True) for b in blocks)
  if not body:body='\n'.join(b.get_text(' ',strip=True) for b in soup.select('.elementor-widget-text-editor'))
  og=soup.select_one('meta[property="og:image"]');hero=og.get('content') if og else None
  images=[]
  for im in soup.select('.elementor-widget-theme-post-featured-image img'):
   src=im.get('data-src') or im.get('src')
   if src:images.append(dict(url=urljoin(u,src),alt=im.get('alt',''),srcset=im.get('srcset','')))
  links=[dict(url=urljoin(u,a['href']),text=a.get_text(' ',strip=True)) for b in blocks for a in b.select('a[href]')]
  raw.append(dict(source_id='IM-FR-'+hashlib.sha256(u.encode()).hexdigest()[:12],page_title=title,original_name=item['title'],date_candidates='retained in source_text',category='France directory; issuer pending review',grade_material_clues='retained in source_text',object_page=u,cache_path=p.relative_to(R).as_posix(),source_text=body,hero_image=hero,content_images=images,links=links,status='read_pending_merge',accessed='2026-09-30'))
 except Exception as e:failed.append(dict(url=u,error=str(e)))
 save()
 if (i+1)%10==0:print(f'{i+1}/{len(seed)}; read={len(raw)} failed={len(failed)}',flush=True)
print(json.dumps(dict(read=len(raw),failed=len(failed))))
