"""Create one complete representative row for every pictured Saudi family page."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ROWS=[json.loads(x) for x in (ROOT/'data/raw_candidates/wawards_saudi-arabia.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
NAMES={
'great-badr-collar':'大巴德尔颈饰','collar-of-king-abdulaziz':'阿卜杜勒阿齐兹国王颈饰','grand-cordon-of-king-abdulaziz':'阿卜杜勒阿齐兹国王大绶章','order-of-king-abdulaziz':'阿卜杜勒阿齐兹国王勋章','king-abdulaziz-al-saud-decoration':'阿卜杜勒阿齐兹·阿勒沙特荣饰','order-of-social-services':'社会服务勋章','order-of-king-faisal':'费萨尔国王勋章','order-of-king-saud':'沙特国王勋章','order-of-king-khalid':'哈立德国王勋章','order-of-king-fahd':'法赫德国王勋章','order-of-king-abdullah':'阿卜杜拉国王勋章','medal-of-merit':'功绩奖章','holy-mosque-medal':'圣寺服务奖章','military-appreciation-medal':'军事嘉奖奖章','naval-forces-medal':'海军奖章','air-falcon-medal':'空军猎鹰奖章','bravery-medal':'英勇奖章','medal-for-leadership':'领导奖章','combat-medal':'战斗奖章','honor-medal':'荣誉奖章','medal-for-military-management':'军事管理奖章','security-medal':'安全奖章','rescue-medal':'救援奖章','teacher-medal':'教员奖章','perfection-medal':'精通奖章','innovation-medal':'创新奖章','shooting-medal':'射击奖章','military-service-medal':'军事服务奖章','medal-for-the-liberation-of-kuwait':'科威特解放奖章','island-shield-medal':'岛屿之盾演习奖章','abdullah-s-sword-exercise-medal':'阿卜杜拉之剑演习奖章','centenary-of-the-founding-of-the-kingdom-of-saudi-arabia':'沙特王国建立百周年奖章'}
FAMILY_OVERRIDE={'grand-cordon-of-king-abdulaziz':'order-of-king-abdulaziz'}
OUT=ROOT/'assets/images/wawards_saudi_arabia';OUT.mkdir(parents=True,exist_ok=True);records=[];images=[];unpictured=[]
for n,row in enumerate(ROWS,1):
 slug=Path(urlparse(row['object_url']).path).stem;name=NAMES.get(slug,slug.replace('-',' '));family_slug=FAMILY_OVERRIDE.get(slug,slug);family=f'SAU-WAWARDS-{family_slug.upper().replace("-","_")}'
 if not row['original_images']:unpictured.append({'source_id':row['source_id'],'name':name,'reason':'source object page has no exposed full image'});continue
 item=row['original_images'][0];src=ROOT/item['local_path'];rel=f'assets/images/wawards_saudi_arabia/{slug}{src.suffix.lower()}';shutil.copy2(src,ROOT/rel)
 with Image.open(src) as im:w,h=im.size;im.verify()
 rid=f'SAU-WAWARDS-{slug.upper().replace("-","_")}-REPRESENTATIVE';view=rid+'-VIEW1';date=(row.get('date_candidates') or ['日期待考'])[0]
 if date!='日期待考':date=f'{date}年设立／纪年'
 records.append({'id':rid,'family':family,'country_zh':'沙特阿拉伯王国','name':name,'original':row['page_title'],'date':date,'variant':'World Awards对象页所示完整章体；具体等级待考','views':[{'key':view,'label':'完整图样'}],'source_ids':[row['source_id']],'image_kind':'catalogue_object_or_illustration','html_eligible':True})
 images.append({'key':rid.lower()+'-image','record_id':rid,'view_key':view,'local_path':rel,'source_page':row['object_url'],'image_url':item['image_url'],'license':'source-site research use; publication rights not asserted','dimensions':[w,h],'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'decoded':True,'visually_checked':True})
(ROOT/'data/volumes/saudi_arabia_wawards_families.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'沙特阿拉伯王国','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data/volumes/saudi_arabia_wawards_families_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':unpictured,'notes':['First pass establishes family coverage; all additional source images remain cached for grade-level normalization.']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_rows':len(ROWS),'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images),'unpictured':len(unpictured)},ensure_ascii=False))
