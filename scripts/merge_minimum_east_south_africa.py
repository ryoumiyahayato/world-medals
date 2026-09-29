"""Curated local research rows after object-page and contact-sheet review."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# One complete view per country. No colour-based material/grade attribution.
chosen=[
 ('djibouti','吉布提大星勋章','1978年3月28日设立',0,'胸星；具体等级待考','吉布提'),
 ('somalia','索马里之星勋章','1961年2月12日设立',0,'胸星；具体等级待考','索马里共和国'),
 ('kenya','金心勋章','1966年4月21日设立',0,'蝴蝶结绶带挂章；具体等级待考','肯尼亚'),
 ('uganda','尼罗河之源勋章','设立日期待考',1,'胸星；具体等级待考','乌干达'),
 ('tanzania','乞力马扎罗火炬勋章','1977年设立',0,'蝴蝶结绶带挂章；具体等级待考','坦桑尼亚'),
 ('rwanda','革命勋章','1976年4月7日设立',0,'蝴蝶结绶带挂章；具体等级待考','卢旺达共和国'),
 ('burundi','卡里恩达王家勋章','1962年7月1日设立',2,'胸星；具体等级待考','布隆迪王国'),
 ('comoros','大科摩罗之星勋章','1886年设立；1910年改制',0,'新月及垂星挂章；具体等级与版期待考','大科摩罗苏丹国'),
 ('ethiopia','所罗门勋章','1922年设为特殊等级；1930年独立成章',1,'单一领链级的章体正面；构件归类待考','埃塞俄比亚帝国'),
 ('madagascar','拉达马二世勋章','1862年9月13日设立',0,'有冠挂章；具体等级待考','马达加斯加王国'),
 ('south-africa','沃尔特马德勇敢奖章','1970年5月20日设立',0,'绶带挂章；具体等级及材质待考','南非共和国'),
 ('namibia','鹰勋章','1995年设立',0,'蝴蝶结绶带挂章；章面英文为 Order of the Sea Eagle；具体等级待考','纳米比亚'),
 ('botswana','博茨瓦纳总统勋章','1979年设立',1,'八芒胸星（P.O.B.）','博茨瓦纳'),
 ('zambia','赞比亚之鹰勋章','1965年10月23日设立',0,'绶带挂章；具体等级待考','赞比亚'),
 ('zimbabwe','功绩军团勋章','1970年设立',3,'绶带挂章；具体等级待考','罗得西亚'),
 ('malawi','马拉维雄狮勋章','1967年设立',4,'胸星；具体等级待考','马拉维'),
 ('mozambique','友谊与和平勋章','设立日期待考',0,'绶带挂章；版别及材质待考','莫桑比克'),
 ('lesotho','莫舒舒勋章','1972年设立',1,'胸星；具体等级待考','莱索托'),
 ('swaziland','索布扎二世王家勋章','1975年6月18日设立',2,'胸星；具体等级待考','斯威士兰王国')
]
records=[];images=[];specs=[];sources=json.loads((R/'data/sources.json').read_text(encoding='utf-8'));matrix=[]
for slug,name,date,number,variant,authority in chosen:
 raw=json.loads((R/'data/raw_candidates/minimum_east_south_africa'/f'{slug}.json').read_text(encoding='utf-8'))
 photo=next(i for i in raw['images'] if Path(i['path']).stem==f'{slug}-{number}')
 photo={k:v for k,v in photo.items() if k!='visual_status'}
 path=R/photo['path']
 with Image.open(path) as im:im.load();assert im.width==photo['width']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==photo['sha256']
 rid='MIN-AFR-'+slug.upper()+'-001';sid='WAW-MIN-'+slug.upper();view=rid+'-F'
 records.append(dict(id=rid,family=rid,country_zh=raw['country'],awarding_authority=authority,name=name,original=raw['object_name'],date=date,
  variant=variant+'；低清参考',views=[dict(key=view,label='完整正面')],source_ids=[sid],
  research_notes='Local research source photograph, unchanged watermark. Date from specialist object page; precise grade/material unasserted unless specified. No public redistribution permission inferred.'))
 images.append(dict(**photo,view_key=view,local_path=photo['path'],source_page=raw['object_page'],original_url=photo['url'],author_or_institution='Wawards / Ilja Repetski; original photographer not separately stated',accessed='2026-09-29',visual_status='reviewed_complete_front',reviewer='root',rights_status='local_research_only',image_kind='source_object_image'))
 sources[sid]=dict(page=raw['object_page'],summary=raw['source_text'],accessed='2026-09-29',cache=raw['object_cache'],license=photo['license'])
 title=raw['country'] if authority==raw['country'] else authority
 specs.append(dict(slug='minimum_'+slug.replace('-','_'),title=title,anchor='minimum-'+slug,aliases=raw['country']+' '+slug+' '+authority,country_group=slug.replace('-','_'),record_files=['minimum_east_south_africa_20260929.json'],manifest_files=['minimum_east_south_africa_20260929_manifest.json'],countries=[raw['country']]))
 matrix.append(dict(id=sid,type='specialist_catalogue',language='en',scope=raw['country'],url=raw['object_page'],date_coverage=date,image_capability='complete source photograph; 600px reference',pagination='country index plus selected award object',download_method='direct public originals; 1 second spacing and cache',priority=1,status='partial_minimum_country_object_reviewed',last_checked='2026-09-29',coverage_boundary='All visible country-index candidates saved; only first illustrated award bundle reviewed; remaining candidates queued'))
save(R/'data/volumes/minimum_east_south_africa_20260929.json',dict(as_of='2026-09-29',records=records))
save(R/'data/volumes/minimum_east_south_africa_20260929_manifest.json',dict(as_of='2026-09-29',images=images))
save(R/'data/volumes/minimum_east_south_africa_20260929_specs.json',specs)
save(R/'data/sources.json',sources)
save(R/'data/source_atlas/minimum_east_south_africa_source_matrix.json',dict(as_of='2026-09-29',scope_id='minimum_east_south_africa',sources=matrix))
save(R/'data/queues/minimum_east_south_africa_remaining.json',dict(as_of='2026-09-29',uncovered_countries=['安哥拉','厄立特里亚','南苏丹','塞舌尔','毛里求斯'],notes={'安哥拉':'First source image may be a rendering, awaiting photographic source.','厄立里亚':'Search results concern foreign awards or sporting medals; no domestic formal decoration established by inspected sources.','南苏丹':'2018 army awards documented; full attributable object photos still missing.'},follow_up='Revisit raw index candidates for grade and image provenance; minimum coverage is not source exhaustion.'))
print(len(records),'reviewed families/rows/images prepared')
