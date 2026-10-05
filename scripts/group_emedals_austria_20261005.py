"""Provisional family crosswalk; never count market objects as new award families."""
from pathlib import Path
import json,re,collections
R=Path(__file__).resolve().parents[1];s='emedals_austria_imperial_20261005'
rows=[json.loads(l) for l in (R/'data/raw_candidates'/f'{s}.jsonl').read_text('utf-8').splitlines()]
rules=[('AUT-FAM-AH-008',r'franz.?joseph.*order|order.*franz.?joseph'),('AUT-FAM-AE-003',r'iron crown'),('AUT-FAM-AE-004',r'leopold.*order|order.*leopold'),('AUT-FAM-HAB-005',r'maria theresi?a'),('AUT-FAM-AH-009',r'signum laudis|military merit medal'),('AUT-FAM-HAB-031',r'bravery medal'),('AUT-FAM-AH-012',r'military merit cross'),('AUT-FAM-AH-048',r'war cross.*civil merit'),('AUT-FAM-AH-001',r'order.*elisabeth'),('AUT-FAM-AH-018',r'karl.*(?:troop|truppen).*cross'),('AUT-FAM-AH-019',r'wound medal'),('AUT-FAM-AH-050',r'(?:military )?long service.*(?:decoration|cross)|military service decoration')]
groups=collections.defaultdict(list);pending=[];annex=[]
for x in rows:
 title=x['page_title'].lower()
 if x['category'] not in ('Orders','Medals','Decorations'):
  annex.append(dict(object_id=x['object_id'],category=x['category'],title=x['page_title'],status='annex_or_non_award_review'));continue
 if re.search(r'\b(lot|group|pair|two|three|four|five|six|seven|ten|case|ribbon|miniature|chain)\b',title):
  pending.append(dict(object_id=x['object_id'],title=x['page_title'],status='mixed_objects_or_accessories_review'));continue
 match=next((fid for fid,pattern in rules if re.search(pattern,title)),None)
 if match:groups[match].append(dict(object_id=x['object_id'],title=x['page_title'],status='provisional_family_match_variant_review_required'))
 else:pending.append(dict(object_id=x['object_id'],title=x['page_title'],status='unmatched_family_review'))
out=dict(source_id=s,as_of='2026-10-05',raw_candidates=len(rows),existing_family_groups=dict(groups),pending=pending,annex=annex,counts=dict(provisional_existing_families=len(groups),matched_objects=sum(map(len,groups.values())),pending=len(pending),annex=len(annex)),note='Title crosswalk is provisional. Grade, issuer, period, maker, copy status and photos need object-page review before integration.')
p=R/'data/staging'/s;p.mkdir(parents=True,exist_ok=True)
(p/'family_crosswalk.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(out['counts'])
