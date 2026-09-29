from __future__ import annotations

import hashlib, json, pathlib, shutil
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/"data/raw_candidates/medals_org_mongolia.jsonl"
SOURCE=ROOT/"data/source_sweeps/medals_org_mongolia_2026-09-28.json"
OUT_DIR=ROOT/"assets/images/mongolia_medals_org"
VOLUME=ROOT/"data/volumes/mongolia_medals_org_variants.json"
MANIFEST=ROOT/"data/volumes/mongolia_medals_org_variants_manifest.json"

NAMES={
0:"蒙古人民共和国国家安全五十周年奖章",1:"蒙古人民军五十周年奖章",2:"劳动荣誉奖章",3:"“我们胜利了”奖章",
4:"战胜军国主义日本三十周年奖章",5:"战斗英勇勋章",6:"劳动红旗英勇勋章",7:"苏赫巴托尔勋章",
8:"军事英勇红旗勋章",9:"蒙古人民共和国四十周年奖章",10:"蒙古人民革命五十周年奖章",11:"蒙古人民革命六十周年奖章",
12:"战斗荣誉奖章",13:"蒙古人民共和国英雄金星章",14:"北极星勋章",15:"哈拉哈河胜利四十周年奖章",
16:"蒙古人民共和国劳动英雄章",18:"英雄母亲勋章",19:"蒙古人民共和国二十五周年奖章",20:"无私奖章",
21:"哈拉哈河奖章",22:"处女地开垦者荣誉奖章",23:"友谊奖章",24:"乔巴山奖章",25:"国家奖章",
26:"“人民”荣誉称号章",27:"功勋称号章",28:"达·纳楚克道尔基文学奖章",29:"哈拉哈河胜利二十周年奖章",
30:"哈拉哈河胜利三十周年奖章",31:"蒙古人民共和国警察五十周年奖章",32:"蒙古人民共和国五十周年奖章",
33:"蒙古人民共和国武装力量六十周年奖章",34:"哈拉哈河五十周年奖章",35:"蒙古人民革命七十周年奖章",
36:"蒙古国建国八十周年奖章",37:"战友友谊奖章",
}

DATES={
0:"1972年",1:"1971年",2:"1945年设立",3:"1945年",4:"1975年",5:"1945年设立",6:"1926年设立；1931／1945年改称",
7:"1945年设立",8:"1926年设立；1931年改称",9:"1961年",10:"1971年",11:"1981年",12:"1945年设立",
13:"1936年设称号；1941年起制章",14:"1936年设立",15:"1979年",16:"1956年设立",18:"1957年设立",
19:"1946年",20:"1959年设立",21:"1940年",22:"设立日期待考",23:"设立日期待考",24:"1945年设立",
25:"1962年设立",26:"1935年设称号；1975年制章",27:"1975年",28:"设立日期待考",29:"1959年",
30:"1969年",31:"1971年",32:"1977年",33:"1981年",34:"1989年",35:"1991年",36:"2001年",37:"设立日期待考",
}

# One page may document several real successive types or classes.
VARIANTS={i:[("奖章；完整正反面；低清参考",[1,2])] for i in NAMES}
VARIANTS.update({
2:[("第一型；完整正反面；低清参考",[1,2]),("第二型；完整正反面；低清参考",[3,4])],
3:[("奖章；完整正反面；低清参考",[2,3])],
5:[("勋章；完整正反面；低清参考",[2,3])],
6:[("识字英勇勋章第二型之一；完整正面；低清参考",[2]),("公民英勇勋章第四型之一；完整正面；低清参考",[3]),("劳动红旗英勇勋章1945年型；完整正面；低清参考",[4]),("劳动红旗英勇勋章1970年型；完整正面；低清参考",[5])],
7:[("勋章；完整正面；低清参考",[2])],
8:[("1926年型；完整正面；低清参考",[2]),("1931年型；完整正面；低清参考",[3]),("1940年型·第一次授予章；完整正面；低清参考",[4]),("1940年型·第四次授予章；完整正面；低清参考",[5]),("1945年型·第一次授予章；完整正面；低清参考",[6]),("1945年型·第二次授予章；完整正面；低清参考",[7]),("1945年型·第三次授予章；完整正面；低清参考",[8]),("1945年型·第四次授予章；完整正面；低清参考",[9]),("1970年型；完整正面；低清参考",[10])],
13:[("第一型（1941—1946）；完整正面；低清参考",[2]),("第二型（1946年后）；完整正面；低清参考",[3])],
14:[("第一型（1936）；完整正面；低清参考",[2]),("第二型（1940）；完整正面；低清参考",[3]),("第三型（1941）；完整正面；低清参考",[4]),("第四型（1970）；完整正面；低清参考",[5])],
16:[("英雄章；完整正面；低清参考",[2])],
18:[("一等；完整正面；低清参考",[1]),("二等；完整正面；低清参考",[2])],
20:[("第一型（1959）；完整正反面；低清参考",[2,3]),("第二型（1967）；完整正反面；低清参考",[4,5])],
21:[("奖章；完整正面；低清参考",[2])],
})

def main():
    raw=[json.loads(x) for x in RAW.read_text(encoding="utf-8").splitlines() if x.strip()]
    items=json.loads(SOURCE.read_text(encoding="utf-8"))["items"]
    lookup={(x["record_index"],x["image_index"]):x for x in items}
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    records=[]; images=[]; hashes=set()
    for index in sorted(VARIANTS):
        family=f"MNG-{index:03d}-"+"-".join(raw[index]["family_hint"].upper().split()[:5])
        for variant_no,(variant,selections) in enumerate(VARIANTS[index],1):
            rid=f"MNG-ODM-{index:03d}-V{variant_no:02d}"; views=[]
            for order,image_index in enumerate(selections,1):
                item=lookup[(index,image_index)]; source=ROOT/item["local_path"]
                target=OUT_DIR/f"{index:03d}_{variant_no:02d}_{image_index:02d}{source.suffix.lower()}"; shutil.copy2(source,target)
                sha=hashlib.sha256(target.read_bytes()).hexdigest()
                if sha in hashes: raise RuntimeError(f"duplicate selected payload {index}/{image_index}")
                hashes.add(sha)
                with Image.open(target) as im: dims=list(im.size); im.verify()
                key=f"MNG-ODM-{index:03d}-{variant_no:02d}-VIEW{order}"
                views.append({"key":key,"label":"完整正面" if order==1 else "完整背面"})
                images.append({"key":key.lower(),"record_id":rid,"view_key":key,"local_path":target.relative_to(ROOT).as_posix(),"source_page":raw[index]["page_url"],"image_url":item["url"],"artist":"ODM / medals.org.uk object image","license":"Source terms apply; retained for offline research catalogue","dimensions":dims,"bytes":target.stat().st_size,"sha256":sha,"decoded":True,"visually_checked":True})
            records.append({"id":rid,"family":family,"country_zh":"蒙古国（1992–）" if index==36 else "蒙古人民共和国","name":NAMES[index],"original":raw[index]["page_title"],"date":DATES[index],"variant":variant,"views":views,"source_ids":[raw[index]["source_id"]],"image_kind":"object_photo","html_eligible":True})
    VOLUME.write_text(json.dumps({"as_of":"2026-09-28","volume":"蒙古人民共和国／蒙古国 · ODM", "records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of":"2026-09-28","images":images},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"records":len(records),"families":len({r['family'] for r in records}),"images":len(images)},ensure_ascii=False))

if __name__=="__main__": main()
