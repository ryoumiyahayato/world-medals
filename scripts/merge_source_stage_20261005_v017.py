"""Merge a reviewed object variant and narrow text-only archive records."""
from pathlib import Path
import json, hashlib
from PIL import Image

R=Path(__file__).resolve().parents[1]
def load(path): return json.loads((R/path).read_text(encoding='utf-8'))
def save(path,value): (R/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=load('data/sources.json')
oid='8515397681429'
objects=[json.loads(x) for x in (R/'data/raw_candidates/emedals_austria_imperial_20261005_objects.jsonl').read_text(encoding='utf-8').splitlines()]
obj=next(x for x in objects if x['object_id']==oid)
rid='AUT-EM-'+oid;sid=rid+'-SOURCE'
sources[sid]=dict(page=obj['object_page'],title='1813—1814年军队十字章：金质包边及悬挂环',summary=obj['description'],accessed='2026-10-05',object_id=oid,credit='eMedals',license='Copyright eMedals; no redistribution permission established')
views=[];images=[]
for i,n in enumerate((2,5)):
    path=f'assets/raw/emedals_austria_imperial_20261005/{oid}_{n:02}.jpg'
    key=rid+'-VIEW'+str(i+1)
    with Image.open(R/path) as im: im.load();size=im.size
    views.append(dict(key=key,label='完整正面' if i==0 else '完整背面（同一拍品）'))
    images.append(dict(key=key.lower(),record_id=rid,view_key=key,local_path=path,source_page=obj['object_page'],image_url=obj['images'][n-1]['image_url'],object_reference=oid,artist='eMedals',license='Copyright eMedals; local research only',dimensions=size,sha256=hashlib.sha256((R/path).read_bytes()).hexdigest(),decoded=True,visually_checked=True,visual_review='Full cross outline, wreath and suspension visible; inscriptions distinguish front and reverse; watermark retained',publication_eligible=False))
records=[dict(id=rid,family='AUT-FAM-ARMY-CROSS-1813-14',country_zh='奥地利帝国',name='1813—1814年军队十字章',original='Armeekreuz für 1813/14',date='1814年设立；本件制作年代待考',variant='铜质章体；金质包边及悬挂环（按来源描述）；顶部有印记；32×33.5毫米',views=views,source_ids=[sid],html_eligible=True,body_eligible=True,publication_eligible=False,evidence=[dict(source_page=obj['object_page'],object_id=oid,accessed_at='2026-10-05',source_excerpt=obj['description'])])]
integration={'austrian-empire':[rid],'uk':[],'british-india':[]}
draft=load('data/normalized_drafts/national_archives_british_military_campaign_service_medals_20261005.json')
guide='https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/british-military-campaign-and-service-medals/'
sid='TNA-BRITISH-CAMPAIGN-SERVICE-20261005'
sources[sid]=dict(page=guide,title='British military campaign and service medals',accessed='2026-10-05',summary='Named award types in sections and appendices; qualifying service periods are not institution dates',credit='The National Archives',license='Text fact reference; no image used')
for family in draft['families']:
    fid=family['id'];rid=fid+'-TNA-TEXT-20261005'
    india='BRITISH-INDIA' in fid
    date=family['date']
    if 'TERRITORIAL-FORCE' in fid:date='一战时期；设立日期待考'
    elif 'EDWARD-VII' in fid:date='1902年加冕纪念；来源年份冲突待考'
    elif 'POLAR' in fid:date='1904年起；具体版型待考'
    variant='有记载未配图；具体等级／版型待考'
    records.append(dict(id=rid,family=fid,country_zh='英属印度' if india else '英国／大英帝国',name=family['name_zh'],original=family['original'],date=date,variant=variant,views=[],source_ids=[sid],html_eligible=True,body_eligible=False,evidence=[dict(source_page=guide,accessed_at='2026-10-05',source_excerpt='Named award: '+family['original']+'; institution date and specimen-specific variant not inferred from medal rolls')]))
    integration['british-india' if india else 'uk'].append(rid)
save('data/volumes/source_stage_v017_20261005.json',dict(as_of='2026-10-05',records=records))
save('data/volumes/source_stage_v017_20261005_manifest.json',dict(as_of='2026-10-05',images=images))
save('data/volumes/source_stage_v017_20261005_integration.json',dict(volume_rows=integration))
prior=load('data/volumes/source_batch_20261005.json')
for row in prior['records']:
    if row.get('family')=='AUT-FAM-ARMY-CROSS-1813-14':
        row['date']='1814年设立；具体日月有来源冲突，待考'
save('data/volumes/source_batch_20261005.json',prior)
save('data/sources.json',sources)
print('New pictured families: 0; new pictured variants: 1; accepted views: 2; new text-only families: 9')
