import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text('utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
stats=read('data/normalized/user_soviet_20261003.json')
checkpoint=dict(as_of='2026-10-03',scope='User restored USSR references cross-checked with Mondvor',version='0.010 (dev)',status='local integration complete; detailed historical subtypes remain partial',source_sets=dict(planned=2,completed=2,partial=0,not_started=0,boundary='All 266 files in the supplied Soviet subfolder; existing Mondvor directory crosswalk and selected object pages. Other subfolders not included.'),raw_candidates=266,merged_families=stats['matched_families'],new_independent_families=0,new_body_families_from_previously_unpictured=1,reference_variant_rows=stats['reference_variant_rows'],accepted_processed_images=stats['accepted_reference_images'],source_photographs_added=0,duplicate_files=stats['duplicate_files'],unresolved_files=stats['held_files'],evidence='data/staging/user_soviet_20261003/review.json',outputs=['index.html','data/volumes/user_soviet_20261003.json','mobile/build/world-medals-0.010.apk'],limitations=['User processed references are not source photographs. Material, authenticity and same-specimen front/reverse pairing are not established.','Rows describe visible grade and design; they are not 131 newly proven manufacturing subtypes.','Original Mondvor photo reuse rights remain unresolved; no site photo archive was published.'],next_actions=['Review 23 held files using original object provenance.','Continue the existing 88 order-classification candidate queue without duplicating families.','Find source photographs for remaining missing historical variants.'])
write('data/checkpoints/user_soviet_20261003_v010.json',checkpoint)
review=read('data/staging/user_soviet_20261003/review.json')
write('data/queues/user_soviet_20261003_pending.json',dict(as_of='2026-10-03',items=[x for x in review['items'] if x['status']=='held_for_verification']))
p='data/source_atlas/mondvor_soviet_source_matrix.json';matrix=read(p);matrix['as_of']='2026-10-03';matrix['user_processed_reference_batch']=checkpoint;write(p,matrix)
p='data/source_atlas/global_source_atlas.json';atlas=read(p);atlas['as_of']='2026-10-03';atlas['latest_soviet_reference_checkpoint']='data/checkpoints/user_soviet_20261003_v010.json';write(p,atlas)
# Keep original-photo gaps: a processed reference does not establish original-photo availability.
gaps=read('data/unpictured.json')
for g in gaps:
 if g.get('family')=='USSR-TITLE-HONOURED-TEST-NAVIGATOR':
  g['processed_reference_available']=True;g['processed_reference_record']='USSR-TITLE-HONOURED-TEST-NAVIGATOR-USER-REF-20261003-131'
write('data/unpictured.json',gaps)
print(json.dumps(stats))
