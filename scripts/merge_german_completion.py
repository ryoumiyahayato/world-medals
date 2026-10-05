"""Integrate reviewed German source facts and verified local image views."""
from pathlib import Path
from collections import defaultdict
from PIL import Image
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text('utf-8'))
def save(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
families=load('data/staging/german_completion/families_final.json');views=load('data/staging/german_completion/views_final.json')
existing={x.get('family',x['id']):x for x in load('data/staging/german_completion/existing_active_records.json')}
sources=load('data/sources.json');intro=load('mobile/web/award-intros.json');entries={x['award_id']:x for x in intro['items']}
records=[];related_records=[];manifest=[];specs={};routes={};photo_groups=defaultdict(list)
for v in views:photo_groups[v['family']].append(v)
for f in families:
 fid=f['family'];is_related=bool(f.get('is_related'));anchor='germany-related' if is_related else f['anchor'];title=f['volume_title'];source_ids=[];target_records=related_records if is_related else records
 for n,s in enumerate(f['sources']):
  sid='DE-COMPLETE-'+fid+'-FACT-'+str(n+1);sources[sid]=dict(page=s['url'],title=s['title'],summary=s['summary'],accessed='2026-09-29');source_ids.append(sid)
 if not is_related:specs[anchor]=dict(slug=anchor.replace('-','_'),title=title,anchor=anchor,aliases=title+' Deutschland Germany '+f.get('issuer_original',''),country_group='germany',record_files=['german_completion_20260929.json'],manifest_files=['german_completion_20260929_manifest.json'],awarding_authorities=[title])
 routes[anchor]=['欧洲','中欧','德国']
 if photo_groups[fid]:
  for n,v in enumerate(photo_groups[fid]):
   rid=fid+'-COMPLETE-20260929-'+str(n+1);rv=[];sids=list(source_ids)
   for k,im in enumerate(v['images']):
    p=R/im['local_path'];assert p.is_file()
    with Image.open(p) as pic:pic.verify()
    vk=rid+'-VIEW-'+str(k+1);sid=vk+'-SOURCE';rv.append(dict(key=vk,label=im['label']));sids.append(sid)
    sources[sid]=dict(page=im['source_page'],title=im.get('title',f['name_zh']),summary=im['evidence'],accessed='2026-09-29',license=im['license'],credit=im['artist'])
    manifest.append(dict(im,view_key=vk,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   target_records.append(dict(id=rid,family=fid,name=f['name_zh'],original=f['original'],date=v['date'],variant=v['variant'],awarding_authority=title,views=rv,source_ids=sids))
 elif fid not in existing:
  target_records.append(dict(id=fid+'-TEXT-20260929',family=fid,name=f['name_zh'],original=f['original'],date=f['date'],variant='有记载未配图',awarding_authority=title,country_group='germany',views=[],source_ids=source_ids))
 names=list(dict.fromkeys([f['name_zh'],f['original']]+f.get('aliases',[])+([existing[fid]['name']] if fid in existing else [])))
 anchors=[anchor]+([existing[fid]['volume']] if fid in existing else [])
 entries[fid]=dict(award_id=fid,canonical_name_zh=f['name_zh'],family_ids=[fid],match_names=names,volume_pattern='^(?:'+'|'.join(re.escape(a) for a in anchors)+')(?:-unpictured)?$',introduction_zh=f['introduction_zh'] if isinstance(f['introduction_zh'],list) else [f['introduction_zh']],sources=[dict(title=s['title'],url=s['url']) for s in f['sources']],variant_guidance=dict(period_forms=f.get('variant_guidance',[])))
save('data/volumes/german_completion_related_20260929.json',dict(records=related_records));save('data/volumes/german_completion_related_20260929_manifest.json',dict(images=[]))
save('data/sources.json',sources);intro['items']=list(entries.values());save('mobile/web/award-intros.json',intro)
save('data/volumes/german_completion_20260929.json',dict(records=records));save('data/volumes/german_completion_20260929_manifest.json',dict(images=manifest));save('data/volumes/german_completion_20260929_specs.json',list(specs.values()))
p=R/'mobile/web/hierarchy.js';s=p.read_text('utf-8');s=re.sub(r'\n/\* GERMAN_COMPLETION_START \*/.*?/\* GERMAN_COMPLETION_END \*/\n?','\n',s,flags=re.S);s+='\n/* GERMAN_COMPLETION_START */\n'+''.join('window.CATEGORY_ROUTES['+json.dumps(k)+']='+json.dumps(v,ensure_ascii=False)+';\n' for k,v in routes.items())+'/* GERMAN_COMPLETION_END */\n';p.write_text(s,'utf-8')
stats=dict(verified_families=sum(not f.get('is_related') for f in families),related_topics=len(related_records),new_families=len({f['family'] for f in families if not f.get('is_related')}-set(existing)),new_pictured_families=len({fid for fid, rows in photo_groups.items() if rows}-set(existing)),pictured_variant_rows=sum(bool(r['views']) for r in records),unpictured_records=sum(not r['views'] for r in records),display_views=len(manifest),original_files=len({im.get('original_path',im['local_path']) for im in manifest}))
save('data/normalized/german_completion_20260929.json',stats);print(json.dumps(stats))
