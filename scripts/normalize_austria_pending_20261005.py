import json,hashlib,re,copy,time,io
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
import requests
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/staging/austria_pending_20261005';OUT.mkdir(parents=True,exist_ok=True)
IMG=ROOT/'assets/raw/austria_variants_20261005';IMG.mkdir(parents=True,exist_ok=True)
pending=json.loads((ROOT/'data/staging/austria_variants_20261005/pending.json').read_text(encoding='utf-8'))
allrows=[];used=set()
for f in [ROOT/'data/catalogue.json']+list((ROOT/'data/volumes').glob('*.json')):
 try:d=json.loads(f.read_text(encoding='utf-8-sig'))
 except:continue
 if not isinstance(d,dict):continue
 if isinstance(d.get('records'),list):allrows+=d['records']
 if isinstance(d.get('images'),list):used.update(x.get('image_url') for x in d['images'])
byfam={r.get('family'):r for r in allrows}
# Mappings follow actual award names and page headings, not the page numbers.
mapping={
 '006':('AUT-FAM-GOLDEN-FLEECE-HABSBURG','金羊毛勋章','哈布斯堡王朝','1431年1月10日（该来源纪年，制度年份待复核）','正式王朝勋章'),
 '007':('AUT-FAM-STARRY-CROSS','星十字勋章','哈布斯堡王朝','1668年','正式王朝勋章'),
 '024':('HUN-FAM-ST-STEPHEN-1764','匈牙利王家圣斯蒂芬勋章','匈牙利王国／哈布斯堡君主国','1764年5月5日','正式王朝勋章'),
 '038':('AUT-FAM-TEUTONIC-ORDER','德意志骑士团勋章','德意志骑士团','1834年复兴（来源说法）；古典骑士团始于1190年','宗教骑士团附编'),
 '043':('AUT-FAM-JUBILEE-1898-CIVIL','弗朗茨·约瑟夫在位五十周年纪念奖章（文官）','奥匈帝国','1898年','正式国家纪念授奖'),
 '049':('BAV-FAM-13-INFANTRY-JUBILEE-1901','巴伐利亚皇家第十三步兵团纪念奖章','巴伐利亚王国','1901年','部队纪念附编'),
 '040':('AUT-FAM-RED-CROSS-MERIT-1914-PENDING','1914年红十字功绩奖励','奥地利红十字会','待考','授予性质待核'),
 '047':('AUT-FAM-RED-CROSS-HONOUR-1914','红十字荣誉章','奥匈帝国','1914年8月14日','正式国家荣誉'),
 '055':('AUT-FAM-RED-CROSS-HONOUR-1914','红十字荣誉章','奥匈帝国','1914年8月14日','正式国家荣誉'),
 '037':('AUT-FAM-AE-003','铁王冠勋章','奥地利帝国／奥匈帝国','1816年奥地利帝国复设','正式国家勋章'),
 '036':('AUT-FAM-AE-003','铁王冠勋章','奥地利帝国／奥匈帝国','1816年奥地利帝国复设','正式国家勋章'),
 '023':('AUT-FAM-AH-008','弗朗茨·约瑟夫勋章','奥地利帝国／奥匈帝国','1849年12月2日','正式国家勋章'),
 '029':('AUT-FAM-AH-009','军事功绩奖章（Signum Laudis）','奥匈帝国','1890年','正式国家奖章'),
 '039':('AUT-FAM-AH-009','军事功绩奖章（Signum Laudis）','奥匈帝国','1890年','正式国家奖章'),
 '032':('AUT-FAM-MERIT-CROSS-1850','功绩十字章','奥地利帝国／奥匈帝国','1849／1850年设立（来源日期冲突）','正式国家授奖'),
 '033':('AUT-FAM-MERIT-CROSS-1850','功绩十字章','奥地利帝国／奥匈帝国','1849／1850年设立（来源日期冲突）','正式国家授奖'),
 '056':('AUT-FAM-MERIT-CROSS-1850','功绩十字章','奥地利帝国／奥匈帝国','1849／1850年设立（来源日期冲突）','正式国家授奖'),
 '057':('AUT-FAM-MERIT-CROSS-1850','功绩十字章','奥地利帝国／奥匈帝国','1849／1850年设立（来源日期冲突）','正式国家授奖'),
 '058':('AUT-FAM-MERIT-CROSS-1850','功绩十字章','奥匈帝国','1849／1850年设立（来源日期冲突）','正式国家授奖'),
}
context={'037':'战争装饰','036':'加剑','023':'战争装饰','039':'铜级（来源描述）；弗朗茨·约瑟夫肖像版；1890–1916年；战时绶带','047':'无战争装饰','055':'战争装饰','056':'第一型；1849–1875年','057':'第二型；1875–1914年','058':'第三型；1914–1918年；战时绶带'}
trans={'Grand Cross: Badge':'大十字级挂章','Grand Cross: Star':'大十字级星章','Commander with Star: Badge':'星章指挥官级挂章','Commander with Star: Star':'星章指挥官级星章','Commander':'指挥官级挂章','Officer\'s Cross':'军官级十字章','Officer':'军官级挂章','Knight':'骑士级挂章','Class 1 Cross':'一级十字章','Class 2 Cross':'二级十字章','Class 1':'一级','Class 2':'二级','Class 3':'三级','Collar':'领链','Badge':'挂章','Dame':'女士级挂章','Merit Star':'功绩星章','Franz Joseph':'弗朗茨·约瑟夫肖像版','Obverse':'正面'}
rows=[];imgs=[];dispositions=[];s=requests.Session()
for x in pending:
 u=x['page'];n=re.search(r'empire(\d+)\.htm',u)[1];soup=BeautifulSoup((ROOT/'sources/pages/austria_variants_20261005'/u.rsplit('/',1)[-1]).read_bytes(),'html.parser')
 evidence=' | '.join(p.get_text(' ',strip=True) for p in soup.select('p') if any(z in p.get_text() for z in ['Instituted:','Awarded:','Grades:']))
 original=soup.h3.get_text(' ',strip=True) if soup.h3 else soup.h2.get_text(' ',strip=True).split(':',1)[-1].strip()
 if n not in mapping:
  dispositions.append({'object_page':u,'page_title':soup.title.get_text(),'original_name':original,'source_text':evidence,'status':'text_only_candidate_no_complete_object_photo_on_source','image_count':len(x['images']),'note':'No inferred institution/material or inventedimage; merge/classification pending'});continue
 fam,name,country,date,category=mapping[n];fresh=0
 for i,im in enumerate(x['images']):
  if 'Reverse' in im['caption'] or im['image_url'] in used:continue
  rid='AUT-WMI-PENDING-'+n+'-'+str(i+1).zfill(2);r=copy.deepcopy(byfam.get(fam,{}));r.update({'id':rid,'family':fam,'name':name,'original':original,'country_zh':country,'date':date,'views':[],'source_ids':['WMI-AUT-'+n],'html_eligible':False,'body_eligible':False,'publication_eligible':False,'local_offline':True,'category':category,'rights_note':'仅本地离线研究；未确认公开再发布许可','evidence':[{'source_page':u,'accessed_at':'2026-10-05','source_excerpt':evidence,'image_reference':im['caption'],'page_type_context':context.get(n,'')}],'review_status':'needs_visual_review'})
  cap=im['caption'].replace(', Obverse','').replace('Obverse','').strip(', ')
  for en,zh in trans.items():cap=cap.replace(en,zh)
  r['variant']='；'.join(z for z in [cap,context.get(n,''),'低清参考'] if z)
  if n=='043':r['variant']='文官版；低清参考'
  if n=='049':r['variant']='部队纪念版；具体材质待考；低清参考'
  if n=='040':r['variant']='具体授予性质、等级待考；低清参考'
  pair=[im];rev=im['caption'].replace('Obverse','Reverse')
  if 'Obverse' in im['caption']:pair += [b for b in x['images'][i+1:i+2] if b['caption']==rev]
  for j,p in enumerate(pair):
   url=p['image_url'];path=IMG/(hashlib.sha256(url.encode()).hexdigest()[:20]+'.jpg')
   try:
    if not path.exists():rr=s.get(url,timeout=30);rr.raise_for_status();path.write_bytes(rr.content);time.sleep(.3)
    b=path.read_bytes();pic=Image.open(io.BytesIO(b));pic.load();key=rid+'-VIEW'+str(j+1)
    r['views'].append({'key':key,'label':'正面' if j==0 else '背面（来源同版图示，未保证同一实物）'})
    imgs.append({'key':key.lower(),'record_id':rid,'view_key':key,'local_path':str(path.relative_to(ROOT)).replace('\\','/'),'source_page':u,'image_url':url,'source_caption':p['caption'],'object_reference':n+': '+p['caption'],'dimensions':list(pic.size),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'decoded':True,'visually_checked':False,'license':'No blanket republication license identified; offline research reference only','artist':'World Medals Index; photographer not established'})
   except Exception as e:dispositions.append({'image_url':url,'status':'download_failed','error':str(e)})
  if r['views']:rows.append(r);fresh+=1
 dispositions.append({'object_page':u,'family':fam,'source_text':evidence,'status':'draft_rows_downloaded' if fresh else 'no_new_images_or_duplicate','draft_rows':fresh,'family_existing':fam in byfam,'boundary_note':'Catalogue mixes dynastic,state,religious,regimental andRedCross bodies;category kept explicit'})
for name,obj in [('volume_draft.json',{'as_of':'2026-10-05','volume':'奥地利帝国／奥匈帝国·未归并页面补图草稿','records':rows}),('manifest_draft.json',{'images':imgs}),('page_dispositions.json',dispositions)]: (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
for start in range(0,len(imgs),24):
 chunk=imgs[start:start+24];sheet=Image.new('RGB',(1000,((len(chunk)+3)//4)*330),'#ddd');d=ImageDraw.Draw(sheet)
 for i,x in enumerate(chunk):
  im=Image.open(ROOT/x['local_path']).convert('RGB');im.thumbnail((220,260));xx=i%4*250;yy=i//4*330;sheet.paste(im,(xx+(250-im.width)//2,yy));d.text((xx+4,yy+265),x['record_id'],fill='black');d.text((xx+4,yy+283),x['source_caption'][:34],fill='black')
 sheet.save(OUT/('contact_'+str(start//24+1)+'.jpg'))
print(json.dumps({'pages':len(pending),'draft_rows':len(rows),'photos':len(imgs),'new_families':len({r['family'] for r in rows if r['family'] not in byfam})}))
