import json,re,hashlib,io
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
import requests
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'data/staging/austria_republic_20261005'
v=json.loads((P/'volume_draft.json').read_text(encoding='utf-8'));m=json.loads((P/'manifest_draft.json').read_text(encoding='utf-8'));raw=[json.loads(x) for x in (P/'raw_candidates.jsonl').read_text(encoding='utf-8').splitlines()];source={re.search(r'republic(\d+)\.htm',x['object_page'])[1]:x for x in raw}
mapnew={'019':('AUT-FAM-AUR-018','奥地利共和国功绩奖章'),'020':('AUT-FAM-AUR-018','奥地利共和国功绩奖章'),'024':('AUT-FAM-AUR-012','武装力量行动奖章'),'025':('AUT-FAM-AUR-012','武装力量行动奖章'),'026':('AUT-FAM-AUR-012','武装力量行动奖章'),'031':('AUT-REP-FIRE-BRIGADE-MERIT-CROSS','奥地利消防联合会功绩十字章'),'033':('AUT-REP-RED-CROSS-MERIT-CROSS','奥地利红十字会功绩十字章'),'034':('AUT-REP-FIRE-BRIGADE-MERIT-DECORATION','奥地利消防联合会功绩章'),'052':('AUT-REP-FIRE-BRIGADE-INTERNATIONAL-COOPERATION','奥地利消防联合会国际合作奖章'),'053':('AUT-REP-FIRE-BRIGADE-DISASTER-RELIEF','奥地利消防联合会救灾功绩章'),'035':('AUT-REP-RED-CROSS-MERIT-MEDAL','奥地利红十字会功绩奖章'),'036':('AUT-REP-RED-CROSS-BLOOD-SERVICE','奥地利红十字会献血事业功绩奖章'),'037':('AUT-REP-RED-CROSS-BLOOD-DONATION','奥地利红十字会长期献血奖章'),'030':('AUT-REP-BLUE-HELMETS-DECORATION','奥地利蓝盔联合会荣誉章'),'048':('AUT-REP-CARINTHIA-BORDER-1991','克恩顿州1991年边境部署纪念章'),'049':('AUT-REP-OLRG-HONOUR-CROSS','奥地利救生协会荣誉十字章')}
nums=['','一','二','三','四','五','六','七','八','九','十','十一','十二']
replace={'Cross of Honour Class 1':'一级荣誉十字章','Cross of Honour (Female)':'荣誉十字章·女式','Insignia for Women':'女式挂章','Female insignia':'女式挂章','Male insignia':'男式挂章','Grand Cross of Merit':'功绩大十字章','Cross of Merit Class 1':'一级功绩十字章','Cross of Merit':'功绩十字章','Gold Medal with Gold Wreath':'金级奖章·金级花环','Gold Medal with Silver Wreath':'金级奖章·银级花环','Gold Medal with Bronze Wreath':'金级奖章·铜级花环','Gold Medal':'金级奖章','Silver Medal':'银级奖章','Bronze Medal':'铜级奖章','Commander with Star: Badge':'星章指挥官级挂章','Commander with Star: Star':'星章指挥官级星章','Commander':'指挥官级挂章','Knight Cross in Gold':'金级骑士十字章','Knight Cross in Silver':'银级骑士十字章','Officer':'军官级','Star':'星章','Badge':'挂章','Gold':'金级','Silver':'银级','Male':'男式','Female':'女式','Köflach':'克夫拉赫','Treviso':'特雷维索','Friuli':'弗留利','Gemona':'杰莫纳','Dalmatia':'达尔马提亚','Algeria':'阿尔及利亚','Bulgaria':'保加利亚','Romania':'罗马尼亚','Macedonia':'马其顿'}
def translate(cap):
 cap=re.sub(r',?\s*[Oo]bverse','',cap).strip(', ')
 for en,zh in replace.items():cap=cap.replace(en,zh)
 cap=re.sub(r'Class (\d+)',lambda z:nums[int(z[1])]+'级' if int(z[1])<len(nums) else z[0],cap)
 cap=re.sub(r'Type (\d+)',lambda z:'第'+nums[int(z[1])]+'型',cap)
 return cap.replace(':','·').replace('(','·').replace(')','') or '完整正面'
