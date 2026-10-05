"""Reviewed user illustrations supplement source-backed families; never replace evidence originals."""
import json,hashlib,re
from pathlib import Path
from collections import defaultdict
from PIL import Image
R=Path(__file__).resolve().parents[1];S=R/'data/staging/user_soviet_20261003'
def load(p):return json.loads((R/p).read_text('utf-8'))
def save(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
inventory=load('data/staging/user_soviet_20261003/inventory.json');by_number={x['number']:x for x in inventory}
intros=load('mobile/web/award-intros.json');intro_index={x['award_id']:x for x in intros['items']}
existing=defaultdict(list)
for p in (R/'data/volumes').glob('*.json'):
 if p.name.startswith('user_soviet'):continue
 data=json.loads(p.read_text('utf-8-sig'))
 if isinstance(data,dict) and isinstance(data.get('records'),list):
  for r in data.get('records',[]):
   if r.get('family','').startswith(('USSR-','RSFSR-')):existing[r['family']].append(r)
gap=next(x for x in load('data/unpictured.json') if x.get('family')=='USSR-TITLE-HONOURED-TEST-NAVIGATOR')
existing[gap['family']].append(dict(gap,source_ids=[]))
groups=[]
def add(f,nums,variant,period=None):groups.append(dict(family=f,numbers=nums,variant=variant,period=period))
def med(i,nums,v='章体图式；细分铸模与吊耳亚型待考',period=None):add(f'USSR-MED-{i:02}',nums,v,period)
def order(i,nums,v,period=None):add(f'USSR-ORD-{i:02}',nums,v,period)
# Every selected image was inspected in numbered contact sheets. Reverse references
# share a design group only; this is not evidence that they depict the same specimen.
med(22,[1,4]);med(23,[2,3]);med(24,[5,6]);med(25,[7,8]);med(26,[9,10])
med(14,[11]);med(15,[12]);med(16,[13]);med(17,[14]);med(18,[16]);med(19,[17]);med(20,[18]);med(21,[19,20])
med(3,[21,22]);med(5,[23,24],'早期矩形挂板式；具体模具亚型待考','1938–1943年主要佩带结构')
med(4,[25,26],'早期矩形挂板式；具体模具亚型待考','1938–1943年主要佩带结构')
med(4,[27,28],'1943年以后吊耳悬挂式；图中绶带未完整呈现','1943年以后')
med(2,[29,30],'后期吊耳悬挂式；挂板未示；编号与吊耳亚型待考')
med(9,[31,32]);med(10,[33,34],'一级型式；矩形专用挂板与星形章体')
med(10,[35,36],'二级型式；矩形专用挂板与星形章体')
med(11,[37]);med(12,[38]);med(13,[39])
med(54,[40,41],'二级型式；母子肖像章体，挂板未示')
med(54,[42,43],'一级型式；母子肖像章体，挂板未示')
med(55,[44,45],'一级／20年服役；苏联武装力量背文型；部门及制造亚型待考')
med(55,[46,47],'二级／15年服役；苏联武装力量背文型；部门及制造亚型待考')
med(55,[48,49],'三级／10年服役；苏联武装力量背文型；部门及制造亚型待考')
add('USSR-MED-PUBLIC-ORDER-SERVICE',[50,51],'苏联国徽正面型；细分材质与铸造亚型待考')
med(38,[55,54],'消防救人正面／斧锤背面图式；挂板未示')
med(39,[56,57]);med(40,[58,59],'劳动功绩背文型；章体图式，专用挂板未示')
med(32,[60,61]);med(33,[62,63]);med(34,[64,65]);med(35,[66,67]);med(36,[68,69]);med(50,[70,71]);med(51,[72,73]);med(52,[74,75]);med(53,[76,77])
med(41,[78,79]);med(42,[80,81],'参战者背文型；章体图式，完整绶带未示')
med(43,[82,83],'参战者背文型；章体图式，完整绶带未示')
med(44,[84,85],'早期矩形挂板式；背面1918–1938纪年','1938–1943年主要佩带结构')
med(44,[86,87],'1943年以后五角挂板式；背面1918–1938纪年','1943年以后')
med(27,[88,89]);med(28,[90,91]);med(29,[92,93]);med(30,[95,94]);med(31,[96,97])
order(1,[98],'第一型“拖拉机”图式；背面未配，制造细分待考','1930–1934年')
order(1,[101],'第二型红旗、红星图式；整体一体肖像，背面未配','1934–1936年')
order(1,[103],'独立肖像部件的螺杆式图式；细分亚型待考','1936–1943年')
order(1,[105,107],'吊耳悬挂式、较圆章体参考；正背未证实为同一实物','1943年以后')
order(1,[106,108],'吊耳悬挂式、较椭圆章体参考；正背未证实为同一实物','20世纪50年代以后')
order(2,[112,113],'悬挂式；三铆钉背面参考，细分亚型待考')
order(2,[114,115],'悬挂式；多铆钉背面参考，细分亚型待考')
order(3,[116],'正面整体图式；宝石、材质、制造及真伪不可由修复图确定')
add('RSFSR-ORD-01',[117],'俄罗斯苏维埃联邦社会主义共和国前身；正面Р.С.Ф.С.Р铭文；背面及制造亚型待考')
add('RSFSR-ORD-01',[118],'俄罗斯苏维埃联邦社会主义共和国前身；重复获授数字2型；制造亚型待考')
order(4,[119],'СССР铭文型；固定结构与细分亚型待考')
order(4,[120],'重复获授数字2型；固定结构及细分亚型待考')
order(4,[121],'重复获授数字3型；固定结构及细分亚型待考')
order(4,[122],'重复获授数字4型；固定结构及细分亚型待考')
order(4,[123],'吊耳悬挂式、重复获授数字6型；细分亚型待考')
order(4,[124],'吊耳悬挂式、重复获授数字7型；细分亚型待考')
order(16,[126,127],'一级型式；克里姆林宫塔楼正面、СССР背文；绶带未示')
order(16,[128,129],'二级型式；金色中央章面设计参考；实际材质不据修复图判断')
order(16,[130,131],'三级型式；单色中央章面设计参考；实际材质不据修复图判断')
order(12,[136],'一级早期悬挂式；背面未配','1942–1943年主要佩带结构')
order(12,[137,138],'一级螺杆固定式；战时分体结构参考；细分制造亚型待考','1943年以后')
order(12,[139,141],'二级早期悬挂式；长条连接件背面参考','1942–1943年主要佩带结构')
order(12,[144],'二级螺杆固定式外观；缺背面，战时／1985纪念版待考')
order(9,[142,143],'一级图式；螺杆固定与分体结构参考')
order(9,[145],'二级图式；背面未配')
order(10,[146,151],'二级图式；螺杆固定背面参考')
order(10,[154],'一级图式；背面未配')
order(8,[148,150],'早期矩形挂板悬挂式；长条连接件背面参考','1942–1943年主要佩带结构')
order(8,[152,153],'螺杆固定式；三铆钉结构背面参考','1943年以后')
order(7,[156,157],'一级图式；分体螺杆结构背面参考')
order(7,[158,159],'二级图式；螺杆固定背面参考')
order(7,[160,161],'三级图式；螺杆固定背面参考')
order(6,[162,163],'一级图式；分体螺杆结构背面参考')
order(6,[164,165],'二级早期矩形挂板悬挂式','1942–1943年主要佩带结构')
order(6,[166,167],'二级螺杆固定式','1943年以后')
order(6,[168],'三级螺杆固定式；背面未配','1943年以后')
order(6,[171,173],'三级早期矩形挂板悬挂式；背面参考','1943年主要佩带结构')
order(5,[174,175],'一级早期矩形挂板悬挂式','1942–1943年主要佩带结构')
order(5,[176,177],'一级螺杆固定式','1943年以后')
order(5,[178,179],'二级早期矩形挂板悬挂式','1942–1943年主要佩带结构')
order(5,[180,181],'二级螺杆固定式','1943年以后')
order(11,[182,183],'早期正面士兵图式；背面ГОЗНАК印记参考；细分亚型待考')
order(11,[184,185],'螺杆式；背面无制造铭文参考，细分亚型待考')
order(11,[186,187],'螺杆式；背面МОНЕТНЫЙ ДВОР双行铭文参考')
order(11,[188,189],'螺杆式；背面制造铭文位于螺杆上方参考')
order(13,[192,193],'早期三角红星与齿轮图式；背面МОНДВОР参考，亚型待考')
order(13,[194,195],'红旗／蓝色水面图式；螺杆固定参考，亚型待考')
order(13,[196,197],'红旗／蓝色水面图式；多铆钉螺杆背面参考')
order(13,[198,199],'吊耳悬挂式；平背参考，细分亚型待考')
order(13,[200,201],'吊耳悬挂式；凹背参考，细分亚型待考')
order(15,[202,203],'荣誉徽章：螺杆式；背面МОНДВОР铭文参考')
order(15,[204,205],'荣誉徽章：吊耳悬挂式；平背参考')
order(15,[206,207],'荣誉徽章：吊耳悬挂式；凹背参考')
order(15,[208,209],'1988年更名后的“荣誉勋章”型；取消ЗНАК ПОЧЕТА、增添镰锤附饰','1988–1991年')
order(14,[210,211],'苏联国徽与СССР铭文型；背面参考')
order(20,[214,218],'一级图式；螺杆固定背面参考')
order(20,[215],'二级图式；背面未配')
order(20,[216],'三级图式；背面未配')
order(19,[217,219],'一级图式；红色中央背景')
order(19,[221,222],'二级图式；蓝色中央背景')
order(19,[223,224],'三级图式；银色中央背景')
order(21,[225,226],'苏联型：下部СССР红色铭牌；背面参考')
add('USSR-HON-07',[231],'功勋军事飞行员称号徽章；红色挂板、飞机图式，铭文细节待核')
order(17,[233],'二级；蓝色旗面与II标记；挂板局部结构待核')
order(17,[234],'一级；红色旗面与I标记；挂板未示')
order(17,[236],'三级；III标记；挂板未示')
add('USSR-HON-15',[235,229],'苏联人民艺术家称号徽章；专用红色挂板；背面参考')
med(1,[238,239],'早期三角挂板式；背面编号参考','1938–1943年主要佩带结构')
med(1,[240],'后期吊耳悬挂式；挂板未示','1943年以后')
med(6,[241,242],'章体与锚形结构；上部链饰／完整绶带未示，暂不作为完整佩戴图')
med(7,[243,244]);med(8,[245],'一级图式；细分制造亚型待考')
med(8,[246],'二级图式；细分制造亚型待考')
med(45,[257,258]);med(46,[259,260]);med(47,[261,262]);med(48,[263,264]);med(49,[265,266])
add('USSR-TITLE-HONOURED-TEST-NAVIGATOR',[230,232],'功勋试飞领航员称号佩章；蓝色专用挂板；铭文与螺杆背面型制参考','1958年设立；1960年修订图式')
used={n for g in groups for n in g['numbers']}
duplicates={247:21,248:22,249:23,250:24,251:25,252:26,253:27,254:28,255:29,256:30,220:208,99:98,102:101,104:103,132:130,134:130,190:188}
held={15:'多枚保卫奖章共有背文；不能仅凭通用铭文关联某一正面',52:'出现РСФСР国徽而对应奖励为苏联；需核原始来源与图式',53:'正面52归属待核，暂不配对',100:'旗面颜色与已核第二型图式不符，修复颜色待核',109:'背面缺前图及制造结构信息，无法判定版型',110:'列宁早期背面参考；未确认与98对应的同一版型／实物',111:'列宁早期背面参考；未确认与101对应的同一版型／实物',125:'РСФСР数字3前身型需要独立对象依据，先保留待核',133:'光荣勋章背面；无法确定一级／二级／三级关联',135:'光荣勋章背面；无法确定等级关联',140:'背面有W.MILLER标记，复制／私人制造属性未核',147:'单独背面，无法确定纳希莫夫勋章等级关联',149:'单独早期背面，章种／等级关联未核',155:'背面有S.D.字样，复制或私人制造属性未核',169:'苏沃洛夫图式的中心环颜色与标准等级图式存在疑点',170:'与169关联未核',172:'单独指挥勋章背面，等级／章种关联待核',191:'重复正面188之外的单独背面；不新增版型',212:'非苏联国徽且无СССР铭牌，疑似1992年后俄罗斯型；移至归属待核',213:'与212归属同待核',227:'没有СССР铭牌，疑似1992年后俄罗斯个人英勇勋章型；不入苏联',228:'与227归属同待核',230:'试验领航员称号确有苏联记录，但图中铭文／挂板颜色与原站图式对应尚未确认',232:'单独称号徽章背面，无足够同型对应依据',237:'母亲光荣单独背面，无法确定等级关联'}
records=[];images=[];sources=load('data/sources.json');audit=[]
for gi,g in enumerate(groups,1):
 fid=g['family'];base=next(iter(existing[fid]),None);intro=intro_index.get(fid)
 if not base:
  raise ValueError('Missing existing family '+fid)
 rid=fid+'-USER-REF-20261003-'+str(gi).zfill(3)
 refs=(intro or {}).get('sources',[]);url=next((x['url'] for x in refs if 'mondvor.narod.ru' in x.get('url','')),None)
 if not url: url=next((sources[s].get('page') for s in base.get('source_ids',[]) if s in sources and 'mondvor.narod.ru' in sources[s].get('page','')),None)
 url={'RSFSR-ORD-01':'https://mondvor.narod.ru/ORBan.html','USSR-HON-07':'https://mondvor.narod.ru/pzvoenlet.htm','USSR-HON-15':'https://mondvor.narod.ru/pznarart.htm'}.get(fid,url)
 if fid=='USSR-TITLE-HONOURED-TEST-NAVIGATOR':url='https://mondvor.narod.ru/pzletispitat.htm'
 sid=rid+'-SOURCE'
 sources[sid]=dict(page=url or 'https://mondvor.narod.ru/',title=base['name']+'：用户修复参考图及版型对照',summary=g['variant']+'。用户于2026年10月3日提供处理图；已按整体图式和可见结构对照，细微工艺、实际材质、真伪及实物配对未经证实。',accessed='2026-10-03',license='User-supplied processed references for this local project; underlying original image provenance and republication rights not established.',credit='用户提供的修复参考图')
 views=[]
 for vi,n in enumerate(g['numbers']):
  im=by_number[n];vk=rid+'-V'+str(vi+1)
  label='用户修复参考图·'+('正面' if vi==0 else '背面型制参考（未经证实为同一实物）')
  views.append(dict(key=vk,label=label))
  images.append(dict(view_key=vk,local_path=im['local_path'],original_path=im['local_path'],original_url=None,source_page=url or 'https://mondvor.narod.ru/',width=im['width'],height=im['height'],sha256=im['sha256'],artist='用户提供',license=sources[sid]['license'],image_kind='user_restored_reference',processing='用户修复参考图（非来源摄影原图）',provenance_source_file=im['source_file'],visual_review='完整章体轮廓已审；未从处理图推断材质、真伪或具体颁发日期；无实物配对保证',accessed='2026-10-03'))
  audit.append(dict(number=n,family=fid,record_id=rid,view='front' if vi==0 else 'reverse_design_reference',status='accepted_processed_reference',variant=g['variant'],source_page=url,sha256=im['sha256']))
 date=re.sub(r'（Wikipedia总表日期；非具体实物颁发日）','',base['date'])
 if g['period']:date+='；所示型式：'+g['period']
 original=next((x for x in (intro or {}).get('match_names',[]) if re.search('[А-Яа-я]',x)),base['original'])
 records.append(dict(id=rid,family=fid,name=(intro or {}).get('canonical_name_zh',base['name']),original=original,date=date,variant=g['variant']+'；用户修复参考图',views=views,source_ids=[sid],image_kind='user_restored_reference'))
for im in inventory:
 n=im['number']
 if n in used:continue
 audit.append(dict(number=n,sha256=im['sha256'],status='duplicate_reference' if n in duplicates else 'held_for_verification',duplicate_of=duplicates.get(n),reason='同型近似处理图不重复计为新版型' if n in duplicates else held.get(n,'未确认型式对应关系；保留待核')))
save('data/volumes/user_soviet_20261003.json',dict(as_of='2026-10-03',scope='User processed design references; source photographs preserved separately',records=records))
save('data/volumes/user_soviet_20261003_manifest.json',dict(images=images))
save('data/staging/user_soviet_20261003/review.json',dict(as_of='2026-10-03',method='All 23 contact sheets inspected by root; structural matches and captions cross-referenced to existing source-backed families. No photographic authenticity claim.',items=sorted(audit,key=lambda x:x['number'])))
save('data/sources.json',sources)
# Explicit reviewed links for timeline thumbnails; no name-based image guessing.
timeline_links={'USSR-ORD-01':{0:98,1:101,2:103,3:105,4:106},'USSR-ORD-12':{0:136,1:137},'USSR-ORD-15':{2:204,3:206,4:208}}
number_to_record={n:r['id'] for g,r in zip(groups,records) for n in g['numbers']}
for fid,links in timeline_links.items():
 forms=intro_index[fid].get('variant_guidance',{}).get('period_forms',[])
 for i,n in links.items():
  if i<len(forms):forms[i]['reference_record_id']=number_to_record[n]
save('mobile/web/award-intros.json',intros)
stats=dict(input_files=len(inventory),new_independent_families=0,reference_variant_rows=len(records),accepted_reference_images=len(images),matched_families=len({r['family'] for r in records}),duplicate_files=len(duplicates),held_files=len(inventory)-len(used)-len(duplicates),new_source_photographs=0)
save('data/normalized/user_soviet_20261003.json',stats);print(json.dumps(stats))
