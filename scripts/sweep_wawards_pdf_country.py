"""Exhaust a cached World Awards country PDF and all linked award pages/images."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin,urlparse
from PIL import Image
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def fetch(url,out):
 out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists() and out.stat().st_size:return True
 p=subprocess.run(['curl.exe','-L','--fail','--retry','2','--retry-delay','2','--connect-timeout','20','--max-time','90','-A','Mozilla/5.0','-o',str(out),url],cwd=ROOT,capture_output=True,text=True)
 return p.returncode==0 and out.exists() and out.stat().st_size>0
def clean(x):return re.sub(r'<[^>]+>',' ',re.sub(r'\s+',' ',x)).strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('scope');p.add_argument('pdf');a=p.parse_args();scope=a.scope;pdf=ROOT/a.pdf
 pages=ROOT/f'sources/pages/wawards_{scope}';raw=ROOT/f'assets/raw/wawards_{scope}';out=ROOT/f'data/raw_candidates/wawards_{scope}.jsonl';report=ROOT/f'data/source_sweeps/wawards_{scope}_2026-09-28.json';reader=PdfReader(pdf);urls=[]
 for page in reader.pages:
  for ann in page.get('/Annots',[]):
   o=ann.get_object();act=o.get('/A');uri=act.get('/URI') if act else None
   if uri and f'/{scope}/' in uri and uri.lower().endswith('.html') and uri not in urls:urls.append(uri)
 rows=[];fail=[];image_count=0;image_scopes={scope,scope.replace('-','')}
 for n,url in enumerate(urls,1):
  slug=Path(urlparse(url).path).stem;page=pages/f'{n:03d}_{slug}.html'
  if not fetch(url,page):fail.append({'stage':'page','url':url});continue
  body=page.read_text(encoding='utf-8',errors='replace');m=re.search(r'<h1[^>]*>(.*?)</h1>',body,re.I|re.S) or re.search(r'<title>(.*?)</title>',body,re.I|re.S);title=clean(m.group(1)) if m else slug.replace('-',' ').title();text=clean(body)
  image_urls=[]
  for href in re.findall(r'(?:href|src)=["\']([^"\']+)["\']',body,re.I):
   if any(re.search(fr'/images/{re.escape(s)}/.+\.(?:jpe?g|png)$',href,re.I) for s in image_scopes) and '_thumb.' not in href:
    absolute=urljoin(url,href)
    if absolute not in image_urls:image_urls.append(absolute)
  local=[]
  for j,image_url in enumerate(image_urls,1):
   suffix=Path(urlparse(image_url).path).suffix.lower() or '.jpg';dest=raw/f'{n:03d}_{slug}_{j:02d}{suffix}'
   if not fetch(image_url,dest):fail.append({'stage':'image','url':image_url,'object_url':url});continue
   try:
    with Image.open(dest) as im:im.verify()
    with Image.open(dest) as im:w,h=im.size
   except Exception as exc:fail.append({'stage':'decode','url':image_url,'error':str(exc)});dest.unlink(missing_ok=True);continue
   local.append({'view_no':j,'image_url':image_url,'local_path':dest.relative_to(ROOT).as_posix(),'width':w,'height':h,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()});image_count+=1
  rows.append({'source_id':f'wawards-{scope}-{n:03d}','source_system':'World Awards complete reference catalogue','page_title':title,'working_name_zh':'待归并','name_original':title,'date_candidates':re.findall(r'(?<!\d)(?:1[789]\d{2}|20\d{2})(?!\d)',text),'category':'order_or_medal','grade_material_clues':text[:1500],'object_url':url,'original_images':local,'status':'harvested' if local else 'UNPICTURED','access_date':date.today().isoformat()});time.sleep(.15)
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 result={'source_id':f'wawards-{scope}','source_file':pdf.relative_to(ROOT).as_posix(),'accessed':date.today().isoformat(),'scope':'Complete PDF, every linked award page and every exposed full-size image.','status':'complete' if len(rows)==len(urls) and not fail else 'partial','pdf_pages':len(reader.pages),'planned_object_pages':len(urls),'processed_object_pages':len(rows),'downloaded_images':image_count,'failures':fail,'raw_output':out.relative_to(ROOT).as_posix()};report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
