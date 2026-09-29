"""Normalize the recursively completed ODM Nepal directory, excluding ribbon-only files."""
from __future__ import annotations

import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/"data/raw_candidates/medals_org_nepal.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
ITEMS=json.loads((ROOT/"data/source_sweeps/medals_org_nepal_2026-09-28.json").read_text(encoding="utf-8"))["items"]
BY={(x["record_index"],x["image_index"]):x for x in ITEMS if x.get("status")=="downloaded"}
OUT=ROOT/"assets/images/medals_org_nepal"; OUT.mkdir(parents=True,exist_ok=True)

# index,suffix,name,family,date,variant,[(image index,label)]
E=[
 (4,"trib-dem-2star","特里布万民主勋章","NPL-ORD-TRIBHUVAN-DEMOCRACY","1956年设立","二等章星章",[(2,"完整正面")]),
 (4,"trib-dem-3","特里布万民主勋章","NPL-ORD-TRIBHUVAN-DEMOCRACY","1956年设立","三等章",[(3,"完整正面")]),
 (4,"trib-dem-4","特里布万民主勋章","NPL-ORD-TRIBHUVAN-DEMOCRACY","1956年设立","四等章",[(4,"完整正面")]),
 (4,"trib-dem-5","特里布万民主勋章","NPL-ORD-TRIBHUVAN-DEMOCRACY","1956年设立","五等章",[(5,"完整正面")]),
 (5,"shripada-2star","尼泊尔吉祥足迹勋章","NPL-ORD-SHRIPADA","1962年设立","二等章星章",[(2,"完整正面")]),
 (6,"star-1star","尼泊尔之星勋章","NPL-ORD-STAR-NEPAL","1918年设立","一等章星章",[(2,"完整正面")]),
 (6,"star-2badge","尼泊尔之星勋章","NPL-ORD-STAR-NEPAL","1918年设立","二等章章饰",[(3,"完整正面")]),
 (8,"tri-1badge","三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","一等章章饰",[(2,"完整正面")]),
 (8,"tri-1star","三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","一等章星章",[(3,"完整正面")]),
 (8,"tri-2star","三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","二等章星章",[(4,"完整正面")]),
 (9,"gorkha-1badge","廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","一等章章饰",[(2,"完整正面")]),
 (9,"gorkha-1star","廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","一等章星章",[(3,"完整正面")]),
 (9,"gorkha-2star","廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","二等章星章",[(4,"完整正面")]),
 (9,"gorkha-3","廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","三等章",[(5,"完整正面")]),
 (17,"mahendra-coronation","马亨德拉国王加冕纪念章","NPL-MED-MAHENDRA-CORONATION","1955年","加冕纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (20,"army-public-order","陆军治安英勇章","NPL-MED-ARMY-PUBLIC-ORDER","1963年设立","陆军治安行动英勇章",[(1,"完整正面"),(2,"完整背面")]),
 (24,"police-gallantry","警察英勇之星","NPL-MED-POLICE-GALLANTRY-STAR","1965年设立","警察英勇星章",[(1,"完整正面"),(2,"完整背面")]),
 (37,"air-service","航空服役奖章","NPL-MED-AIR-SERVICE","1966年设立","飞行员版",[(1,"完整正面"),(2,"完整背面")]),
 (41,"tribhuvan-jubilee","特里布万国王银禧纪念章","NPL-MED-TRIBHUVAN-JUBILEE","1936年设立（纪念1935年银禧）","纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (42,"birendra-coronation","比兰德拉国王加冕纪念章","NPL-MED-BIRENDRA-CORONATION","1975年","加冕纪念章",[(2,"完整正面"),(3,"完整背面")]),
 (44,"earthquake35","1935年大地震纪念章","NPL-MED-EARTHQUAKE-1935","1935年","地震纪念章",[(1,"完整正面"),(2,"完整背面")]),
 (49,"gorkha-medal","廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1936年设立","奖章级",[(2,"完整正面"),(3,"完整背面")]),
]
records=[]; images=[]; used=set()
for idx,suffix,name,family,date,variant,picks in E:
    raw=RAW[idx]; rid=f"NPL-ODM-{idx:03d}-{suffix.upper()}"; views=[]
    for n,(image_index,label) in enumerate(picks,1):
        item=BY[(idx,image_index)]
        if Path(item["local_path"]).suffix.lower()==".gif": raise ValueError(f"ribbon promoted {idx}:{image_index}")
        if item["sha256"] in used: raise ValueError(f"duplicate payload {idx}:{image_index}")
        used.add(item["sha256"]); ext=Path(item["local_path"]).suffix.lower() or ".jpg"
        rel=f"assets/images/medals_org_nepal/{idx:03d}_{suffix}_{image_index:02d}{ext}"; shutil.copy2(ROOT/item["local_path"],ROOT/rel)
        view=f"NPL-ODM-{idx:03d}-{suffix.upper()}-VIEW{n}"; views.append({"key":view,"label":label})
        images.append({"key":f"npl-odm-{idx:03d}-{suffix}-{image_index:02d}","record_id":rid,"view_key":view,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"ODM / medals.org.uk catalogue image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
    records.append({"id":rid,"family":family,"country_zh":"尼泊尔王国／尼泊尔","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})

pending=[]
for idx,raw in enumerate(RAW):
    object_items=[x for x in ITEMS if x["record_index"]==idx and Path(x["local_path"]).suffix.lower()!=".gif" and x["height"]>70]
    if not object_items: pending.append({"source_id":raw["source_id"],"name":raw["page_title"],"date":raw.get("instituted_text") or "待考","page_url":raw["page_url"],"status":"有记载未配完整章体图"})
(ROOT/"data/volumes/nepal_medals_org_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"尼泊尔王国／尼泊尔 · ODM","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/nepal_medals_org_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending":len(pending)},ensure_ascii=False))
