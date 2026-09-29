"""Normalize usable pictured objects from the complete MedalBook Bhutan sweep."""
from __future__ import annotations
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(x) for x in (ROOT/"data/raw_candidates/medalbook_bhutan.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
ITEMS=json.loads((ROOT/"data/source_sweeps/medalbook_bhutan_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]; BY={(x["record_index"],x["image_index"]):x for x in ITEMS}
OUT=ROOT/"assets/images/medalbook_bhutan"; OUT.mkdir(parents=True,exist_ok=True)
ROWS={
 12:("吉格梅·辛格国王加冕纪念章","BHT-MED-JIGME-SINGYE-CORONATION","1974年","二等章",[(2,"完整正面"),(1,"完整背面")]),
 35:("不丹皇家勋章","BHT-ORD-ROYAL-BHUTAN","1966年设立；2008年改制","一等章章饰；第一型",[(1,"完整正面"),(3,"完整背面")]),
 36:("不丹皇家勋章","BHT-ORD-ROYAL-BHUTAN","1966年设立；2008年改制","一等章星章；第一型",[(1,"完整正面"),(2,"完整背面")]),
}
records=[];images=[];used=set()
for idx,(name,family,date,variant,picks) in ROWS.items():
 raw=RAW[idx];rid=f"BHT-MB-{idx:03d}-V01";views=[]
 for n,(image_index,label) in enumerate(picks,1):
  item=BY[(idx,image_index)]
  if item["sha256"] in used: raise ValueError(f"duplicate {idx}:{image_index}")
  used.add(item["sha256"]);ext=Path(item["local_path"]).suffix.lower() or ".jpg";rel=f"assets/images/medalbook_bhutan/{idx:03d}_{image_index:02d}{ext}";shutil.copy2(ROOT/item["local_path"],ROOT/rel)
  view=f"BHT-MB-{idx:03d}-VIEW{n}";views.append({"key":view,"label":label});images.append({"key":f"bht-mb-{idx:03d}-{image_index:02d}","record_id":rid,"view_key":view,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"MedalBook catalogue object image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
 records.append({"id":rid,"family":family,"country_zh":"不丹王国","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})
pending=[{"source_id":r["source_id"],"name":r["page_title"],"date":"待考","page_url":r["page_url"],"status":"有记载未配完整图"} for i,r in enumerate(RAW) if i not in ROWS]
(ROOT/"data/volumes/bhutan_medalbook_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"不丹王国 · MedalBook","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/bhutan_medalbook_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":pending,"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"pending":len(pending)},ensure_ascii=False))
