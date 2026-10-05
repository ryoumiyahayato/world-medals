"""Persist source boundaries, unresolved work and local-only publication decisions."""
from pathlib import Path
import json,collections
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text('utf-8-sig'))
def save(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
matrix='data/source_atlas/user_supplied_europe_global_20261005_source_matrix.json'
m=load(matrix);coverage=collections.Counter(s['status'] for s in m['sources']);m['coverage']=dict(planned=len(m['sources']),completed=coverage['completed'],partial=coverage['partial'],blocked=coverage['blocked'],not_started=coverage['not_started']);save(matrix,m)
atlas=load('data/source_atlas/global_source_atlas.json')
byid={s['source_id']:s for s in atlas['sources']}
for s in m['sources']:byid[s['source_id']]=dict(s,scope_ids=[m['scope_id']],matrix_file=matrix)
atlas['sources']=list(byid.values());atlas['source_count']=len(byid);atlas['as_of']='2026-10-05'
c=collections.Counter(s.get('status','not_started') for s in atlas['sources'])
def normalize(status):
 if status in ('completed','complete'):return 'completed'
 if 'blocked' in status or 'unreachable' in status:return 'blocked'
 if 'partial' in status or 'pending' in status:return 'partial'
 if status in ('not_started','planned'):return 'not_started'
 return 'completed' if 'complete' in status else 'partial'
counts=collections.Counter(normalize(s.get('status','not_started')) for s in atlas['sources'])
atlas['coverage']=dict(planned=len(byid),**{k:counts[k] for k in ['completed','partial','blocked','not_started']})
scope=dict(scope_id=m['scope_id'],scope_label='User supplied global and European sources',matrix_file=matrix,coverage=m['coverage'],next_action='Finish Austria unmatched pages and eMedals family/variant review; extend remaining listed source categories; seek open-license replacement photos.')
atlas['scopes']=[s for s in atlas['scopes'] if s['scope_id']!=m['scope_id']]+[scope]
atlas['latest_source_batch_checkpoint']='data/checkpoints/source_batch_20261005.json';save('data/source_atlas/global_source_atlas.json',atlas)
batch=load('data/volumes/source_batch_20261005.json');man=load('data/volumes/source_batch_20261005_manifest.json')
html=BeautifulSoup((R/'index.html').read_text('utf-8'),'html.parser')
for r in batch['records']:
 tr=html.find('tr',id=r['id']);assert tr is not None and len(tr.find_all('td',recursive=False))==3
 assert len(tr.select('img'))==len(r['views'])
 assert (tr.get('data-publication-eligible')=='false')==(r['publication_eligible'] is False)
pending=[dict(source='emedals_austria_imperial',raw_records=1724,matched_existing_objects=491,pending_classification=774,annex_or_other=459,next='Read remaining object pages; reconcile grades, periods and makers; select nonduplicate variants; acquire publishable photos'),dict(source='medals_org_austria',unmapped_pages=28,held_rows=2,next='Normalize issuing systems and widow award; replace boundary-cropped Iron Crown image'),dict(source='france_official_world_map',restricted_image_candidates=80,next='Deduplicate 80 museum image leads; use accessible object evidence and open-license/user-owned photos'),dict(source='onebid_auction3987681_category9246',unmatched_formal_lots=1,formal_candidate_lots=7,next='Resolve WWI commemorative medal issuing body; complete exact-variant original images')]
save('data/queues/user_supplied_sources_20261005_remaining.json',dict(as_of='2026-10-05',items=pending))
result=dict(as_of='2026-10-05',status='bounded_batch_integrated_overall_request_in_progress',source_coverage=m['coverage'],raw_candidates=dict(emedals=1724,austria_refreshed_object_pages=70,france_objects=80,onebid_lots=20),new_independent_families=4,new_variant_rows=len(batch['records']),accepted_complete_views=len(man['images']),publication_eligible_rows=2,publication_eligible_images=2,local_research_only_rows=26,local_research_only_images=44,already_registered_family_completed_with_image=['FRA-SAMLHOC-ORDRE_SAINT_LOUIS'],outputs=['index.html','data/volumes/source_batch_20261005.json','data/volumes/source_batch_20261005_manifest.json'],pending=pending,verification='All46accepted images decoded, checksummed and visually reviewed; all28rows present with3cells and localimages; browser confirmed French images loaded. APK not rebuilt; restricted newrows excluded by exporter.',next='Continue1724marketrecordfamily/variantreview and28Austriaunmappedpages, then remaining supplied websites; no all-site exhaustion claim')
save('data/checkpoints/source_batch_20261005.json',result)
print(json.dumps(dict(new_families=4,rows=28,views=46,source_coverage=m['coverage']),ensure_ascii=False))
