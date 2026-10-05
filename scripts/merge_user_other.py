"""Reviewed visual references, isolated from source photographs and unresolved material."""
import json, hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image

R=Path(__file__).resolve().parents[1]
S=R/'data/staging/user_other_20261003'
def read(p): return json.loads((R/p).read_text('utf-8'))
def save(p,x): (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
inventory=read('data/staging/user_other_20261003/inventory.json')
by_number={x['number']:x for x in inventory}
soup=BeautifulSoup((R/'index.html').read_text('utf-8'),'html.parser')
sources=read('data/sources.json')
groups=[]
def add(n,base,variant,side='front'):
    tr=soup.find('tr',id=base)
    assert tr is not None,base
    section=tr.find_parent('section')
    groups.append(dict(numbers=n,base=base,volume=section['id'],family=tr['data-award-family'],
        name=tr.select_one('td.name strong').get_text(),original=tr.select_one('.original').get_text(),
        date=tr.select_one('.date').get_text(),variant=variant,side=side,
        source_ids=[x for x in tr.get('data-source-ids','').split(',') if x]))

add([6],'EGY-WAWARDS-MAJOR-12-ORDER-OF-THE-VIRTUES','第一型星章图式；蓝白花瓣与الكمال铭文；细分等级待考')
add([1],'EGY-MEDALS-ORG-MUHAMMAD-ALI-COMMANDER','后期六臂绿色珐琅挂章图式；细分等级待考')
add([5],'EGY-MEDALS-ORG-ISMAIL-COMMANDER','蓝色五角章体与冠形悬挂结构；指挥官式挂章参考，绶带未示')
add([10],'EGY-MEDALS-ORG-MUHAMMAD-ALI-SILVER-MEDAL','穆罕默德·阿里奖章背面图式；章面纪年1333；不据图推断实际材质','reverse')
add([14],'EGY-WAWARDS-MAJOR-03-ORDER-OF-MUHAMMAD-ALI','早期六臂挂章型；细分等级、制造商待考')
add([18],'EGY-WAWARDS-MAJOR-06-ORDER-OF-MUHAMMAD-ALI','后期放射式星章；六臂中心图式')
add([23],'EGY-WAWARDS-MAJOR-04-ORDER-OF-MUHAMMAD-ALI','早期放射式星章；六臂绿色中心图式')
add([27],'EGY-WAWARDS-MAJOR-02-ORDER-OF-ISMAIL','蓝色五角星章；金色格状放射图式，实际材质待考')
add([4],'KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA-MEDALBOOK-030','军官级绶带花结图式；金色放射章体参考')
add([19],'KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA-MEDALBOOK-030','军官级绶带花结图式；银色放射章体参考，色差不作为实际材质鉴定')
add([13],'TKM-AWARD-GOLDEN-CRESCENT-MEDAL-PORTRAIT','尼亚佐夫肖像型；金新月与红色铭牌图式')
add([9],'JPN-MB-071','大绶正章／佩挂章体；白色放射臂、红色中心与菊花悬挂图式；绶带未示')
add([21,20],'VNM-MB-021-V01','黑色十字佩挂章体；正面徽记／背面FEDERATION TAI；细分等级待考，正背未经证实为同一实物')
groups[-1]['page']='https://www.indochinamedals.com/tai_and_nung/tn01_order_of_civil_merit.html'
add([22],'VNM-MB-021-V01','大十字级星章图式；八组金色格状放射臂，实际材质待考')
groups[-1]['page']='https://www.indochinamedals.com/tai_and_nung/tn01_order_of_civil_merit.html'
add([24],'VNM-MB-067-V01','龙饰星章；红边蓝色汉字中心与银色放射臂；大十字／大军官细分等级待考')
# Newly pictured family: identification uses the four crowns, Damavand and rays,
# not the filename. 1925 is the Iranica date; differing catalog dates retained.
groups.append(dict(numbers=[17],base=None,volume='iran',family='IRN-ORDER-PAHLAVI',name='巴列维勋章',
    original='Nešān-e Pahlavī / Order of Pahlavi',date='1304太阳历／1925年设立（Iranica）；其他目录纪年有异',
    variant='四冠与达马万德山图式星章；一级／二级细分等级待考',side='front',source_ids=[],
    page='https://www.iranicaonline.org/articles/decorations/'))
groups.append(dict(numbers=[26],base=None,volume='annam-protectorate',family='ANNAM-ORDER-AGRICULTURAL-MERIT',name='安南农业功绩勋章',
    original='Ordre du Mérite Agricole / Order of Agricultural Merit',date='20世纪使用；设立日期待考',
    variant='指挥官式领绶挂章参考；蓝色回纹方形边框、稻穗与红色日轮；具体等级及制造亚型待考',side='front',source_ids=[],
    page='https://www.emering.com/medals/french/annam.html'))

records=[];images=[];audit=[];volume_rows={}
for i,g in enumerate(groups,1):
    rid=g['family']+'-USER-OTHER-20261003-'+str(i).zfill(2)
    sid=rid+'-SOURCE'
    page=g.get('page') or next((sources[s].get('page') for s in g['source_ids'] if s in sources),None)
    summary=g['variant']+'。已与本项目存档完整照片／对象页图式对照。用户处理图仅作型制参考，不能用于鉴定材质、真伪、微型变体或具体颁发日期。'
    if g['family']=='IRN-ORDER-PAHLAVI':summary+=' Iranica：四冠、达马万德山与升日；1925年设立。MedalBook记1926，差异保留。'
    sources[sid]=dict(page=page,title=g['name']+'：用户修复参考图核对',summary=summary,accessed='2026-10-03',
        license='User supplied for local project; underlying image origin and republication rights not established.',credit='用户提供')
    views=[]
    for j,n in enumerate(g['numbers']):
        im=by_number[n];path=R/im['local_path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==im['sha256']
        with Image.open(path) as picture:picture.verify()
        side='reverse' if g['side']=='reverse' or j else 'front'
        vk=rid+'-V'+str(j+1)
        label='参考·'+('背面型制参考' if side=='reverse' else '正面')
        if j:label+='（不同实物配对未核）'
        views.append(dict(key=vk,label=label))
        images.append(dict(view_key=vk,local_path=im['local_path'],original_path=im['local_path'],source_page=page,
            width=im['width'],height=im['height'],sha256=im['sha256'],image_kind='user_restored_reference',
            processing='用户修复参考图（非来源摄影原图）',provenance_source_file=im['source_file'],license=sources[sid]['license'],accessed='2026-10-03'))
        audit.append(dict(number=n,status='accepted_processed_reference',record_id=rid,family=g['family'],
            compared_record_id=g['base'],variant=g['variant'],side=side,source_page=page,sha256=im['sha256']))
    records.append(dict(id=rid,family=g['family'],name=g['name'],original=g['original'],date=g['date'],
        variant=g['variant']+'；参考',views=views,source_ids=g['source_ids']+[sid],image_kind='user_restored_reference',**({'supersedes_id':g['base']} if g['base'] else {})))
    volume_rows.setdefault(g['volume'],[]).append(rid)
used={a['number'] for a in audit}
held={2:'掌叶、雪松中心图式，具体黎巴嫩奖励等级及原始对象依据未确认',3:'四臂神像与环饰图式，授予主体及章種待核',
6:'蓝白花形章体与阿拉伯文中心，尚无对应对象依据',7:'金色八角几何星章，尚无对应对象依据',8:'王储Savang纪念章背面，缺对应正面及版型依据',
11:'中央绿色纹样与放射章体，正背关联及章种待核',12:'单独星章背面，无确定章种及等级依据',15:'与3相近四臂神像图式，来源及章种待核',
16:'红色汉字中心与放射章体，不与现有龙章挂饰形制直接对应',25:'国徽中心星章，授予主体及版型待核',
26:'疑似安南农业功绩勋章，来源图片访问403，尚未完成对象图片核对',28:'缅文中心十二芒星章，缺完整对象图片依据'}
for im in inventory:
    if im['number'] not in used:audit.append(dict(number=im['number'],status='held_for_verification',reason=held.get(im['number'],'对应关系待核'),sha256=im['sha256']))
save('data/volumes/user_other_20261003.json',dict(as_of='2026-10-03',records=records))
save('data/volumes/user_other_20261003_manifest.json',dict(images=images))
save('data/volumes/user_other_20261003_integration.json',dict(volume_rows=volume_rows))
save('data/staging/user_other_20261003/review.json',dict(as_of='2026-10-03',items=sorted(audit,key=lambda x:x['number'])))
save('data/sources.json',sources)
stats=dict(input_files=len(inventory),accepted_reference_images=len(images),reference_rows=len(records),matched_families=len({r['family'] for r in records}),new_independent_families=2,new_source_photographs=0,held_files=len(inventory)-len(used))
save('data/normalized/user_other_20261003.json',stats)
print(json.dumps(stats))
