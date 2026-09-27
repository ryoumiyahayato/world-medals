"""Static offline acceptance checks; no browser network or file fetch required."""
import hashlib,json,re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.html').read_text(encoding='utf-8')
css=(ROOT/'assets/site.css').read_text(encoding='utf-8')
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.images=[];self.links=[];self.scripts=[];self.styles=[]
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='img':self.images.append(a.get('src',''))
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='script' and 'src' in a:self.scripts.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a.get('href',''))
p=Page();p.feed(html)
gallery_images=[url for url in p.images if url]
catalogue=json.loads((ROOT/'data/catalogue.json').read_text(encoding='utf-8'))['records']
related=json.loads((ROOT/'data/related.json').read_text(encoding='utf-8'))
volume_records=[]
all_view_paths={}
asset_countries=defaultdict(set)
volume_files={
 'ottoman_extra':(['ottoman_commons_batch1.json','mena_round7_2026-09-26.json','ottoman_medalbook_pack2.json'],['ottoman_commons_batch1_manifest.json','mena_round7_manifest_2026-09-26.json','ottoman_medalbook_pack2_manifest.json'],{'奥斯曼帝国'},{'ottoman_commons_batch1.json','ottoman_medalbook_pack2.json'}),
 'egypt':(['egypt_republic_pack1.json','mena_round7_2026-09-26.json','mena_gap_round1_2026-09-26.json'],['egypt_republic_pack1_manifest.json','mena_round7_manifest_2026-09-26.json','mena_gap_round1_manifest_2026-09-26.json'],{'埃及'},{'egypt_republic_pack1.json'}),
 'sudan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'苏丹'},set()),
 'iran':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'伊朗／波斯'},set()),
 'turkey':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'土耳其共和国'},set()),
 'syria':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'叙利亚'},set()),
 'oman':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿曼'},set()),
 'afghanistan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿富汗'},set()),
 'pakistan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'巴基斯坦'},set()),
 'morocco':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'摩洛哥'},set()),
 'algeria':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿尔及利亚'},set()),
 'azerbaijan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿塞拜疆'},set()),
 'armenia':(['armenia_pack1.json'],['armenia_pack1_manifest.json']),
 'kazakhstan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'哈萨克斯坦'},set()),
 'uzbekistan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'乌兹别克斯坦'},set()),
 'yemen':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'也门'},set()),
 'spain_republic':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'西班牙第二共和国'},set()),
 'spain_kingdom':(['spain_military_batch1_2026-09-26.json','spain_boe2025_campaigns_pack1.json','spain_boe2025_discontinued_pack1.json','spain_boe2025_commemorative_pack1.json','spain_boe2025_institutional_pack1.json'],['spain_military_batch1_2026-09-26_manifest.json','spain_boe2025_campaigns_pack1_manifest.json','spain_boe2025_discontinued_pack1_manifest.json','spain_boe2025_commemorative_pack1_manifest.json','spain_boe2025_institutional_pack1_manifest.json']),
 'savoy_italy':(['mena_round7_2026-09-26.json','italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json','italy_crown_pack1_manifest.json','italy_medalbook_pack2_2026-09-26_manifest.json','italy_medalbook_pack3_2026-09-26_manifest.json','italy_medalbook_pack4_2026-09-26_manifest.json','italy_medalbook_pack5_2026-09-26_manifest.json'],{'意大利／萨佛依王朝'},{'italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'}),
 'finland':(['finland_orders_pack1.json'],['finland_orders_pack1_manifest.json']),
 'sweden':(['sweden_orders_pack1.json'],['sweden_orders_pack1_manifest.json']),
 'norway':(['norway_orders_pack1.json'],['norway_orders_pack1_manifest.json']),
 'uk':(['uk_mod_pack1.json','uk_us_gap_round2_2026-09-26.json'],['uk_mod_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],{'英国／大英帝国'},{'uk_mod_pack1.json'}),
 'united_states':(['us_nhhc_pack1.json','uk_us_gap_round2_2026-09-26.json'],['us_nhhc_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],{'美国'},{'us_nhhc_pack1.json'}),
 'russian_empire':(['russian_empire_pack1.json','russian_empire_gap_2026-09-26.json'],['russian_empire_pack1_manifest.json','russian_empire_gap_2026-09-26_manifest.json']),
 'soviet_union':(['soviet_union_pack1.json','russia_bulk_pack2.json','russia_bulk_pack3.json','soviet_gap_round4_2026-09-26.json'],['soviet_union_pack1_manifest.json','russia_bulk_pack2_manifest.json','russia_bulk_pack3_manifest.json','soviet_gap_round4_2026-09-26_manifest.json']),
 'russian_federation':(['russian_federation_pack1.json'],['russian_federation_pack1_manifest.json']),
 'republic_of_china':(['east_asia_gap_round1_2026-09-26.json'],['east_asia_gap_round1_2026-09-26_manifest.json'],{'中华民国'},set()),
 'korean_empire':(['east_asia_gap_round1_2026-09-26.json'],['east_asia_gap_round1_2026-09-26_manifest.json'],{'大韩帝国'},set()),
 'south_korea':(['east_asia_gap_round1_2026-09-26.json','south_korea_official_complete_2026-09-27.json'],['east_asia_gap_round1_2026-09-26_manifest.json','south_korea_official_complete_2026-09-27_manifest.json'],{'韩国'},set()),
 'north_korea':(['east_asia_gap_round1_2026-09-26.json'],['east_asia_gap_round1_2026-09-26_manifest.json'],{'朝鲜'},set()),
 'japan_meiji':(['japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json'],['japan_meiji_manifest.json','japan_meiji_round2_manifest.json','japan_meiji_round3_manifest.json','japan_meiji_pack4_new_manifest.json']),
 'japan_taisho':(['japan_taisho_pack1.json','japan_taisho_pack4_new.json'],['japan_taisho_pack1_manifest.json','japan_taisho_pack4_new_manifest.json']),
 'france_first_empire':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_bourbon':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_july':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_second_republic':(['france_legion_evolution_pack1.json'],['france_legion_evolution_pack1_manifest.json']),
 'france_fourth_fifth':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'germany_1933_1945':(['germany_1933_1945_gap_round1_2026-09-26.json'],['germany_1933_1945_gap_round1_2026-09-26_manifest.json']),
 'prussia_kingdom':(['prussia_kingdom.json','prussia_batch1_2026-09-26.json','prussia_batch2_2026-09-26.json'],['prussia_kingdom_manifest.json','prussia_batch1_manifest_2026-09-26.json','prussia_batch2_manifest_2026-09-26.json']),
 'france_third_republic':(['france_third_republic.json','france_third_republic_pack1.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_third_republic_manifest.json','france_third_republic_pack1_manifest.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_second_empire':(['france_second_empire_pack1_2026-09-26.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json'],['france_second_empire_pack1_manifest_2026-09-26.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json']),
 'bavaria_kingdom':(['bavaria_kingdom_pack1.json','bavaria_kingdom_pack2.json'],['bavaria_kingdom_pack1_manifest.json','bavaria_kingdom_pack2_manifest.json']),
}
include_ids={
 'france_first_empire':{'FRA-LEGION-EVOLUTION-FIRST-EMPIRE-MODEL-GROUP'},
 'france_bourbon':{'FRA-LEGION-EVOLUTION-BOURBON-RESTORATION-MODEL-GROUP','FRA-LEGION-RESTORATION-OFFICER-DUDEVANT','FRA-LEGION-RESTORATION-CHEVALIER-HUGO-REDUCTION'},
 'france_july':{'FRA-LEGION-EVOLUTION-JULY-MONARCHY-MODEL-GROUP','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-1837','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-REDUCTION'},
 'france_second_republic':{'FRA-LEGION-EVOLUTION-SECOND-REPUBLIC-MODEL-GROUP'},
 'france_fourth_fifth':{'FRA-LEGION-EVOLUTION-FOURTH-FIFTH-REPUBLICS-MODEL-GROUP','FRA-LEGION-1945-GRAND-OFFICER-LECLERC-PLAQUE','FRA-LEGION-POST-1951-COMMANDER-NOHAIN','FRA-LEGION-FIFTH-REPUBLIC-OFFICER-FOUQUER-1971'},
 'france_second_empire':{'FRA-SE-ITALY-1859-PRESENTATION-01','FRA-SE-MEXICO-1863-01','FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01','FRA-LEGION-EVOLUTION-SECOND-EMPIRE-MODEL-GROUP'},
}
for slug,spec in volume_files.items():
    record_names,manifest_names=spec[:2]
    countries=spec[2] if len(spec)>2 else None
    unfiltered=spec[3] if len(spec)>3 else set()
    record_paths=[ROOT/'data/volumes'/name for name in record_names if (ROOT/'data/volumes'/name).is_file()]
    manifest_paths=[ROOT/'data/volumes'/name for name in manifest_names if (ROOT/'data/volumes'/name).is_file()]
    if not record_paths or not manifest_paths:continue
    records=[]
    for path in record_paths:
        loaded=json.loads(path.read_text(encoding='utf-8'))['records']
        if countries and path.name not in unfiltered:
            loaded=[r for r in loaded if r.get('country_zh') in countries]
        if slug=='france_third_republic' and path.name=='france_legion_evolution_pack1.json':
            loaded=[r for r in loaded if r['id']=='FRA-LEGION-EVOLUTION-THIRD-REPUBLIC-MODEL-GROUP']
        if slug=='france_third_republic' and path.name=='france_legion_official_batch2.json':
            loaded=[r for r in loaded if r['id']=='FRA-LEGION-THIRD-REPUBLIC-CHEVALIER-RENDU']
        records.extend(loaded)
    if slug in include_ids:
        records=[r for r in records if r['id'] in include_ids[slug]]
    if slug=='france_third_republic':
        records=[r for r in records if r['id']!='FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01']
    if slug=='savoy_italy':
        records=[r for r in records if r['id']!='IT-KOI-058-V51']
    if slug=='germany_1933_1945':
        records=[r for r in records if r['id']!='GER-1933-1945-GERMAN-OLYMPIC-CROSS-V1']
    superseded={r['supersedes_id'] for r in records if r.get('supersedes_id')}
    records=[r for r in records if r['id'] not in superseded]
    manifests=[json.loads(path.read_text(encoding='utf-8')) for path in manifest_paths]
    mapping={item['view_key']:item['local_path'] for data in manifests for item in data.get('images',[])}
    for record in records:
        if not record.get('views'):continue
        for view in record['views']:
            key=view['key']
            assert key in mapping,(slug,key)
            assert key not in all_view_paths,key
            all_view_paths[key]=mapping[key]
            asset_countries[mapping[key]].add(next(iter(countries)) if countries else slug)
        volume_records.append(record)
base_manifest={x['key']:x for x in json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))}
for record in catalogue:
    for view in record['views']:
        path='assets/images/ottoman/'+Path(base_manifest[view['key']]['path']).name
        asset_countries[path].add('奥斯曼帝国')
cross_country_paths={path:sorted(countries) for path,countries in asset_countries.items() if len(countries)>1}
assert not cross_country_paths,cross_country_paths
hash_countries=defaultdict(set)
for path,countries in asset_countries.items():
    digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    hash_countries[digest].update(countries)
cross_country_hashes={digest:sorted(countries) for digest,countries in hash_countries.items() if len(countries)>1}
assert not cross_country_hashes,cross_country_hashes
expected_images=sum(len(x['views']) for x in catalogue+related+volume_records)
assert len(gallery_images)==expected_images,(len(gallery_images),expected_images)
assert all(url.startswith('assets/images/') and '..' not in url for url in gallery_images)
assert all(path in gallery_images for path in all_view_paths.values())
assert not re.search(r'<img[^>]+src=["\']https?://',html,re.I)
assert 'fetch(' not in html and 'type="module"' not in html
assert 'object-fit:contain' in css and 'object-fit:cover' not in css
for url in gallery_images+p.scripts+p.styles:
    f=ROOT/url
    assert f.is_file(),url
    if url in gallery_images:
        with Image.open(f) as img:img.verify()
assert all(h[1:] in p.ids for h in p.links if h.startswith('#')),[h for h in p.links if h.startswith('#') and h[1:] not in p.ids]
migration=json.loads((ROOT/'data/migration_log.json').read_text(encoding='utf-8'))['items']
assert len(migration)==28 and len({x['legacy_key'] for x in migration})==28
assert len(catalogue)>=27 and len({x['family'] for x in catalogue})>=20
assert all(x['id'] in p.ids for x in catalogue+related)
assert all(x['id'] in p.ids for x in volume_records)
assert len({x['id'] for x in catalogue+related+volume_records})==len(catalogue+related+volume_records)
assert len({x['family'] for x in catalogue+volume_records})<=len(catalogue+volume_records)
assert all(x['disposition'] in ('main_gallery','related_gallery','merged','unpictured_appendix') for x in migration)
assert len([x for x in migration if x['disposition']=='unpictured_appendix'])==0
assert 'Prussia' in html and 'Bavaria' in html and '奥斯曼帝国' in html
assert all(label not in html for label in ('第一轮整理中','开放图源补充卷','中东与穆斯林国家'))
assert 'france-legion-history' not in html
assert all(bad_id not in html for bad_id in (
    'MENA7-KING-FOUAD-MILITARY-STAR',
    'MENA7-ARMED-FORCES-CAMPAIGN',
    'MENA7-ARMED-FORCES-ENDURANCE',
))
assert all(anchor in p.ids for anchor in ('ottoman','egypt','sudan','iran','turkey','azerbaijan','armenia'))
all_records=catalogue+volume_records
print(f'PASS: {len(all_records)} official rows, {len({x["family"] for x in all_records})} families, {len(gallery_images)} decoded local images, 28 migration decisions; all links and local resources exist')
