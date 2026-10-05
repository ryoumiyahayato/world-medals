"""Build isolated OneBid auction-27 evidence; never promote cart thumbnails."""
import json,re,pathlib,hashlib,time,requests
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/'sources/pages'/n).read_text(encoding='utf8'))
details=read('onebid_auction3987681_web_evidence_20261005.json')
prices=read('onebid_auction3987681_prices_20261005.json')
links=read('onebid_auction3987681_binary_links_20261005.json')
blocks=details.split('-'*80); pb=prices.split('-'*80); lb=links.split('-'*80)
for start in (10,15):
 extra=read('onebid_auction3987681_details_'+str(start)+'_20261005.json').split('-'*80)
 blocks[start:start+5]=extra
existing=[]
for f in (ROOT/'data/volumes').glob('*.json'):
 if 'manifest' in f.name:continue
 try:
  d=json.loads(f.read_text(encoding='utf-8-sig'))
  for r in d.get('records',[]):existing.append(r)
 except (ValueError,AttributeError):pass
families={0:('Great War Commemorative Medal','Kriegserinnerungsmedaille'),2:('Jubilee Medal 1898','Signum Memoriae','Jubiläums-Erinnerungsmedaille'),3:('Medal of Bravery','Tapferkeitsmedaille'),9:('Mobilisation Cross','Mobilisierungskreuz','Mobilisierungs-Erinnerungskreuz'),10:('Medal of Bravery','Tapferkeitsmedaille'),11:('Military Merit Medal','Signum Laudis'),13:('War Medal 1873','Kriegsmedaille')}
rows=[];draft=[]
for i,b in enumerate(blocks):
 if not b.strip():continue
 url=re.search(r'\((https://one\.bid/[^)]+)\)',b).group(1); oid=url.rsplit('/',1)[1]
 title=b.split(' - Online auction')[0].strip(); plain=re.sub(r'L\d+:\s*','',b)
 description=plain.split('Lot description',1)[-1].split('Labels ^',1)[0].strip() if 'Lot description' in plain else ''
 lot=re.search(r'L201: (\d{4})',b)
 pp=re.sub(r'L\d+:\s*','',pb[i]) if i<len(pb) else ''
 price=re.search(r'Hammer price\s*\n\s*(\d+[\d ,.]* EUR|no offers)',plain+'\n'+pp)
 if i in families:category='formal_award_candidate'
 elif i in [7,12]:category='mixed_decoration_group_pending_identification'
 elif i in [6,14,18,19]:category='non_award_militaria_or_photography'
 else:category='related_badge_or_commemorative_annex'
 matches=[]
 if i in families:
  for rr in existing:
   text=(rr.get('original','')+' '+rr.get('name','')).lower()
   if str(rr.get('id','')).startswith('AUT-') and not str(rr.get('id','')).startswith('AUT-AUR-') and any(term.lower() in text for term in families[i]):matches.append({'id':rr['id'],'family':rr.get('family'),'original':rr.get('original')})
 image_url=None
 if i<len(lb):
  m=re.search(r'https://img1\.one\.bid/[^\s)]+',lb[i]);image_url=m.group(0) if m else None
 row={'source_id':'onebid-rda27-ah-'+oid,'object_id':oid,'lot_number':lot.group(1) if lot else None,'auction_id':'3987681','auction_house':'Rzeszowski Dom Aukcyjny','accessed_at':'2026-10-05','page_title':title,'original_name':title,'description':description,'date_candidates':re.findall(r'\b(?:18|19)\d{2}(?:[-–]\d{2,4})?\b',title),'date_kind':'title inscription/period candidates; not established institution dates','category':category,'object_page':url,'image_page':url,'image_url':image_url,'image_kind':'cart_thumbnail_only' if image_url else 'not_resolved','original_image_url':None,'rights':'OneBid all rights reserved; publication permission not established','status':'pending_original_image_and_variant_identification','hammer_price_display':price.group(1) if price else None,'price_scope':'Displayed EUR conversion; excludes premium; auction date is not award date','existing_family_matches':matches}
 rows.append(row)
 if i in families:draft.append({'candidate_id':row['source_id'],'family_terms':families[i],'existing_family_matches':matches,'merge_action':'link_existing_family_if_confirmed' if matches else 'needs_family_crosswalk','variant_action':'do not create variant until grade and full object view verified','body_eligible':False})
out=ROOT/'data/raw_candidates/onebid_rda27_austrohungary_20261005.jsonl';out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf8')
(ROOT/'data/normalized_drafts/onebid_rda27_austrohungary_20261005.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding='utf8')
checkpoint={'source':'OneBid RDA auction27 category9246','accessed_at':'2026-10-05','category_url':'https://one.bid/en/auction/3987681/9246/Orders-Decorations-Badges-Militaria-Austro-Hungary','expected_lots':20,'object_pages_opened':len(rows),'category_pages':1,'raw_candidates':len(rows),'formal_award_lots':sum(r['category']=='formal_award_candidate' for r in rows),'mixed_groups':2,'related_annex_lots':7,'non_award_lots':4,'new_body_families':0,'new_body_variants':0,'complete_original_images_downloaded':0,'boundary':'All20 listed object pages opened. Browser-readable descriptions cached. Direct object-page HTTP403; web-parser cart thumbnail tested HTTP200, decodable300x300, not treated as full original. Image/variant stage partial.','next':'Resolve original gallery files through permitted public source, then visually verify grade and match existing families; alternatively open-licensed full views.'}
(ROOT/'data/source_sweeps/onebid_rda27_austrohungary_20261005.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(checkpoint,ensure_ascii=False));print([(r['page_title'],len(r['existing_family_matches'])) for r in rows if r['category']=='formal_award_candidate'])

