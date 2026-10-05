"""Persist bounded source coverage and the remaining image queue."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text('utf-8'))
def save(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
S='data/staging/uk_mod_completion/'
stats=load('data/normalized/uk_mod_completion_20260930.json')
alt=load(S+'alternate_images.json');rows=load('data/volumes/uk_mod_completion_20260930.json')['records']
matrix=load('data/source_atlas/uk_mod_completion_20260930_source_matrix.json')
matrix['sources'][0]['status']='completed_bounded_page'
matrix['sources'][0]['image_capability']='53个页面图片地址；52完整图复用，1张伊叙拼图曾下载但裁断章体，未纳入'
common=dict(language=['en'],date_coverage='本批指定对象',pagination='有界对象页集合',download_method='HTML缓存与来源提供原图，逐图解码及视觉核对',priority='gap_image',last_checked='2026-09-30')
matrix['sources']=matrix['sources'][:1]+[
 dict(common,id='UK-NAM-6-OBJECTS',url='https://collection.nam.ac.uk/',type='museum',status='completed_bounded_objects',coverage_boundary='六个已登记NAM对象页及全部11张对应可见图；不代表全馆目录耗尽',object_pages=[x['object_page'] for x in alt['alternates'] if x['source_object_id'].startswith('NAM')],image_capability='11张完整实物照，页面标示Out of Copyright'),
 dict(common,id='UK-AUCKLAND-COMMONS',url='https://commons.wikimedia.org/',type='museum_image_repository',status='partial',coverage_boundary='皇家红十字一级成功；1953年加冕章已检查候选均不合格，待找新对象',image_capability='1张完整CC BY 4.0原图；遮挡、裁断、关盒图排除'),
 dict(common,id='UK-OSM-IRAQ-SYRIA-GAP',url='https://www.gov.uk/guidance/medals-campaigns-descriptions-and-eligibility#operational-service-medal---iraq-and-syria',type='alternate_image_discovery',status='partial',coverage_boundary='本批未取得经核验完整章体照片；公开仪式图、绶带图不充当完整实物',image_capability='未取得')]
plan=dict(planned=4,completed=2,partial=2,blocked=0,not_started=0)
matrix['source_plan']=plan;save('data/source_atlas/uk_mod_completion_20260930_source_matrix.json',matrix)
atlas=load('data/source_atlas/global_source_atlas.json')
previous=next((s.get('coverage') or {} for s in atlas['scopes'] if s['scope_id']=='uk_mod_completion_20260930'),{})
atlas['scopes']=[s for s in atlas['scopes'] if s['scope_id']!='uk_mod_completion_20260930']
atlas['scopes'].append(dict(scope_id='uk_mod_completion_20260930',scope_label='英国国防部指南及馆藏缺图补充',matrix_file='data/source_atlas/uk_mod_completion_20260930_source_matrix.json',coverage=plan,next_action='补7项完整图，先1953加冕与伊拉克/叙利亚版，再五项旧预备役奖励；扩展专门官方链接'))
atlas['coverage']={k:atlas.get('coverage',{}).get(k,0)-previous.get(k,0)+plan[k] for k in plan};atlas['source_count']=atlas['coverage']['planned'];atlas['as_of']='2026-09-30';save('data/source_atlas/global_source_atlas.json',atlas)
pending=[dict(id=r['id'],family=r['family'],name=r['name'],variant=r['variant'],status='needs_complete_image',source_ids=r['source_ids']) for r in rows if not r['views']]
save('data/queues/uk_mod_completion_next.json',dict(as_of='2026-09-30',pending_images=pending,source_matrix='data/source_atlas/uk_mod_completion_20260930_source_matrix.json',next_scope='英国官方奖项专门说明与历史预备役体系；不重复下载现有图片'))
raw=[]
for x in alt['alternates']:
 raw.append(dict(source_id=x['source_object_id'],page_title=x['name'],original_name=x['name'],date_candidates=x['date_note'],category='museum_object',grade_material_clues=x['variant'],object_page=x['object_page'],original_image_urls=[i['image_url'] for i in x['images']],notes=x['object_summary'],status='merged_verified_complete_views',accessed='2026-09-30'))
(R/'data/raw_candidates/uk_mod_alternate_images_20260930.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in raw)+'\n','utf-8')
save('data/checkpoints/uk_mod_completion_2026-09-30_v009.json',dict(as_of='2026-09-30',scope='用户指定英国MOD指南整页及缺图补充',status='merged_build_verification_pending',version='0.009',statistics=stats,source_plan=plan,raw_heading_nodes=82,award_fact_items=68,normalized_guide_families=63,merged_source_objects=7,unresolved_image_rows=len(pending),source_matrix='data/source_atlas/uk_mod_completion_20260930_source_matrix.json',next_queue='data/queues/uk_mod_completion_next.json',files=['index.html','mobile/build/world-medals-0.009.apk'],limitations=['仅完成该指南正文的有界对照，不等于穷尽英国全部历史奖励','七项仍缺完整图','DSO实物页题名与正文日期差异已保留于conflicts','未在实体安卓设备安装测试','现有全库含受限图片，只保留本地研究版本，不上传公网']))
print(json.dumps(dict(source_plan=plan,pending_images=len(pending))))
