"""Exhaust the complete World Awards Jordan PDF and every linked object page."""
from __future__ import annotations
import hashlib, json, re, subprocess, time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'sources/books/jordan/wawards_jordan.pdf'
PAGES=ROOT/'sources/pages/wawards_jordan'; RAW=ROOT/'assets/raw/wawards_jordan'
OUT=ROOT/'data/raw_candidates/wawards_jordan.jsonl'
REPORT=ROOT/'data/source_sweeps/wawards_jordan_2026-09-28.json'

def fetch(url: str, out: Path) -> bool:
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and out.stat().st_size: return True
    p=subprocess.run(['curl.exe','-L','--fail','--retry','2','--retry-delay','2','--connect-timeout','20','--max-time','90','-A','Mozilla/5.0','-o',str(out),url],cwd=ROOT,capture_output=True,text=True)
    return p.returncode==0 and out.exists() and out.stat().st_size>0

def title(html: str, fallback: str) -> str:
    m=re.search(r'<title>(.*?)</title>',html,re.I|re.S)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else fallback

def main() -> None:
    for p in (PAGES,RAW,OUT.parent,REPORT.parent): p.mkdir(parents=True,exist_ok=True)
    reader=PdfReader(PDF); urls=[]
    for page in reader.pages:
        for annotation in page.get('/Annots',[]):
            obj=annotation.get_object(); action=obj.get('/A'); uri=action.get('/URI') if action else None
            if uri and '/jordan/' in uri and uri.lower().endswith('.html') and uri not in urls: urls.append(uri)
    rows=[]; failures=[]; image_count=0
    for n,url in enumerate(urls,1):
        slug=Path(urlparse(url).path).stem; page_path=PAGES/f'{n:03d}_{slug}.html'
        if not fetch(url,page_path): failures.append({'stage':'page','url':url}); continue
        html=page_path.read_text(encoding='utf-8',errors='replace'); page_title=title(html,slug.replace('-',' ').title())
        image_urls=[]
        for href in re.findall(r'(?:href|src)=["\']([^"\']+)["\']',html,re.I):
            if re.search(r'/images/jordan/.+\.(?:jpe?g|png)$',href,re.I):
                absolute=urljoin(url,href)
                if absolute not in image_urls: image_urls.append(absolute)
        local=[]
        for view_no,image_url in enumerate(image_urls,1):
            suffix=Path(urlparse(image_url).path).suffix.lower() or '.jpg'; image_path=RAW/f'{n:03d}_{slug}_{view_no:02d}{suffix}'
            if not fetch(image_url,image_path): failures.append({'stage':'image','url':image_url,'object_url':url}); continue
            try:
                with Image.open(image_path) as im: im.verify()
                with Image.open(image_path) as im: width,height=im.size
            except Exception as exc:
                failures.append({'stage':'decode','url':image_url,'error':str(exc)}); image_path.unlink(missing_ok=True); continue
            local.append({'view_no':view_no,'image_url':image_url,'local_path':image_path.relative_to(ROOT).as_posix(),'width':width,'height':height,'sha256':hashlib.sha256(image_path.read_bytes()).hexdigest()}); image_count+=1
        rows.append({'source_id':f'wawards-jordan-{n:03d}','source_system':'World Awards Jordan catalogue','page_title':page_title,'working_name_zh':'待归并','name_original':page_title,'name_en':page_title,'date_candidates':[],'category':'order_or_medal','grade_material_clues':'待核','object_url':url,'image_page_url':url,'original_images':local,'notes':'Complete Jordan PDF linked-object sweep; title and grade follow the object page.','status':'harvested' if local else 'UNPICTURED','access_date':date.today().isoformat()})
        time.sleep(.2)
    with OUT.open('w',encoding='utf-8') as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False)+'\n')
    report={'source_id':'wawards-jordan','source_url':'https://wawards.org/images/jordan/jordan.pdf','accessed':date.today().isoformat(),'scope':'Complete PDF, every linked Jordan object page and every exposed full-size Jordan image.','status':'complete' if len(rows)==len(urls) and not failures else 'partial','pdf_pages':len(reader.pages),'planned_object_pages':len(urls),'processed_object_pages':len(rows),'downloaded_images':image_count,'failures':failures,'raw_output':OUT.relative_to(ROOT).as_posix()}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
