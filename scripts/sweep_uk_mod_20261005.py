"""Cache and enumerate every section of the supplied single-page MOD guide."""
from pathlib import Path
import json, hashlib
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
url='https://www.gov.uk/guidance/medals-campaigns-descriptions-and-eligibility'
cache=R/'sources/pages/uk_mod_20261005.html';cache.parent.mkdir(parents=True,exist_ok=True)
if not cache.exists():
    response=requests.get(url,timeout=35,headers={'User-Agent':'World-medals public source research/1.0'});response.raise_for_status();cache.write_bytes(response.content)
soup=BeautifulSoup(cache.read_bytes(),'html.parser')
article=soup.select_one('.gem-c-govspeak')
assert article is not None
headings=article.find_all(['h2','h3','h4'])
rows=[]
for i,h in enumerate(headings):
    text=[];images=[];links=[]
    for sibling in h.next_siblings:
        if getattr(sibling,'name',None) in ('h2','h3','h4'):break
        if hasattr(sibling,'find_all'):
            value=sibling.get_text(' ',strip=True)
            if value:text.append(value)
            for im in sibling.find_all('img'):
                if im.get('src'):images.append(dict(image_url=urljoin(url,im['src']),caption=im.get('alt','')))
            for a in sibling.find_all('a',href=True):links.append(dict(url=urljoin(url,a['href']),title=a.get_text(' ',strip=True)))
    rows.append(dict(source_id='user_20261005_uk_mod',section=i+1,level=h.name,title=h.get_text(' ',strip=True),object_page=url+'#'+h.get('id',''),accessed='2026-10-05',description_original=' '.join(text),images=images,links=links,status='section_read_crosswalk_pending_not_necessarily_an_award'))
out=R/'data/raw_candidates/uk_mod_guide_20261005.jsonl';out.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
checkpoint=dict(as_of='2026-10-05',source_id='user_20261005_uk_mod',status='completed_bounded_article',scope='Supplied guide only: all visible headings, descriptions, image and outbound reference links. Linked documents are queued, not claimed exhausted.',pages=1,sections=len(rows),unique_image_leads=len({im['image_url'] for x in rows for im in x['images']}),article_sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),next='Crosswalk to existing UK MOD completion records and resolve remaining image gaps; no new awards asserted by heading count')
(R/'data/checkpoints/uk_mod_guide_20261005.json').write_text(json.dumps(checkpoint,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checkpoint))
