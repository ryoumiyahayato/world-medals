"""Retain reviewed originals and lossless single-object crops of a group plate."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
raw=json.loads((R/'sources/cache/france_commons_completion/photos.json').read_text('utf-8'))
by={x['title']:x for x in raw};out=[]
def add(title,slug,variant,label='完整正面',crop=None,grade=None):
 r=by[title];p=R/r['local_path'];original=r['local_path']
 if crop:
  p=p.with_name(p.stem+'-'+grade+'.png')
  with Image.open(R/original) as im:im.crop(crop).save(p)
 with Image.open(p) as im:im.load();w,h=im.size
 out.append(dict(slug=slug,variant=variant,label=label,local_path=p.relative_to(R).as_posix(),source_page=r['source_page'],original_url=r['original_url'],original_path=original,crop_region=crop,width=w,height=h,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),license='; '.join(r['license']),license_urls=r['license_urls'],artist=r['source_fields'].get('Author',''),object_description=next((v for k,v in r['source_fields'].items() if k.startswith('Description')),''),visual_review='Root inspected full original: complete medal and suspension. Crops, if any, retain the complete object and original source plate.',accessed='2026-09-29'))
add("File:Médaille d'honneur des douanes.png",'medaille_honneur_douanes','正面悬挂式实物；具体等级与生产时期待考；低清参考')
add("File:1905-maintenant Médaille d'honneur des Eaux et Forêts 2e modèle 2e ty.jpg",'medaille_honneur_eaux_forets','第二式第二型（来源分类），1905年起；完整正背合图','完整正背合图')
for grade,zh,box in [('gold','金级',(0,0,1400,3000)),('silver','银级',(1450,0,2800,3000)),('bronze','铜级',(2850,0,4000,3000))]:
 add("File:Les médailles d'honneur de l'engagement ultramarin.jpg",'medaille_honneur_engagement_ultramarin',zh+'；完整正面；级别名称不推定实金／实银材质',crop=box,grade=grade)
target=R/'data/staging/france_completion';target.mkdir(parents=True,exist_ok=True)
(target/'reviewed_images.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print(len(out),'reviewed variant views from',len({x['original_path'] for x in out}),'original files')
