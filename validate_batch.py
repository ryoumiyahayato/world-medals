import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'/'ottoman-20260925'
book=OUT/'ottoman_catalogue_2026-09-25.xlsx'
site=ROOT/'index.html'
catalogue=json.loads((ROOT/'data'/'catalogue.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))
sources=json.loads((ROOT/'data'/'sources.json').read_text(encoding='utf-8'))

class Reader(HTMLParser):
    def __init__(self): super().__init__();self.img=[];self.rows=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='img' and a.get('src'): self.img.append(a['src'])
        if tag=='tr' and 'data-search' in a: self.rows+=1

html=site.read_text(encoding='utf-8')
p=Reader();p.feed(html)
assert p.rows==len(catalogue['records'])==9
assert len(p.img)==len(manifest)==12
assert 'object-fit:cover' not in html and 'object-fit:contain' in html
assert 'fetch(' not in html and 'https://' not in html
for src in p.img:
    assert src and not re.match(r'^[a-z]+:',src,re.I)
    full=ROOT/src
    assert full.is_file(),src
    with Image.open(full) as im: im.verify()

for im in manifest:
    raw=ROOT/im['path']
    assert raw.is_file()
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==im['sha256']
    assert (ROOT/'assets'/'images'/'ottoman'/raw.name).read_bytes()==raw.read_bytes()
for r in catalogue['records']:
    assert r['source_ids'] and all(sid in sources for sid in r['source_ids'])
    assert all(v['key'] in {x['key'] for x in manifest} for v in r['views'])

with zipfile.ZipFile(book) as z:
    assert z.testzip() is None
    media=[n for n in z.namelist() if n.startswith('xl/media/')]
    assert len(media)==12
    ns={'x':'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'}
    drawing=ET.fromstring(z.read('xl/drawings/drawing1.xml'))
    assert len(drawing)==12
    rowcounts={}
    for anchor in drawing:
        origin=anchor.find('x:from',ns)
        col=int(origin.find('x:col',ns).text)
        row=int(origin.find('x:row',ns).text)
        x=int(origin.find('x:colOff',ns).text)/9525
        y=int(origin.find('x:rowOff',ns).text)/9525
        ext=anchor.find('x:ext',ns)
        w=int(ext.attrib['cx'])/9525
        h=int(ext.attrib['cy'])/9525
        assert col==2 and 1<=row<=9
        assert x>=0 and y>=0 and x+w<=640 and y+h<=300,(row,x,y,w,h)
        rowcounts[row]=rowcounts.get(row,0)+1
    assert list(sorted(rowcounts))==list(range(1,10))
    assert all(rowcounts[i]==len(catalogue['records'][i-1]['views']) for i in range(1,10))

package=OUT/'world_medals_offline_2026-09-25.zip'
files=[site,book,ROOT/'data'/'catalogue.json',ROOT/'data'/'sources.json',ROOT/'data'/'global_queue.json']
files += sorted((ROOT/'assets'/'images'/'ottoman').glob('*'))
with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:
        z.write(f,f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    assert 'index.html' in z.namelist()
    assert len([n for n in z.namelist() if n.startswith('assets/images/ottoman/')])==12

report={'rows':p.rows,'independent_families':len({r['family'] for r in catalogue['records']}),
        'local_photos':len(p.img),'excel_embedded_photos':len(media),
        'excel_image_anchors_inside_cells':len(drawing),'offline_relative_images':True,
        'archive':str(package),'limitation':'浏览器 file:// 访问被界面安全策略阻止；以静态检查、逐图解码与 XLSX 图片锚点检查替代。'}
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
