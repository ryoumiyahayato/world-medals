import hashlib,json,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
source=root/'sources/legacy_review/PLEVNE-1.jpg'
archive=root/'originals/ottoman_2026-09-25/PLEVNE-1.jpg'
asset=root/'assets/images/ottoman/PLEVNE-1.jpg'
for dest in (archive,asset):shutil.copy2(source,dest)
with Image.open(source) as im:width,height=im.size
digest=hashlib.sha256(source.read_bytes()).hexdigest()
manifest_path=root/'image_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
assert not any(x['key']=='PLEVNE-KUENKER' for x in manifest)
page='https://www.kuenker.de/tuerkei-osmanisches-reich-the-ottoman-collection-orden-und-ehrenzeichen/199996'
url='https://kuenker.s3.eu-central-1.amazonaws.com/images/auction/00092/07259q00.jpg'
manifest.append({'key':'PLEVNE-KUENKER','path':str(archive.relative_to(root)).replace('\\','/'),
                 'source_page':page,'image_url':url,'description':'Künker Auction 299, lot 7259; Plevne medal silver, full obverse and reverse',
                 'license':'Künker copyright; local research only','artist':'Künker','sha256':digest,
                 'width':width,'height':height,'accessed':'2026-09-25'})
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
sources_path=root/'data/sources.json';sources=json.loads(sources_path.read_text(encoding='utf-8'))
sources['kuenker-plevne']={'page':page,'summary':'Auction 299 lot 7259: silver 26.8mm Plevne medal with old original ribbon; 1877 siege, awarded in 1878; former ANS and Morton & Eden collection.',
 'object_id':'Auction 299, lot 7259','accessed':'2026-09-25'}
sources['image-PLEVNE-KUENKER']={'page':page,'image_url':url,'summary':'complete front and reverse in one photograph',
 'dimensions':[width,height],'sha256':digest,'license':'Künker copyright; local research only','accessed':'2026-09-25'}
sources_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
cat_path=root/'data/catalogue.json';cat=json.loads(cat_path.read_text(encoding='utf-8'))
cat['records'].append({'id':'OTT-PLEVNE-SILVER-01','family':'OTT-PLEVNA','name':'普列夫纳战役奖章',
 'original':'Plevne Muhârebesi Madalyası / Plevne Campaign Medal',
 'date':'1877年战役／1878年颁发','variant':'银质；26.8毫米；原绶带；正背同图',
 'views':[{'key':'PLEVNE-KUENKER','label':'正背同图'}],'source_ids':['kuenker-plevne','tdv-madalya','image-PLEVNE-KUENKER']})
cat_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding='utf-8')
pending_path=root/'data/unpictured.json';pending=json.loads(pending_path.read_text(encoding='utf-8'))
pending=[x for x in pending if x['family']!='OTT-PLEVNA']
pending_path.write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf-8')
print('Plevne added')
