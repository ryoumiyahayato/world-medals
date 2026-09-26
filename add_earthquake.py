"""One-time intake of Sotheby's complete 1894 earthquake medal image."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parent
catpath=root/'data/catalogue.json'
cat=json.loads(catpath.read_text(encoding='utf-8'))
if any(r['id']=='OTT-EARTHQUAKE-GOLD-SMALL-01' for r in cat['records']):
    raise SystemExit('Earthquake medal already recorded')
src=root/'sources/legacy_review/EARTHQUAKE-SOTHEBYS-1.jpg'
with Image.open(src) as im:im.verify()
with Image.open(src) as im:w,h=im.size
key='EARTHQUAKE-GOLD-SMALL-1'
url='https://sothebys-brightspot.s3.amazonaws.com/media-desk/a2/39/32b93f664d318ef0bdfc168fef48/l26220-dkf4s.jpg'
page='https://www.sothebys.com/en/buy/auction/2026/arts-of-the-islamic-world-india-l26220/istanbul-earthquake-medal-1894'
archive=root/f'originals/ottoman_2026-09-25/{key}.jpg'
asset=root/f'assets/images/ottoman/{key}.jpg'
archive.parent.mkdir(parents=True,exist_ok=True)
asset.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,archive)
shutil.copy2(src,asset)
digest=hashlib.sha256(src.read_bytes()).hexdigest()
manifest_path=root/'image_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.append({'key':key,'path':str(archive.relative_to(root)).replace('\\','/'),
 'source_page':page,'image_url':url,'description':'Sotheby’s L26220 lot 246 complete obverse and original ribbon',
 'license':'Sotheby’s copyright; local research only','artist':'Sotheby’s',
 'sha256':digest,'width':w,'height':h,'accessed':'2026-09-25'})
source_path=root/'data/sources.json'
sources=json.loads(source_path.read_text(encoding='utf-8'))
sources['sothebys-earthquake-gold']={'page':page,'object_id':'L26220, lot 246','accessed':'2026-09-25',
 'summary':'Istanbul Earthquake Medal 1894, gold, 28 mm excluding suspension, original ribbon and stickpin, reverse engraved Abbas Hilmi Pasha; awarded to supporters of victims of 10 July 1894 earthquake. Only complete obverse view downloaded.',
 'image_url':url,'sha256':digest,'dimensions':[w,h],
 'license':'Sotheby’s copyright; local research only'}
cat['records'].append({'id':'OTT-EARTHQUAKE-GOLD-SMALL-01','family':'OTT-EARTHQUAKE',
 'name':'地震救济奖章','original':'Hareket-i Arz Madalyası / Istanbul Earthquake Medal',
 'date':'1894','variant':'金质；小型28毫米；原绶带；正面完整；背面暂缺图',
 'views':[{'key':key,'label':'正面'}],
 'source_ids':['tdv-madalya','sothebys-earthquake-gold']})
unpath=root/'data/unpictured.json'
unpictured=json.loads(unpath.read_text(encoding='utf-8'))
unpictured=[r for r in unpictured if r['family']!='OTT-EARTHQUAKE']
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
source_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding='utf-8')
unpath.write_text(json.dumps(unpictured,ensure_ascii=False,indent=2),encoding='utf-8')
print('earthquake medal added')
