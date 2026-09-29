"""Follow historical period subdirectories missed by the flat minimum sweep."""
from pathlib import Path
from urllib.parse import urljoin
import requests,json,time,hashlib,re
from bs4 import BeautifulSoup
from PIL import Image
R=Path(__file__).resolve().parents[1]
C=R/'sources/cache/minimum_east_south_africa'; O=R/'data/raw_candidates/minimum_east_south_africa'; I=R/'assets/raw/minimum_east_south_africa'
s=requests.Session();s.headers['User-Agent']='world-medals-research/1.0'
for slug in ['ethiopia','madagascar','south-africa','zimbabwe']:
 p=O/(slug+'.json');row=json.loads(p.read_text(encoding='utf-8'))
 if row['images']:continue
 links={}
 for cache in sorted(C.glob(slug+'-object-*.html')):
  soup=BeautifulSoup(cache.read_bytes(),'html.parser')
  for a in soup.select('a[href]'):
   href=a['href']
   if href.startswith('/'+slug+'/') and href.count('/')>=3:
    links[urljoin('https://wawards.org',href)]=a.get_text(' ',strip=True)
 row['nested_candidates']=[dict(url=u,name=n) for u,n in links.items()]
 for n,(url,name) in enumerate(list(links.items())[:8]):
  try:
   op=C/(slug+'-nested-'+str(n)+'.html')
   if not op.exists():
    r=s.get(url,timeout=20);r.raise_for_status();op.write_bytes(r.content);time.sleep(1)
   soup=BeautifulSoup(op.read_bytes(),'html.parser')
   image_urls=list(dict.fromkeys(urljoin(url,a['href']) for a in soup.select('a[href]') if a['href'].startswith('/images/') and re.search(r'\.(jpg|jpeg|png)$',a['href'],re.I)))
   if not image_urls:continue
   row.update(object_page=url,object_name=name,object_cache=op.relative_to(R).as_posix(),source_text=soup.get_text(' ',strip=True),image_candidates=image_urls)
   for j,iu in enumerate(image_urls[:5]):
    ip=I/(slug+'-'+str(j)+Path(iu).suffix)
    try:
     if not ip.exists():
      r=s.get(iu,timeout=20);r.raise_for_status();ip.write_bytes(r.content);time.sleep(1)
     with Image.open(ip) as im:im.load();w,h=im.size
     row['images'].append(dict(url=iu,path=ip.relative_to(R).as_posix(),width=w,height=h,sha256=hashlib.sha256(ip.read_bytes()).hexdigest(),visual_status='pending',license='Copyright source owners; local research reference only'))
    except Exception as e:row.setdefault('errors',[]).append(str(e))
   if row['images']:break
  except Exception as e:row.setdefault('errors',[]).append(str(e))
 row['status']='downloaded_pending_review' if row['images'] else 'nested_source_boundary'
 p.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
 print(slug,len(row['images']),flush=True)
