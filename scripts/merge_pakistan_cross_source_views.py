"""Merge alternate ODM photographs into matching MedalBook variants instead of duplicating rows."""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
mb_path=ROOT/"data/volumes/pakistan_medalbook_variants.json"
mbm_path=ROOT/"data/volumes/pakistan_medalbook_variants_manifest.json"
odm_path=ROOT/"data/volumes/pakistan_medals_org_variants.json"
odmm_path=ROOT/"data/volumes/pakistan_medals_org_variants_manifest.json"
mb=json.loads(mb_path.read_text(encoding="utf-8")); mbm=json.loads(mbm_path.read_text(encoding="utf-8"))
odm=json.loads(odm_path.read_text(encoding="utf-8")); odmm=json.loads(odmm_path.read_text(encoding="utf-8"))

donor_to_target={
    "PAK-ODM-017-SITARA-JURAT":"PAK-MB-040-V01",
    "PAK-ODM-018-TAMGHA-JURAT":"PAK-MB-019-V01",
    "PAK-ODM-021-POLICE-GALLANTRY":"PAK-MB-028-V01",
    "PAK-ODM-028-WAR-MEDAL65":"PAK-MB-042-V01",
    "PAK-ODM-030-INDEPENDENCE":"PAK-MB-027-V01",
    "PAK-ODM-034-HIJRI":"PAK-MB-016-V01",
}
mb_by_id={r["id"]:r for r in mb["records"]}; odm_by_id={r["id"]:r for r in odm["records"]}
transferred=[]
for donor_id,target_id in donor_to_target.items():
    donor=odm_by_id[donor_id]; target=mb_by_id[target_id]
    target["source_ids"]=list(dict.fromkeys(target.get("source_ids",[])+donor.get("source_ids",[])))
    donor_images=[x for x in odmm["images"] if x["record_id"]==donor_id]
    for n,(view,img) in enumerate(zip(donor["views"],donor_images),1):
        new_view=f"{target_id}-ODM-VIEW{n}"
        target["views"].append({"key":new_view,"label":"ODM来源·"+view["label"]})
        img["record_id"]=target_id; img["view_key"]=new_view; img["key"]+="-merged"
        transferred.append(img)

odm["records"]=[r for r in odm["records"] if r["id"] not in donor_to_target]
odmm["images"]=[x for x in odmm["images"] if x not in transferred]
mbm["images"].extend(transferred)
hashes=[x["sha256"] for x in mbm["images"]+odmm["images"]]
if len(hashes)!=len(set(hashes)): raise ValueError("duplicate Pakistan image payload after merge")
for path,data in ((mb_path,mb),(mbm_path,mbm),(odm_path,odm),(odmm_path,odmm)):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"merged_rows":len(donor_to_target),"transferred_views":len(transferred),"remaining_odm_rows":len(odm["records"])},ensure_ascii=False))
