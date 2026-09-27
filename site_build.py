"""Regenerate the existing offline index.html from local records and images."""
import json,re
from collections import defaultdict
from html import escape
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
read=lambda name:json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
catalogue=read('catalogue.json')['records']
related=read('related.json')
unpictured=read('unpictured.json')
queue=read('global_queue.json')
manifest={x['key']:x for x in json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))}
volume_specs=[
 {'slug':'ottoman_extra','title':'奥斯曼帝国','anchor':'ottoman-extra-internal','aliases':'奥斯曼 Ottoman Empire Osmanlı',
  'record_files':['ottoman_commons_batch1.json','mena_round7_2026-09-26.json','ottoman_medalbook_pack2.json'],
  'manifest_files':['ottoman_commons_batch1_manifest.json','mena_round7_manifest_2026-09-26.json','ottoman_medalbook_pack2_manifest.json'],
  'countries':['奥斯曼帝国'],'unfiltered_record_files':['ottoman_commons_batch1.json','ottoman_medalbook_pack2.json']},
 {'slug':'egypt','title':'埃及','anchor':'egypt','aliases':'埃及 Egypt مصر Khedivate Republic',
  'record_files':['egypt_republic_pack1.json','mena_round7_2026-09-26.json','mena_gap_round1_2026-09-26.json'],
  'manifest_files':['egypt_republic_pack1_manifest.json','mena_round7_manifest_2026-09-26.json','mena_gap_round1_manifest_2026-09-26.json'],
  'countries':['埃及'],'unfiltered_record_files':['egypt_republic_pack1.json']},
 {'slug':'sudan','title':'苏丹','anchor':'sudan','aliases':'苏丹 Sudan Anglo-Egyptian Sudan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['苏丹']},
 {'slug':'iran','title':'波斯／伊朗','anchor':'iran','aliases':'波斯 伊朗 Persia Iran Qajar Pahlavi',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['伊朗／波斯']},
 {'slug':'turkey','title':'土耳其共和国','anchor':'turkey','aliases':'土耳其 Turkey Türkiye Republic',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['土耳其共和国']},
 {'slug':'syria','title':'叙利亚','anchor':'syria','aliases':'叙利亚 Syria',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['叙利亚']},
 {'slug':'oman','title':'阿曼','anchor':'oman','aliases':'阿曼 Oman',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿曼']},
 {'slug':'afghanistan','title':'阿富汗','anchor':'afghanistan','aliases':'阿富汗 Afghanistan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿富汗']},
 {'slug':'pakistan','title':'巴基斯坦','anchor':'pakistan','aliases':'巴基斯坦 Pakistan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['巴基斯坦']},
 {'slug':'morocco','title':'摩洛哥','anchor':'morocco','aliases':'摩洛哥 Morocco',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['摩洛哥']},
 {'slug':'algeria','title':'阿尔及利亚','anchor':'algeria','aliases':'阿尔及利亚 Algeria',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿尔及利亚']},
 {'slug':'azerbaijan','title':'阿塞拜疆','anchor':'azerbaijan','aliases':'阿塞拜疆 Azerbaijan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿塞拜疆']},
 {'slug':'armenia','title':'亚美尼亚','anchor':'armenia','aliases':'亚美尼亚 Armenia Հայաստան',
  'record_files':['armenia_pack1.json'],'manifest_files':['armenia_pack1_manifest.json']},
 {'slug':'kazakhstan','title':'哈萨克斯坦','anchor':'kazakhstan','aliases':'哈萨克斯坦 Kazakhstan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['哈萨克斯坦']},
 {'slug':'uzbekistan','title':'乌兹别克斯坦','anchor':'uzbekistan','aliases':'乌兹别克斯坦 Uzbekistan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['乌兹别克斯坦']},
 {'slug':'yemen','title':'也门','anchor':'yemen','aliases':'也门 Yemen',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['也门']},
 {'slug':'spain_republic','title':'西班牙第二共和国','anchor':'spain-republic','aliases':'西班牙 第二共和国 Spain Second Republic Isabella',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['西班牙第二共和国'],'country_group':'spain'},
 {'slug':'spain_kingdom','title':'西班牙王国','anchor':'spain-kingdom','aliases':'西班牙王国 Spain Reino de España BOE',
  'record_files':['spain_military_batch1_2026-09-26.json','spain_boe2025_campaigns_pack1.json','spain_boe2025_discontinued_pack1.json','spain_boe2025_commemorative_pack1.json','spain_boe2025_institutional_pack1.json'],'manifest_files':['spain_military_batch1_2026-09-26_manifest.json','spain_boe2025_campaigns_pack1_manifest.json','spain_boe2025_discontinued_pack1_manifest.json','spain_boe2025_commemorative_pack1_manifest.json','spain_boe2025_institutional_pack1_manifest.json'],'country_group':'spain'},
 {'slug':'savoy_italy','title':'萨佛依王朝／意大利王国','anchor':'savoy-italy','aliases':'萨佛依 意大利 Savoy Italy Annunciation',
  'record_files':['mena_round7_2026-09-26.json','italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','italy_crown_pack1_manifest.json','italy_medalbook_pack2_2026-09-26_manifest.json','italy_medalbook_pack3_2026-09-26_manifest.json','italy_medalbook_pack4_2026-09-26_manifest.json','italy_medalbook_pack5_2026-09-26_manifest.json'],'countries':['意大利／萨佛依王朝'],'unfiltered_record_files':['italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],'exclude_ids':['IT-KOI-058-V51']},
 {'slug':'finland','title':'芬兰共和国','anchor':'finland','aliases':'芬兰 Finland Suomi White Rose Lion Cross of Liberty',
  'record_files':['finland_orders_pack1.json'],'manifest_files':['finland_orders_pack1_manifest.json']},
 {'slug':'sweden','title':'瑞典王国','anchor':'sweden','aliases':'瑞典 Sweden Sverige Serafimerorden Seraphim',
  'record_files':['sweden_orders_pack1.json'],'manifest_files':['sweden_orders_pack1_manifest.json']},
 {'slug':'norway','title':'挪威王国','anchor':'norway','aliases':'挪威 Norway Norge St Olav Sankt Olavs Orden',
  'record_files':['norway_orders_pack1.json'],'manifest_files':['norway_orders_pack1_manifest.json']},
 {'slug':'uk','title':'英国／大英帝国','anchor':'uk','aliases':'英国 大英帝国 United Kingdom Great Britain British Empire England Scotland Wales Northern Ireland',
  'record_files':['uk_mod_pack1.json','uk_us_gap_round2_2026-09-26.json'],'manifest_files':['uk_mod_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],'countries':['英国／大英帝国'],'unfiltered_record_files':['uk_mod_pack1.json']},
 {'slug':'united_states','title':'美国','anchor':'united-states','aliases':'美国 United States USA U.S. NHHC NARA',
  'record_files':['us_nhhc_pack1.json','uk_us_gap_round2_2026-09-26.json'],'manifest_files':['us_nhhc_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],'countries':['美国'],'unfiltered_record_files':['us_nhhc_pack1.json']},
 {'slug':'russian_empire','title':'俄罗斯帝国','anchor':'russian-empire','aliases':'俄罗斯帝国 Imperial Russia Российская империя',
  'record_files':['russian_empire_pack1.json','russian_empire_gap_2026-09-26.json'],'manifest_files':['russian_empire_pack1_manifest.json','russian_empire_gap_2026-09-26_manifest.json'],'country_group':'russia'},
 {'slug':'soviet_union','title':'苏联','anchor':'soviet-union','aliases':'苏联 USSR Soviet Union СССР',
  'record_files':['soviet_union_pack1.json','russia_bulk_pack2.json','russia_bulk_pack3.json','soviet_gap_round4_2026-09-26.json'],'manifest_files':['soviet_union_pack1_manifest.json','russia_bulk_pack2_manifest.json','russia_bulk_pack3_manifest.json','soviet_gap_round4_2026-09-26_manifest.json'],'country_group':'russia'},
 {'slug':'russian_federation','title':'俄罗斯联邦','anchor':'russian-federation','aliases':'俄罗斯联邦 Russia Russian Federation Российская Федерация',
  'record_files':['russian_federation_pack1.json'],'manifest_files':['russian_federation_pack1_manifest.json'],'country_group':'russia'},
 {'slug':'republic_of_china','title':'中华民国（1912–）','anchor':'republic-of-china','aliases':'中华民国 Republic of China ROC 勋章',
  'record_files':['east_asia_gap_round1_2026-09-26.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json'],'countries':['中华民国'],'country_group':'china'},
 {'slug':'korean_empire','title':'大韩帝国（1897–1910）','anchor':'korean-empire','aliases':'大韩帝国 Korean Empire 대한제국',
  'record_files':['east_asia_gap_round1_2026-09-26.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json'],'countries':['大韩帝国'],'country_group':'korea'},
 {'slug':'south_korea','title':'韩国','anchor':'south-korea','aliases':'韩国 大韩民国 South Korea Republic of Korea 대한민국',
  'record_files':['east_asia_gap_round1_2026-09-26.json','south_korea_official_complete_2026-09-27.json'],
  'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json','south_korea_official_complete_2026-09-27_manifest.json'],
  'countries':['韩国'],'country_group':'korea'},
 {'slug':'north_korea','title':'朝鲜','anchor':'north-korea','aliases':'朝鲜 朝鲜民主主义人民共和国 North Korea DPRK 조선',
  'record_files':['east_asia_gap_round1_2026-09-26.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json'],'countries':['朝鲜'],'country_group':'korea'},
 {'slug':'japan_meiji','title':'日本 · 明治时期（1868–1912）','anchor':'japan-meiji','aliases':'日本 日本帝国 Japan Meiji 明治',
  'record_files':['japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json'],
  'manifest_files':['japan_meiji_manifest.json','japan_meiji_round2_manifest.json','japan_meiji_round3_manifest.json','japan_meiji_pack4_new_manifest.json']},
 {'slug':'japan_taisho','title':'日本 · 大正时期（1912–1926）','anchor':'japan-taisho','aliases':'日本 日本帝国 Japan Taisho 大正',
  'record_files':['japan_taisho_pack1.json','japan_taisho_pack4_new.json'],
  'manifest_files':['japan_taisho_pack1_manifest.json','japan_taisho_pack4_new_manifest.json']},
 {'slug':'france_first_empire','title':'法国第一帝国（1804–1814）','anchor':'france-first-empire','aliases':'法国 第一帝国 Napoleon I 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-FIRST-EMPIRE-MODEL-GROUP'],'country_group':'france'},
 {'slug':'france_bourbon','title':'法国波旁复辟（1814–1830）','anchor':'france-bourbon','aliases':'法国 波旁复辟 Bourbon Restoration 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-BOURBON-RESTORATION-MODEL-GROUP','FRA-LEGION-RESTORATION-OFFICER-DUDEVANT','FRA-LEGION-RESTORATION-CHEVALIER-HUGO-REDUCTION'],'country_group':'france'},
 {'slug':'france_july','title':'法国七月王朝（1830–1848）','anchor':'france-july','aliases':'法国 七月王朝 July Monarchy 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-JULY-MONARCHY-MODEL-GROUP','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-1837','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-REDUCTION'],'country_group':'france'},
 {'slug':'france_second_republic','title':'法国第二共和国（1848–1852）','anchor':'france-second-republic','aliases':'法国 第二共和国 Second Republic 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-SECOND-REPUBLIC-MODEL-GROUP'],'country_group':'france'},
 {'slug':'france_fourth_fifth','title':'法国第四／第五共和国（1946–）','anchor':'france-fourth-fifth','aliases':'法国 第四共和国 第五共和国 Fourth Fifth Republic 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-FOURTH-FIFTH-REPUBLICS-MODEL-GROUP','FRA-LEGION-1945-GRAND-OFFICER-LECLERC-PLAQUE','FRA-LEGION-POST-1951-COMMANDER-NOHAIN','FRA-LEGION-FIFTH-REPUBLIC-OFFICER-FOUQUER-1971'],'country_group':'france'},
 {'slug':'germany_1933_1945','title':'德国（1933–1945）','anchor':'germany-1933-1945','aliases':'德国 德意志国 Germany Deutsches Reich 1933 1945',
  'record_files':['germany_1933_1945_gap_round1_2026-09-26.json'],'manifest_files':['germany_1933_1945_gap_round1_2026-09-26_manifest.json'],
  'exclude_ids':['GER-1933-1945-GERMAN-OLYMPIC-CROSS-V1']},
 {'slug':'prussia_kingdom','title':'普鲁士王国（1701–1918）','anchor':'prussia-kingdom','aliases':'普鲁士 Prussia Kingdom of Prussia',
  'record_files':['prussia_kingdom.json','prussia_batch1_2026-09-26.json','prussia_batch2_2026-09-26.json'],
  'manifest_files':['prussia_kingdom_manifest.json','prussia_batch1_manifest_2026-09-26.json','prussia_batch2_manifest_2026-09-26.json']},
 {'slug':'france_third_republic','title':'法国第三共和国（1870–1940）','anchor':'france-third-republic','aliases':'法国 France Third Republic',
  'record_files':['france_third_republic.json','france_third_republic_pack1.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_third_republic_manifest.json','france_third_republic_pack1_manifest.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'exclude_ids':['FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01'],
  'file_include_ids':{'france_legion_evolution_pack1.json':['FRA-LEGION-EVOLUTION-THIRD-REPUBLIC-MODEL-GROUP'],'france_legion_official_batch2.json':['FRA-LEGION-THIRD-REPUBLIC-CHEVALIER-RENDU']},'country_group':'france'},
 {'slug':'france_second_empire','title':'法国第二帝国（1852–1870）','anchor':'france-second-empire','aliases':'法国 France Second Empire Napoleon III',
  'record_files':['france_second_empire_pack1_2026-09-26.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json'],
  'manifest_files':['france_second_empire_pack1_manifest_2026-09-26.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json'],
  'include_ids':['FRA-SE-ITALY-1859-PRESENTATION-01','FRA-SE-MEXICO-1863-01','FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01','FRA-LEGION-EVOLUTION-SECOND-EMPIRE-MODEL-GROUP'],'country_group':'france'},
 {'slug':'bavaria_kingdom','title':'巴伐利亚王国（1806–1918）','anchor':'bavaria-kingdom','aliases':'巴伐利亚 Bavaria Kingdom of Bavaria',
  'record_files':['bavaria_kingdom_pack1.json','bavaria_kingdom_pack2.json'],
  'manifest_files':['bavaria_kingdom_pack1_manifest.json','bavaria_kingdom_pack2_manifest.json']},
]
volumes=[]
view_paths={}
for spec in volume_specs:
    slug,title,anchor,aliases=(spec[k] for k in ('slug','title','anchor','aliases'))
    data_paths=[ROOT/'data/volumes'/name for name in spec['record_files'] if (ROOT/'data/volumes'/name).is_file()]
    manifest_paths=[ROOT/'data/volumes'/name for name in spec['manifest_files'] if (ROOT/'data/volumes'/name).is_file()]
    if not data_paths or not manifest_paths:continue
    records=[]
    for data_path in data_paths:
        loaded=json.loads(data_path.read_text(encoding='utf-8'))['records']
        if spec.get('countries') and data_path.name not in spec.get('unfiltered_record_files',[]):
            loaded=[r for r in loaded if r.get('country_zh') in spec['countries']]
        if data_path.name in spec.get('file_include_ids',{}):
            allowed=set(spec['file_include_ids'][data_path.name])
            loaded=[r for r in loaded if r['id'] in allowed]
        records.extend(loaded)
    if spec.get('include_ids'):
        records=[r for r in records if r['id'] in spec['include_ids']]
    if spec.get('exclude_ids'):
        records=[r for r in records if r['id'] not in spec['exclude_ids']]
    superseded={r['supersedes_id'] for r in records if r.get('supersedes_id')}
    records=[r for r in records if r['id'] not in superseded]
    metadata=[json.loads(path.read_text(encoding='utf-8')) for path in manifest_paths]
    mapping={x['view_key']:x['local_path'] for meta in metadata for x in meta.get('images',[])}
    pictured=[];pending=[]
    for r in records:
        if not r.get('views'):pending.append(r);continue
        for view in r['views']:
            key=view['key']
            if key not in mapping:raise ValueError(f'Missing image mapping: {slug} {r["id"]} {key}')
            if key in view_paths:raise ValueError(f'Duplicate view key: {key}')
            path=ROOT/mapping[key]
            if not path.is_file():raise FileNotFoundError(path)
            with Image.open(path) as im:im.verify()
            view_paths[key]=mapping[key]
        pictured.append(r)
    if not pictured and not pending:
        continue
    country_group=spec.get('country_group') or ('japan' if slug.startswith('japan_') else slug)
    volumes.append({'slug':slug,'title':title,'anchor':anchor,'aliases':aliases,'country':country_group,'records':pictured,'pending':pending,
                    'candidates':[x for meta in metadata for x in meta.get('unpictured_candidates',[])]})
if len({r['id'] for vol in volumes for r in vol['records']+vol['pending']})!=sum(len(v['records']+v['pending']) for v in volumes):
    raise ValueError('Duplicate volume record ID')
image_keys={v['key'] for r in catalogue+related for v in r['views']}
assert len({r['id'] for r in catalogue+related})==len(catalogue+related)
for key in image_keys:
    img=manifest[key]
    path=ROOT/'assets/images/ottoman'/Path(img['path']).name
    assert path.is_file(),path
    with Image.open(path) as im: im.verify()
for key,img in manifest.items():
    if key in image_keys:view_paths[key]='assets/images/ottoman/'+Path(img['path']).name

# Ottoman records harvested in later source batches belong to the same historical
# state and therefore join the main Ottoman section instead of becoming a
# user-visible "supplement volume".
ottoman_extra=next((v for v in volumes if v['slug']=='ottoman_extra'),None)
if ottoman_extra:
    catalogue.extend(ottoman_extra['records'])
    volumes=[v for v in volumes if v['slug']!='ottoman_extra']
families={r['family'] for r in catalogue}
all_record_ids=[r['id'] for r in catalogue+related]+[r['id'] for v in volumes for r in v['records']]
if len(set(all_record_ids))!=len(all_record_ids):
    raise ValueError('Duplicate record ID across country sections')

style=(ROOT/'assets/site.css').read_text(encoding='utf-8-sig')
if '/* WORLD_MEDALS_V2 */' not in style:
 style+='''
/* WORLD_MEDALS_V2 */
html{scroll-behavior:smooth}body{--accent:#214a45}
.layout{grid-template-columns:300px minmax(0,1fr)}nav{max-height:calc(100vh - 10px);font-size:13px}
nav a{display:block;color:#244d49;text-decoration:none;padding:3px 8px;border-radius:3px}
nav a:hover,nav a:focus{background:#eaf0ed;text-decoration:underline}
#showAll{width:100%;margin:0 0 8px;padding:7px 9px;border:1px solid var(--line);border-radius:4px;background:#fff;color:#244d49;text-align:left;cursor:pointer}#showAll:hover,#showAll:focus{background:#eaf0ed}
nav details{padding-left:9px}nav summary{padding:3px 0}nav .count{font-size:11px;color:#687a75;display:block;padding-left:8px}
nav .queued{color:#687a75}nav .rulers{margin-left:11px;border-left:1px solid #dce5e1}
.period-section{scroll-margin-top:18px;margin-bottom:38px}.period-section h2{font-size:20px;margin:22px 20px 4px}
.period-section .years{margin:0 20px 12px;color:#61736e}.section-note{margin:12px 20px}
tr{scroll-margin-top:15px}tr:target{outline:3px solid #bc9162;outline-offset:-3px}
#searchResults{margin:4px 0 0;max-height:220px;overflow:auto;border:1px solid var(--line);max-width:670px;background:white}
#searchResults[hidden]{display:none}#searchResults a{display:block;padding:6px 10px;color:#214a45;text-decoration:none;border-bottom:1px solid var(--line)}
#searchResults a:hover,#searchResults a:focus{background:#edf4f0}
#queue-status{padding:18px 20px;margin:20px;border:1px solid var(--line);background:var(--soft);scroll-margin-top:10px}
#queue-status[hidden]{display:none}.noimage{padding:4px 0;list-style:none}.noimage li{margin:5px 0}
.gallery-meta{font-size:12px;color:#60716e;margin:0 20px 10px}
@media(max-width:850px){.layout{display:block}nav{max-height:300px}.period-section h2{margin-left:9px}}
'''
(ROOT/'assets/site.css').write_text(style,encoding='utf-8')

def year(r):
    m=re.search(r'\d{4}',r['date'])
    return int(m.group()) if m else 9999
search_index=[]
def add_search(label,target,extra='',context=''):
    search_index.append({'label':label,'target':target,'text':label+' '+extra,'context':context})
def queued_link(name):
    add_search(name,'queue-status','queued '+('Prussia' if '普鲁士' in name else '')+' '+('Bavaria' if '巴伐利亚' in name else ''))
    return '<a class="queued" href="#queue-status" data-queued="'+escape(name,quote=True)+'">'+escape(name)+' · 待收录</a>'

node_anchor_map={
 '明治时期（1868–1912）':'japan-meiji','大正时期（1912–1926）':'japan-taisho',
 '埃及':'egypt','苏丹':'sudan','波斯／伊朗':'iran','土耳其共和国':'turkey',
 '叙利亚':'syria','阿曼':'oman','阿富汗':'afghanistan','巴基斯坦':'pakistan',
 '摩洛哥':'morocco','阿尔及利亚':'algeria','阿塞拜疆':'azerbaijan','亚美尼亚':'armenia',
 '哈萨克斯坦':'kazakhstan','乌兹别克斯坦':'uzbekistan','也门':'yemen',
 '英国／大英帝国':'uk','大英帝国':'uk',
 '美国':'united-states',
 '俄罗斯帝国':'russian-empire','苏联':'soviet-union','俄罗斯联邦':'russian-federation','瑞典':'sweden','挪威':'norway',
 '意大利诸政权':'savoy-italy',
 '芬兰':'finland',
 '西班牙王国':'spain-kingdom','西班牙第二共和国':'spain-republic',
 '普鲁士王国':'prussia-kingdom','普鲁士王国（1701–1918）':'prussia-kingdom',
 '普鲁士王国（1871–1918）':'prussia-kingdom','第一帝国（1804–1814）':'france-first-empire',
 '波旁复辟（1814–1830）':'france-bourbon','七月王朝（1830–1848）':'france-july',
 '第二共和国（1848–1852）':'france-second-republic','第二帝国（1852–1870）':'france-second-empire',
 '第三共和国（1870–1940）':'france-third-republic','第四／第五共和国（1946–）':'france-fourth-fifth',
 '巴伐利亚王国':'bavaria-kingdom',
 '德国（1933–1945）':'germany-1933-1945',
 '中华民国（1912–）':'republic-of-china','大韩帝国（1897–1910）':'korean-empire',
 '韩国':'south-korea','朝鲜':'north-korea',
}
def render_node(node,level=0):
    name=node['name']; children=node.get('periods',[])
    if name in node_anchor_map:
        anchor=node_anchor_map[name]
        volume=next((v for v in volumes if v['anchor']==anchor),None)
        if volume:
            count=f'{len({r["family"] for r in volume["records"]})}独立章种 · {len(volume["records"])}等级／版型 · {sum(len(r["views"]) for r in volume["records"])}图'
            add_search(name,anchor,volume['aliases'])
            return '<a href="#'+anchor+'" data-section-filter="'+anchor+'">'+escape(name)+'</a><span class="count">'+count+'</span>'
    if node.get('target')=='ottoman':
        count=f'{len(families)}章种 · {len(catalogue)}版型 · {len({v["key"] for r in catalogue for v in r["views"]})}图'
        add_search(name,'ottoman','Ottoman Empire Osmanlı')
        return '<a href="#ottoman" data-country-filter="ottoman">'+escape(name)+'</a><span class="count">'+count+'</span>'
    if children:
        nested=''.join(render_node(x,level+1) for x in children)
        if name=='日本' and any(v['anchor']=='japan-meiji' for v in volumes):
            add_search(name,'japan-meiji','Japan 日本')
            return '<details><summary>'+escape(name)+'</summary><a href="#japan-meiji" data-country-filter="japan">日本</a>'+nested+'</details>'
        if name=='中国' and any(v['anchor']=='republic-of-china' for v in volumes):
            add_search(name,'republic-of-china','中国 中华民国 China Republic of China')
            return '<details><summary>'+escape(name)+'</summary><a href="#republic-of-china" data-country-filter="china">中国</a>'+nested+'</details>'
        if name=='朝鲜半岛' and any(v['anchor']=='korean-empire' for v in volumes):
            add_search(name,'korean-empire','朝鲜半岛 Korea 韩国 朝鲜 大韩帝国')
            return '<details open><summary>'+escape(name)+'</summary><a href="#korean-empire" data-country-filter="korea">朝鲜半岛</a>'+nested+'</details>'
        if name=='法国' and any(v['anchor']=='france-third-republic' for v in volumes):
            add_search(name,'france-third-republic','France 法国')
            return '<details open><summary>'+escape(name)+'</summary><a href="#france-first-empire" data-country-filter="france">法国</a>'+nested+'</details>'
        if name=='德国／德意志地区' and any(v['anchor']=='prussia-kingdom' for v in volumes):
            add_search(name,'prussia-kingdom','Germany Prussia')
            return '<details><summary>'+escape(name)+'</summary><a href="#prussia-kingdom" data-country-filter="prussia_kingdom">普鲁士王国</a>'+nested+'</details>'
        if name=='俄罗斯帝国／苏联／俄罗斯联邦' and any(v['anchor']=='russian-empire' for v in volumes):
            add_search(name,'russian-empire','Russia USSR Soviet Imperial Russian Federation')
            return '<details open><summary>'+escape(name)+'</summary><a href="#russian-empire" data-country-filter="russia">俄罗斯诸时期</a>'+nested+'</details>'
        if name=='西班牙' and any(v['anchor']=='spain-kingdom' for v in volumes):
            add_search(name,'spain-kingdom','Spain España 西班牙')
            return '<details open><summary>'+escape(name)+'</summary><a href="#spain-kingdom" data-country-filter="spain">西班牙</a>'+nested+'</details>'
        return '<details><summary>'+escape(name)+'</summary>'+queued_link(name)+nested+'</details>'
    return queued_link(name)

nav=['<button type="button" id="showAll">显示全部国家</button><details open><summary>世界</summary>']
for c in queue['continents']:
    nav.append('<details'+(' open' if c['name']=='亚洲' else '')+'><summary>'+escape(c['name'])+'</summary>')
    for region in c['regions']:
        nav.append('<details'+(' open' if region['name']=='西亚' else '')+'><summary>'+escape(region['name'])+'</summary>')
        for node in region['systems']:nav.append(render_node(node))
        nav.append('</details>')
    nav.append('</details>')
nav.append('<details><summary>跨区域历史体系</summary>')
for item in queue['historical_crosslinks']:
    if item['target']=='ottoman':nav.append('<a href="#ottoman" data-country-filter="ottoman">'+escape(item['name'])+'</a>')
    elif item['name'] in ('俄罗斯帝国','苏联') and any(v['anchor']==node_anchor_map[item['name']] for v in volumes):
        anchor=node_anchor_map[item['name']]
        nav.append('<a href="#'+anchor+'" data-section-filter="'+anchor+'">'+escape(item['name'])+'</a>')
    elif item['name'] in node_anchor_map and any(v['anchor']==node_anchor_map[item['name']] for v in volumes):
        anchor=node_anchor_map[item['name']]
        nav.append('<a href="#'+anchor+'" data-section-filter="'+anchor+'">'+escape(item['name'])+'</a>')
    else:nav.append(queued_link(item['name']))
nav.append('</details><details><summary>国际授予机构</summary>')
for item in queue['international']:nav.append(queued_link(item['name']))
nav.append('</details></details>')

def row_html(r):
    pics=[]
    for v in r['views']:
        url=view_paths[v['key']]
        alt=r['name']+' '+r['variant']+' '+v['label']
        pics.append('<figure class="imagebox"><img loading="lazy" src="'+escape(url,quote=True)+'" alt="'+escape(alt,quote=True)+'"><figcaption>'+escape(v['label'])+'</figcaption></figure>')
    name=' '.join([r['name'],r['original'],r['date'],r['variant']])
    volume=next((volume for volume in volumes if r in volume['records']),None)
    alias=(r.get('country_zh') or volume['aliases']) if volume else 'Ottoman Empire Osmanlı'
    context=volume['title'] if volume else '奥斯曼帝国'
    add_search(name,r['id'],alias,context)
    return '<tr id="'+escape(r['id'],quote=True)+'" data-source-ids="'+escape(','.join(r['source_ids']),quote=True)+'"><td class="name"><strong>'+escape(r['name'])+'</strong><span class="original">'+escape(r['original'])+'</span><span class="date">'+escape(r['date'])+'</span></td><td class="meta">'+escape(r['variant'])+'</td><td class="pictures"><div class="imagegrid'+(' pair' if len(pics)>1 else '')+'">'+''.join(pics)+'</div></td></tr>'
def table(records):
    return '<div class="scroller"><table><colgroup><col class="namecol"><col class="kindcol"><col class="imagecol"></colgroup><thead><tr><th>名称＋日期</th><th>等级／版别</th><th>完整图样</th></tr></thead><tbody>'+''.join(row_html(r) for r in records)+'</tbody></table></div>'

sections=['<section class="period-section" data-country="ottoman" id="ottoman"><h2>奥斯曼帝国（约1299–1922）</h2><p class="section-note">'+str(len(families))+'独立章种 · '+str(len(catalogue))+'等级／版型 · '+str(len({v['key'] for r in catalogue for v in r['views']}))+'张本地图</p>'+table(sorted(catalogue,key=lambda r:(year(r),r['family'],r['id'])))+'</section>']
for volume in volumes:
    records=sorted(volume['records'],key=lambda r:(year(r),r['family'],r['id']))
    add_search(volume['title'],volume['anchor'],volume['aliases'])
    count=f'{len({r["family"] for r in records})}独立章种 · {len(records)}等级／版型 · {sum(len(r["views"]) for r in records)}张本地图'
    sections.append('<section class="period-section" data-country="'+escape(volume['country'],quote=True)+'" id="'+volume['anchor']+'"><h2>'+escape(volume['title'])+'</h2><p class="section-note">'+count+'</p>'+table(records)+'</section>')
    if volume['pending'] or volume['candidates']:
        pending_id=volume['anchor']+'-unpictured'
        items=[r['name']+' · '+r['date'] for r in volume['pending']+volume['candidates']]
        for item in items:add_search(item,pending_id,volume['aliases'])
        pending_lines=''.join('<li>'+escape(item)+'</li>' for item in items)
        sections.append('<section class="period-section" data-country="'+escape(volume['country'],quote=True)+'" id="'+pending_id+'"><h2>'+escape(volume['title']+' · 有记载，暂缺完整图片')+'</h2><ul class="noimage">'+pending_lines+'</ul></section>')
if related:
    sections.append('<section class="period-section" id="related"><h2>相关奖励与纪念佩饰</h2><p class="gallery-meta">此附编不计入正式勋奖章章种数；复制品已明示。</p>'+table(sorted(related,key=year))+'</section>')
if unpictured:
    lines=[]
    for item in unpictured:
        label=item['name']+' · '+item['date']+' · '+item['known_grade']
        add_search(label,'unpictured',item['original'])
        lines.append('<li>'+escape(label)+'</li>')
    sections.append('<section class="period-section" id="unpictured"><h2>有记载，暂缺完整图片</h2><ul class="noimage">'+''.join(lines)+'</ul></section>')
for system in ('奥斯曼帝国 Ottoman Empire','亚洲 西亚'):
    add_search(system,'ottoman')

script='''const index=window.WORLD_MEDALS_SEARCH;
const input=document.getElementById('search'), results=document.getElementById('searchResults');
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const gallerySections=[...document.querySelectorAll('main > section.period-section')];
function showAllSections(){for(const section of gallerySections)section.hidden=false;document.getElementById('queue-status').hidden=true;}
function showCountry(country){for(const section of gallerySections)section.hidden=section.dataset.country!==country;document.getElementById('queue-status').hidden=true;}
function showTarget(target){const node=document.getElementById(target);const section=node&&node.closest('section.period-section');if(!section)return;for(const item of gallerySections)item.hidden=item!==section;document.getElementById('queue-status').hidden=true;}
function showResults(){const q=norm(input.value.trim());results.innerHTML='';results.hidden=!q;if(!q)return;
 let found=index.filter(x=>norm(x.text).includes(q)).sort((a,b)=>(a.target==='queue-status')-(b.target==='queue-status'));
 const count=document.createElement('p');count.className='search-count';count.textContent='共 '+found.length+' 项';results.append(count);
 for(const x of found){const a=document.createElement('a');a.href='#'+x.target;a.textContent=(x.context?'【'+x.context+'】':'')+x.label;a.addEventListener('click',()=>{results.hidden=true;input.value='';if(x.target==='queue-status'){for(const section of gallerySections)section.hidden=true;document.getElementById('queueName').textContent=x.label;document.getElementById('queue-status').hidden=false}else showTarget(x.target)});results.append(a)}
 if(!found.length){const p=document.createElement('p');p.textContent='未找到已登记项目';results.append(p)} }
for(const eventName of ['input','search','change','compositionend','keyup'])input.addEventListener(eventName,showResults);
document.getElementById('showAll').addEventListener('click',showAllSections);
for(const a of document.querySelectorAll('a[data-country-filter]'))a.addEventListener('click',()=>showCountry(a.dataset.countryFilter));
for(const a of document.querySelectorAll('a[data-section-filter]'))a.addEventListener('click',()=>showTarget(a.dataset.sectionFilter));
for(const a of document.querySelectorAll('a[data-queued]'))a.addEventListener('click',()=>{for(const section of gallerySections)section.hidden=true;document.getElementById('queueName').textContent=a.dataset.queued;document.getElementById('queue-status').hidden=false});
const viewer=document.getElementById('viewer');document.getElementById('closeViewer').onclick=()=>viewer.close();
for(const im of document.querySelectorAll('td.pictures img'))im.addEventListener('click',()=>{document.getElementById('viewerTitle').textContent=im.alt;document.getElementById('viewerImage').src=im.src;viewer.showModal()});
viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close()});
'''
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Cache-Control" content="no-store"><title>全球勋章、奖章与官方奖励图鉴</title><link rel="stylesheet" href="assets/site.css"></head><body>'''
all_records=catalogue+[r for v in volumes for r in v['records']]
all_family_count=len({r['family'] for r in all_records})
html+='<header><h1>全球勋章、奖章与官方奖励图鉴</h1><p>'+str(all_family_count)+'独立章种 · '+str(len(all_records))+'等级／版型</p><label for="search">检索</label> <input id="search" type="search" placeholder="名称、原名、年代、国家；支持单字" autocomplete="off"><div id="searchResults" hidden></div><p class="small">点击国家或时期后仅显示该栏目；点击图片查看完整原图。</p></header>'
html+='<div class="layout"><nav aria-label="全球目录">'+''.join(nav)+'</nav><main>'+''.join(sections)+'<section id="queue-status" hidden><h2 id="queueName">待收录</h2><p>该范围尚未开始实物收录。此节点保留在全球工作目录中。</p></section></main></div>'
html+='<dialog id="viewer"><div class="dialogtop"><span id="viewerTitle"></span><button type="button" id="closeViewer">关闭</button></div><img id="viewerImage" alt="完整原图"></dialog>'
html+='<script>window.WORLD_MEDALS_SEARCH='+json.dumps(search_index,ensure_ascii=False).replace('</','<\\/')+';</script><script>'+script+'</script></body></html>'
(ROOT/'index.html').write_text(html,encoding='utf-8')
print('index',len(all_records),'main rows',all_family_count,'main families',len(related),'related rows',len(view_paths),'local files')