held=[];keep=[]
for r in v['records']:
 n=re.search(r'WMI-(\d+)-',r['id'])[1];cand=source[n]
 if r['id'] in ['AUT-REP-WMI-043-01','AUT-REP-WMI-043-02','AUT-REP-WMI-003-03']:
  r['hold_reason']='Collar extends beyond both image borders' if n=='043' else 'Bottomtipborderambiguity; completealternatepreferable';held.append(r);continue
 if r['id']=='AUT-REP-WMI-035-04':continue # Mislabelled reverse, moved into03.
 if n in mapnew:r['family'],r['name']=mapnew[n]
 cap=r['evidence'][0]['image_reference'];r['variant']=translate(cap)+'；低清参考'
 if n in ['019','020']:r['variant']=('银级；' if n=='019' else '铜级；')+r['variant']
 if n in ['024','025','026']:r['variant']={'024':'国内公共秩序行动','025':'自然灾害救援行动','026':'海外行动'}[n]+'；低清参考'
 if n=='012':r['variant']='军事防卫行动·第二型；低清参考'
 if n=='014':r['variant']='二级；完全康复的负伤；低清参考'
 if n=='050':r['variant']='二级；执法人员负伤·完全康复；低清参考';r['evidence'][0]['caption_correction']='Source050-03altincorrectClass1; containingtablerowexplicitlyClass2';r['evidence'][0]['image_reference']='Class2,Obverse (tablecontext corrects alt)'
 if n=='053':r['variant']=translate(cap)+'救灾饰牌；低清参考'
 if n in ['031','034','052','053']:r['awarding_authority']='奥地利消防联合会';r['country_zh']='奥地利·消防联合会';r['category']='行业团体奖励附编'
 elif n in ['033','035','036','037']:r['awarding_authority']='奥地利红十字会';r['country_zh']='奥地利·红十字会';r['category']='慈善团体奖励附编'
 elif n=='030':r['awarding_authority']='奥地利蓝盔联合会';r['country_zh']='奥地利·蓝盔联合会';r['category']='社团奖励附编'
 elif n=='049':r['awarding_authority']='奥地利救生协会（ÖLRG）';r['country_zh']='奥地利·救生协会';r['category']='救生团体奖励附编'
 elif n=='048':r['awarding_authority']='克恩顿州';r['country_zh']='奥地利·克恩顿州';r['category']='地方正式纪念授奖'
 else:r['awarding_authority']='奥地利共和国';r['category']='联邦正式授奖'
 r['period_scope']='奥地利共和国；具体版型期以来源记录为准'
 if r.get('date')=='待考':
  match=re.search(r'Instituted:\s*([^.|]+)',cand['date_grade_candidates'])
  date=match[1].strip() if match else 'Unknown'
  try:r['date']=datetime.strptime(date,'%d %B %Y').strftime('%Y年%m月%d日')
  except:r['date']=date+'年' if re.fullmatch(r'\d{4}',date) else '待考'
 r['review_status']='draft_normalized_and_visually_checked';keep.append(r)
ids={r['id'] for r in keep};heldims=[];keepims=[]
for im in m['images']:
 if im['record_id']=='AUT-REP-WMI-035-04':
  im.update({'record_id':'AUT-REP-WMI-035-03','view_key':'AUT-REP-WMI-035-03-VIEW2','key':'aut-rep-wmi-035-03-view2','source_caption':'Silver Medal (Male), Reverse (corrected by actualimage androwposition)','caption_error_note':'OriginalsitealtincorrectObverse; actualimagehasreverseinscriptionFOR SERVICE TO AUSTRIANRED CROSS'});keepims.append(im)
 elif im['record_id'] not in ids:heldims.append(im)
 else:keepims.append(im)
for r in keep:
 if r['id']=='AUT-REP-WMI-035-03':r['views'].append({'key':'AUT-REP-WMI-035-03-VIEW2','label':'背面（来源同版图示）'})
# The Class2policeback wasn'tpairedbythemislabelledsourcealt; fetchit once.
u='https://www.medals.org.uk/austria/austria-republic/images/austria050-04.jpg';path=ROOT/'assets/raw/austria_republic_20261005'/(hashlib.sha256(u.encode()).hexdigest()[:20]+'.jpg')
if not path.exists():rr=requests.get(u,timeout=25);rr.raise_for_status();path.write_bytes(rr.content)
b=path.read_bytes();pic=Image.open(io.BytesIO(b));pic.load();rid='AUT-REP-WMI-050-03';key=rid+'-VIEW2'
keepims.append({'key':key.lower(),'record_id':rid,'view_key':key,'local_path':str(path.relative_to(ROOT)).replace('\\','/'),'source_page':'https://www.medals.org.uk/austria/austria-republic/austria-republic050.htm','image_url':u,'source_caption':'Class2,Reverse','object_reference':'SourceClass2row','dimensions':list(pic.size),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'decoded':True,'visually_checked':False,'license':'No blanket publicationlicense;local offline researchonly'})
for r in keep:
 if r['id']==rid:r['views'].append({'key':key,'label':'背面（来源同版图示）'})
for im in keepims:
 if im['image_url']!=u:im['visually_checked']=True;im['visual_review']='Full medaloutline andcorrespondencecheckedin5contactsheets; original004frontopenedseparately.'
v['records']=keep;m['images']=keepims
for name,obj in [('volume_draft.json',v),('manifest_draft.json',m),('held_rows_images.json',{'records':held,'images':heldims}),('family_crosswalk_notes.json',{'notes':['019and020aregradesofexisting018family,notnewfamilies','024025026areWGoperationbranchesofexisting012family,notnewfamilies','001highesthonourdecorationand018lowestmedalgradesmayrequirecanonicalfamilyconsolidation; noexistingrowdeleted','035silverbackaltmislabelledObversecorrected','050Class2frontaltmislabelledClass1correctedbytablecontext','043partialcollarheld; sourcefamilyrepresentedbytextuntilfullimagefound','FirebrigadeRedCrossBlueHelmetsOLRGawardskeptseparatefromnationalfederalawards'],'publication_eligible':False})]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(keep),'images':len(keepims),'held_rows':len(held),'families':len({r['family'] for r in keep})}))
