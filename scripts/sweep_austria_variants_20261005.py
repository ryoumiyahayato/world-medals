import json, hashlib, re, time, io, copy
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/staging/austria_variants_20261005'; OUT.mkdir(parents=True,exist_ok=True)
CACHE=ROOT/'sources/pages/austria_variants_20261005'; CACHE.mkdir(parents=True,exist_ok=True)
IMGS=ROOT/'assets/raw/austria_variants_20261005'; IMGS.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers['User-Agent']='WorldMedals local research catalogue (limited cached requests)'
def get(url, path):
 if path.exists(): return path.read_bytes()
 r=s.get(url,timeout=30); r.raise_for_status(); path.write_bytes(r.content); time.sleep(.25); return r.content
existing={}; used=set()
for f in (ROOT/'data/volumes').glob('*.json'):
 try: d=json.loads(f.read_text(encoding='utf-8-sig'))
 except: continue
 if not isinstance(d,dict): continue
 for row in (d.get('records',[]) if isinstance(d.get('records',[]),list) else []):
  for e in row.get('evidence',[]):
   u=e.get('source_page','')
   if '/austria-empire/' in u: existing.setdefault(u,row)
 for im in d.get('images',[]): used.add(im.get('image_url'))
raw=[json.loads(x) for x in (ROOT/'data/raw_candidates/medalsorg_austria_full_directories_2026-09-28.jsonl').read_text(encoding='utf-8-sig').splitlines()]
raw=[r for r in raw if '/austria-empire/' in r['object_page']]
records=[]; images=[]; refreshed=[]; pending=[]
original_map={re.sub(r'[^\w]','',r.get('original','').lower()):r for r in existing.values()}
trans={'Grand Cross':'大十字级','Class 1':'一级','Class 2':'二级','Class 3':'三级','Commander':'指挥官级','Knight':'骑士级','Badge':'挂章','Star':'星章','Obverse':'正面','Reverse':'背面','Gold':'金质（按来源描述）','Silver':'银质（按来源描述）','Bronze':'铜质（按来源描述）','with Swords':'加剑','without Swords':'无剑','War Decoration':'战争装饰'}
for cand in raw:
 u=cand['object_page']; stem=u.rsplit('/',1)[-1]; print(stem,flush=True)
 try:
  soup=BeautifulSoup(get(u,CACHE/stem),'html.parser')
  actual=[]
  for tag in soup.find_all('img'):
   cap=tag.get('alt','').strip() or tag.get('title','').strip()
   imurl=urljoin(u,tag.get('src',''))
   if cap and re.search(r'\.(jpg|jpeg|png)$',imurl,re.I):
    tr=tag.find_parent('tr'); context=''
    if tr:
     first=tr.find('td',recursive=False)
     if first and not first.find('img'): context=first.get_text(' ',strip=True)
    actual.append({'image_url':imurl,'caption':cap,'context':context})
  for link in soup.find_all('a',href=True):
   child=urljoin(u,link['href'])
   if re.search(r'/austria-empire/austria-empire\d+\.htm$',child) and child not in {r['object_page'] for r in raw}:
    raw.append({'source_id':'medalsorg-austria-empire-'+child.rsplit('/',1)[-1][:-4],'object_page':child,'notes':'','original_name':''})
  if not cand.get('notes'): cand['notes']=' | '.join(p.get_text(' ',strip=True) for p in soup.find_all('p') if any(x in p.get_text() for x in ['Instituted:','Awarded:','Grades:']))
  if not cand.get('original_name') and soup.find('h3'):cand['original_name']=soup.find('h3').get_text(' ',strip=True)
  cand['images_refreshed']=actual; cand['accessed_at']='2026-10-05'; refreshed.append(cand)
  template=existing.get(u) or original_map.get(re.sub(r'[^\w]','',cand.get('original_name','').lower()))
  if not template: pending.append({'page':u,'reason':'Family/authority not yet normalized','images':actual}); continue
  for n,im in enumerate(actual):
   if re.search('Reverse',im['caption'],re.I) or im['image_url'] in used: continue
   # Source-caption distinct view; all rows remain review drafts until visual approval.
   rid=template['id'].split('-V')[0]+'-V20261005'+stem.removesuffix('.htm').removeprefix('austria-empire')+str(n+1).zfill(2)
   rr=copy.deepcopy(template); rr['id']=rid; rr['views']=[]; rr['html_eligible']=False; rr['body_eligible']=False
   label=(im.get('context','')+'; '+im['caption']).strip('; ')
   for en,zh in trans.items(): label=label.replace(en,zh)
   rr['variant']=label+'；低清参考'; rr['review_status']='needs_visual_and_variant_review'
   rr['evidence']=[{'source_page':u,'accessed_at':'2026-10-05','source_excerpt':cand.get('notes',''),'image_reference':im['caption']}]
   pair=[im]
   rev=im['caption'].replace('Obverse','Reverse')
   if 'Obverse' in im['caption']:pair += [p for p in actual[n+1:n+2] if p['caption']==rev][:1]
   for j,p in enumerate(pair):
    try:
     path=IMGS/(hashlib.sha256(p['image_url'].encode()).hexdigest()[:20]+'.jpg')
     content=get(p['image_url'],path)
     decoded=Image.open(io.BytesIO(content)); decoded.load()
     key=rid+'-VIEW'+str(j+1); rr['views'].append({'key':key,'label':'正面' if j==0 else '背面（来源成对图示，实物一致性待复核）'})
     images.append({'key':key.lower(),'record_id':rid,'view_key':key,'local_path':str(path.relative_to(ROOT)).replace('\\','/'),'source_page':u,'image_url':p['image_url'],'source_caption':p['caption'],'object_reference':stem+': '+p['caption'],'artist':'World Medals Index; original contributor as credited on object page','license':'No blanket publication license; local research draft only, no public distribution approval','dimensions':list(decoded.size),'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'decoded':True,'visually_checked':False})
    except Exception as e: pending.append({'image':p,'error':str(e)})
   if rr['views']: records.append(rr)
 except Exception as e: pending.append({'page':u,'error':str(e)})
for name,obj in [('volume_draft.json',{'as_of':'2026-10-05','volume':'奥地利帝国／奥匈帝国·新增版型审核草稿','records':records}),('manifest_draft.json',{'images':images}),('pending.json',pending)]: (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'raw_refreshed.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in refreshed),encoding='utf-8')
fronts=[im for im in images if not 'Reverse' in im['source_caption']]
for start in range(0,len(fronts),24):
 chunk=fronts[start:start+24]; sheet=Image.new('RGB',(1000,((len(chunk)+3)//4)*330),'#ddd'); draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(chunk):
  pic=Image.open(ROOT/im['local_path']).convert('RGB'); pic.thumbnail((220,260)); x=(i%4)*250;y=(i//4)*330;sheet.paste(pic,(x+(250-pic.width)//2,y));draw.text((x+5,y+264),im['record_id'][-20:],fill='black');draw.text((x+5,y+281),im['source_caption'][:32],fill='black')
 sheet.save(OUT/('contact_'+str(start//24+1)+'.jpg'))
print(json.dumps({'pages':len(refreshed),'draft_rows':len(records),'downloaded_images':len(images),'pending':len(pending)}))
