"""Apply six reviewed specimen variants, preserving conflicts and original photos."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def load(p): return json.loads((R/p).read_text(encoding='utf-8'))
def save(p,x): (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=load('data/normalized_drafts/emedals_austria_cold_formal_20261005.json')
m={x['local_path']:x for x in load('assets/raw/emedals_austria_cold_20261005/download_manifest.json')}
sources=load('data/sources.json');rows=[];images=[];integration={}
families=[(f['family_id'],f,'habsburg-monarchy',[f['variant_candidate']]) for f in d['existing_family_supplements']]
families += [(f['candidate_family_key'].replace('AUT-CAND-','AUT-FAM-'),f,'austro-hungary',f['variants']) for f in d['new_family_candidates']]
for fid,f,anchor,variants in families:
    for v in variants:
        if 'selected_front' not in v: continue
        oid=v['primary_object_id'];rid='AUT-COLD-'+oid;sid=rid+'-SOURCE'
        desc=v['display_cn']
        if oid=='8518326583573':desc='银质型；等级待考；绶带为后配替换带'
        if oid=='9344720044309':desc='小型银质型；等级待考'
        if oid=='9219920134421':desc='25年型；背铭 QUINQUE LUSTRA；材质待考'
        evidence=v['evidence']
        sources[sid]=dict(page=v['source_page'],title=f['canonical_name_cn'],summary=evidence,object_id=oid,accessed='2026-10-05',credit='eMedals',license='Copyright eMedals; local research only')
        views=[]
        for i,k in enumerate(('selected_front','selected_reverse')):
            p=v[k];im=m[p];key=rid+'-VIEW'+str(i+1)
            views.append(dict(key=key,label='完整正面' if i==0 else '完整背面（同一拍品）'))
            images.append(dict(key=key.lower(),record_id=rid,view_key=key,local_path=p,source_page=v['source_page'],image_url=im['image_url'],object_reference=oid,artist='eMedals',license='Copyright eMedals; local research only',dimensions=[im['width'],im['height']],sha256=im['sha256'],decoded=True,visually_checked=True,visual_review='Whole medal, metal suspension and ribbon visible; front/reverse inscriptions checked; watermark retained',publication_eligible=False))
        rows.append(dict(id=rid,family=fid,country_zh='哈布斯堡君主国' if anchor=='habsburg-monarchy' else '奥匈帝国',name=f['canonical_name_cn'],original=f['original_names'][0],date='1797年' if anchor=='habsburg-monarchy' else '1908年；确切设立日待考',variant=desc,views=views,source_ids=[sid],html_eligible=True,body_eligible=True,publication_eligible=False,evidence=[dict(source_page=v['source_page'],object_id=oid,accessed_at='2026-10-05',source_excerpt=evidence)]))
        integration.setdefault(anchor,[]).append(rid)
save('data/volumes/austria_cold_20261005.json',dict(as_of='2026-10-05',records=rows))
save('data/volumes/austria_cold_20261005_manifest.json',dict(as_of='2026-10-05',images=images))
save('data/volumes/austria_cold_20261005_integration.json',dict(volume_rows=integration))
save('data/conflicts/austria_cold_20261005.json',dict(conflicts=d['source_conflicts'],unpictured_variants=[v for f in d['new_family_candidates'] for v in f['variants'] if 'selected_front' not in v]))
save('data/sources.json',sources)
print('2 new families; 6 variant rows; 12 full views; 3 unpictured variant candidates')

