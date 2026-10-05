"""Bounded, cached Commons category sweep for French award object photography."""
from pathlib import Path
import json,hashlib,time,re
import requests
R=Path(__file__).resolve().parents[1];C=R/'sources/cache/france_commons_completion';C.mkdir(exist_ok=True)
P=R/'data/queues/france_commons_completion.json'
roots=['Category:Orders of France','Category:Civil decorations of France','Category:Military awards and decorations of France']
skip=re.compile(r'recipients|members of|knights of|commanders of|officers of|grand crosses of|dames of|portraits|presentation|ribbon|SVG|associatives|people|by recipient|chevaliers|titulaire',re.I)
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0 (local award source catalog)'
def get(params):
 key=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()[:20];p=C/(key+'.json')
 if p.exists():return json.loads(p.read_text('utf-8'))
 r=s.get('https://commons.wikimedia.org/w/api.php',params=dict(params,format='json'),timeout=25)
 if r.status_code==429:raise InterruptedError('Commons rate limit; stop and resume after cooldown')
 r.raise_for_status();j=r.json();p.write_text(json.dumps(j,ensure_ascii=False,indent=2),'utf-8');time.sleep(3);return j
state=json.loads(P.read_text('utf-8')) if P.exists() else dict(pending=[[r,0] for r in roots],done=[],excluded=[],files={},failures=[])
def save():P.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
while state['pending']:
 cat,depth=state['pending'].pop(0)
 if cat in state['done']:continue
 try:
  params=dict(action='query',list='categorymembers',cmtitle=cat,cmlimit=500)
  while True:
   j=get(params)
   for row in j.get('query',{}).get('categorymembers',[]):
    title=row['title']
    if row['ns']==6:
     if title.lower().endswith(('.jpg','.jpeg','.png','.tif','.tiff','.webp')):state['files'].setdefault(title,[]).append(cat)
    elif row['ns']==14:
     if skip.search(title) or depth>=3:state['excluded'].append(dict(category=title,parent=cat,reason='recipient/ribbon/non-state branch or depth boundary'))
     elif title not in state['done'] and not any(x[0]==title for x in state['pending']):state['pending'].append([title,depth+1])
   if 'continue' not in j:break
   params.update(j['continue'])
  state['done'].append(cat)
 except InterruptedError:
  state['pending'].insert(0,[cat,depth]);save();raise
 except Exception as e:state['failures'].append(dict(category=cat,error=str(e)))
 save();print(len(state['done']),len(state['pending']),len(state['files']),cat,flush=True)
titles=list(state['files']);metadata={}
for offset in range(0,len(titles),40):
 try:
  j=get(dict(action='query',prop='imageinfo',iiprop='url|size|extmetadata',titles='|'.join(titles[offset:offset+40])))
  for row in j.get('query',{}).get('pages',{}).values():
   if row.get('imageinfo'):metadata[row['title']]=dict(row['imageinfo'][0],categories=state['files'].get(row['title'],[]))
 except Exception as e:state['failures'].append(dict(metadata_offset=offset,error=str(e)));save()
 (C/'imageinfo.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),'utf-8')
print('Metadata',len(metadata),flush=True)
