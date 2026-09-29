"""Bounded country-index discovery and first award image bundle; no automatic ingestion."""
from pathlib import Path
from urllib.parse import urljoin
import requests, json, time, hashlib, re
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'sources/cache/minimum_east_south_africa'
OUT=ROOT/'data/raw_candidates/minimum_east_south_africa'
IMAGES=ROOT/'assets/raw/minimum_east_south_africa'
for p in (CACHE,OUT,IMAGES):p.mkdir(parents=True,exist_ok=True)
countries={'ethiopia':'埃塞俄比亚','djibouti':'吉布提','somalia':'索马里','kenya':'肯尼亚','uganda':'乌干达','tanzania':'坦桑尼亚','rwanda':'卢旺达','burundi':'布隆迪','comoros':'科摩罗','madagascar':'马达加斯加','south-africa':'南非','namibia':'纳米比亚','botswana':'博茨瓦纳','zimbabwe':'津巴布韦','zambia':'赞比亚','malawi':'马拉维','mozambique':'莫桑比克','angola':'安哥拉','lesotho':'莱索托','swaziland':'斯威士兰／埃斯瓦蒂尼'}
s=requests.Session();s.headers['User-Agent']='world-medals-research/1.0 (cached offline research)'
def fetch(url,path):
    if not path.exists():
        r=s.get(url,timeout=20);r.raise_for_status();path.write_bytes(r.content);time.sleep(1)
    return path.read_bytes()
for slug,zh in countries.items():
    result=OUT/(slug+'.json')
    if result.exists():continue
    row={'country':zh,'slug':slug,'accessed':'2026-09-29','status':'pending','candidates':[],'images':[]}
    try:
        url='https://wawards.org/'+slug+'.html'
        p=CACHE/(slug+'.html'); soup=BeautifulSoup(fetch(url,p),'html.parser')
        links={urljoin(url,a['href']):a.get_text(' ',strip=True) for a in soup.select('a[href]') if a['href'].startswith('/'+slug+'/')}
        row.update(directory=url,directory_cache=p.relative_to(ROOT).as_posix(),candidates=[{'url':u,'name':n} for u,n in links.items()])
        # Minimum country coverage: preserve all index candidates, inspect up to
        # three leading entries until an illustrated object page is found.
        for i,(page,name) in enumerate(list(links.items())[:3]):
            op=CACHE/(slug+'-object-'+str(i)+'.html'); obj=BeautifulSoup(fetch(page,op),'html.parser')
            image_urls=list(dict.fromkeys(urljoin(page,a['href']) for a in obj.select('a[href]') if a['href'].startswith('/images/'+slug+'/') and re.search(r'\.(jpg|jpeg|png)$',a['href'],re.I)))
            if not image_urls:continue
            row.update(object_page=page,object_name=name,object_cache=op.relative_to(ROOT).as_posix(),source_text=obj.get_text(' ',strip=True),image_candidates=image_urls)
            for j,iu in enumerate(image_urls[:5]):
                ip=IMAGES/(slug+'-'+str(j)+Path(iu).suffix)
                try:
                    b=fetch(iu,ip)
                    with Image.open(ip) as im:im.load();w,h=im.size
                    row['images'].append({'url':iu,'path':ip.relative_to(ROOT).as_posix(),'width':w,'height':h,'sha256':hashlib.sha256(b).hexdigest(),'visual_status':'pending','license':'Copyright Ilja Repetski / source image owners; no open licence identified; local research reference only'})
                except Exception as e:row.setdefault('errors',[]).append(str(e))
            break
        row['status']='downloaded_pending_review' if row['images'] else 'no_image_in_bounded_sample'
    except Exception as e:row.update(status='blocked',error=str(e))
    result.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(slug,row['status'],len(row['images']),flush=True)
