"""Cache the public Austria Imperial product catalogue; preserve research-only image leads."""
from pathlib import Path
import requests,json,time,re,hashlib
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
S='emedals_austria_imperial_20261005'
C=R/'sources/pages'/S; C.mkdir(parents=True,exist_ok=True)
raw=R/'data/raw_candidates'/f'{S}.jsonl'
session=requests.Session();session.headers['User-Agent']='World-medals bounded catalogue research/1.0'
rows=[];pages=[]
for page in range(1,101):
    url=f'https://www.emedals.com/collections/europe-austria-imperial/products.json?limit=250&page={page}'
    cache=C/f'products-{page}.json'
    if cache.exists(): payload=cache.read_bytes()
    else:
        response=session.get(url,timeout=45);response.raise_for_status();payload=response.content
        cache.write_bytes(payload);time.sleep(1)
    products=json.loads(payload)['products'];pages.append({'url':url,'products':len(products),'sha256':hashlib.sha256(payload).hexdigest()})
    for p in products:
        body=BeautifulSoup(p.get('body_html',''),'html.parser').get_text(' ',strip=True)
        rows.append(dict(source_id=S,object_id=str(p['id']),page_title=p['title'],original_name=p['title'],aliases=[],date_candidates=re.findall(r'\b(?:17|18|19|20)\d{2}\b',body),category=p.get('product_type',''),tags=p.get('tags',[]),description=body,object_page='https://www.emedals.com/products/'+p['handle'],image_page='https://www.emedals.com/products/'+p['handle'],images=[dict(image_url=i['src'],image_id=str(i['id']),width=i.get('width'),height=i.get('height'),alt=i.get('alt')) for i in p.get('images',[])],market_variants=p.get('variants',[]),accessed='2026-10-05',status='raw_pending_family_variant_review',rights='No redistribution permission established; research cache only'))
    raw.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
    print('page',page,'products',len(products),'total',len(rows),flush=True)
    if len(products)<250:break
out=R/'data/source_sweeps'/f'{S}.json'
out.write_text(json.dumps(dict(source_id=S,accessed='2026-10-05',scope='Austria Imperial collection public products API including archived products; object HTML and image review pending',status='catalogue_fields_complete' if len(products)<250 else 'partial',pages=pages,raw_candidates=len(rows),image_leads=sum(len(x['images']) for x in rows)),ensure_ascii=False,indent=2),encoding='utf-8')
