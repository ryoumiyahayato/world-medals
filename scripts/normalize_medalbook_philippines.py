from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image


ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(line) for line in (ROOT/'data/raw_candidates/medalbook_philippines.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
SWEEP=json.loads((ROOT/'data/source_sweeps/medalbook_philippines_images_2026-09-28.json').read_text(encoding='utf-8'))
OUT_DIR=ROOT/'assets/images/medalbook_philippines'

# index: country, family, Chinese name, variant, date, selected complete views
ROWS={
21:('菲律宾共和国','PHL-DISTINGUISHED-CONDUCT-STAR','杰出行为星章','章饰；正背','1939年设立',[2,1]),
27:('菲律宾共和国','PHL-ORDER-GOLDEN-HEART','金心勋章','1954年总统奖章型；正背','1954年设立；2003年改组为勋章',[3,2]),
35:('菲律宾共和国','PHL-KOREAN-CAMPAIGN','朝鲜战役奖章','章饰；正背','朝鲜战争时期',[5,6]),
42:('菲律宾共和国','PHL-MILITARY-MERIT','军事功绩奖章','章饰；正背','设立时间待考',[2,3]),
65:('菲律宾共和国','PHL-PNP-MERIT','菲律宾国家警察功绩奖章','章饰与略章合图','设立时间待考',[1]),
69:('菲律宾共和国','PHL-PNP-SERVICE','菲律宾国家警察服务奖章','章饰；正背','设立时间待考',[3,2]),
73:('菲律宾共和国','PHL-PRESIDENTIAL-GOLDEN-PLOW','总统土地改革金犁奖章','章饰；正背','设立时间待考',[3,4]),
81:('菲律宾群岛政府（1901–1935）','PHL-INSULAR-VICTORY-WWI','第一次世界大战胜利奖章','章饰；正背','1917–1918年服役奖',[3,2]),
82:('菲律宾共和国','PHL-VIETNAM-SERVICE','越南服役奖章','章饰；正背','越南战争时期',[1,3]),
86:('菲律宾共和国','PHL-WOUNDED-PERSONNEL','负伤人员奖章','章饰；正背','1986年版',[1,2]),
93:('菲律宾共和国','PHL-ORDER-KALANTIAO','卡兰蒂奥勋章','指挥官级；正背','1971年设立',[1,2]),
95:('菲律宾共和国','PHL-ORDER-KALANTIAO','卡兰蒂奥勋章','大十字级星章；正背','1971年设立',[1,2]),
109:('菲律宾共和国','PHL-ORDER-SIKATUNA','锡卡图纳勋章','大项链级项链章','1953年设立',[2]),
110:('菲律宾共和国','PHL-ORDER-SIKATUNA','锡卡图纳勋章','大十字级挂章','1953年设立',[3]),
111:('菲律宾共和国','PHL-ORDER-SIKATUNA','锡卡图纳勋章','大十字级星章；正背','1953年设立',[2,3]),
114:('菲律宾共和国','PHL-ORDER-SIKATUNA','锡卡图纳勋章','成员级；正背','1953年设立',[1,2]),
117:('菲律宾共和国','PHL-ORDER-GOLDEN-HEART','金心勋章','大项链级项链章','1954年设立；2003年改组',[7]),
125:('菲律宾共和国','PHL-KNIGHTS-RIZAL','黎刹骑士勋章','指挥官级；正背','1911年创立；1951年依法确认',[3,5]),
127:('菲律宾共和国','PHL-LEGION-HONOUR','菲律宾荣誉军团勋章','指挥官级；正背','1947年设立',[2,3]),
132:('菲律宾共和国','PHL-LEGION-HONOUR','菲律宾荣誉军团勋章','军团成员级；正背','1947年设立',[1,3]),
133:('菲律宾共和国','PHL-LEGION-HONOUR','菲律宾荣誉军团勋章','军官级；正背','1947年设立',[1,3]),
}


def main()->None:
    OUT_DIR.mkdir(parents=True,exist_ok=True); records=[]; images=[]; hashes=set()
    items={(x['record_index'],x['image_index']):x for x in SWEEP['items'] if x['status']=='downloaded'}
    for index,(country,family,name,variant,date_text,picks) in ROWS.items():
        source=RAW[index]; record_id=f'{family}-MEDALBOOK-{index:03d}'; views=[]
        for order,image_no in enumerate(picks,1):
            item=items[(index,image_no)]
            if item['sha256'] in hashes: raise ValueError(f'duplicate selected payload {index}:{image_no}')
            hashes.add(item['sha256']); source_path=ROOT/item['local_path']
            with Image.open(source_path) as decoded: decoded.verify()
            relative=f"assets/images/medalbook_philippines/{index:03d}_{image_no:02d}{source_path.suffix.lower()}"; shutil.copy2(source_path,ROOT/relative)
            view_key=f'{record_id}-VIEW{order}'; views.append({'key':view_key,'label':'完整正面' if order==1 else '完整背面'})
            images.append({'key':f'philippines-medalbook-{index:03d}-{image_no:02d}','record_id':record_id,'view_key':view_key,'local_path':relative,'source_page':source['page_url'],'image_url':item['url'],'artist':'MedalBook catalogue object photograph','license':'Source terms apply; retained for offline research catalogue','dimensions':[item['width'],item['height']],'bytes':item['bytes'],'sha256':item['sha256'],'decoded':True,'visually_checked':True})
        records.append({'id':record_id,'family':family,'country_zh':country,'name':name,'original':source['page_title'],'date':date_text,'variant':variant,'views':views,'source_ids':[source['source_id']],'image_kind':'object_photo','html_eligible':True})
    (ROOT/'data/volumes/philippines_medalbook_variants.json').write_text(json.dumps({'as_of':'2026-09-28','volume':'菲律宾诸历史授予主体','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'data/volumes/philippines_medalbook_variants_manifest.json').write_text(json.dumps({'as_of':'2026-09-28','images':images,'unpictured_candidates':[],'excluded_candidates':[{'record_index':22,'name':'Medal of Honour for the St. Louis World’s Fair of 1904','reason':'souvenir/commemorative object, not a formal Philippine award'},{'record_index':80,'name':'United Nations Service Medal for Korea','reason':'United Nations awarding authority; do not misassign to Philippines'},{'count':111,'reason':'MedalBook pages without a public object image remain in raw candidates and the official/Commons image queue'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(records),'families':len({r['family'] for r in records}),'views':len(images),'unpictured':111},ensure_ascii=False))


if __name__=='__main__': main()
