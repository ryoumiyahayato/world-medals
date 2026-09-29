"""Normalize the recursively completed ODM Pakistan source without ribbon-only rows."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(line) for line in (ROOT/"data/raw_candidates/medals_org_pakistan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
ITEMS=json.loads((ROOT/"data/source_sweeps/medals_org_pakistan_2026-09-28.json").read_text(encoding="utf-8"))["items"]
BY_KEY={(x["record_index"],x["image_index"]):x for x in ITEMS if x.get("status")=="downloaded"}
OUT=ROOT/"assets/images/medals_org_pakistan"; OUT.mkdir(parents=True,exist_ok=True)

# index, suffix, Chinese name, family, date, exact variant, [(image index, view label)]
E=[
 (0,"lion","海德尔勋章","PAK-ORD-NISHAN-HAIDER","1957年设立","Nishan-e-Haider；单级军功勋章",[(2,"完整正面")]),
 (1,"pak3-collar","巴基斯坦勋章","PAK-ORD-PAKISTAN","1986年起","第三型；大项链",[(2,"完整正面")]),
 (1,"pak3-1badge","巴基斯坦勋章","PAK-ORD-PAKISTAN","1986年起","第三型；一等章章饰（Nishan-i-Pakistan）",[(3,"完整正面")]),
 (1,"pak3-1star","巴基斯坦勋章","PAK-ORD-PAKISTAN","1986年起","第三型；一等章星章（Nishan-i-Pakistan）",[(4,"完整正面")]),
 (1,"pak3-4","巴基斯坦勋章","PAK-ORD-PAKISTAN","1986年起","第三型；四等章",[(5,"完整正面")]),
 (2,"pak1-1","巴基斯坦勋章","PAK-ORD-PAKISTAN","1957–1975年","第一型；一等章（Nishan-e-Pakistan）",[(5,"完整正面")]),
 (2,"pak1-2","巴基斯坦勋章","PAK-ORD-PAKISTAN","1957–1975年","第一型；二等章（Hilal-e-Pakistan）",[(6,"完整正面")]),
 (2,"pak1-medal","巴基斯坦勋章","PAK-ORD-PAKISTAN","1957–1975年","第一型；奖章（Tamgha-e-Pakistan）",[(7,"完整正面")]),
 (4,"bravery2-2","英勇勋章","PAK-ORD-SHUJAAT","1986年起","第二型；二等章",[(2,"完整正面")]),
 (4,"bravery2-medal","英勇勋章","PAK-ORD-SHUJAAT","1986年起","第二型；奖章（Tamgha-i-Shujaat）",[(3,"完整正面")]),
 (5,"bravery1-medal","英勇勋章","PAK-ORD-SHUJAAT","1957–1986年","第一型；奖章（Tamgha-i-Shujaat）",[(5,"完整正面")]),
 (6,"performance3-1badge","杰出成就勋章","PAK-ORD-IMTIAZ","1986年起","第三型；一等章章饰（Nishan-i-Imtiaz）",[(2,"完整正面")]),
 (6,"performance3-1star","杰出成就勋章","PAK-ORD-IMTIAZ","1986年起","第三型；一等章星章（Nishan-i-Imtiaz）",[(3,"完整正面")]),
 (6,"performance3-2badge","杰出成就勋章","PAK-ORD-IMTIAZ","1986年起","第三型；二等章章饰（Hilal-i-Imtiaz）",[(4,"完整正面")]),
 (6,"performance3-2star","杰出成就勋章","PAK-ORD-IMTIAZ","1986年起","第三型；二等章星章（Hilal-i-Imtiaz）",[(5,"完整正面")]),
 (8,"performance2-1","杰出成就勋章","PAK-ORD-IMTIAZ","1975–1986年","第二型；一等章章饰",[(5,"完整正面")]),
 (8,"performance2-2badge","杰出成就勋章","PAK-ORD-IMTIAZ","1975–1986年","第二型；二等章章饰",[(6,"完整正面")]),
 (8,"performance2-2star","杰出成就勋章","PAK-ORD-IMTIAZ","1975–1986年","第二型；二等章星章",[(7,"完整正面")]),
 (8,"performance2-3","杰出成就勋章","PAK-ORD-IMTIAZ","1975–1986年","第二型；三等章",[(8,"完整正面")]),
 (8,"performance2-4","杰出成就勋章","PAK-ORD-IMTIAZ","1975–1986年","第二型；四等章",[(9,"完整正面")]),
 (9,"leader3-3","伟大领袖勋章","PAK-ORD-QUAID-AZAM","1986年起","第三型；三等章",[(2,"完整正面")]),
 (10,"leader1-2","伟大领袖勋章","PAK-ORD-QUAID-AZAM","1957–1975年","第一型；二等章",[(5,"完整正面")]),
 (10,"leader1-3","伟大领袖勋章","PAK-ORD-QUAID-AZAM","1957–1975年","第一型；三等章",[(6,"完整正面")]),
 (15,"pride","总统卓越成就奖章","PAK-MED-PRIDE-PERFORMANCE","1983年设立","总统卓越成就奖章",[(2,"完整正面")]),
 (16,"hilal-jurat","勇气新月勋章","PAK-MED-HILAL-JURAT","1957年设立","Hilal-i-Jur'at；战斗英勇章",[(2,"完整正面")]),
 (17,"sitara-jurat","勇气之星","MENA7-SITARA-E-JURAT","1957年设立","Sitara-i-Jur'at；军官／准尉级战斗英勇章",[(2,"完整正面"),(3,"完整背面")]),
 (18,"tamgha-jurat","勇气奖章","PAK-MED-TAMGHA-JURAT","1957年设立","Tamgha-i-Jur'at；战斗英勇奖章",[(2,"完整正面")]),
 (19,"sitara-basalat","英勇品行之星","PAK-MED-SITARA-BASALAT","1957年设立","Sitara-i-Basalat；非战斗英勇章",[(2,"完整正面")]),
 (21,"police-gallantry","警察英勇奖章","PAK-MED-POLICE-GALLANTRY","1954年设立","警察英勇版",[(2,"完整正面"),(3,"完整背面")]),
 (25,"general-service","国防服役奖章","PAK-MED-TAMGHA-DIFFA","1957年设立","Tamgha-i-Diffa；基础章及 Kashmir 1948、Dir-Bajaur 1960–62、Kashmir 1964–65、Kutch 1965、Siachen Glacier 扣饰",[(2,"完整正面"),(3,"完整背面"),(4,"KASHMIR 1948扣饰"),(5,"DIR-BAJAUR 1960–62扣饰"),(6,"KASHMIR 1964–65扣饰"),(7,"KUTCH 1965扣饰"),(8,"SIACHEN GLACIER扣饰")]),
 (26,"war-star65","1965年战争之星","PAK-MED-WAR-STAR-1965","1965年","Istar-i-Herb 1385",[(2,"完整正面"),(3,"完整背面")]),
 (27,"war-star71","1971年战争之星","PAK-MED-WAR-STAR-1971","1971年","Istar-i-Herb 1971",[(2,"完整正面"),(3,"完整背面")]),
 (28,"war-medal65","1965年战争奖章","PAK-MED-WAR-1965","1965年","1385 Tamgha-i-Jang",[(2,"完整正面"),(3,"完整背面")]),
 (29,"war-medal71","1971年战争奖章","PAK-MED-WAR-1971","1971年","Tamgha-i-Jang 1971",[(2,"完整正面"),(3,"完整背面")]),
 (30,"independence","巴基斯坦独立纪念章","PAK-MED-INDEPENDENCE","1948年设立（纪念1947年独立）","纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (31,"republic56","1956年共和国纪念章","PAK-MED-REPUBLIC-1956","1957年设立（纪念1956年共和）","Tamgha-i-Jamhuria 1375",[(2,"完整正面"),(3,"完整背面")]),
 (32,"service2-1","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第二型；军职一等章",[(4,"完整正面")]),
 (32,"service2-2","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第二型；军职二等章",[(5,"完整正面")]),
 (32,"service2-3","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第二型；军职三等章",[(6,"完整正面")]),
 (34,"hijri","伊斯兰历十四世纪纪念章","PAK-MED-HIJRI","1979年","纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (37,"jinnah100","真纳诞辰百周年纪念章","PAK-MED-JINNAH-CENTENARY","1976年","Tamgah-i-Sad Saala Jashan-i-Wiladat-i-Quaid-i-Azam",[(2,"完整正面"),(3,"完整背面")]),
 (38,"jamhuriat88","1988年民主纪念章","PAK-MED-JAMHURIAT-1988","1988年","Jamhuriat Medal",[(2,"完整正面"),(3,"完整背面")]),
 (39,"revolution-jubilee","巴基斯坦革命金禧纪念章","PAK-MED-REVOLUTION-JUBILEE","1988年","金禧纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (40,"independence-jubilee","独立金禧纪念章","PAK-MED-INDEPENDENCE-JUBILEE","1997年","独立50周年纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (43,"service20","20年服役奖章","PAK-MED-SERVICE-20","1992年设立","20年服役版",[(2,"完整正面"),(3,"完整背面")]),
 (44,"service10","10年服役奖章","PAK-MED-SERVICE-10","1992年设立","10年服役版",[(2,"完整正面"),(3,"完整背面")]),
 (45,"azad-kashmir","自由克什米尔纪念章","PAK-MED-AZAD-KASHMIR","设立年待考","纪念章",[(1,"完整正面"),(2,"完整背面")]),
 (46,"chagai","查盖-I纪念章","PAK-MED-CHAGAI-I","1998年","首次核试验纪念章",[(2,"完整正面")]),
 (47,"service1-1","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第一型；军职一等章",[(4,"完整正面")]),
 (47,"service1-2","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第一型；军职二等章",[(5,"完整正面")]),
 (47,"service1-3","服务勋章","PAK-ORD-NISHAN-KHIDMAT","1957年设立","第一型；军职三等章",[(6,"完整正面")]),
 (48,"standoff","2001–2002年印巴对峙服役章","PAK-MED-ISTAQLAL-2002","2002年设立","Tamgha-e-Istaqlal Pakistan",[(2,"完整正面")]),
 (49,"service35","35年服役奖章","PAK-MED-SERVICE-35","设立年待考","35年服役版",[(2,"完整正面")]),
]

records=[]; images=[]; used=set(); used_pages=set()
for idx,suffix,name,family,date,variant,picks in E:
    raw=RAW[idx]; rid=f"PAK-ODM-{idx:03d}-{suffix.upper()}"; views=[]; used_pages.add(idx)
    for n,(image_index,label) in enumerate(picks,1):
        item=BY_KEY[(idx,image_index)]
        if Path(item["local_path"]).suffix.lower()==".gif" or (item["height"]<=70 and "扣饰" not in label):
            raise ValueError(f"ribbon/detail promoted as award image: {idx}:{image_index}")
        if item["sha256"] in used: raise ValueError(f"duplicate selected payload: {idx}:{image_index}")
        used.add(item["sha256"]); ext=Path(item["local_path"]).suffix.lower() or ".jpg"
        rel=f"assets/images/medals_org_pakistan/{idx:03d}_{suffix}_{image_index:02d}{ext}"
        shutil.copy2(ROOT/item["local_path"],ROOT/rel)
        view_key=f"PAK-ODM-{idx:03d}-{suffix.upper()}-VIEW{n}"; views.append({"key":view_key,"label":label})
        images.append({"key":f"pak-odm-{idx:03d}-{suffix}-{image_index:02d}","record_id":rid,"view_key":view_key,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"ODM / medals.org.uk catalogue image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
    records.append({"id":rid,"family":family,"country_zh":"巴基斯坦","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})

pending=[]
for idx,raw in enumerate(RAW):
    object_items=[x for x in ITEMS if x["record_index"]==idx and Path(x["local_path"]).suffix.lower()!=".gif" and x["height"]>70]
    if not object_items:
        pending.append({"source_id":raw["source_id"],"name":raw["page_title"],"date":raw.get("instituted_text") or "待考","page_url":raw["page_url"],"status":"有记载未配完整章体图"})

(ROOT/"data/volumes/pakistan_medals_org_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"巴基斯坦 · ODM","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/pakistan_medals_org_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending_pages":len(pending)},ensure_ascii=False))
