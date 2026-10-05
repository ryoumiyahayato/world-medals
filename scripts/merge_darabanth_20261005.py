"""Review-selected full objects, with cases and repeated same-type specimens excluded."""
from pathlib import Path
import json, hashlib, collections
from PIL import Image
R=Path(__file__).resolve().parents[1]
def lines(path):return [json.loads(x) for x in (R/path).read_text(encoding='utf-8').splitlines() if x.strip()]
def save(path,value):(R/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=lines('data/source_sweeps/darabanth_46_faleristics_20261005_lot_review.jsonl')
families={x['family_proposal_id']:x for x in lines('data/normalized_drafts/darabanth_46_faleristics_20261005_families.jsonl')}
names=['劳动红旗勋章','劳动功绩奖章','四月四日功绩勋章','匈牙利人民共和国星勋章','匈牙利共和国功绩勋章','警察服役荣誉章','边防服役荣誉章','消防服役荣誉章','民防服役荣誉章','公共服务功绩章','塞迈赖·拜尔陶隆功绩章','圣乔治功绩章','圣拉迪斯劳斯功绩章','圣弗洛里安功绩章','防洪服务荣誉章','肖普朗音乐协会歌唱徽章','托勒克圣米克洛什志愿消防二十五周年纪念章','匈牙利青年红十字会徽章','献血者徽章','匈牙利童军帽徽','加冠红十字花环徽章','青年红十字会功绩奖章','青年红十字会纪念章','匈牙利红十字会荣誉章','南匈牙利公共文化协会徽章','月桂花环优秀劳动者奖章','月桂花环优秀技术劳动者奖章','匈牙利声誉奖奖杯','团结勋章','布加勒斯特世界青年节游泳奖章','仁慈圣母修会荣誉十字章']
assert len(names)==len(families)
names=dict(zip(families,names))
cross={'HUN-RED-FLAG-ORDER-OF-LABOUR':'HUN-ORDER-OF-RED-BANNER-OF-LABOUR','HUN-ORDER-OF-MERIT-REPUBLIC':'HUN-ORDER-OF-MERIT-HUNGARIAN-REPUBLIC','HUN-BORDER-GUARD-SERVICE-DECORATION':'HUN-BORDER-GUARDS-SERVICE-DECORATION'}
# These repeat already selected grades/configurations without a documented new type.
held={'30835':'Same police ten-year configuration as 30834','30851':'Same flood-prevention configuration as 30850','30864':'Same silver-plated bronze male ribbon type as 30863','30873':'Award trophy, not a medal; retained as raw material','30829':'Sword overlay damaged/incomplete; retained as damaged-object research reference'}
labels={
'30825':'铜质镀金、珐琅；绶带挂章；等级待考', '30826':'铜质、珐琅；绶带挂章', '30827':'铜质镀金、珐琅；绶带挂章',
'30828':'金色花环附饰；铜质镀金、珐琅', '30830':'无花环、无剑附饰；铜质镀金、珐琅', '30831':'军官十字章、民事类；镀金及珐琅；配勋表及微型章',
'30843':'金级；铜质镀金、珐琅', '30844':'银级；铜质镀银、珐琅', '30845':'铜级；铜质、珐琅',
'30852':'歌唱徽章；珐琅金属；39×47毫米；BELADÁ制造标记', '30853':'二十五周年纪念章；悬挂式；材质待考',
'30854':'青年部门胸徽；铜质、珐琅；竖直背针；BERÁN BPEST制造标记；25×19毫米', '30855':'三种献血者小徽章合图；铜质、珐琅；13×13毫米；有珐琅缺损',
'30856':'青年部门胸徽；铜质、珐琅；竖直背针；20×17毫米', '30857':'童军帽徽；铜质；45×35毫米', '30858':'加冠花环型；镀金、珐琅；斜背带；60×44毫米',
'30859':'银质、有边缘印记；女性蝴蝶结绶带；31毫米；边缘损伤', '30860':'铜质；三角绶带；31毫米', '30861':'铜质镀金；三角绶带；31毫米；边缘损伤',
'30862':'铜质镀金；女性蝴蝶结绶带；31毫米', '30863':'铜质镀银；边缘BRONZE标记；三角绶带；31毫米', '30865':'铜质、无悬挂耳；纪念章；31毫米；边缘损伤',
'30866':'铜质镀银；女性蝴蝶结绶带；31毫米；边缘损伤、轻微弯曲', '30867':'铜质；女性蝴蝶结绶带；31毫米', '30868':'青年部门帽徽；铜质、珐琅；BERÁN制造标记；30×45毫米；珐琅修补',
'30869':'铜质镀金、珐琅；62×62毫米主章及24×24毫米微型章合图；微型章附饰松动', '30870':'纽孔徽章；珐琅金属；HAVAS制造标记；17×13毫米；背带锈斑',
'30871':'月桂花环型；珐琅金属；拉科西时期国徽', '30872':'月桂花环型；珐琅金属；拉科西时期国徽', '30874':'金属挂章；原绶带；背针缺失',
'30875':'游泳赛事型；铜质镀银；绶带挂章；镀银磨损', '30876':'大十字型（按来源名称）；铜质镀金、珐琅；55×88毫米', '30877':'十字挂章；铜质镀金、珐琅；45×71毫米'}
for lot,years in [('30832',30),('30833',20),('30834',10),('30836',30),('30837',30),('30838',20),('30839',10),('30840',30),('30841',20),('30842',10)]:labels[lot]=f'{years}年服役型；银质、有印记；配勋表及微型章'
for lot in ('30846','30847','30848','30849'):labels[lot]='铜质镀金、珐琅；配勋表及微型章'
labels['30850']='绶带挂章；配勋表；材质待考'
main=[];related=[];mi=[];ri=[];integration=collections.defaultdict(list)
sources=json.loads((R/'data/sources.json').read_text(encoding='utf-8'))
for row in rows:
    lot=row['catalogue_lot']
    if lot in held:continue
    family=families[row['family_proposal_id']];fid=cross.get(row['family_proposal_id'],row['family_proposal_id'])
    formal=family['editorial_category']=='formal_award_candidate'
    rid='DAR46-'+lot;sid=rid+'-SOURCE'
    # The first images show the object; actual reverse is selected only after visual review.
    count=2 if (int(lot) in (30826,30827,30828,30830,30831,30850) or 30852<=int(lot)<=30870 and lot!='30855' or lot in ('30871','30874','30875')) else 1
    if lot=='30877':count=2
    views=[];dest=mi if formal else ri
    for n,image in enumerate(row['local_images'][:count]):
        with Image.open(R/image['path']) as im:im.load();size=im.size
        assert hashlib.sha256((R/image['path']).read_bytes()).hexdigest()==image['sha256']
        label='完整正面' if n==0 else ('另一视图（同一拍品）' if lot=='30877' else '完整背面（同一拍品）')
        key=rid+'-VIEW'+str(n+1);views.append(dict(key=key,label=label))
        dest.append(dict(key=key.lower(),record_id=rid,view_key=key,local_path=image['path'],source_page=row['object_page'],image_url=image['url'],object_reference='46th Major Auction lot '+lot,dimensions=size,sha256=image['sha256'],decoded=True,visually_checked=True,artist='Darabanth Auction House',license='No publication license located; private research only',publication_eligible=False))
    date='来源标年：'+', '.join(row['date_candidates'])+'；非具体颁发日期' if row['date_candidates'] else '待考'
    country='古巴' if lot=='30874' else ('罗马尼亚·青年节赛事' if lot=='30875' else ('西班牙·仁慈圣母修会' if lot in ('30876','30877') else '匈牙利'))
    if int(lot)<=30830 or lot in ('30871','30872'):country='匈牙利人民共和国'
    elif 30831<=int(lot)<=30851:country='匈牙利共和国'
    record=dict(id=rid,family=fid,name=names[row['family_proposal_id']],original=family['name_original'],country_zh=country,date=date,variant=labels[lot],views=views,source_ids=[sid],html_eligible=True,body_eligible=True,publication_eligible=False,evidence=[dict(source_page=row['object_page'],object_reference='lot '+lot,accessed_at='2026-10-05',source_excerpt=row['description_original'])])
    (main if formal else related).append(record)
    if formal:integration['cuba' if lot=='30874' else 'hungary'].append(rid)
    sources[sid]=dict(page=row['object_page'],title=row['page_title'],summary=row['description_original'],object_id=lot,accessed='2026-10-05',credit='Darabanth Auction House',license='No publication license located; private research only')
save('data/volumes/darabanth_20261005.json',dict(as_of='2026-10-05',records=main))
save('data/volumes/darabanth_20261005_manifest.json',dict(images=mi))
save('data/volumes/darabanth_20261005_integration.json',dict(volume_rows=dict(integration)))
save('data/volumes/darabanth_related_20261005.json',dict(records=related))
save('data/volumes/darabanth_related_20261005_manifest.json',dict(images=ri))
save('data/sources.json',sources)
save('data/checkpoints/darabanth_merge_20261005.json',dict(main_variant_rows=len(main),main_family_count=len({x['family'] for x in main}),new_main_families=len({x['family'] for x in main}-set(cross.values())),related_rows=len(related),related_families=len({x['family'] for x in related}),accepted_views=len(mi)+len(ri),held_lots=held))
print('Formal rows',len(main),'related rows',len(related),'accepted views',len(mi)+len(ri))
