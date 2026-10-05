import json,re,time,hashlib
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/staging/wmi_global_atlas_20261005';OUT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/'sources/pages/wmi_global_atlas_20261005';CACHE.mkdir(parents=True,exist_ok=True)
s=requests.Session();errors=[]
def page(u):
 p=CACHE/(hashlib.sha256(u.encode()).hexdigest()[:20]+'.html')
 if not p.exists():r=s.get(u,timeout=20);r.raise_for_status();p.write_bytes(r.content);time.sleep(.3)
 return BeautifulSoup(p.read_bytes(),'html.parser')
base='https://www.medals.org.uk/';home=page(base);alphas=[urljoin(base,a['href']) for a in home.find_all('a',href=True) if re.search(r'index-[a-z]\.htm$',a['href'])]
entries=[];dirs={};discovery=[]
def directory(url,label,entry):
 key=hashlib.sha256(url.encode()).hexdigest()[:12]
 dirs.setdefault(url,{'source_id':'wmi-dir-'+key,'source_name':'Medals of the World','label':label,'index_entry':entry,'directory_url':url,'source_type':'specialist_directory','language':'en; original awardnames vary','status':'queued','last_checked':'2026-10-05','recursive_boundary':{'host':'www.medals.org.uk','object_path_prefix':url.rsplit('/',1)[0]+'/','start':url,'follow':'all linked award/grade/typepageswithinprefix; exclude ribboncharts,refs,indexnav; retain externalcrossreferencesseparately','image_selection':'full objectimages notflag/ribbon/navigationgraphics','completion':'allreachableobjectpagesandtheirimagefilesprocessed; notadded-N limit'}})
for u in alphas:
 try:
  soup=page(u);current=None
  for a in soup.find_all('a',href=True):
   label=a.get_text(' ',strip=True);href=urljoin(u,a['href'])
   if urlparse(href).netloc!='www.medals.org.uk':continue
   if label=='Text List' and current:directory(href,current['label'],current['url']);current['text_directory']=href
   elif label and '/' in urlparse(href).path.strip('/') and not any(z in href for z in ['-ribbons','-links','-text']):
    current={'label':label,'url':href,'alphabet_index':u};entries.append(current)
 except Exception as e:errors.append({'url':u,'error':str(e)})
for i,e in enumerate(entries):
 print(i+1,len(entries),e['label'],flush=True)
 try:
  soup=page(e['url']);prefix=e['url'].split('/')[3]+'/'
  seen=set();landing_queue=[(e['url'],soup)]
  while landing_queue:
   lu,ls=landing_queue.pop(0)
   if lu in seen:continue
   seen.add(lu)
   for a in ls.find_all('a',href=True):
    child=urljoin(lu,a['href']);label=a.get_text(' ',strip=True)
    if urlparse(child).netloc!='www.medals.org.uk' or not urlparse(child).path.lstrip('/').startswith(prefix):continue
    if re.search(r'-text\.htm$',child):directory(child,label or e['label'],e['url'])
    elif child!=lu and re.search(r'\.htm$',child) and not any(z in child for z in ['-ribbons','-links','images/']) and not re.search(r'\d+\.htm$',child):
     # A catalogue landing page uses same basename as its containingdirectory.
     parts=urlparse(child).path.strip('/').split('/')
     if len(parts)>=2 and parts[-1][:-4]==parts[-2] and child not in seen:
      try:landing_queue.append((child,page(child)))
      except Exception as er:errors.append({'url':child,'error':str(er)})
  e['landing_pages_inspected']=len(seen);e['status']='landing_discovery_complete'
 except Exception as er:e['status']='landing_access_failed';errors.append({'url':e['url'],'error':str(er)})
atlas={'as_of':'2026-10-05','source':'Medals of the World','scope':'all25publicalphabetindicesandreachablecountry/periodlandingpages','alphabet_indices':alphas,'indexed_entries':entries,'directory_sources':list(dirs.values()),'errors':errors,'counts':{'alphabet_indices':len(alphas),'country_historical_entries':len(entries),'text_directories':len(dirs),'errors':len(errors)},'rights':'Sourcephotosnotblanketlicensed; researchcacheonly; publicationpermissionperimage','boundary':'Thisisglobaldirectorydiscovery,notglobalaward/object sweepcompletion.'}
(OUT/'source_atlas_draft.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'sweep_queue_draft.json').write_text(json.dumps({'as_of':'2026-10-05','tasks':list(dirs.values())},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'discovery_queue_draft.json').write_text(json.dumps({'as_of':'2026-10-05','tasks':errors,'next':'Eachscopefindindependentofficialinstitutionandsources; noassumptionmoderncountryincludesallhistoricalawardingauthorities'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(atlas['counts']))
