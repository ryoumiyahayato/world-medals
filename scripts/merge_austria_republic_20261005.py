"""Merge reviewed variants and backs, preserving historical authorities and rights."""
from pathlib import Path
import json,hashlib,collections
from PIL import Image
R=Path(__file__).resolve().parents[1];S='data/staging/austria_republic_20261005/'
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def save(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
records=load(S+'volume_draft.json')['records'];images=load(S+'manifest_draft.json')['images'];backs=load(S+'existing_back_augmentation.json');sources=load('data/sources.json')
for image in images+backs['images']:
    path=R/image['local_path']
    with Image.open(path) as im:im.verify()
    assert image['visually_checked'] and hashlib.sha256(path.read_bytes()).hexdigest()==image['sha256']
    image['publication_eligible']=False
main=[];related=[]
for record in records:
    assert record['review_status']=='draft_normalized_and_visually_checked'
    record.update(body_eligible=True,html_eligible=True,publication_eligible=False)
    sid=record['id']+'-REVIEWED-SOURCE';evidence=record['evidence']
    sources[sid]=dict(page=evidence[0]['source_page'],title=record['name']+'：'+record['variant'],accessed='2026-10-05',summary=' | '.join(e.get('source_excerpt','') for e in evidence),license='No blanket photo republication permission; private research only',credit='World Medals Index')
    if sid not in record['source_ids']:record['source_ids'].append(sid)
    (related if '附编' in record['category'] else main).append(record)
for name,group in [('austria_republic_20261005',main),('austria_republic_related_20261005',related)]:
    ids={r['id'] for r in group};save('data/volumes/'+name+'.json',dict(as_of='2026-10-05',records=group));save('data/volumes/'+name+'_manifest.json',dict(as_of='2026-10-05',images=[i for i in images if i['record_id'] in ids]))
save('data/volumes/austria_republic_20261005_integration.json',dict(volume_rows={
    'austria-republic':[r['id'] for r in main if r['category']!='地方正式纪念授奖'],
    'austria-carinthia':[r['id'] for r in main if r['category']=='地方正式纪念授奖']}))
old_name='data/volumes/austria_republic_medalsorg_fast_2026-09-28';old=load(old_name+'.json');manifest=load(old_name+'_manifest.json');byid={r['id']:r for r in old['records']};keys={i['view_key'] for i in manifest['images']}
for update in backs['record_updates']:
    record=byid[update['record_id']];view=dict(update['add_view'],publication_eligible=False)
    if not any(v['key']==view['key'] for v in record['views']):record['views'].append(view)
for image in backs['images']:
    if image['view_key'] not in keys:manifest['images'].append(image)
for record in old['records']:
    # The old source already explicitly restricted these photographs to local research.
    record['publication_eligible']=False
    if record['id']=='AUT-AUR-001-V01' and record['views']:
        record['held_views']=record['views']
        record['views']=[]
        record['body_eligible']=False
        record['quality_note']='Source image touches/cuts lower badge tip; retained as source evidence, moved to unpictured appendix pending complete replacement.'
save(old_name+'.json',old);save(old_name+'_manifest.json',manifest);save('data/sources.json',sources)
save('data/queues/austria_republic_remaining_20261005.json',dict(as_of='2026-10-05',missing_image_candidates=load(S+'missing_image_candidates.json'),held=load(S+'held_rows_images.json'),old_quality_flags=load(S+'existing_front_quality_flags.json'),un_crossreferences=load(S+'un_crossreferences.json'),next='Resolve issuing authority and existing family aliases; obtain alternative complete/open-license images; normalize UN mission references under UN issuing authority'))
print('Main/appendix variants, new views and existing backs:',len(main),len(related),len(images),len(backs['images']))
