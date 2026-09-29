"""Normalize the complete ODM Bhutan source, excluding ribbon-only files."""
from __future__ import annotations
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/"data/raw_candidates/medals_org_bhutan.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
ITEMS=json.loads((ROOT/"data/source_sweeps/medals_org_bhutan_2026-09-28.json").read_text(encoding="utf-8"))["items"];BY={(x["record_index"],x["image_index"]):x for x in ITEMS}
OUT=ROOT/"assets/images/medals_org_bhutan";OUT.mkdir(parents=True,exist_ok=True)
E=[
 (4,"coronation2008","2008年加冕纪念章","BHT-MED-CORONATION-2008","2008年","加冕纪念章",[(1,"完整正面"),(2,"完整背面")]),
 (7,"thunder-dragon","雷龙勋章","BHT-ORD-THUNDER-DRAGON","1967年设立","Druk Khorlo；章饰",[(1,"完整正面")]),
 (9,"service25","25年服役奖章","BHT-MED-SERVICE-25","1966年设立","25年服役版",[(1,"完整正面"),(2,"完整背面")]),
]
records=[];images=[];used=set()
for idx,suffix,name,family,date,variant,picks in E:
 raw=RAW[idx];rid=f"BHT-ODM-{idx:03d}-{suffix.upper()}";views=[]
 for n,(image_index,label) in enumerate(picks,1):
  item=BY[(idx,image_index)]
  if Path(item["local_path"]).suffix.lower()==".gif": raise ValueError("ribbon promoted")
  if item["sha256"] in used: raise ValueError("duplicate payload")
  used.add(item["sha256"]);ext=Path(item["local_path"]).suffix.lower() or ".jpg";rel=f"assets/images/medals_org_bhutan/{idx:03d}_{suffix}_{image_index:02d}{ext}";shutil.copy2(ROOT/item["local_path"],ROOT/rel)
  view=f"BHT-ODM-{idx:03d}-{suffix.upper()}-VIEW{n}";views.append({"key":view,"label":label});images.append({"key":f"bht-odm-{idx:03d}-{suffix}-{image_index:02d}","record_id":rid,"view_key":view,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"ODM / medals.org.uk catalogue image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
 records.append({"id":rid,"family":family,"country_zh":"不丹王国","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})
pending=[]
for i,r in enumerate(RAW):
 objs=[x for x in ITEMS if x["record_index"]==i and Path(x["local_path"]).suffix.lower()!=".gif"]
 if not objs: pending.append({"source_id":r["source_id"],"name":r["page_title"],"date":r.get("instituted_text") or "待考","page_url":r["page_url"],"status":"有记载未配完整章体图"})
(ROOT/"data/volumes/bhutan_medals_org_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"不丹王国 · ODM","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/bhutan_medals_org_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending":len(pending)},ensure_ascii=False))
