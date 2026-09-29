from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(line) for line in (ROOT/'data/raw_candidates/istiadat_malaysia_federal.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
OUT_DIR=ROOT/'assets/images/istiadat_malaysia_federal'

# popup id: family, Chinese name, grade/variant, family date
META={
'9267':('MYS-FED-MALAYSIA-COMMEMORATIVE','马来西亚纪念奖章','金、银、铜三级合图','1965年设立'),
'9269':('MYS-FED-CORONATION-XVI','第十六任最高元首加冕纪念奖章','章饰与配套缩章合图','2019年版'),
'9265':('MYS-FED-NATIONAL-HEROES-SERVICE','国家英雄服务奖章','章饰','2014年设立'),
'9263':('MYS-FED-NATIONAL-SOVEREIGNTY','国家主权奖章','章饰','2015年设立'),
'9261':('MYS-FED-EXCELLENT-SERVICE','卓越服务奖章','章饰','2011年设立'),
'9258':('MYS-FED-MALAYSIA-SERVICE','马来西亚服务奖章','章饰','2004年设立'),
'9256':('MYS-FED-LOYAL-SERVICE','忠诚服务奖章','章饰','1970年设立'),
'9254':('MYS-FED-GENERAL-SERVICE','一般服务奖章','章饰','1989年设立'),
'9252':('MYS-FED-MERITORIOUS-DUTY','功勋服务奖章','章饰','1960年设立'),
'9250':('MYS-FED-SERVICE','服务奖章','章饰','1960年设立'),
'9248':('MYS-FED-AIR-FORCE','空军奖章','章饰','1968年设立'),
'9246':('MYS-FED-MENTION-BRAVERY','英勇传令嘉奖','金色棕榈枝佩饰','1960年设立'),
'9244':('MYS-FED-FEDERATION-GALLANTRY','联邦勇绩星章','星形章饰','1960年设立'),
'9242':('MYS-FED-COMMANDER-VALOUR','英勇统帅星章','星形章饰','1960年设立'),
'9240':('MYS-FED-GRAND-KNIGHT-VALOUR','最高英勇勋章','挂章','1960年设立'),
'9216':('MYS-FED-ORDER-MERIT','功绩勋章','挂章','1975年设立'),
'9211':('MYS-FED-LOYALTY-ROYAL-HOUSEHOLD','王室忠诚勋章','使者级章饰','1965年设立'),
'9204':('MYS-FED-LOYALTY-ROYAL-HOUSEHOLD','王室忠诚勋章','骑士级章饰','1965年设立'),
'9199':('MYS-FED-LOYALTY-ROYAL-HOUSEHOLD','王室忠诚勋章','伙伴级章饰','1965年设立'),
'9194':('MYS-FED-LOYALTY-ROYAL-HOUSEHOLD','王室忠诚勋章','统帅级挂章','1965年设立'),
'9183':('MYS-FED-MERITORIOUS-SERVICE-ORDER','国家功绩服务勋章','统帅级挂章','1995年设立'),
'9170':('MYS-FED-LOYALTY-CROWN','效忠马来西亚王冠勋章','伙伴级章饰','1966年设立'),
'9162':('MYS-FED-LOYALTY-CROWN','效忠马来西亚王冠勋章','指挥官级挂章','1966年设立'),
'9153':('MYS-FED-LOYALTY-CROWN','效忠马来西亚王冠勋章','大指挥官级项链章','1966年设立'),
'9148':('MYS-FED-DEFENDER-REALM','护国勋章','奖章级','1958年设立'),
'9142':('MYS-FED-DEFENDER-REALM','护国勋章','成员级章饰','1958年设立'),
'9133':('MYS-FED-DEFENDER-REALM','护国勋章','骑士级章饰','1958年设立'),
'9047':('MYS-FED-ROYAL-FAMILY-MALAYSIA','马来西亚王室家族勋章','项链章','1966年设立'),
'9070':('MYS-FED-CROWN-REALM','王国王冠勋章','项链章','1958年设立'),
'9088':('MYS-FED-DEFENDER-REALM','护国勋章','大指挥官级项链章','1958年设立'),
'9090':('MYS-FED-DEFENDER-REALM','护国勋章','指挥官级挂章','1958年设立'),
'9105':('MYS-FED-DEFENDER-REALM','护国勋章','伙伴级章饰','1958年设立'),
}


def main()->None:
    OUT_DIR.mkdir(parents=True,exist_ok=True); records=[]; images=[]; hashes=set()
    for row in RAW:
        popup=row['source_id'].rsplit('-',1)[-1]
        family,name,grade,date_text=META[popup]
        item=row['original_images'][0]
        if item['sha256'] in hashes: raise ValueError(f'duplicate official payload {popup}')
        hashes.add(item['sha256']); source_path=ROOT/item['local_path']
        with Image.open(source_path) as decoded: decoded.verify()
        relative=f"assets/images/istiadat_malaysia_federal/{popup}{source_path.suffix.lower()}"; shutil.copy2(source_path,ROOT/relative)
        record_id=f'{family}-ISTIADAT-{popup}'; view_key=record_id+'-VIEW1'
        records.append({'id':record_id,'family':family,'country_zh':'马来西亚联邦','name':name,'original':row['name_original'],'date':date_text,'variant':grade+'；官方图式','views':[{'key':view_key,'label':'完整官方图式'}],'source_ids':[row['source_id']],'image_kind':'official_illustration','html_eligible':True})
        images.append({'key':f'malaysia-istiadat-{popup}','record_id':record_id,'view_key':view_key,'local_path':relative,'source_page':row['object_url'],'image_url':item['image_url'],'artist':'Bahagian Istiadat dan Urusetia Persidangan Antarabangsa','license':'Malaysian Government official website terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
    (ROOT/'data/volumes/malaysia_federal_istiadat_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'马来西亚联邦','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'data/volumes/malaysia_federal_istiadat_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images)},ensure_ascii=False))


if __name__=='__main__': main()
