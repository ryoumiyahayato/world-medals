"""Recover complete 1200px Commons thumbnails for originals that remain rate-limited."""
from __future__ import annotations
import argparse, hashlib, json, time, urllib.parse, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; API='https://commons.wikimedia.org/w/api.php'
p=argparse.ArgumentParser(); p.add_argument('scope'); args=p.parse_args(); scope=args.scope
sweep_path=ROOT/f'data/source_sweeps/commons_{scope}_2026-09-28.json'; raw_path=ROOT/f'data/raw_candidates/commons_{scope}.jsonl'; raw_dir=ROOT/f'assets/raw/commons_{scope}'
state=json.loads(sweep_path.read_text(encoding='utf-8')); rows=[json.loads(x) for x in raw_path.read_text(encoding='utf-8').splitlines() if x.strip()]; by={x['file_title']:x for x in rows}
recovered=[]; remaining=[]
for n,item in enumerate(state.get('download_failures',[]),1):
 title=item['title']
 try:
  params=urllib.parse.urlencode({'action':'query','format':'json','formatversion':2,'prop':'imageinfo','titles':title,'iiprop':'url|size','iiurlwidth':1200})
  req=urllib.request.Request(API+'?'+params,headers={'User-Agent':'world-medals-research/1.0 (offline catalogue; thumbnail recovery)'})
  with urllib.request.urlopen(req,timeout=60) as response: info=json.load(response)['query']['pages'][0]['imageinfo'][0]
  url=info.get('thumburl') or info['url']; ext=Path(urllib.parse.urlparse(url).path).suffix.lower() or Path(urllib.parse.urlparse(info['url']).path).suffix.lower()
  req=urllib.request.Request(url,headers={'User-Agent':'world-medals-research/1.0 (offline catalogue; thumbnail recovery)','Referer':'https://commons.wikimedia.org/'})
  with urllib.request.urlopen(req,timeout=90) as response: data=response.read()
  with Image.open(BytesIO(data)) as im: im.load(); width,height=im.size
  path=raw_dir/(hashlib.sha256(title.encode('utf-8')).hexdigest()[:16]+'_1200'+ext); path.write_bytes(data); row=by[title]
  row['local_raw_image']=path.relative_to(ROOT).as_posix(); row['cached_image_url']=url; row['cache_kind']='commons_1200px_thumbnail'; row['width']=width; row['height']=height
  recovered.append({'title':title,'thumbnail_url':url,'local_path':row['local_raw_image'],'width':width,'height':height,'bytes':len(data)})
 except Exception as exc: remaining.append({'title':title,'url':item['url'],'error':repr(exc)})
 print(f'{scope} thumbnail {n}/{len(state.get("download_failures",[]))}: {title}',flush=True); time.sleep(2)
raw_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
state['download_failures']=remaining; state['thumbnail_recovered']=recovered; state['raster_files_cached']=sum(bool(x.get('local_raw_image')) for x in rows); state['status']='complete' if not remaining else 'complete_with_download_failures'
sweep_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scope':scope,'thumbnail_recovered':len(recovered),'remaining':len(remaining),'cached':state['raster_files_cached']},ensure_ascii=False))
