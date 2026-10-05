"""Merge visually checked missing Soviet families; keep original evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text('utf-8-sig'))
def save(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
raw={r['key']:r for r in read('sources/cache/soviet_completion/manifest.json')}
gaps={r['family']:r for r in read('data/normalized/mondvor_soviet_unpictured_gap_merge_2026-09-29.json')['records']}
chosen=[('public-order','USSR-MED-PUBLIC-ORDER-SERVICE','Fdutil','CC BY-SA 3.0; https://creativecommons.org/licenses/by-sa/3.0/','绶带悬挂式；正面实物照片；具体生产版型待考；低清参考',680),
 ('hammer-sickle','USSR-SOCIALIST-LABOUR-HAMMER-SICKLE','Engelberthumperdink','CC BY-SA 4.0; https://creativecommons.org/licenses/by-sa/4.0/','柳博芙·斯米尔诺娃受授实物；正面；具体生产版型待考',2250),
 ('gold-star','USSR-HERO-GOLD-STAR','Aizag（上传及裁取）；源页署名设计者 Ivan Dubasov','Commons marks PD-RU-exempt; retain source attribution','金星奖章；正面实物照片；具体生产版型待考；低清参考',700)]
records=[];images=[];sources=read('data/sources.json')
for key,family,author,rights,variant,effective in chosen:
 r=raw[key];assert r['status']=='decoded_pending_visual_review';g=gaps[family];sid='soviet-completion-'+key;view=sid+'-front'
 records.append(dict(id=family+'-COMPLETE-20260929',family=family,name=g['name'],original=g['original'],date=g['date']+'设立',variant=variant,views=[dict(key=view,label='完整正面')],source_ids=[sid]))
 images.append(dict(view_key=view,local_path=r['local_path'],source_page=r['source_page'],original_url=r['image_url'],artist=author,license=rights,width=r['width'],height=r['height'],sha256=r['sha256'],accessed=r['accessed'],image_kind='physical_photo',object_effective_long_edge_px_approx=effective,visual_review='Root viewed each decoded original; full front, suspension and outline present. No reverse paired.'))
 sources[sid]=dict(page=r['source_page'],summary=g['evidence_excerpt'],fact_page=g['object_page_url'],accessed='2026-09-29',license=rights,credit=author)
r=raw['lenin-type2'];sid='soviet-completion-lenin-type2';view=sid+'-front'
records.append(dict(id='USSR-ORD-01-TYPE-II-COMPLETE-20260929',family='USSR-ORD-01',name='列宁勋章',original='Орден Ленина',date='1934—1936年型式',variant='第2型（来源分类）；完整正面；具体制造批次待考；低清参考',views=[dict(key=view,label='完整正面')],source_ids=[sid]))
images.append(dict(view_key=view,local_path=r['local_path'],source_page=r['source_page'],original_url=r['image_url'],artist='Ilich',license='Public domain, released by author (PD-self)',width=r['width'],height=r['height'],sha256=r['sha256'],accessed=r['accessed'],image_kind='physical_photo',object_effective_long_edge_px_approx=800,visual_review='Root viewed original: complete front outline; no reverse supplied. Source identifies Type II; no independent authenticity guarantee.'))
sources[sid]=dict(page=r['source_page'],summary='Commons object description: Order of Lenin II type; own work by Ilich, released into public domain. Date range is the historical type period, not a production or award date for this object.',fact_page='https://mondvor.narod.ru/OLenin.html',accessed='2026-09-29',license='PD-self',credit='Ilich')
save('data/volumes/soviet_completion_20260929.json',dict(records=records))
save('data/volumes/soviet_completion_20260929_manifest.json',dict(images=images))
save('data/sources.json',sources)
print('3 existing unpictured families now pictured; 1 Lenin type added. 4 reviewed complete front views.')

