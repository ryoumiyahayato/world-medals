import hashlib,json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'assets/images/greece_medals_org_fast_2026-09-28'
items=[
('army_formation_command','greece_army_formation_command.jpg','希腊共和国','陆军编队指挥奖章','Army Formation Command Medal','1991','完整正面；低清参考','https://www.medals.org.uk/greece/greece024.htm'),
('bavarian_volunteers','greece_bavarian_volunteers_cross.jpg','希腊王国','巴伐利亚志愿军十字章','Cross of Bavarian Volunteers','1837-05-26','完整正面；低清参考','https://www.medals.org.uk/greece/greece032.htm'),
('beneficence','greece_beneficence_commander.jpg','希腊王国／希腊共和国','慈善勋章','Order of Beneficence / Order of Welfare','1948','指挥官级；完整正面；低清参考','https://www.medals.org.uk/greece/greece007.htm'),
('commendation_medal','greece_commendation_medal_merit_honour.jpg','希腊共和国','功绩与荣誉嘉奖奖章','Commendation Medal of Merit and Honour','1991-05-15','完整正面；低清参考','https://www.medals.org.uk/greece/greece019.htm'),
('commendation_star','greece_commendation_star_merit_honour.jpg','希腊共和国','功绩与荣誉嘉奖星章','Commendation Star of Merit and Honour','1996','完整正面；低清参考','https://www.medals.org.uk/greece/greece077.htm'),
('cross_valour','greece_cross_valour_gold_cross.jpg','希腊王国／希腊共和国','英勇十字章','Cross of Valour','1913-05-13','金十字级；完整正面；低清参考','https://www.medals.org.uk/greece/greece008.htm'),
('george_constantine','greece_george_constantine_collar_star.jpg','希腊王国','圣乔治与圣君士坦丁王室勋章','Royal House Order of SS. George and Constantine','1936-01','领饰骑士星章；完整正面；低清参考','https://www.medals.org.uk/greece/greece004.htm'),
('george_i','greece_george_i_gc_badge.jpg','希腊王国','乔治一世王室勋章','Royal Order of George I','1915-01-16','大十字挂章；完整正面；低清参考','https://www.medals.org.uk/greece/greece002.htm'),
('honour','greece_honour_grand_commander_badge.jpg','希腊共和国','荣誉勋章','Order of Honour','1975-08-18','大指挥官级挂章；完整正面；低清参考','https://www.medals.org.uk/greece/greece006.htm'),
('independence','greece_independence_cross_silver_officers.jpg','希腊王国','希腊独立战争十字章','Cross of the War of Independence 1821-1829','1834-05-20','银质军官级；完整正面；低清参考','https://www.medals.org.uk/greece/greece031.htm'),
('exceptional_acts','greece_medal_exceptional_acts.jpg','希腊共和国','卓越行为奖章','Medal for Exceptional Acts','1998','完整正面；低清参考','https://www.medals.org.uk/greece/greece067.htm'),
('outstanding_acts','greece_medal_outstanding_acts_type1.jpg','希腊王国／希腊共和国','杰出行为奖章','Medal for Outstanding Acts','1940-11-11','第一型（1940–1950）；完整正面；低清参考','https://www.medals.org.uk/greece/greece018.htm'),
('meritorious_command','greece_meritorious_command_class1_gold.jpg','希腊共和国','优良指挥嘉奖奖章','Meritorious Command Commendation Medal','1991-05-15','一级金质；完整正面；低清参考','https://www.medals.org.uk/greece/greece025.htm'),
('military_merit','greece_military_merit_class1.jpg','希腊共和国','军事功绩奖章','Medal of Military Merit','1917-06-30','一级；完整正面；低清参考','https://www.medals.org.uk/greece/greece068.htm'),
('officers_longevity','greece_officers_longevity_class1_gold.jpg','希腊共和国','军官长期服役嘉奖奖章','Officers Longevity Service Commendation Medal','1991-05-15','一级金质；完整正面；低清参考','https://www.medals.org.uk/greece/greece042.htm'),
('olga_sophia','greece_olga_sophia_dame_gc_badge.jpg','希腊王国','圣奥尔加与圣索菲亚王室勋章','Royal House Order of SS. Olga and Sophia','1936-01','女大十字级挂章；完整正面；低清参考','https://www.medals.org.uk/greece/greece005.htm'),
('phoenix','greece_phoenix_commander.jpg','希腊王国／希腊共和国','凤凰勋章','Order of the Phoenix','1926-05-13','指挥官级；完整正面；低清参考','https://www.medals.org.uk/greece/greece003.htm'),
('redeemer','greece_redeemer_type2_gc_badge.jpg','希腊王国／希腊共和国','救世主勋章','Order of the Redeemer','1833-06-01','第二型（1863–1975）大十字挂章；完整正面；低清参考','https://www.medals.org.uk/greece/greece001.htm'),
('war_cross_1917','greece_war_cross_1917_class1_2stars.jpg','希腊王国','1917年战争十字章','War Cross 1917','1917-02-28','一级，附两星表示追加授予；完整正面；低清参考','https://www.medals.org.uk/greece/greece072.htm'),
('war_cross_1940','greece_war_cross_1940_class1.jpg','希腊王国／希腊共和国','战争十字章','War Cross','1940-11-11','一级；完整正面；低清参考','https://www.medals.org.uk/greece/greece009.htm')]
records=[];images=[]
for slug,file,country,name,original,date,variant,url in items:
 p=IMG/file; data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
 with Image.open(p) as im: dims=list(im.size); im.verify()
 rid=f'GRC-ODM-{slug.upper().replace("-","_")}-01'; family=f'GRC-ODM-{slug.upper().replace("-","_")}'
 view=f'{rid}-VIEW1'
 records.append({'id':rid,'family':family,'country_zh':country,'name':name,'original':original,'date':date,'variant':variant,'views':[{'key':view,'label':'完整正面'}],'source_ids':[f'odm-greece-{slug}'],'image_kind':'complete_object_low_resolution','html_eligible':True})
 images.append({'key':f'grc-odm-{slug}-image-01','record_id':rid,'view_key':view,'local_path':str(p.relative_to(ROOT)).replace('\\','/'),'source_page':url,'image_url':url,'license':'source-site research use; publication rights not asserted','dimensions':dims,'bytes':len(data),'sha256':sha,'decoded':True,'visually_checked':True})
(ROOT/'data/volumes/greece_medals_org_fast_2026-09-28.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'greece_medals_org_fast_2026-09-28','records':records},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/volumes/greece_medals_org_fast_2026-09-28_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'greece_medals_org_fast_2026-09-28','images':images},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(records),len(images),len({x['sha256'] for x in images}))
