"""Resumable bounded object-page sweep of the complete cached imperial collection."""
from pathlib import Path
import json,time,hashlib
import requests
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];sid='emedals_austria_imperial_20261005'
rows=[json.loads(line) for line in (R/'data/raw_candidates'/f'{sid}.jsonl').read_text(encoding='utf-8').splitlines()]
C=R/'sources/pages'/sid;C.mkdir(parents=True,exist_ok=True)
out=R/'data/raw_candidates'/f'{sid}_objects.jsonl'
done={}
if out.exists():
    done={x['object_id']:x for x in map(json.loads,out.read_text(encoding='utf-8').splitlines())}
s=requests.Session();s.headers['User-Agent']='World-medals public catalogue research/1.0'
for row in rows:
    oid=row['object_id']
    if oid in done and done[oid]['status']=='object_page_cached':continue
    p=C/(oid+'.html');record=dict(object_id=oid,object_page=row['object_page'],accessed='2026-10-05')
    try:
        if not p.exists():
            response=s.get(row['object_page'],timeout=30)
            if response.status_code in (403,429):
                record.update(status='access_limited',http_status=response.status_code)
                done[oid]=record;break
            response.raise_for_status();p.write_bytes(response.content);time.sleep(1)
        payload=p.read_bytes();soup=BeautifulSoup(payload,'html.parser')
        article=soup.select_one('.product__description') or soup.select_one('[class*="product-description"]')
        record.update(status='object_page_cached',html=p.relative_to(R).as_posix(),sha256=hashlib.sha256(payload).hexdigest(),title=soup.title.get_text(' ',strip=True) if soup.title else '',description=article.get_text(' ',strip=True) if article else row['description'],images=row['images'],rights=row['rights'])
    except Exception as exc:record.update(status='fetch_failed',error_type=type(exc).__name__)
    done[oid]=record
    if len(done)%25==0:
        out.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in done.values()),encoding='utf-8')
        print('Processed object pages',len(done),'of',len(rows),flush=True)
out.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in done.values()),encoding='utf-8')
checkpoint=dict(as_of='2026-10-05',scope=sid,planned=len(rows),cached=sum(x['status']=='object_page_cached' for x in done.values()),failed=sum(x['status']!='object_page_cached' for x in done.values()),remaining=len(rows)-len(done),next='Reconcile family/variant evidence and obtain complete photos; cached pages are not confirmed new awards')
(R/'data/checkpoints/emedals_objects_20261005.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
print(json.dumps(checkpoint),flush=True)
