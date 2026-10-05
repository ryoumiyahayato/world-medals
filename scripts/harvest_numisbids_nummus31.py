"""Isolated complete Austria category sweep. No unidentified images promoted."""
import json,re,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
existing=[]
for f in (ROOT/'data/volumes').glob('*austr*json'):
 if 'manifest' not in f.name:existing+=json.loads(f.read_text(encoding='utf-8-sig')).get('records',[])
terms=[('Military Order of Maria Theresia','Militär-Maria-Theresien-Orden'),('Order of St.Stephan','Sankt-Stephans'),('Order of Leopold','Leopold-Orden'),('Order of the Iron Crown','Orden der Eisernen Krone'),('Order of Franz Joseph','Franz-Joseph-Orden'),('Military Merit Cross','Militär-Verdienstkreuz'),('Braver Medal','Tapferkeitsmedaille'),('War Medal 1873','Kriegsmedaille 1873'),('Tirol Defence Commemorative','Erinnerungsmedaille für die Tiroler Verteidiger')]
rows=[];draft=[]
for f in sorted((ROOT/'sources/pages').glob('numisbids_nummus31_austria_lots_*_20261005.json')):
 for b in json.loads(f.read_text(encoding='utf8')).split('-'*80):
  u=re.search(r'https://www.numisbids.com/sale/10985/lot/(\d+)',b)
  if not u:continue
  lot=int(u.group(1));plain=re.sub(r'L\d+: *','',b)
  after=plain.split('Save a note here',1)
  text=after[1].split('Question about this auction?',1)[0].strip() if len(after)>1 else ''
  lines=[x.strip() for x in text.splitlines() if x.strip()];name=lines[0] if lines else b.split(' : ',1)[-1].split('(')[0].strip()
  material_description=' '.join(lines[1:])
  cat='formal_award_candidate'
  if lot in (11,18):cat='case_only_non_award'
  elif lot in (20,28,31,33):cat='related_insignia_or_commemorative_pending_scope'
  elif lot==32:cat='mixed_group_pending_individual_identification'
  copy='collector_copy_after1918_circa1950_1960' if lot==3 else None
  matches=[]
  for en,de in terms:
   if en.lower() in name.lower():
    matches=[{'id':r['id'],'family':r.get('family'),'original':r.get('original')} for r in existing if de.lower() in r.get('original','').lower()]
    break
  row={'source_id':'numisbids-nummus31-lot-'+str(lot),'auction_id':'10985','lot_number':lot,'object_page':u.group(0),'auction_date':'2026-09-19','accessed_at':'2026-10-05','original_name':name,'description_original':material_description,'category':cat,'copy_status':copy,'date_candidates':re.findall(r'\b(?:17|18|19)\d{2}(?:[-–/]\d{2,4})?\b',material_description),'date_kind':'source description candidate; institution/manufacture/use distinguished before merge','price_start':(re.search(r'Starting price: ([^\n]+)',plain) or [None,None])[1],'price_realized':(re.search(r'Price realized: ([^\n]+)',plain) or [None,None])[1],'image_urls':[],'status':'description_swept_original_image_unresolved','rights':'Copyright NumisBids LLC; auction photo permission not established','existing_family_matches':matches,'body_eligible':False}
  rows.append(row)
  draft.append({'candidate_id':row['source_id'],'family_name':name,'category':cat,'existing_family_matches':matches,'variant_description':material_description,'copy_status':copy,'merge_action':'hold_for_full_image_identification','body_eligible':False})
rows.sort(key=lambda r:r['lot_number']);draft.sort(key=lambda r:int(r['candidate_id'].rsplit('-',1)[-1]))
assert [r['lot_number'] for r in rows]==list(range(1,35)),[r['lot_number'] for r in rows]
assert all(r['description_original'] for r in rows),'Missing object description'
(ROOT/'data/raw_candidates/numisbids_nummus31_austria_20261005.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf8')
(ROOT/'data/normalized_drafts/numisbids_nummus31_austria_20261005.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding='utf8')
counts={c:sum(r['category']==c for r in rows) for c in sorted({r['category'] for r in rows})}
check={'source':'NumisBids V.L.Nummus OnlineAuction31 Austria category343144','category_url':'https://www.numisbids.com/sale/10985/category/343144?so=2','accessed_at':'2026-10-05','status':'description_sweep_complete_image_stage_partial','category_pages':1,'category_lots_expected':34,'object_pages_opened':34,'raw_candidates':len(rows),'categories':counts,'copy_lots':1,'complete_original_images':0,'body_new_family':0,'body_new_variants':0,'direct_source_access':'HTTP403; public web text reader accessed all34 pages','original_auction':'https://numis24.com/auctions/view/6a63216f4326cd11f603cb94','next':'Resolve full photos from public auction gallery and permission, then verify exact degree, war decoration, swords, manufacturer, replicas. Do not count case-only lots or collector copy as original historical award.'}
(ROOT/'data/source_sweeps/numisbids_nummus31_austria_20261005.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(check,ensure_ascii=False))
