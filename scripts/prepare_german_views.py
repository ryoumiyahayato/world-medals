"""Materialize only visually reviewed German photographs; retain originals and crop provenance."""
from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text('utf-8'))
out=[]
commons=load('sources/cache/german_commons_20260929/photos.json')
shm={x['id']:x for x in load('sources/cache/german_shm_20260929/objects.json')}
for mode in ['museum','shm']:
 for row in load('data/staging/german_completion/'+mode+'_review.json')['rows']:
  v={k:row[k] for k in ['family','date','variant']};v['images']=[]
  for spec in row['images']:
   if mode=='museum':
    p=commons[spec['index']];evidence=next((v for k,v in p['source_fields'].items() if k.startswith('Description')),p['title'])
    im=dict(p,artist=p['source_fields'].get('Author','Borodun'),license='CC BY-SA 4.0',evidence=evidence)
   else:
    o=shm[row['id']];p=o['images'][spec['index']];lic=o['metadata']['image']['license']['name']
    im=dict(p,source_page=o['source_page'],title=o['metadata']['title'],artist=o['metadata']['image']['displayCredits'],license=lic,evidence=o['source_text'].split('URI har kopierats')[0],object_id=o['metadata']['fields']['objectNumber']['value'])
   im['label']=spec['label'];im['original_path']=im['local_path'];im['visual_review']='complete medal contour; source correspondence checked 2026-09-29'
   if spec.get('crop'):
    dest=R/'assets/images/german_completion'/((R/im['local_path']).stem+'-complete-crop.jpg')
    with Image.open(R/im['local_path']) as pic:pic.crop(spec['crop']).save(dest,quality=95)
    im['local_path']=dest.relative_to(R).as_posix();im['crop_region']=spec['crop'];im['processing']='rectangular crop only; original retained; no generated detail'
   v['images'].append(im)
  out.append(v)
bvo=load('data/staging/german_completion/deutschen_bundesverdienstorden.json')['items'][0]
dates=['2000–2004年','1955年起','1951年起','1979–2023年','1957–1966年','1951年起','1979–2023年','1951年起','1954年起','1968年起（80毫米胸星型）',None,'1952年起','1956年起','1951年起','1954年起；2023年3月女式改用男式挂章','1955年起','1955年起','1952年至最迟1968年','1954／1998年特殊颁授型（来源分类）','2023年特殊颁授型（来源分类）']
for n,x in enumerate(bvo['variants']):
 if n==10:continue # exact same photograph as second-form star, not a separate pictured variant
 form=x['level_zh']+'；'+x['form_zh']
 if n==9:form='大功绩十字星章级；第二式胸星；男女式来源条目共用照片'
 if n in [11,12,13,14,15,16,18,19]:form+='；图示挂章'
 if x['image_resolution_note']:form+='；'+x['image_resolution_note']
 out.append(dict(family=bvo['family_id'],date=dates[n]+'（型式时期，非本件颁发日期）',variant=form,images=[dict(local_path=x['image_file'],original_path=x['image_file'],label='正面',source_page=x['source_page'],original_url=x['image_url'],title=x['original_name'],evidence=x['source_summary'],license='Private non-commercial copies permitted; public redistribution not licensed',artist='Alexander von Sallach / die-deutschen-orden.de',visual_review='complete medal contour; grade and displayed component checked 2026-09-29',publication_status='local private research only')]))
for family in load('data/staging/german_completion/deutschen_federal_other_awards.json')['items']:
 for x in family['variants']:
  period=x['period_or_date_candidate'][0].replace('seit ','').replace('von ','').replace(' bis ','–')
  period+='年起' if x['period_or_date_candidate'][0].startswith('seit ') else '年'
  out.append(dict(family=family['family_id'],date=period+'（来源所述型式时期）',variant=x['name_zh']+'；低清参考',images=[dict(local_path=x['image_file'],original_path=x['image_file'],label='正面',source_page=x['source_page'],original_url=x['image_url'],title=x['original_name'],evidence=x['source_summary'],license='Private non-commercial copies permitted; public redistribution not licensed',artist='Alexander von Sallach / die-deutschen-orden.de',visual_review='complete medal contour; grade and displayed component checked 2026-09-29',publication_status='local private research only')]))
(R/'data/staging/german_completion/views_final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Reviewed variant rows:',len(out),'display views:',sum(len(x['images']) for x in out))
