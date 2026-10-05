"""Register supplied source scopes without overwriting earlier sweep progress."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sources=[
('medals_world','https://www.medals.org.uk/','specialist','global','en',1),
('omsa','https://www.omsa.org/','specialist','global','en',1),
('emedals','https://www.emedals.com/','market','global','en',1),
('numisbids','https://www.numisbids.com/results','auction_aggregator','global','multilingual',1),
('onebid','https://one.bid/','auction_aggregator','central_europe','multilingual',1),
('uk_mod','https://www.gov.uk/guidance/medals-campaigns-descriptions-and-eligibility','official','uk','en',1),
('uk_archives','https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/british-military-campaign-and-service-medals','archives','uk','en',1),
('noonans','https://www.noonans.co.uk/','auction','uk_global','en',1),
('london_medals','https://london-medals.co.uk/','market','uk_global','en',2),
('legion','https://www.legiondhonneur.fr/fr/les-ordres-nationaux-et-decorations','official','france','fr',1),
('france_phaleristique','https://www.france-phaleristique.com/','specialist','france','fr',1),
('hgm','https://www.hgm.at/sammlungen-forschung/sammlungen','museum','habsburg_successors','de',1),
('darabanth','https://www.darabanth.com/en/','auction','habsburg_successors','en_hu',2),
('spink','https://www.spink.com/','auction','uk_global','en',2)]
items=[]
for sid,url,typ,scope,lang,priority in sources:
 items.append(dict(source_id='user_20261005_'+sid,source_name=sid,base_url=url,source_type=typ,scope=scope,languages=[lang],date_coverage='historical_to_modern; source-specific boundaries pending',has_images=typ!='archives',has_pagination=True,download_method='cached bounded classification/object-page sweep',priority=priority,status='blocked' if sid=='hgm' else 'partial' if sid in ('emedals','medals_world','omsa','onebid','legion') else 'not_started',last_checked='2026-10-05',coverage_boundary='Collection catalogue temporarily unavailable during website rebuild' if sid=='hgm' else 'Registered source; no claim that entire site is exhausted'))
path=R/'data/source_atlas/user_supplied_europe_global_20261005_source_matrix.json'
path.write_text(json.dumps(dict(schema_version='2.0',as_of='2026-10-05',scope_id='user_supplied_europe_global_20261005',sources=items),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
queuepath=R/'data/queues/source_sweep_queue.json';queue=json.loads(queuepath.read_text('utf-8-sig'))
known={x['source_id'] for x in queue['items']}
for x in items:
 if x['source_id'] not in known:queue['items'].append(dict(x,matrix_file=path.relative_to(R).as_posix(),next_action='Exhaust a bounded catalogue/category/auction, then merge families and review image rights and completeness.'))
queue['as_of']='2026-10-05';queuepath.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Registered',len(items),'source entry points; existing queues preserved')
