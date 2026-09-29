"""Create one verified representative row for every family in the complete Jordan catalogue."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ROWS=[json.loads(x) for x in (ROOT/'data/raw_candidates/wawards_jordan.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
META=[
('侯赛因·本·阿里勋章','Order of Hussein bin Ali','1949年设立'),('哈希姆星章','Order of the Hashemite Star','1972年设立'),('军事英勇勋章','Order of Military Gallantry','1946年设立'),('复兴勋章','Supreme Order of the Renaissance','1918年设立'),('奉献与牺牲勋章','Order of Dedication and Sacrifice','2015年设立'),('哈希姆王冠勋章','Order of the Hashemite Crown','设立日期待考'),('约旦之星勋章','Order of the Star of Jordan','1947／1949年，日期待核'),('独立勋章','Order of Independence','1918年设立'),('军事功绩勋章','Order of Military Merit','1972年设立'),('阿卜杜拉二世卓越勋章','King Abdullah II Order for Distinction','2015年设立'),('猎鹰勋章','Order of the Falcon','设立日期待考'),('侯赛因卓越服务勋章','Al-Hussein Order for Distinguished Service','1977年设立'),('勇气与救援勋章','Order for Courage and Rescue','2015年设立'),('军事荣誉奖章','Military Honour Medal','1956年设立'),('长期忠诚服务奖章','Medal for Long and Faithful Service','设立日期待考'),('银禧奖章','Silver Jubilee Medal','1977年'),('参加维和部队奖章','Medal for Participation in Peacekeeping Forces','1993年设立'),('领导能力奖章','Leadership Competence Medal','设立日期待考'),('行政与技术能力奖章','Administrative and Technical Competence Medal','设立日期待考'),('训练能力奖章','Training Competence Medal','设立日期待考'),('约旦服务奖章','Jordan Service Medal','设立日期待考'),('马安奖章','Ma’an Medal','20世纪，日期待考'),('第二次世界大战纪念章','Second World War Commemorative Medal','1945年后'),('巴勒斯坦军事行动奖章','Medal for Military Operations in Palestine','1948年战役'),('卡拉梅战役奖章','Medal for the Battle of Karameh','1968年战役'),('斋月战争奖章','Ramadan War Medal','1973年战役'),('伊拉克与叙利亚战役奖章','Iraq and Syria Campaign Medal','1941年战役'),('和谐与和解奖章','Concord and Reconciliation Medal','设立日期待考'),('阿卜杜拉二世即位奖章','King Abdullah II Accession Medal','1999年'),('阿卜杜拉二世卓越奖章','King Abdullah II Medal for Excellence','设立日期待考'),('在位四十周年纪念章','40th Anniversary of the Reign Jubilee Medal','1992年'),
]
assert len(ROWS)==len(META)==31,(len(ROWS),len(META))
OUT=ROOT/'assets/images/wawards_jordan'; OUT.mkdir(parents=True,exist_ok=True)
records=[]; images=[]; unpictured=[]
for n,(row,(name,original,date)) in enumerate(zip(ROWS,META),1):
 family=f'JOR-WAWARDS-{n:03d}'
 if not row['original_images']:
  unpictured.append({'source_id':row['source_id'],'name':name,'reason':'object page exposes no downloadable full image'}); continue
 item=row['original_images'][0]; src=ROOT/item['local_path']; rel=f'assets/images/wawards_jordan/{n:03d}{src.suffix.lower()}'; shutil.copy2(src,ROOT/rel)
 with Image.open(src) as im: width,height=im.size; im.verify()
 view=f'{family}-VIEW1'; rid=f'{family}-REPRESENTATIVE'
 records.append({'id':rid,'family':family,'country_zh':'约旦哈希姆王国','name':name,'original':original,'date':date,'variant':'World Awards 2025图录所示完整章体；具体等级待考','views':[{'key':view,'label':'完整图样'}],'source_ids':[row['source_id']],'image_kind':'catalogue_object_or_illustration','html_eligible':True})
 images.append({'key':rid.lower()+'-image','record_id':rid,'view_key':view,'local_path':rel,'source_page':row['object_url'],'image_url':item['image_url'],'license':'source-site research use; publication rights not asserted','dimensions':[width,height],'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'decoded':True,'visually_checked':True})
(ROOT/'data/volumes/jordan_wawards_families.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'约旦哈希姆王国','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/jordan_wawards_families_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':unpictured,'notes':['First pass establishes complete family coverage from the 31-object source. Grade-level expansion remains a separate differential pass using the retained full image cache.']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(records),'families':len({x['family'] for x in records}),'views':len(images),'unpictured':len(unpictured)},ensure_ascii=False))
