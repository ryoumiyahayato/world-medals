"""Merge visually reviewed variants into the local research catalogue, not APK publication."""
from pathlib import Path
import json,collections,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text('utf-8-sig'))
def save(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft=load('data/staging/austria_variants_20261005/volume_draft.json')
manifest=load('data/staging/austria_variants_20261005/manifest_draft.json')
records=draft['records'];images=manifest['images'];sources=load('data/sources.json')
specs=[
('9575620313365','AUT-FAM-AH-009','军事功绩奖章（Signum Laudis）','Militär-Verdienstmedaille','弗朗茨·约瑟夫一世时期；具体实物年代待考','银级；红色绶带；材质按来源描述',[1,2],'austro-hungary'),
('8521757819157','AUT-FAM-AH-009','军事功绩奖章（Signum Laudis）','Militär-Verdienstmedaille','1890–1917年版','铜级镀金；弗朗茨·约瑟夫一世头像；材质按来源描述',[4,5],'austro-hungary'),
('9515819434261','AUT-FAM-MERIT-CROSS-1850','功绩十字章','Verdienstkreuz','1850年2月16日设立；来源称本件为1875–1914年版','金级、无冠；补配绶带；来源制造商描述冲突，待考',[2,3],'austrian-empire'),
('9490202919189','AUT-FAM-MERIT-CROSS-1850','功绩十字章','Verdienstkreuz','1850年2月16日设立；本件约1880年（来源估年）','金级、有冠；来源称18K金及珐琅；补配绶带',[2,1],'austrian-empire'),
('9486246936853','AUT-FAM-RED-CROSS-HONOUR-1914','红十字荣誉章','Ehrenzeichen vom Roten Kreuz','1914年8月14日设立；本件制作年代待考','二级十字章、战争装饰；来源称银质及珐琅',[1,2],'austro-hungary'),
('8522061873429','AUT-FAM-ARMY-CROSS-1813-14','1813—1814年军队十字章','Armeekreuz für 1813/14','1814年5月13日设立','炮铜十字章；来源称铜质镀金；具体实物年代待考',[2,3],'austrian-empire')]
research=load('data/staging/emedals_austria_imperial_20261005/review_candidates.json');research={x['object_id']:x for x in research}
integration=collections.defaultdict(list)
for r in records:
    # Every row was inspected against caption and page context. No blanket publication rights assumed.
    r.update(html_eligible=True,body_eligible=True,publication_eligible=False,review_status='local_research_visual_review_complete')
    sid=r['id']+'-REVIEWED-SOURCE'
    evidence=r.get('evidence',[])
    if evidence:
        sources[sid]=dict(page=evidence[0]['source_page'],title=r['name']+'：'+r['variant'],summary=' | '.join(e.get('source_excerpt','') for e in evidence),accessed='2026-10-05',license='No blanket publication license; local research reference only',credit='World Medals Index')
        if sid not in r['source_ids']:r['source_ids'].append(sid)
    anchor={'奥地利帝国':'austrian-empire','奥匈帝国':'austro-hungary'}.get(r['country_zh'],'austria-habsburg')
    if anchor=='austria-habsburg':anchor='habsburg-monarchy'
    integration[anchor].append(r['id'])
for oid,fid,name,original,date,variant,ordinals,anchor in specs:
    x=research[oid];rid='AUT-EM-'+oid;sid=rid+'-SOURCE';views=[]
    for n,ordinal in enumerate(ordinals):
        im=x['images'][ordinal-1];vk=rid+'-VIEW'+str(n+1)
        with Image.open(R/im['local_path']) as pic:pic.verify()
        views.append(dict(key=vk,label='完整正面' if n==0 else '完整背面（同一拍品）'))
        images.append(dict(im,key=vk.lower(),record_id=rid,view_key=vk,source_page=x['object_page'],artist='eMedals',license='Copyright eMedals; no redistribution permission established; local research reference only',visually_checked=True,publication_eligible=False))
    r=dict(id=rid,family=fid,country_zh='奥匈帝国' if anchor=='austro-hungary' else '奥地利帝国',name=name,original=original,date=date,variant=variant,views=views,source_ids=[sid],html_eligible=True,body_eligible=True,local_offline=True,publication_eligible=False,evidence=[dict(source_page=x['object_page'],accessed_at='2026-10-05',source_excerpt=x['description'],object_id=oid)],rights_note='仅本地研究参考；未取得再发布许可')
    records.append(r);integration[anchor].append(rid)
    sources[sid]=dict(page=x['object_page'],title=x['page_title'],accessed='2026-10-05',summary=x['description'],license='Copyright eMedals; no redistribution permission established',credit='eMedals',object_id=oid)
for im in images:
    im['publication_eligible']=False
    im['visually_checked']=True
    p=R/im['local_path']
    with Image.open(p) as pic:pic.verify()
    if hashlib.sha256(p.read_bytes()).hexdigest()!=im['sha256']:raise ValueError('Image checksum mismatch')
french=load('data/normalized_drafts/france_official_20261005/records.json')['records']
for r in french:
    r.update(country_zh='法国王国',publication_eligible=True,html_eligible=True,body_eligible=True)
    if r['family']=='FRA-ORDER-HOLY-SPIRIT':r['date']='本件1740—1760年制作（卢浮宫断代）'
    else:r['supersedes_id']='FRA-SAMLHOC-ORDRE_SAINT_LOUIS-TEXT-20260929'
    records.append(r);integration['france-kingdom'].append(r['id'])
for im in load('data/normalized_drafts/france_official_20261005/manifest.json')['items']:
    p=R/im['local_path']
    with Image.open(p) as pic:pic.verify()
    if hashlib.sha256(p.read_bytes()).hexdigest()!=im['sha256']:raise ValueError('French image mismatch')
    images.append(dict(im,key=im['view_key'].lower(),image_url=im['source_url'],decoded=True,visually_checked=True,publication_eligible=True))
sources.update(load('data/normalized_drafts/france_official_20261005/sources.json'))
save('data/volumes/source_batch_20261005.json',dict(as_of='2026-10-05',records=records))
save('data/volumes/source_batch_20261005_manifest.json',dict(as_of='2026-10-05',images=images))
save('data/volumes/source_batch_20261005_integration.json',dict(volume_rows=dict(integration)))
save('data/sources.json',sources)
print('Rows',len(records),'families',len({r['family'] for r in records}),'views',len(images));print(dict((k,len(v)) for k,v in integration.items()))
