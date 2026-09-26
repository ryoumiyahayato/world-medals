import hashlib
import json
import re
import time
from datetime import date
from html import unescape
from pathlib import Path

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'originals' / 'ottoman_2026-09-25'
OUT.mkdir(parents=True, exist_ok=True)

FILES = [
    ('MEDJIDIE', 'Medal, order (AM 809240-1).jpg'),
    ('MEDJIDIE_BACK', 'Medal, order (AM 809240-2).jpg'),
    ('OSMANIEH', 'Order of Osmanieh 1st class badge star (Ottoman Empire) - Tallinn Museum of Orders.jpg'),
    ('CHARITY', 'Order of Charity 1st class badge (Ottoman Empire 1900) - Tallinn Museum of Orders.jpg'),
    ('LIYAKAT', 'Gold Liyakat Medal (miniature, obverse).jpg'),
    ('LIYAKAT_BACK', 'Gold Liyakat Medal (miniature, reverse).jpg'),
    ('GALLIPOLI', 'Medal, decoration (AM 774643-1).jpg'),
    ('CRIMEA', 'Medal, campaign (AM 799886-1).jpg'),
    ('CRIMEA_FRONT', 'Medal, campaign (AM 799886-2).jpg'),
    ('ACRE', 'Medal, campaign (AM 806826-1).jpg'),
    ('ACRE_BACK', 'Medal, campaign (AM 806826-2).jpg'),
    ('MONTENEGRO', 'Medal, campaign (AM 800964-1).jpg'),
    ('MONTENEGRO_BACK', 'Medal, campaign (AM 800964-2).jpg'),
    ('CONSTITUTION', 'TR Kanûn-u Esâsî Madalyası.jpg'),
]

headers = {'User-Agent': 'WorldMedalsResearch/0.1 (personal catalog; respectful request rate)'}
def get(url):
    with urlopen(Request(url, headers=headers), timeout=90) as r:
        return r.read()
records = []
thumbs = []
for key, filename in FILES:
    params = {'action':'query','titles':'File:'+filename,'prop':'imageinfo',
              'iiprop':'url|size|extmetadata','format':'json'}
    data = json.loads(get('https://commons.wikimedia.org/w/api.php?'+urlencode(params)))
    page = next(iter(data['query']['pages'].values()))
    if 'imageinfo' not in page:
        print('MISSING', key, filename)
        continue
    info = page['imageinfo'][0]
    raw = OUT / (key.lower()+'.'+filename.rsplit('.',1)[-1].lower())
    if not raw.exists():
        try:
            raw.write_bytes(get(info['url']))
        except Exception as e:
            print('DOWNLOAD FAILED', key, type(e).__name__, str(e))
            time.sleep(3)
            continue
    with Image.open(raw) as im:
        im.verify()
    with Image.open(raw) as im:
        dims = im.size
        rgb = ImageOps.exif_transpose(im).convert('RGB')
        tile = Image.new('RGB', (340, 390), 'white')
        rgb.thumbnail((330, 350))
        tile.paste(rgb, ((340-rgb.width)//2, 10+(350-rgb.height)//2))
        ImageDraw.Draw(tile).text((10,365),key,fill='black')
        thumbs.append(tile)
    ext = info.get('extmetadata',{})
    clean = lambda k: re.sub('<[^>]+>','',unescape(ext.get(k,{}).get('value',''))).strip()
    rec = {'key':key,'file_title':page['title'],'source_page':'https://commons.wikimedia.org/wiki/'+page['title'].replace(' ','_'),
           'image_url':info['url'],'path':str(raw.relative_to(ROOT)),'width':dims[0],'height':dims[1],
           'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'license':clean('LicenseShortName'),
           'artist':clean('Artist'),'credit':clean('Credit'),'description':clean('ImageDescription'),
           'accessed':str(date.today())}
    records.append(rec)
    print(key, dims, len(raw.read_bytes()), rec['license'])
    time.sleep(2)

if thumbs:
    cols = 5
    sheet = Image.new('RGB',(cols*340, ((len(thumbs)+cols-1)//cols)*390),'#ddd')
    for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*340,(i//cols)*390))
    sheet.save(ROOT/'contact_sheet.jpg',quality=88)
(ROOT/'image_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
