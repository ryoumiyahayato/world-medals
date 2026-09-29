"""Normalize every usable pictured object from the complete MedalBook Nepal sweep."""
from __future__ import annotations

import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/"data/raw_candidates/medalbook_nepal.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
ITEMS=json.loads((ROOT/"data/source_sweeps/medalbook_nepal_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
BY={(x["record_index"],x["image_index"]):x for x in ITEMS if x.get("status")=="downloaded"}
OUT=ROOT/"assets/images/medalbook_nepal"; OUT.mkdir(parents=True,exist_ok=True)

# index: Chinese name, family, date, exact pictured variant, [(image index,label)]
ROWS={
 13:("尼泊尔荣誉章","NPL-MED-DECORATION-NEPAL","1966年设立","奖章",[(2,"完整正面"),(3,"完整背面")]),
 23:("特里布万国王银禧纪念章","NPL-MED-TRIBHUVAN-JUBILEE","1936年设立（纪念1935年银禧）","纪念章；来源页题名误作Bihendra",[(2,"完整正面"),(3,"完整背面")]),
 27:("马亨德拉国王加冕纪念章","NPL-MED-MAHENDRA-CORONATION","1955年","加冕纪念章",[(1,"完整正面"),(4,"完整背面")]),
 35:("军队长期服役及良好品行奖章","NPL-MED-MIL-LSGC","1966年设立","长期服役及良好品行章",[(2,"完整正面"),(3,"完整背面")]),
 53:("王室长期服务章","NPL-MED-ROYAL-HOUSEHOLD-LS","1966年设立","奖章级",[(2,"完整正面"),(3,"完整背面")]),
 63:("比兰德拉民主勋章","NPL-ORD-BIRENDRA-DEMOCRACY","2002年设立","一等章章饰",[(1,"完整正面")]),
 64:("比兰德拉民主勋章","NPL-ORD-BIRENDRA-DEMOCRACY","2002年设立","一等章星章",[(1,"完整正面")]),
 83:("廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","一等章章饰",[(4,"完整正面"),(5,"完整背面")]),
 84:("廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","一等章星章",[(6,"完整正面"),(5,"完整背面")]),
 87:("廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","三等章",[(5,"完整正面"),(4,"完整背面")]),
 88:("廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","四等章",[(2,"完整正面"),(3,"完整背面")]),
 90:("廓尔喀右臂勋章","NPL-ORD-GORKHA-DAKSHINA-BAHU","1896年设立；1932年改制","五等章",[(1,"完整正面"),(5,"完整背面")]),
 92:("尼泊尔之星勋章","NPL-ORD-STAR-NEPAL","1918年设立","一等章星章",[(2,"完整正面"),(4,"完整背面")]),
 106:("三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","一等章章饰",[(1,"完整正面")]),
 107:("三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","一等章星章",[(2,"完整正面")]),
 108:("三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","二等章章饰",[(2,"完整正面")]),
 109:("三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","二等章星章",[(1,"完整正面")]),
 110:("三力勋章","NPL-ORD-TRISHAKTI-PATTA","1937年设立","三等章",[(3,"完整正面"),(2,"完整背面")]),
}
records=[]; images=[]; used=set()
for idx,(name,family,date,variant,picks) in ROWS.items():
    raw=RAW[idx]; rid=f"NPL-MB-{idx:03d}-V01"; views=[]
    for n,(image_index,label) in enumerate(picks,1):
        item=BY[(idx,image_index)]
        if item["sha256"] in used: raise ValueError(f"duplicate payload {idx}:{image_index}")
        used.add(item["sha256"]); ext=Path(item["local_path"]).suffix.lower() or ".jpg"
        rel=f"assets/images/medalbook_nepal/{idx:03d}_{image_index:02d}{ext}"; shutil.copy2(ROOT/item["local_path"],ROOT/rel)
        view=f"NPL-MB-{idx:03d}-VIEW{n}"; views.append({"key":view,"label":label})
        images.append({"key":f"npl-mb-{idx:03d}-{image_index:02d}","record_id":rid,"view_key":view,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"MedalBook catalogue object image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
    records.append({"id":rid,"family":family,"country_zh":"尼泊尔王国／尼泊尔","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})

pending=[]
for idx,raw in enumerate(RAW):
    if idx in ROWS: continue
    status="仅有背面／盒装参考，缺完整正面" if idx==113 else "有记载未配完整图"
    pending.append({"source_id":raw["source_id"],"name":raw["page_title"],"date":"待考","page_url":raw["page_url"],"status":status})
(ROOT/"data/volumes/nepal_medalbook_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"尼泊尔王国／尼泊尔 · MedalBook","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/nepal_medalbook_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending":len(pending)},ensure_ascii=False))
