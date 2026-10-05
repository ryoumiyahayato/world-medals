from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1]
def save(p,x): (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'data/source_atlas/user_supplied_europe_global_20261005_source_matrix.json';matrix=json.loads(p.read_text(encoding='utf-8'))
for s in matrix['sources']:
    if s['source_name']=='london_medal_company':
        s.update(status='partial',last_checked='2026-10-05',coverage_boundary='British Miscellaneous page1: 28 listings, 10 readable object pages; page2 and 17 objects timed out; one object 404. Full British/World categories remain queued.')
    if s['source_name']=='spink':
        s.update(status='partial',last_checked='2026-10-05',coverage_boundary='Auction 26001: all 19 list pages and 375 object pages cached; image download/review and family normalization ongoing. Not entire Spink archive.')
counts=dict(planned=len(matrix['sources']),completed=0,partial=0,blocked=0,not_started=0)
for s in matrix['sources']:
    status=s['status'];k='partial' if status.startswith('partial') else status
    if k in counts:counts[k]+=1
matrix['coverage_summary']=counts;save(p.relative_to(R),matrix)
apk=R/'mobile/build/world-medals-0.018.apk'
with zipfile.ZipFile(apk) as z:
    assert z.testzip() is None
    for f in ('index.html','catalog.json','hierarchy.js','version.js'):
        q=R/'mobile/build/site'/f
        if q.exists():assert z.read('assets/site/'+f)==q.read_bytes(),f
save('data/checkpoints/source_stage_20261005_v018.json',dict(as_of='2026-10-05',status='built_verified_pending_github_release',apk_version='0.018',apk_sha256=hashlib.sha256(apk.read_bytes()).hexdigest(),new_pictured_formal_families=2,new_formal_variant_rows=6,accepted_complete_views=12,unpictured_variant_candidates=3,raw_target_objects=23,decoded_source_images=30,source_scope_counts=counts,validation=['APK v2/v3 signature','CRC','Exact packaged index/catalog/hierarchy/version comparison','Search and reader navigation regressions','Publication policy','Browser rendering with complete front/reverse'],known_limits='206 restricted research records retain facts but exclude photographs from APK; new photographs available in private local index.html. No native phone installation test.',next='Merge Spink 26001 image-reviewed families; continue cached Malta/Teutonic issuer leads; complete remaining source queues.'))
print(counts)
