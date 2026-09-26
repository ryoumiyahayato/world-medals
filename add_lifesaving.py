import hashlib,json,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
if any(x['id']=='OTT-LIFESAVING-SILVER-01' for x in json.loads((root/'data/catalogue.json').read_text(encoding='utf-8'))['records']):
 raise SystemExit('Life saving medal is already recorded.')
urls=['https://www.emedals.com/cdn/shop/files/ai1_0846.jpg?v=1692910018&width=1946',
      'https://www.emedals.com/cdn/shop/files/ai1_0848.jpg?v=1692910025&width=1946']
page='https://www.emedals.com/products/turkey-ottoman-empire-a-life-saving-medal-medal-of-tahlisiye-eu21417'
manifest_path=root/'image_manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
source_path=root/'data/sources.json';sources=json.loads(source_path.read_text(encoding='utf-8'))
views=[]
for n,url in enumerate(urls,1):
 key=f'TAHLISIYE-{n}'
 photo=root/f'sources/legacy_review/{key}.jpg'
 archive=root/f'originals/ottoman_2026-09-25/{key}.jpg'
 asset=root/f'assets/images/ottoman/{key}.jpg'
 for dest in (archive,asset):shutil.copy2(photo,dest)
 with Image.open(photo) as im:w,h=im.size
 sha=hashlib.sha256(photo.read_bytes()).hexdigest()
 label='正面' if n==1 else '背面'
 manifest.append({'key':key,'path':str(archive.relative_to(root)).replace('\\','/'),
  'source_page':page,'image_url':url,'description':f'eMedals EU21417 {label}, complete medal and ribbon',
  'license':'eMedals copyright; local research only','artist':'eMedals','sha256':sha,'width':w,'height':h,'accessed':'2026-09-25'})
 sources['image-'+key]={'page':page,'image_url':url,'summary':f'EU21417 {label}; 1000x750 source file',
  'sha256':sha,'dimensions':[w,h],'license':'eMedals copyright; local research only','accessed':'2026-09-25'}
 views.append({'key':key,'label':label})
sources['emedals-tahlisiye']={'page':page,'object_id':'EU21417','accessed':'2026-09-25',
 'summary':'Tahlisiye Madalyası, instituted 1859; silver, 36.7 mm; original hanger, replacement ribbon; front and reverse source photos.'}
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
source_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
catpath=root/'data/catalogue.json';cat=json.loads(catpath.read_text(encoding='utf-8'))
cat['records'].append({'id':'OTT-LIFESAVING-SILVER-01','family':'OTT-LIFESAVING','name':'救生奖章',
 'original':'Tahlîs-i Can / Tahlisiye Madalyası / Life Saving Medal','date':'1859–1860',
 'variant':'银质；36.7毫米；原悬挂件；替换绶带；正背同件',
 'views':views,'source_ids':['tdv-madalya','emedals-tahlisiye']+['image-'+v['key'] for v in views]})
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding='utf-8')
unpath=root/'data/unpictured.json';un=json.loads(unpath.read_text(encoding='utf-8'))
un=[x for x in un if x['family']!='OTT-LIFESAVING']
unpath.write_text(json.dumps(un,ensure_ascii=False,indent=2),encoding='utf-8')
print('lifesaving added')
