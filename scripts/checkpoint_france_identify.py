"""Persist bounded France source coverage, including unfinished image work."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
S='data/staging/france_identify_20260930/'
def load(p): return json.loads((R/p).read_text('utf-8'))
def save(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
discovery=load(S+'discovery.json'); images=load(S+'image_manifest.json')
review=load(S+'image_review.json'); mapping=load(S+'mapping.json')
stats=load('data/normalized/france_identify_20260930.json')
rows=load('data/volumes/france_identify_20260930.json')['records']
plan=dict(planned=2,completed=2,partial=0,blocked=0,not_started=0)
matrix=dict(as_of='2026-09-30',scope='France IdentifyMedals cross-reference supplement',source_plan=plan,sources=[
 dict(id='FR-IDENTIFY-20260930',url='https://www.identifymedals.com/medals-database-medals-from-france/',type='specialist_directory',language=['en','fr'],date_coverage='Medieval references to contemporary awards',image_capability='89 source images downloaded and decoded; image review determines eligible complete fronts',pagination='Six visible France/period directories; no visible pagination',download_method='Cached HTML, web reader for one failed HTML fetch, original provided image files',priority='user_supplied',status='completed_bounded_directory',last_checked='2026-09-30',coverage_boundary='89 visible object links from six directories, not all French awards; related-country entries retained separately',raw_objects=89,rights='Publisher permits attributed reuse retaining watermarks; upstream rights uncertainty retained. Local research edition only.'),
 dict(id='FR-CHANCELLERIE-ROYAL-20260930',url='https://www.legiondhonneur.fr/fr/la-france-frise',type='official',language=['fr'],date_coverage='1469–1830',image_capability='Not used for new images',pagination='Single timeline',download_method='HTML cached',priority='fact_verification',status='completed_bounded_page',last_checked='2026-09-30',coverage_boundary='Saint-Michel and Saint-Esprit institutional facts only')])
mf='data/source_atlas/france_identify_20260930_source_matrix.json';save(mf,matrix)
atlas=load('data/source_atlas/global_source_atlas.json');sid='france_identify_20260930'
old=next((s.get('coverage',{}) for s in atlas['scopes'] if s['scope_id']==sid),{})
atlas['scopes']=[s for s in atlas['scopes'] if s['scope_id']!=sid]
atlas['scopes'].append(dict(scope_id=sid,scope_label='法国IdentifyMedals目录对照补图',matrix_file=mf,coverage=plan,next_action='优先补仍缺完整正面的条目、查更高清且权利明确的实物来源'))
atlas['coverage']={k:atlas.get('coverage',{}).get(k,0)-old.get(k,0)+v for k,v in plan.items()};atlas['source_count']=atlas['coverage']['planned'];atlas['as_of']='2026-09-30';save('data/source_atlas/global_source_atlas.json',atlas)
pending=[x for x in review.get('entries',[]) if not x.get('accepted_as_front')]
q='data/queues/france_identify_next.json'
save(q,dict(as_of='2026-09-30',source_matrix=mf,missing_or_unsuitable_fronts=pending,mapping_file=S+'mapping.json',next_actions=['Resolve unmerged source candidates by actual issuer','Find full obverse for reverse-only image candidates','Replace low-resolution references with source-backed higher-resolution originals when available'],scope_complete='Six visible directories exhausted; new high-resolution sources remain open'))
save('data/checkpoints/france_identify_2026-09-30_v010.json',dict(as_of='2026-09-30',status='merged_build_verification_pending',version='0.010',statistics=stats,source_plan=plan,raw_candidates=89,downloaded_images=len(images),unresolved_front_candidates=len(pending),matrix=mf,next_queue=q,files=['index.html','mobile/build/world-medals-0.010.apk'],limitations=['有界目录完成不等于法国勋奖章穷尽','保留原图水印；低清图如实标识','未在实体安卓设备安装测试','上游图片权利仍有不确定性，本批仅本地研究，不发布整库']))
print(json.dumps(dict(statistics=stats,source_plan=plan,unresolved_front_candidates=len(pending)),ensure_ascii=False))
