"""Merge the bounded MOD guide sweep and reviewed museum objects, without duplicating families."""
from pathlib import Path
from collections import defaultdict
import json, hashlib
from PIL import Image

R=Path(__file__).resolve().parents[1]
ST='data/staging/uk_mod_completion/'
def load(p): return json.loads((R/p).read_text('utf-8'))
def save(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')

def merge():
    facts=load(ST+'facts.json')['items']
    # The final bridge uses object-specific dates, grades and view labels.
    additions=load(ST+'additions_final.json')
    review=load(ST+'review_final.json')
    original=load(ST+'existing_records.json')
    baseline={r['family'] for r in original}
    pack=load('data/volumes/uk_mod_pack1.json')
    manifest=load('data/volumes/uk_mod_pack1_manifest.json')
    sources=load('data/sources.json')
    intros=load('mobile/web/award-intros.json')
    grouped=defaultdict(list)
    for f in facts:
        fid=f.get('existing_family_id') or f.get('new_canonical_suggestion')
        if fid and fid.startswith('GB-'): grouped[fid].append(f)
    for r in pack['records']:
        v=review.get(r['id'])
        if v:
            r['variant']=v['variant_zh']
            r['views'][0]['label']=v['view_label']
    entries={i['award_id']:i for i in intros['items']}
    for fid,rows in grouped.items():
        if fid in ('GB-ORDER-BATH','GB-ORDER-OBE'): continue
        previous=next((r for r in original if r['family']==fid),None)
        addition=next((r for r in additions if r['family']==fid),None)
        name=(previous or addition or {}).get('name',rows[0]['name_zh'])
        paragraphs=list(dict.fromkeys(f['introduction_zh'] for f in rows))
        if fid=='GB-UK-1914-STAR':
            paragraphs=['授予在1914年8月5日至11月22日期间于法国、比利时服役的人员。该时间是服役资格范围，不是每一枚实物的颁发日期。','图示为弗兰克·亚历山大·德帕斯中尉的馆藏实物，加有“5 AUG–22 NOV 1914”扣饰；正背面来自同一件藏品。']
        elif fid=='GB-UK-1914-15-STAR':
            paragraphs=['授予在1914年8月5日至1915年12月31日期间于战争战区服役、且未取得1914年星章资格的人员。','章体为带冠冕的青铜四芒星，交叉双剑、橡叶环及乔治五世花押构成正面；背面刻受授者军阶、姓名与单位。图示为牛顿·威廉斯上尉的馆藏实物。']
        elif fid=='GB-UK-BRITISH-WAR-MEDAL-1914-20':
            paragraphs=['为第一次世界大战期间的合资格服役颁发；资格范围后来延至1920年，涵盖战后扫雷及俄国、波罗的海等地行动。','图示为银质乔治五世头像版，背面以骑马的圣乔治为主体，并有1914、1918纪年。名称中的1914–1920是资格覆盖范围，不能与背面纪年混为一谈。']
        elif fid=='GB-UK-VICTORY-MEDAL-1914-19':
            paragraphs=['英国版协约国胜利奖章，授予第一次世界大战期间在战区服役的人员。国防部指南指出，获1914年或1914–1915年星章的人员也获此章。','英国版由威廉·麦克米伦设计，青铜圆章正面为手持棕榈枝的翼形胜利女神，背面为战争纪念铭文和1914–1919纪年，配双虹色绶带。馆藏说明指出它与英国战争奖章配套颁发。']
        elif fid=='GB-UK-DISTINGUISHED-SERVICE-ORDER-DSO':
            paragraphs=['1886年设立，最初用于表彰军官的卓越服务；1993年起向各军阶开放。','英国国防部现行指南将其列为表彰作战行动中卓越指挥与领导的奖励，现行规则不予追授。历史实物应按当时制度及具体记录理解。']
        elif fid=='GB-UK-MERITORIOUS-SERVICE-MEDAL':
            paragraphs.insert(0,'1845年设立，奖励资深军士的忠实、优异服务与良好品行。早期绶带为深红色，1916年加入白色边条和中条；图示为维多利亚女王时期旧式绶带版。')
        elif fid=='GB-UK-CORONATION-MEDAL-1953':
            paragraphs=['1953年伊丽莎白二世加冕纪念奖章。英国国防部官方指南将其列为历史奖项。']
        elif fid in ('GB-UK-ROYAL-NAVAL-RESERVE-DECORATION','GB-UK-RESERVE-LSGC-MEDAL-RN-RM','GB-UK-TERRITORIAL-DECORATION','GB-UK-EFFICIENCY-MEDAL-ARMY-RESERVE','GB-UK-AIR-EFFICIENCY-AWARD-RAAF'):
            paragraphs=['属于志愿预备役服务奖章统一制度以前的分军种预备役奖励。1999年4月1日前结束的合资格服役，仍可能按旧制度获授本奖项。']
        variants=[v for f in rows for v in f.get('variants',[])]
        refs=list({f['source_page']:{'title':'英国国防部：'+f['original'],'url':f['source_page']} for f in rows}.values())
        entries[fid]=dict(award_id=fid,canonical_name_zh=name,family_ids=[fid],match_names=list(dict.fromkeys([name]+[f['name_zh'] for f in rows]+[f['original'] for f in rows])),volume_pattern='^uk(?:-unpictured)?$',introduction_zh=paragraphs,sources=refs,variant_guidance=dict(period_forms=variants))
        for n,f in enumerate(rows):
            sid='UK-MOD-20260930-'+fid+'-'+str(n+1)
            sources[sid]=dict(page=f['source_page'],title=f['original'],summary=f['evidence_summary'],accessed='2026-09-30',license='Open Government Licence v3.0 (exceptions apply)',credit='Ministry of Defence')
            for r in pack['records']:
                if r['family']==fid and sid not in r['source_ids']:r['source_ids'].append(sid)
    new_records=[];new_images=[]
    for a in additions:
        r={k:v for k,v in a.items() if k!='images'}
        r.update(country_zh='英国／大英帝国',views=[],source_ids=[])
        for n,f in enumerate(grouped[r['family']]):r['source_ids'].append('UK-MOD-20260930-'+r['family']+'-'+str(n+1))
        for n,im in enumerate(a.get('images',[])):
            p=R/im['local_path']
            with Image.open(p) as pic:pic.verify()
            vk=r['id']+'-IMAGE-'+str(n+1);sid=vk+'-SOURCE'
            r['views'].append(dict(key=vk,label=im['label']));r['source_ids'].append(sid)
            new_images.append(dict(im,view_key=vk,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
            sources[sid]=dict(page=im['source_page'],title=im.get('title',r['name']),summary=im['evidence'],accessed='2026-09-30',license=im['license'],credit=im['artist'])
            intro=entries.get(r['family'])
            if intro and not any(s['url']==im['source_page'] for s in intro['sources']):intro['sources'].append(dict(title=im.get('title',r['name']),url=im['source_page']))
        new_records.append(r)
    save('data/volumes/uk_mod_pack1.json',pack)
    save('data/volumes/uk_mod_completion_20260930.json',dict(as_of='2026-09-30',records=new_records))
    save('data/volumes/uk_mod_completion_20260930_manifest.json',dict(images=new_images))
    save('data/sources.json',sources);intros['items']=list(entries.values());save('mobile/web/award-intros.json',intros)
    stats=dict(new_families=len({r['family'] for r in new_records}-baseline),new_pictured_families=len({r['family'] for r in new_records if r['views']}-baseline),new_variant_rows=len(new_records),new_pictured_variant_rows=sum(bool(r['views']) for r in new_records),new_complete_images=len(new_images),unpictured_rows=sum(not r['views'] for r in new_records),existing_image_rows_reviewed=len(review),guide_families_with_introductions=len(grouped)-2,total_uk_families=len(baseline|{r['family'] for r in new_records}))
    save('data/normalized/uk_mod_completion_20260930.json',stats)
    print(json.dumps(stats))

if __name__=='__main__':merge()
