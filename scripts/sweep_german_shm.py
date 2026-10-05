"""Public museum API discovery; German-state query results are candidates, not identifications."""
from pathlib import Path
import requests,time,json
R=Path(__file__).resolve().parents[1];C=R/'sources/cache/german_shm_20260929';C.mkdir(parents=True,exist_ok=True)
queries=['Baden','Braunschweig','Sachsen','Hessen','Oldenburg','Mecklenburg','Anhalt','Lippe','Württemberg','Hannover']
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0'
allitems={};counts={}
for query in queries:
 offset=0
 while True:
  p=C/(query+'_'+str(offset)+'.json')
  if p.exists():j=json.loads(p.read_text('utf-8'))
  else:
   try:r=s.get('https://samlingar.shm.se/api/v1/search',params=dict(type='object',query=query,hasImage=1,institution='Livrustkammaren',limit=50,offset=offset),timeout=25)
   except requests.RequestException as e:
    counts[query]=dict(status='partial_timeout',next_offset=offset,error=str(e));print(query,'timeout, queued',flush=True);break
   if r.status_code==429:raise InterruptedError('rate limited, stop')
   r.raise_for_status();j=r.json();p.write_text(json.dumps(j,ensure_ascii=False,indent=2),'utf-8');time.sleep(3)
  for x in j.get('items',[]):
   if x['id'] not in allitems:allitems[x['id']]=dict(x,queries=[])
   allitems[x['id']]['queries'].append(query)
  counts[query]=dict(total=j.get('totalResults'),scanned=offset+len(j.get('items',[])))
  (C/'candidates.json').write_text(json.dumps(list(allitems.values()),ensure_ascii=False,indent=2),'utf-8');(C/'sweep.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),'utf-8')
  print(query,counts[query],flush=True)
  offset+=50
  if offset>=j.get('totalResults',0) or not j.get('items'):break
