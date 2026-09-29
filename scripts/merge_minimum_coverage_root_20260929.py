"""Merge the manually reviewed first minimum-coverage batch; originals stay intact."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

volume = ROOT/'data/volumes'
stage = ROOT/'data/staging/minimum_coverage_asia'
iraq = json.loads((stage/'records.json').read_text(encoding='utf-8'))
# Family identifier describes this award, rather than all police medals.
iraq['records'][0]['family'] = 'IQ-POLICE-EXCELLENT-SERVICE'
iraq['records'][0]['variant'] += '；低清参考'
save(volume/'minimum_coverage_iraq_20260929.json', iraq)
shutil.copyfile(stage/'manifest.json', volume/'minimum_coverage_iraq_20260929_manifest.json')

ca = 'https://www.canada.ca/en/department-national-defence/services/medals/medals-chart-index/companion-order-canada-cc.html'
nz = 'https://www.dpmc.govt.nz/image-galleries/2468/media?page=8'
nzh = 'https://www.dpmc.govt.nz/our-programmes/new-zealand-royal-honours/new-zealand-royal-honours-system/history'
records = [
 {'id':'CAN-ORDER-CANADA-COMPANION-OFFICIAL','family':'CAN-ORDER-CANADA','country_zh':'加拿大','awarding_authority':'加拿大',
  'name':'加拿大勋章','original':'Order of Canada','date':'1967年设立',
  'variant':'同伴级（Companion，C.C.）；颈挂章；官方图式·低清参考',
  'views':[{'key':'CAN-ORDER-CANADA-COMPANION-F','label':'官方正面图式'}],
  'source_ids':['CAN-DND-CC-20260929']},
 {'id':'NZ-ORDER-MERIT-MEMBER-OFFICIAL','family':'NZ-ORDER-MERIT','country_zh':'新西兰','awarding_authority':'新西兰',
  'name':'新西兰功绩勋章','original':'The New Zealand Order of Merit','date':'1996年5月30日设立',
  'variant':'成员级（Member，MNZM）；银质及珐琅；直绶带佩章',
  'views':[{'key':'NZ-ORDER-MERIT-MEMBER-F','label':'完整正面'}],
  'source_ids':['NZ-DPMC-MNZM-20260929','NZ-DPMC-HISTORY-20260929']}
]
images=[]
for key,filename,url,page,credit,license,kind in [
 ('CAN-ORDER-CANADA-COMPANION-F','canada_front.png','https://www.canada.ca/content/dam/themes/defence/caf/dhr/medals/companion-order-canada-cc-300.png',ca,'Department of National Defence, Canada','Government of Canada material; retain attribution; local non-commercial research copy, not an official edition.','official_diagram'),
 ('NZ-ORDER-MERIT-MEMBER-F','new_zealand.jpg','https://www.dpmc.govt.nz/sites/default/files/2018-12/MNZM-FS-M-WB-01-clearcut-v2.jpg',nz,'Department of the Prime Minister and Cabinet, New Zealand','CC BY 4.0; explicit notice on original photograph; https://creativecommons.org/licenses/by/4.0/','physical_photo')]:
    path=ROOT/'assets/images/minimum_coverage_root'/filename
    with Image.open(path) as im:
        im.load(); w,h=im.size
    images.append(dict(view_key=key,local_path=path.relative_to(ROOT).as_posix(),source_page=page,original_url=url,
                       author_or_institution=credit,license=license,image_kind=kind,width=w,height=h,
                       sha256=hashlib.sha256(path.read_bytes()).hexdigest(),accessed='2026-09-29',
                       visual_review='Complete insignia and suspension checked by root; original retained without cropping.'))
save(volume/'minimum_coverage_root_20260929.json',{'as_of':'2026-09-29','records':records})
save(volume/'minimum_coverage_root_20260929_manifest.json',{'as_of':'2026-09-29','images':images,
 'excluded_images':[{'path':'assets/images/minimum_coverage_root/australia.jpg','reason':'AWM REL47338.002 shows overlapping mounted group; target badge partly obscured.'},
 {'path':'assets/images/minimum_coverage_root/canada_back.png','reason':'No evidence establishing same physical object as the official obverse illustration; retained as reference only.'}]})
sources=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
for s in json.loads((stage/'sources.json').read_text(encoding='utf-8'))['sources']:
    sources[s['source_id']]={**s,'page':s['page_url'],'summary':s.get('source_description') or s.get('image_note') or s.get('published_reference') or s.get('caption') or s['title']}
sources.update({
 'CAN-DND-CC-20260929':{'page':ca,'accessed':'2026-09-29','summary':'加拿大国防部：加拿大勋章1967年设立；本页为Companion级，颈佩。保存官方正面图式；低清参考。'},
 'NZ-DPMC-MNZM-20260929':{'page':nz,'accessed':'2026-09-29','summary':'DPMC官方图像页第9/11项：Member级，银质及珐琅，直绶带。原图4000×2667，照片自带CC BY 4.0标识；完整正面。'},
 'NZ-DPMC-HISTORY-20260929':{'page':nzh,'accessed':'2026-09-29','summary':'DPMC荣誉制度史：新西兰功绩勋章于1996年5月30日设立。'}
})
save(ROOT/'data/sources.json', sources)
save(ROOT/'data/raw_candidates/minimum_coverage_root_20260929.json',{'as_of':'2026-09-29','records':records,'images':images})
print('Prepared Iraq, Canada and New Zealand: 3 families, 3 variants, 3 complete images (2 photographs + 1 official diagram).')
