"""Merge reviewed French source summaries and photos; unpictured awards stay in appendices."""
from pathlib import Path
from collections import defaultdict
import json,re,hashlib
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text('utf-8-sig'))
def save(p,j):(R/p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
items=[]
for f in ['orders.json','decorations.json','medals.json']:
 j=read('data/staging/france_completion/'+f);items.extend(j['items'])
assert len({x['slug'] for x in items})==len(items)
html=BeautifulSoup((R/'index.html').read_text('utf-8'),'html.parser')
active={tr['id']:tr.find_parent('section')['id'] for tr in html.select('section tr[id]')}
existing=defaultdict(list)
for p in (R/'data/volumes').glob('*.json'):
 if 'france_completion_20260929' in p.name:continue
 try:j=json.loads(p.read_text('utf-8-sig'))
 except (ValueError,UnicodeError):continue
 if isinstance(j,dict) and isinstance(j.get('records'),list):
  for rec in j.get('records',[]):
   if rec.get('id') in active:existing[rec.get('family',rec['id'])].append(rec)
photos=read('data/staging/france_completion/reviewed_images.json');byphoto=defaultdict(list)
for p in photos:byphoto[p['slug']].append(p)
sources=read('data/sources.json');intros=read('mobile/web/award-intros.json');intro_map={x['award_id']:x for x in intros['items']}
groups=defaultdict(list);slugmap={};sourceids={}
for x in items:
 family=x.get('family_match') or 'FRA-SAMLHOC-'+x['slug'].upper().replace('-','_')
 assert isinstance(family,str),(x['slug'],family)
 x['resolved_family']=family;groups[family].append(x);slugmap[x['slug']]=family
 ids=[]
 for n,s in enumerate(x['sources']):
  sid=s.get('source_id') or 'FR-SAMLHOC-COMPLETE-'+x['slug']+'-'+str(n)
  ids.append(sid);sources[sid]=dict(page=s['url'],summary=s.get('evidence_summary_zh',''),accessed='2026-09-29',title=s['title'])
 sourceids[x['slug']]=ids
def grouping(x):
 slug=x['slug'];issuer=x.get('issuer','')
 if 'indochine' in slug or 'indochinois' in slug:
  if slug.startswith('medaille_commemorative') or slug=='medaille_merite_travailleurs_indochinois':pass
  else:return ('indochina','法属印度支那·地方奖励体系','亚洲','东南亚','法属印度支那')
 special={'ordre_cambodge':('cambodia','柬埔寨王国·法国保护国时期','亚洲','东南亚','柬埔寨'), 'ordre_dragon_annam':('annam','安南帝国·法国保护国时期','亚洲','东南亚','越南'), 'ordre_couronne_fer':('italy','拿破仑时期意大利王国','欧洲','南欧','意大利'),'ordre_merite_cameroun':('cameroon','法属喀麦隆','非洲','中非','喀麦隆'),'ordre_tahiti_nui':('polynesia','法属波利尼西亚','大洋洲','波利尼西亚','法属波利尼西亚'),'ordre_etoile_anjouan':('anjouan','昂儒昂·法国殖民授奖体系','非洲','东非','科摩罗'),'ordre_nichan_el-anouar':('tadjoura','塔朱拉·法国殖民授奖体系','非洲','东非','吉布提'),'ordre_etoile_noire':('dahomey','达荷美·法国殖民授奖体系','非洲','西非','贝宁')}
 if slug in special:return special[slug]
 if 'madagascar_dependances' in slug or slug=='medaille_honneur_ptt_outre-mer':return ('madagascar','法属马达加斯加及属地','非洲','东非','马达加斯加')
 if 'contributions_diverses_algerie' in slug:return ('algeria','法属阿尔及利亚·地方奖励','非洲','北非','阿尔及利亚')
 if 'forces_publiques_inde' in slug:return ('india','法属印度·公共部队奖励','亚洲','南亚','印度')
 if 'mines_sarre' in slug:return ('saar','萨尔·法国管理时期矿业奖励','欧洲','西欧','德国')
 related=slug=='decorations_juillet' or any(w in x.get('category','') for w in ['非法国国家','纪念徽章','专题','政治性','展览'])
 return ('related','法国·相关历史佩饰与专题','欧洲','西欧','法国') if related else ('national','法国·勋奖章制度沿革','欧洲','西欧','法国')
records=[];manifest=[];specs={};routes={};registered=[]
for family,family_items in groups.items():
 first=family_items[0];g=grouping(first);anchor='france-source-'+g[0];title=g[1]
 family_photos=[(x,p) for x in family_items for p in byphoto[x['slug']]]
 if family not in existing or family_photos:
  specs[anchor]=dict(slug=anchor.replace('-','_'),title=title,anchor=anchor,aliases=title+' France '+first.get('issuer',''),country_group='france' if g[0] in ['national','related'] else g[0],record_files=['france_completion_20260929.json'],manifest_files=['france_completion_20260929_manifest.json'],awarding_authorities=[title])
  routes[anchor]=list(g[2:])
 if family_photos:
  for n,(x,p) in enumerate(family_photos):
   rid=family+'-COMPLETE-20260929-'+str(n+1);view=rid+'-VIEW';sid=rid+'-PHOTO'
   sources[sid]=dict(page=p['source_page'],summary=p['object_description'],accessed=p['accessed'],license=p['license'],credit=p['artist'])
   records.append(dict(id=rid,family=family,name=x['name_zh'],original=x['original'],date=x['date']+'（制度日期）',variant=p['variant'],awarding_authority=title,views=[dict(key=view,label=p['label'])],source_ids=sourceids[x['slug']]+[sid]))
   manifest.append(dict(p,view_key=view))
 elif family not in existing:
  records.append(dict(id=family+'-TEXT-20260929',family=family,name=first['name_zh'],original=first['original'],date=first['date'],variant='有记载未配图',awarding_authority=title,views=[],source_ids=list(dict.fromkeys(s for x in family_items for s in sourceids[x['slug']]))))
  registered.append(family)
 names={x['name_zh'] for x in family_items}|{r['name'] for r in existing.get(family,[])}
 volumes={active[r['id']] for r in existing.get(family,[])}|{anchor}
 paragraphs=[];refs={};forms=[]
 for x in family_items:
  text=x['introduction_zh'];paragraphs.extend(text if isinstance(text,list) else [text])
  for s in x['sources']:refs[s['url']]=s
  for v in x.get('variants',[]):
   if isinstance(v,str):forms.append(dict(period='等级／型式',form=v))
   else:forms.append(dict(period=v.get('period') or v.get('label') or ('等级' if v.get('name_zh') else '时期待考'),form='：'.join(filter(None,[v.get('label') or v.get('name_zh'),v.get('description') or v.get('form') or v.get('description_zh')]))))
 entry=dict(award_id=family,canonical_name_zh=first['name_zh'],family_ids=[family],match_names=sorted(names),volume_pattern='^(?:'+'|'.join(re.escape(v) for v in sorted(volumes))+')(?:-unpictured)?$',introduction_zh=list(dict.fromkeys(paragraphs)),sources=list(refs.values()),variant_guidance=dict(period_forms=[f for f in forms if f['form']]))
 if family=='FRA-LEGION-HONOUR' and family in intro_map:
  old=intro_map[family];old['match_names']=sorted(set(old['match_names'])|names|{'荣誉军团勋章'});old['family_ids']=[family,'france-legion-of-honour'];old['sources']=list({s['url']:s for s in old['sources']+entry['sources']}.values())
 else:intro_map[family]=entry
intros['items']=list(intro_map.values());intros['as_of']='2026-09-29'
save('mobile/web/award-intros.json',intros);save('data/sources.json',sources)
save('data/volumes/france_completion_20260929.json',dict(records=records));save('data/volumes/france_completion_20260929_manifest.json',dict(images=manifest));save('data/volumes/france_completion_20260929_specs.json',list(specs.values()))
crosswalk=dict(source_groups=len(items),resolved_families=len(groups),existing_families=sum(f in existing for f in groups),new_pictured_families=len({r['family'] for r in records if r['views']} - set(existing)),new_unpictured_family_or_topic_records=len(registered),new_variant_rows=sum(bool(r['views']) for r in records),new_original_images=len({p['original_path'] for p in photos}),reviewed_display_images=len(photos),slug_to_family=slugmap,registered_unpictured=registered)
save('data/normalized/france_completion_20260929.json',crosswalk)
p=R/'mobile/web/hierarchy.js';text=p.read_text('utf-8');text=re.sub(r'\n/\* FRANCE_COMPLETION_START \*/.*?/\* FRANCE_COMPLETION_END \*/\n?','\n',text,flags=re.S)
text+='\n/* FRANCE_COMPLETION_START */\n'+''.join('window.CATEGORY_ROUTES['+json.dumps(k)+']='+json.dumps(v,ensure_ascii=False)+';\n' for k,v in routes.items())+'/* FRANCE_COMPLETION_END */\n';p.write_text(text,'utf-8')
print(json.dumps({k:v for k,v in crosswalk.items() if k not in ['slug_to_family','registered_unpictured']},ensure_ascii=False))
