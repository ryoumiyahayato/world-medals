import hashlib,json,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
catpath=root/'data/catalogue.json';cat=json.loads(catpath.read_text(encoding='utf-8'))
if any(x['id']=='OTT-LEG-IFT-ORDER' for x in cat['records']):
    raise SystemExit('Two order images are already restored.')
unpath=root/'data/unpictured.json';un=json.loads(unpath.read_text(encoding='utf-8'))
logpath=root/'data/migration_log.json';log=json.loads(logpath.read_text(encoding='utf-8'))
srcpath=root/'data/sources.json';sources=json.loads(srcpath.read_text(encoding='utf-8'))
manpath=root/'image_manifest.json';manifest=json.loads(manpath.read_text(encoding='utf-8'))
legacy={x['legacy_key']:x for x in json.loads((root/'data/legacy_pending.json').read_text(encoding='utf-8'))}
orders=[('IFT-ORDER','OTT-IFTIHAR-ORDER','荣誉勋章','Nişan-ı İftihar / Order of Glory','1833年章程；创设年份待考','镶饰挂章；等级待核；正面',
         'TDV：1833年公布章程，早期金银镶钻；1851–1852年停用。'),
        ('IMT-ORDER','OTT-IMTIYAZ-ORDER','伊姆提雅兹勋章','Nişan-ı İmtiyaz / Order of Distinction','1841年已有授予记载','镶钻章；等级不分；低清参考',
         'TDV：阿卜杜勒迈吉德时期创设，1841年已有授予记录，制度不分等级。')]
for key,family,name,original,date,variant,note in orders:
    file=root/f'sources/legacy_review/{key}-1.jpg'
    dest=root/f'originals/ottoman_legacy_2026-09-25/{key}-1.jpg'
    asset=root/f'assets/images/ottoman/{key}-1.jpg'
    for target in (dest,asset):shutil.copy2(file,target)
    with Image.open(file) as im:w,h=im.size
    sha=hashlib.sha256(file.read_bytes()).hexdigest()
    image_key='LEG-'+key+'-1';page=legacy[key]['source_page'];url=legacy[key]['image_urls'][0]
    manifest.append({'key':image_key,'path':str(dest.relative_to(root)).replace('\\','/'),
       'source_page':page,'image_url':url,'description':name+'; complete obverse',
       'license':'Commons file page: PD-Ottoman / PD-US (check jurisdiction)','artist':'unknown',
       'sha256':sha,'width':w,'height':h,'accessed':'2026-09-25'})
    sources['image-'+image_key]={'page':page,'image_url':url,'summary':name+'完整正面；'+note,
       'dimensions':[w,h],'sha256':sha,'accessed':'2026-09-25','license':'Commons file page: PD-Ottoman / PD-US'}
    recid='OTT-LEG-'+key
    cat['records'].append({'id':recid,'family':family,'name':name,'original':original,'date':date,
       'variant':variant,'views':[{'key':image_key,'label':'正面'}],
       'source_ids':['tdv-nisan','legacy-page-'+key,'image-'+image_key],
       'origin_legacy_key':key})
    un=[x for x in un if x.get('legacy_key')!=key]
    for item in log['items']:
        if item['legacy_key']==key:
            item.update(disposition='main_gallery',target=recid,reason='已恢复原站完整图片并依据TDV修正制度年代；'+note,local_images=1)
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding='utf-8')
unpath.write_text(json.dumps(un,ensure_ascii=False,indent=2),encoding='utf-8')
logpath.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
srcpath.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
manpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('restored',len(orders),'orders')
