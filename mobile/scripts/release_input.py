"""Portable catalogue input. No original image bytes enter the repository."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_display import public_metadata

def snapshot(root):
    soup = BeautifulSoup((root/'index.html').read_text(encoding='utf-8'), 'html.parser')
    rows = {}
    for tr in soup.select('section.period-section tr[id]'):
        cells = tr.find_all('td', recursive=False)
        if len(cells) != 3:
            continue
        rows[tr['id']] = [cell.decode_contents() for cell in cells]
        for cell in cells:
            cell.clear()
    records = {}
    def collect(value, inherited=None):
        if isinstance(value, list):
            for item in value: collect(item, inherited)
        elif isinstance(value, dict):
            rights = dict(inherited or {})
            for key in ('license','rights','copyright','institution','artist','credit'):
                if isinstance(value.get(key),str): rights[key]=value[key]
            for key in ('local_path','path','file','local_file','original_path'):
                path = value.get(key)
                if isinstance(path,str) and path.replace('\\','/').startswith(('assets/','originals/')):
                    records[path.replace('\\','/')] = public_metadata(dict(rights,**value))
            for item in value.values():
                if isinstance(item,(dict,list)): collect(item,rights)
    for path in [root/'image_manifest.json',*sorted((root/'data/volumes').glob('*manifest*.json'))]:
        collect(json.loads(path.read_text(encoding='utf-8-sig')))
    needed={im['src'] for cells in rows.values() for im in BeautifulSoup(cells[2],'html.parser').select('img[src]')}
    data={'schema':1,'rows':rows,'images':{key:value for key,value in records.items() if key in needed},
          'sources':public_metadata(json.loads((root/'data/sources.json').read_text(encoding='utf-8')))}
    (root/'data/release-input.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    (root/'mobile/web/desktop-template.html').write_text(str(soup),encoding='utf-8')

def source(root):
    data=json.loads((root/'data/release-input.json').read_text(encoding='utf-8'))
    soup=BeautifulSoup((root/'mobile/web/desktop-template.html').read_text(encoding='utf-8'),'html.parser')
    for tr in soup.select('section.period-section tr[id]'):
        if tr['id'] in data['rows']:
            for cell, content in zip(tr.find_all('td',recursive=False),data['rows'][tr['id']]):
                cell.append(BeautifulSoup(content,'html.parser'))
    return str(soup).encode('utf-8'),data

if __name__=='__main__':
    snapshot(Path(__file__).resolve().parents[2])
