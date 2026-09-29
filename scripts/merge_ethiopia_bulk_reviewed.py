"""First reviewed family batch from the full Ethiopian source tree."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
approved={
 'Silver Jubilee Medal':('银禧纪念奖章','1955年设立',0,'绶带挂章；具体等级及材质待考'),
 'Emperor Haile Selassie I Medal of National Service':('海尔·塞拉西一世国家服务奖章','1932年设立',0,'绶带挂章；具体等级及材质待考'),
 'Order of the Seal of Solomon':('所罗门印玺勋章','1874年设立；1930年改制',0,'六角星形挂章；具体等级待考'),
 'Scholarship Medal':('学术奖章','1959年设立',0,'椭圆形绶带挂章；具体等级及材质待考'),
 'Emperor Haile Selassie I Coronation Medal':('海尔·塞拉西一世加冕纪念奖章','1930年设立',0,'绶带挂章；具体等级及材质待考'),
 'Eritrea Medal':('厄立特里亚奖章','1952年设立（据专题目录）',0,'有冠绶带挂章；具体等级待考'),
 'Medal of the Patriot Refugees':('流亡爱国者奖章','1944年设立',0,'单一等级绶带挂章；图示不带火炬年资附饰'),
 'Commemorative Medal for the Korean War':('朝鲜战争纪念奖章','1959年设立',0,'四叶形有冠绶带挂章'),
 'Star of Victory':('胜利之星奖章','1941年设立',1,'有冠十字形挂章；星形中心正面；具体等级待考'),
 'Order of the Star of Ethiopia':('埃塞俄比亚之星勋章','1879年设立',0,'绶带挂章；具体等级待考'),
 'Medal of the Campaign':('抗战战役奖章','1944年设立；纪念1936–1941年战役',0,'单一等级有冠挂章；图示不带火炬年资附饰'),
 'Medal of Menelik II':('孟尼利克二世奖章','1899年设立',0,'绶带挂章；具体等级及材质待考')}
records=[];images=[];sources=json.loads((R/'data/sources.json').read_text(encoding='utf-8'))
for p in sorted((R/'data/raw_candidates/east_south_africa_bulk').glob('ethiopia-*.json')):
 row=json.loads(p.read_text(encoding='utf-8'));title=row['title']
 if title not in approved:continue
 name,date,n,var=approved[title];pic=row['images'][n];key='ETH-BULK-'+p.stem.split('-')[-1].upper();sid=row['source_id']
 records.append(dict(id=key,family=key,country_zh='埃塞俄比亚',awarding_authority='埃塞俄比亚帝国',name=name,original=title,date=date,variant=var+'；低清参考',views=[dict(key=key+'-F',label='完整正面')],source_ids=[sid]))
 images.append({**pic,'view_key':key+'-F','source_page':row['source_page'],'original_url':pic['url'],'author_or_institution':'Wawards / Ilja Repetski; original photographer not separately identified','accessed':'2026-09-29','visual_status':'root reviewed complete obverse','rights_status':'local_research_only','object_effective_long_edge_px_approx':350,'object_size_method':'approximate visual size excluding ribbon and background'})
 sources[sid]=dict(page=row['source_page'],summary=row['source_text'],accessed='2026-09-29',cache=row['cache'],license=pic['license'])
assert len(records)==len(approved)
save(R/'data/volumes/ethiopia_bulk_reviewed_20260929.json',dict(as_of='2026-09-29',records=records))
save(R/'data/volumes/ethiopia_bulk_reviewed_20260929_manifest.json',dict(as_of='2026-09-29',images=images))
save(R/'data/sources.json',sources)
p=R/'data/volumes/minimum_east_south_africa_20260929_specs.json';specs=json.loads(p.read_text(encoding='utf-8'))
for spec in specs:
 if spec['countries']==['埃塞俄比亚']:
  for field,value in [('record_files','ethiopia_bulk_reviewed_20260929.json'),('manifest_files','ethiopia_bulk_reviewed_20260929_manifest.json')]:
   if value not in spec[field]:spec[field].append(value)
save(p,specs)
print(len(records),'additional Ethiopian families and complete front views merged into build inputs')
