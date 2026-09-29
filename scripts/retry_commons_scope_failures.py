"""Retry only recorded Commons original-image failures for one scope, slowly and once."""
from __future__ import annotations
import argparse, hashlib, json, time, urllib.parse, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('scope'); args=p.parse_args(); scope=args.scope
sweep_path=ROOT/f'data/source_sweeps/commons_{scope}_2026-09-28.json'
raw_path=ROOT/f'data/raw_candidates/commons_{scope}.jsonl'; raw_dir=ROOT/f'assets/raw/commons_{scope}'
state=json.loads(sweep_path.read_text(encoding='utf-8')); rows=[json.loads(x) for x in raw_path.read_text(encoding='utf-8').splitlines() if x.strip()]
by_title={x['file_title']:x for x in rows}; remaining=[]; recovered=[]
for n,item in enumerate(state.get('download_failures',[]),1):
 title=item['title']; url=item['url'].split('?',1)[0]; ext=Path(urllib.parse.urlparse(url).path).suffix.lower(); path=raw_dir/(hashlib.sha256(title.encode('utf-8')).hexdigest()[:16]+ext)
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'world-medals-research/1.0 (offline catalogue; respectful retry)','Referer':'https://commons.wikimedia.org/'})
  with urllib.request.urlopen(req,timeout=90) as response: data=response.read()
  with Image.open(BytesIO(data)) as im: im.load(); width,height=im.size
  path.write_bytes(data); row=by_title[title]; row['local_raw_image']=path.relative_to(ROOT).as_posix(); row['width']=width; row['height']=height; recovered.append({'title':title,'local_path':row['local_raw_image'],'bytes':len(data)})
 except Exception as exc:
  path.unlink(missing_ok=True); remaining.append({'title':title,'url':item['url'],'error':repr(exc)})
 print(f'{scope} retry {n}/{len(state.get("download_failures",[]))}: {title}',flush=True); time.sleep(3)
raw_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
state['download_failures']=remaining; state['raster_files_cached']=sum(bool(x.get('local_raw_image')) for x in rows); state['status']='complete' if not remaining else 'complete_with_download_failures'; state['retry_recovered']=recovered
sweep_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scope':scope,'recovered':len(recovered),'remaining':len(remaining),'cached':state['raster_files_cached']},ensure_ascii=False))
