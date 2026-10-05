import json,hashlib,re,time,io,copy
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/staging/austria_republic_20261005';OUT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/'sources/pages/austria_republic_20261005';CACHE.mkdir(parents=True,exist_ok=True);IMG=ROOT/'assets/raw/austria_republic_20261005';IMG.mkdir(parents=True,exist_ok=True)
s=requests.Session();errors=[]
def get(u,p):
 if p.exists():return p.read_bytes()
 r=s.get(u,timeout=25);r.raise_for_status();p.write_bytes(r.content);time.sleep(.35);return r.content
base='https://www.medals.org.uk/austria/austria-republic/';du=base+'austria-republic-text.htm';directory=BeautifulSoup(get(du,CACHE/'directory.html'),'html.parser')
queue=[];labels={};category=''
for tag in directory.find_all(['h3','li']):
 if tag.name=='h3':category=tag.get_text(' ',strip=True)
 else:
  for a in tag.find_all('a',href=True):
   u=urljoin(du,a['href'])
   if u.startswith(base) and re.search(r'\d+\.htm$',u):queue.append(u);labels[u]={'listing_name':a.get_text(' ',strip=True),'section':category}
existing={};used=set();origmap={}
for f in (ROOT/'data/volumes').glob('*.json'):
 try:d=json.loads(f.read_text(encoding='utf-8-sig'))
 except:continue
 if not isinstance(d,dict):continue
 if isinstance(d.get('records'),list):
  for row in d['records']:
   for e in row.get('evidence',[]):
    u=e.get('source_page','')
    if u.startswith(base):existing.setdefault(u,row);origmap.setdefault(re.sub(r'[^\w]','',row.get('original','').lower()),row)
 if isinstance(d.get('images'),list):used.update(x.get('image_url') for x in d['images'])
raw=[];rows=[];images=[];seen=set()
for u in queue:
 if u in seen:continue
 seen.add(u);stem=u.rsplit('/',1)[-1];print(stem,flush=True)
 try:
  soup=BeautifulSoup(get(u,CACHE/stem),'html.parser');title=soup.h2.get_text(' ',strip=True) if soup.h2 else soup.title.get_text();original=soup.h3.get_text(' ',strip=True) if soup.h3 else ''
  evidence=' | '.join(p.get_text(' ',strip=True) for p in soup.select('p') if any(z in p.get_text() for z in ['Instituted:','Awarded:','Grades:','Discontinued:']))
  ims=[]
  for t in soup.find_all('img'):
   url=urljoin(u,t.get('src',''));cap=t.get('alt','').strip() or t.get('title','').strip()
   if not cap or not re.search(r'\.(jpg|jpeg|png)$',url,re.I):continue
   tr=t.find_parent('tr');context=''
   if tr:
    first=tr.find('td',recursive=False)
    if first and not first.find('img') and len(first.get_text())<180:context=first.get_text(' ',strip=True)
   ims.append({'image_url':url,'caption':cap,'context':context})
  cand={'source_id':'wmi-'+stem[:-4],'object_page':u,'page_title':title,'original_name':original,'directory_section':labels.get(u,{}).get('section','linked_variant_page'),'date_grade_candidates':evidence,'images':ims,'accessed_at':'2026-10-05','status':'object_page_processed'};raw.append(cand)
  for a in soup.find_all('a',href=True):
   child=urljoin(u,a['href'])
   if child.startswith(base) and re.search(r'\d+\.htm$',child) and child not in queue:queue.append(child)
  template=existing.get(u) or origmap.get(re.sub(r'[^\w]','',original.lower()))
  for i,im in enumerate(ims):
   if 'Reverse' in im['caption'] or im['image_url'] in used:continue
   rid='AUT-REP-WMI-'+stem[:-4].split('republic')[-1]+'-'+str(i+1).zfill(2);r=copy.deepcopy(template or {});r.update({'id':rid,'family':template['family'] if template else 'AUT-REP-PENDING-'+stem[:-4].split('republic')[-1],'country_zh':template.get('country_zh','奥地利共和国') if template else '奥地利共和国','name':template['name'] if template else title.split(':',1)[-1].strip(),'original':original,'date':template.get('date','待考') if template else '待考','variant':'; '.join(z for z in [im['context'],im['caption']] if z)+'；低清参考','views':[],'source_ids':[cand['source_id']],'evidence':[{'source_page':u,'accessed_at':'2026-10-05','source_excerpt':evidence,'image_reference':im['caption']}],'html_eligible':False,'body_eligible':False,'publication_eligible':False,'local_offline':True,'rights_note':'仅本地离线研究；公开再发布许可未确认','review_status':'needs_family_authority_and_visual_review','directory_section':cand['directory_section']})
   pair=[im];rev=im['caption'].replace('Obverse','Reverse')
   if 'Obverse' in im['caption']:pair += [p for p in ims[i+1:i+2] if p['caption']==rev]
   for j,p in enumerate(pair):
    try:
     path=IMG/(hashlib.sha256(p['image_url'].encode()).hexdigest()[:20]+'.jpg');b=get(p['image_url'],path);pic=Image.open(io.BytesIO(b));pic.load();key=rid+'-VIEW'+str(j+1);r['views'].append({'key':key,'label':'正面' if j==0 else '背面（来源同版图示，不保证同一实物）'})
     images.append({'key':key.lower(),'record_id':rid,'view_key':key,'local_path':str(path.relative_to(ROOT)).replace('\\','/'),'source_page':u,'image_url':p['image_url'],'source_caption':p['caption'],'object_reference':stem+': '+p['caption'],'dimensions':list(pic.size),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'decoded':True,'visually_checked':False,'license':'No blanket publicationlicense;local offline researchonly','artist':'World Medals Index; photographer not established'})
    except Exception as e:errors.append({'image_url':p['image_url'],'error':str(e)})
   if r['views']:rows.append(r)
 except Exception as e:errors.append({'object_page':u,'error':str(e)})
for name,obj in [('volume_draft.json',{'as_of':'2026-10-05','volume':'奥地利共和国及地方、团体·补图审核草稿','records':rows}),('manifest_draft.json',{'images':images}),('errors.json',errors)]: (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'raw_candidates.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in raw),encoding='utf-8')
for start in range(0,len(images),24):
 chunk=images[start:start+24];sheet=Image.new('RGB',(1000,((len(chunk)+3)//4)*330),'#ddd');d=ImageDraw.Draw(sheet)
 for i,x in enumerate(chunk):
  im=Image.open(ROOT/x['local_path']).convert('RGB');im.thumbnail((220,260));xx=i%4*250;yy=i//4*330;sheet.paste(im,(xx+(250-im.width)//2,yy));d.text((xx+4,yy+265),x['record_id'],fill='black');d.text((xx+4,yy+283),x['source_caption'][:33],fill='black')
 sheet.save(OUT/('contact_'+str(start//24+1)+'.jpg'))
print(json.dumps({'master_links':len(labels),'recursive_pages':len(raw),'rows':len(rows),'photos':len(images),'errors':len(errors)}))
