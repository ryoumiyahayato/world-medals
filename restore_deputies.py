import hashlib,json,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
if any(x['id']=='OTT-LEG-DEPUTIES' for x in json.loads((root/'data/related.json').read_text(encoding='utf-8'))):
 raise SystemExit('Deputies badge is already restored.')
file=root/'sources/legacy_review/DEPUTIES-1.jpg'
archive=root/'originals/ottoman_legacy_2026-09-25/DEPUTIES-1.jpg'
asset=root/'assets/images/ottoman/DEPUTIES-1.jpg'
for dest in (archive,asset):shutil.copy2(file,dest)
with Image.open(file) as im:w,h=im.size
sha=hashlib.sha256(file.read_bytes()).hexdigest()
lead=next(x for x in json.loads((root/'data/legacy_pending.json').read_text(encoding='utf-8')) if x['legacy_key']=='DEPUTIES')
key='LEG-DEPUTIES-1';page=lead['source_page'];url=lead['image_urls'][0]
manpath=root/'image_manifest.json';man=json.loads(manpath.read_text(encoding='utf-8'))
man.append({'key':key,'path':str(archive.relative_to(root)).replace('\\','/'),'source_page':page,'image_url':url,
 'description':'Ottoman Chamber of Deputies badge, full front','license':'Commons file page: PD-Ottoman / PD-US (check jurisdiction)',
 'artist':'unknown','sha256':sha,'width':w,'height':h,'accessed':'2026-09-25'})
manpath.write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
srcpath=root/'data/sources.json';sources=json.loads(srcpath.read_text(encoding='utf-8'))
sources['image-'+key]={'page':page,'image_url':url,'summary':'Complete front, Commons label says Ottoman Chamber of Deputies order; photographer/author unknown.',
 'dimensions':[w,h],'sha256':sha,'accessed':'2026-09-25','license':'Commons file page: PD-Ottoman / PD-US'}
srcpath.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
relpath=root/'data/related.json';rel=json.loads(relpath.read_text(encoding='utf-8'))
rel.append({'id':'OTT-LEG-DEPUTIES','family':'OTT-DEPUTIES-BADGE','name':'奥斯曼众议院议员徽章',
 'original':'Meclis-i Mebusan Azalarına Mahsus Nişan / Chamber of Deputies Badge',
 'date':'设立日期待考；照片来源标注1912–1917',
 'variant':'议员专用佩章；等级待核；不计入正式功绩章种',
 'views':[{'key':key,'label':'正面'}],'source_ids':['legacy-page-DEPUTIES','image-'+key],'origin_legacy_key':'DEPUTIES'})
relpath.write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding='utf-8')
unpath=root/'data/unpictured.json';un=json.loads(unpath.read_text(encoding='utf-8'))
un=[x for x in un if x.get('legacy_key')!='DEPUTIES']
unpath.write_text(json.dumps(un,ensure_ascii=False,indent=2),encoding='utf-8')
logpath=root/'data/migration_log.json';log=json.loads(logpath.read_text(encoding='utf-8'))
for x in log['items']:
 if x['legacy_key']=='DEPUTIES':
  x.update(disposition='related_gallery',target='OTT-LEG-DEPUTIES',
   reason='原图恢复并解码；照片完整。属议员专用佩章，相关附编收录；设立制度日期仍待考。',local_images=1)
logpath.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
print('deputies restored')
