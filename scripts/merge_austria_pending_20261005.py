"""Integrate reviewed public-source photos into private offline research only."""
from pathlib import Path
import json,hashlib,collections
from PIL import Image
R=Path(__file__).resolve().parents[1]
def load(path):return json.loads((R/path).read_text(encoding='utf-8-sig'))
def save(path,data):(R/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft=load('data/staging/austria_pending_20261005/volume_draft.json')['records']
images=load('data/staging/austria_pending_20261005/manifest_draft.json')['images']
sources=load('data/sources.json');groups=collections.defaultdict(list);main=[];related=[]
for image in images:
    p=R/image['local_path']
    with Image.open(p) as im:im.verify()
    assert image['visually_checked'] and hashlib.sha256(p.read_bytes()).hexdigest()==image['sha256']
    image['publication_eligible']=False
for record in draft:
    assert record['review_status']=='front_and_reverse_visual_review_complete'
    record.update(html_eligible=True,body_eligible=True,publication_eligible=False)
    sid=record['id']+'-REVIEWED-SOURCE'
    evidence=record['evidence']
    sources[sid]=dict(page=evidence[0]['source_page'],title=record['name']+'：'+record['variant'],accessed='2026-10-05',summary=' | '.join(e.get('source_excerpt','') for e in evidence),license='No blanket publication permission; private offline research only',credit='World Medals Index')
    record['source_ids'].append(sid)
    if '附编' in record['category']:
        related.append(record);continue
    main.append(record)
    anchor={'哈布斯堡王朝':'habsburg-monarchy','奥地利帝国':'austrian-empire','奥匈帝国':'austro-hungary','奥地利帝国／奥匈帝国':'austrian-empire','匈牙利王国／哈布斯堡君主国':'habsburg-monarchy'}.get(record['country_zh'])
    if not anchor:raise ValueError('Unmapped historical authority: '+record['country_zh'])
    groups[anchor].append(record['id'])
for name,records in [('austria_pending_20261005',main),('austria_pending_related_20261005',related)]:
    ids={r['id'] for r in records}
    save('data/volumes/'+name+'.json',dict(as_of='2026-10-05',records=records))
    save('data/volumes/'+name+'_manifest.json',dict(as_of='2026-10-05',images=[i for i in images if i['record_id'] in ids]))
save('data/volumes/austria_pending_20261005_integration.json',dict(volume_rows=dict(groups)))
save('data/sources.json',sources)
print('Integrated main/appendix rows and complete views:',len(main),len(related),len(images))
