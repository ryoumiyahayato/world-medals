"""Merge ODM alternate photographs into the matching MedalBook Nepal variants."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/"data/volumes/nepal_medalbook_variants.json",ROOT/"data/volumes/nepal_medalbook_variants_manifest.json",ROOT/"data/volumes/nepal_medals_org_variants.json",ROOT/"data/volumes/nepal_medals_org_variants_manifest.json"]
mb,mbm,odm,odmm=[json.loads(p.read_text(encoding="utf-8")) for p in paths]
mapping={
 "NPL-ODM-006-STAR-1STAR":"NPL-MB-092-V01",
 "NPL-ODM-008-TRI-1BADGE":"NPL-MB-106-V01",
 "NPL-ODM-008-TRI-1STAR":"NPL-MB-107-V01",
 "NPL-ODM-008-TRI-2STAR":"NPL-MB-109-V01",
 "NPL-ODM-009-GORKHA-1BADGE":"NPL-MB-083-V01",
 "NPL-ODM-009-GORKHA-1STAR":"NPL-MB-084-V01",
 "NPL-ODM-009-GORKHA-3":"NPL-MB-087-V01",
 "NPL-ODM-017-MAHENDRA-CORONATION":"NPL-MB-027-V01",
 "NPL-ODM-041-TRIBHUVAN-JUBILEE":"NPL-MB-023-V01",
}
mb_by={r["id"]:r for r in mb["records"]}; odm_by={r["id"]:r for r in odm["records"]}; moved=[]
for donor_id,target_id in mapping.items():
    donor=odm_by[donor_id]; target=mb_by[target_id]
    target["source_ids"]=list(dict.fromkeys(target.get("source_ids",[])+donor.get("source_ids",[])))
    donor_images=[x for x in odmm["images"] if x["record_id"]==donor_id]
    for n,(view,img) in enumerate(zip(donor["views"],donor_images),1):
        new_view=f"{target_id}-ODM-VIEW{n}"; target["views"].append({"key":new_view,"label":"ODM来源·"+view["label"]})
        img["record_id"]=target_id; img["view_key"]=new_view; img["key"]+="-merged"; moved.append(img)
odm["records"]=[r for r in odm["records"] if r["id"] not in mapping]
odmm["images"]=[x for x in odmm["images"] if x not in moved]; mbm["images"].extend(moved)
hashes=[x["sha256"] for x in mbm["images"]+odmm["images"]]
if len(hashes)!=len(set(hashes)): raise ValueError("duplicate Nepal payload after merge")
for p,d in zip(paths,(mb,mbm,odm,odmm)): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"merged_rows":len(mapping),"transferred_views":len(moved),"remaining_odm_rows":len(odm["records"])},ensure_ascii=False))
