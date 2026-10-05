import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
S=R/'data/staging/france_identify_20260930'
p=R/'data/raw_candidates/france_identify_20260930.jsonl'
rows=[json.loads(x) for x in p.read_text('utf-8').splitlines() if x]
u='https://www.identifymedals.com/database/medals-by-period/post-ww2-medals/the-medal-for-voluntary-military-service/'
if not any(x['object_page']==u for x in rows):
 rows.append(dict(source_id='FR-IDENTIFY-VOLUNTARY-MILITARY',page_title='The Medal for Voluntary Military Service',original_name='Médaille des services militaires volontaires',date_candidates=['1975-03-13'],category='post-ww2',grade_material_clues='Three grades; blue/red ribbon with white edges for silver; rosette for gold.',object_page=u,cache_path=None,source_text='The Medal for voluntary military service (Médaille des services militaires volontaires) was established on 13 March 1975 by decree 75-150 for voluntary service in the reserves. Three grades. Obverse: Republic with Phrygian cap; reverse: sword, anchors, wings and SERVICES MILITAIRES VOLONTAIRES. Silver grade has white ribbon edges; gold adds a rosette.',hero_image=None,content_images=[dict(url='https://www.identifymedals.com/wp-content/uploads/2018/12/medals_french_postWW2__Medal-for-Voluntary-Military-Services.jpg',alt='The Medal for Voluntary Military Service',srcset='')],links=[],status='read_via_web_reader',accessed='2026-09-30',read_note='HTML download failed twice; full object page inspected via web reader, image link 32. Concise factual summary retained.'))
 p.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n','utf-8')
d=json.loads((S/'discovery.json').read_text('utf-8'));d.update(read=len(rows),remaining=[],read_via_web_reader=1,html_cache_unavailable=[u]);(S/'discovery.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
m=S/'image_manifest.json';images=json.loads(m.read_text('utf-8'));failed=[x for x in images if x['status']=='failed'];(S/'image_failures_first_attempt.json').write_text(json.dumps(failed,ensure_ascii=False,indent=2),'utf-8')
m.write_text(json.dumps([x for x in images if x['status']!='failed'],ensure_ascii=False,indent=2),'utf-8')
print('raw',len(rows),'bounded image retries',len(failed))
