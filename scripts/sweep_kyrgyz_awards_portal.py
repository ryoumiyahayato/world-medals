"""Exhaust the active and discontinued catalogues of Kyrgyzstan's official awards portal."""
from __future__ import annotations
import hashlib, html, json, re, shutil, subprocess, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
AS_OF='2026-09-28'
BASE='https://nagrada.srs.kg'
PAGES=[('active',BASE+'/site/awards?Length=4'),('inactive',BASE+'/site/awardsNoActive?Length=4')]
CACHE=ROOT/'sources/pages/kyrgyz_awards_portal'
RAW_DIR=ROOT/'assets/raw/kyrgyz_awards_portal';RAW_DIR.mkdir(parents=True,exist_ok=True)
CAND=ROOT/'data/raw_candidates/kyrgyz_awards_portal.jsonl'
STATE=ROOT/'data/source_sweeps/kyrgyz_awards_portal_2026-09-28.json'

def textify(value:str)->str:
    value=re.sub(r'<script.*?</script>|<style.*?</style>',' ',value,flags=re.I|re.S)
    value=re.sub(r'<[^>]+>',' ',value)
    return ' '.join(html.unescape(value).split())

records=[]
for status,page_url in PAGES:
    doc=(CACHE/f'{status}.html').read_text(encoding='utf-8')
    for ordinal,block in enumerate(re.split(r'<li class="catalog__item[^>]*',doc)[1:],1):
        item_match=re.search(r'\bid="([^"]+)"',block[:100])
        item_id=item_match.group(1) if item_match else f'{status}-{ordinal:03d}'
        title_m=re.search(r'<h3 class="catalog__item-title">(.*?)</h3>',block,re.I|re.S)
        image_m=re.search(r'data-src="([^"]*)"',block,re.I)
        body_m=re.search(r'<div class="catalog__item-body">(.*?)(?:</div>\s*</div>\s*</li>|</li>)',block,re.I|re.S)
        if not title_m: continue
        title=textify(title_m.group(1)); src=html.unescape(image_m.group(1)).strip() if image_m else ''
        image_url=BASE+urllib.parse.quote(src,safe='/') if src else ''
        sid=f'kyrgyz-awards-{status}-{item_id}'
        records.append({'source_id':sid,'source_system':'Kyrgyz Republic State Awards Portal','page_title':title,'working_name_zh':'待译','original_name':title,'english_name':'','aliases':[],'date_candidates':[],'category':'current-state-award-or-honour' if status=='active' else 'discontinued-state-award-or-honour','family_hint':re.sub(r'\W+',' ',title.lower()).strip(),'grade_material_clues':textify(body_m.group(1))[:2000] if body_m else '','page_url':page_url+'#'+str(item_id),'image_page_url':page_url+'#'+str(item_id),'original_image_urls':[image_url] if image_url else [],'notes':'Official portal catalogue item; status='+status,'status':'RAW_CANDIDATE','portal_status':status,'portal_item_id':item_id})

unique=[]
for r in records:
    if r['original_image_urls'] and r['original_image_urls'][0] not in unique: unique.append(r['original_image_urls'][0])

def fetch(job):
    n,url=job; ext=Path(urllib.parse.urlsplit(url).path).suffix.lower() or '.jpg'; out=RAW_DIR/f'{n:03d}{ext}'
    if not out.exists() or out.stat().st_size<100:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 world-medals research'})
        try:
            with urllib.request.urlopen(req,timeout=45) as resp: out.write_bytes(resp.read())
        except Exception:
            subprocess.run(['curl.exe','-L','--retry','1','--connect-timeout','15','--max-time','120','-A','Mozilla/5.0 world-medals research',url,'-o',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with Image.open(out) as im: dims=list(im.size);im.verify()
    data=out.read_bytes();return {'image_index':n,'url':url,'local_path':out.relative_to(ROOT).as_posix(),'status':'downloaded','width':dims[0],'height':dims[1],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

items=[]; failures=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    futures={pool.submit(fetch,(i,u)):(i,u) for i,u in enumerate(unique,1)}
    for future in as_completed(futures):
        i,u=futures[future]
        try: items.append(future.result())
        except Exception as exc: failures.append({'image_index':i,'url':u,'error':repr(exc)})
items.sort(key=lambda x:x['image_index'])
by_url={x['url']:x for x in items}
for r in records:
    if r['original_image_urls'] and r['original_image_urls'][0] in by_url:
        r['local_image_path']=by_url[r['original_image_urls'][0]]['local_path']
CAND.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in records),encoding='utf-8')
STATE.write_text(json.dumps({'as_of':AS_OF,'source_id':'kyrgyz_state_awards_portal','source_name':'Kyrgyz Republic State Awards Portal — active and discontinued catalogues','seed_urls':[x[1] for x in PAGES],'status':'completed' if not failures else 'partial','planned_pages':2,'processed_pages':2,'catalogue_items':len(records),'unique_image_urls':len(unique),'downloaded_images':len(items),'failed_images':failures,'items':items,'completion_rule':'Every catalogue item and every unique non-empty image URL in both the active and discontinued pages was processed.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'completed' if not failures else 'partial','records':len(records),'unique_images':len(unique),'downloaded':len(items),'failures':len(failures)},ensure_ascii=False))
