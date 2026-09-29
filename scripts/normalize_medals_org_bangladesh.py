"""Normalize the completed ODM Bangladesh directory into concrete pictured variants."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(x) for x in (ROOT / "data/raw_candidates/medals_org_bangladesh.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
ITEMS = json.loads((ROOT / "data/source_sweeps/medals_org_bangladesh_2026-09-28.json").read_text(encoding="utf-8"))["items"]
BY = {(x["record_index"], x["image_index"]): x for x in ITEMS if x.get("status") == "downloaded"}
OUT = ROOT / "assets/images/medals_org_bangladesh"
OUT.mkdir(parents=True, exist_ok=True)

# Chinese catalogue names. Dates are the source's institution dates; unknown stays concise.
META = [
 ("独立奖章","BGD-AWARD-INDEPENDENCE","1976年设立","奖章"),
 ("伟大勇士勋章","BGD-ORD-BIR-UTTOM","1973年12月15日设立","勋章"),
 ("勇士勋章","BGD-ORD-BIR-BIKROM","1973年12月15日设立","勋章"),
 ("英勇标志勋章","BGD-ORD-BIR-PROTIK","1973年12月15日设立","勋章"),
 ("战役之星","BGD-MED-CAMPAIGN-STAR","1973年12月16日设立","陆军版"),
 ("战争奖章","BGD-MED-WAR","设立日期待考","奖章"),
 ("解放之星","BGD-MED-LIBERATION-STAR","1973年12月15日设立","奖章"),
 ("胜利奖章","BGD-MED-VICTORY","1973年设立","奖章"),
 ("宪法奖章","BGD-MED-CONSTITUTION","1972年设立","奖章"),
 ("丘陵地区战役奖章","BGD-MED-HILL-TRACTS-WILDFIRE","设立日期待考","野火行动版"),
 ("洪水救灾奖章","BGD-MED-FLOOD-1988","1988年设立","奖章"),
 ("1991年气旋救灾奖章","BGD-MED-CYCLONE-1991","1991年设立","奖章"),
 ("安全奖章","BGD-MED-SECURITY","1991年设立","奖章"),
 ("军事资历奖章","BGD-MED-MILITARY-SENIORITY","设立日期待考","三级"),
 ("军事资历奖章","BGD-MED-MILITARY-SENIORITY","设立日期待考","二级"),
 ("军事资历奖章","BGD-MED-MILITARY-SENIORITY","设立日期待考","一级"),
 ("最高勇士勋章","BGD-ORD-BIR-SRESHTHO","1973年12月15日设立","勋章"),
 ("二十一日奖章","BGD-MED-TWENTY-FIRST","1976年设立","奖章"),
 ("先锋勇士章","BGD-MED-FOREMOST-BRAVES","设立日期待考","章饰"),
 ("不朽勇士章","BGD-MED-IMMORTAL-BRAVES","设立日期待考","章饰"),
 ("廉正勇士章","BGD-MED-INCORRUPTIBLE-BRAVES","设立日期待考","章饰"),
 ("不屈勇士章","BGD-MED-INDOMITABLE-BRAVES","设立日期待考","章饰"),
 ("陆军奖章","BGD-MED-ARMY","设立日期待考","奖章"),
 ("海军奖章","BGD-MED-NAVY","设立日期待考","奖章"),
 ("空军奖章","BGD-MED-AIR-FORCE","设立日期待考","奖章"),
 ("非凡服务奖章","BGD-MED-EXTRAORDINARY-SERVICE","设立日期待考",""),
 ("杰出服务奖章","BGD-MED-DISTINGUISHED-SERVICE","设立日期待考",""),
 ("陆军荣耀奖章","BGD-MED-ARMY-GLORY","设立日期待考","奖章"),
 ("海军光荣服务奖章","BGD-MED-NAVY-GLORIOUS-SERVICE","设立日期待考","奖章"),
 ("杰出飞行奖章","BGD-MED-DISTINGUISHED-FLYING","设立日期待考","奖章"),
 ("卓越奖章","BGD-MED-EXCELLENCE","设立日期待考",""),
 ("效率奖章","BGD-MED-EFFICIENCY","设立日期待考",""),
 ("丘陵地区战役奖章","BGD-MED-HILL-TRACTS-UPLIFTMENT","设立日期待考","发展行动版"),
 ("科威特重建行动奖章","BGD-MED-REBUILDING-KUWAIT","1991年设立",""),
 ("1991年议会选举奖章","BGD-MED-ELECTION-1991","1991年设立","奖章"),
 ("1996年议会选举奖章","BGD-MED-ELECTION-1996","1996年设立","奖章"),
 ("1998年洪水救灾奖章","BGD-MED-FLOOD-1998","1998年设立","奖章"),
 ("纳夫行动奖章","BGD-MED-OPERATION-NAF","2001年设立","奖章"),
 ("2001年议会选举奖章","BGD-MED-ELECTION-2001","2001年设立","奖章"),
 ("2008年议会选举奖章","BGD-MED-ELECTION-2008","2008年设立","奖章"),
 ("2014年议会选举奖章","BGD-MED-ELECTION-2014","2014年设立","奖章"),
 ("2018年议会选举奖章","BGD-MED-ELECTION-2018","2018年设立","奖章"),
 ("2024年议会选举奖章","BGD-MED-ELECTION-2024","2024年设立","奖章"),
 ("独立二十五周年纪念章","BGD-MED-INDEPENDENCE-SILVER-JUBILEE","1996年设立","银禧纪念章"),
 ("独立五十周年纪念章","BGD-MED-INDEPENDENCE-GOLDEN-JUBILEE","2021年设立","金禧纪念章"),
]

SPECIAL = {
 # For 25 and 26 the source deliberately reuses one identical common obverse;
 # keep it once and place the three service reverses beside it in one concrete row.
 25: [("tri-service","三军版（共式正面；陆军、海军、空军背面）",[2,3,5,7])],
 26: [("tri-service","三军版（共式正面；陆军、海军、空军背面）",[2,3,5,7])],
 30: [("army","陆军版",[2,3]),("navy","海军版",[4,5]),("air-force","空军版",[6,7])],
 31: [("army","陆军版",[2,3]),("navy","海军版",[4,5]),("air-force","空军版",[6,7])],
 33: [("type-1","第一型",[2,3]),("type-2","第二型",[4,5])],
}

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

entries = []
for idx, (name, family, date, variant) in enumerate(META):
    if idx in SPECIAL:
        for suffix, concrete_variant, picks in SPECIAL[idx]:
            entries.append((idx, suffix, name, family, date, concrete_variant, picks))
    elif idx in (18,19,20,21):
        entries.append((idx, slug(RAW[idx]["page_title"]), name, family, date, variant, [1]))
    else:
        entries.append((idx, slug(RAW[idx]["page_title"]), name, family, date, variant, [2,3]))

records, images, used = [], [], set()
for idx, suffix, name, family, date, variant, picks in entries:
    raw = RAW[idx]
    rid = f"BGD-ODM-{idx:03d}-{suffix.upper()}"
    views = []
    for n, image_index in enumerate(picks, 1):
        item = BY[(idx, image_index)]
        ext = Path(item["local_path"]).suffix.lower()
        if ext == ".gif" or item["height"] <= 70:
            raise ValueError(f"ribbon/non-object promoted {idx}:{image_index}")
        if item["sha256"] in used:
            raise ValueError(f"duplicate payload {idx}:{image_index}")
        used.add(item["sha256"])
        rel = f"assets/images/medals_org_bangladesh/{idx:03d}_{suffix}_{image_index:02d}{ext or '.jpg'}"
        shutil.copy2(ROOT / item["local_path"], ROOT / rel)
        if idx in (25,26):
            label = ("共式完整正面","陆军版完整背面","海军版完整背面","空军版完整背面")[n-1]
        else:
            label = "完整正面" if n == 1 else "完整背面"
        key = f"{rid}-VIEW{n}"
        views.append({"key":key,"label":label})
        images.append({"key":f"bgd-odm-{idx:03d}-{suffix}-{image_index:02d}","record_id":rid,"view_key":key,"local_path":rel,"source_page":raw["page_url"],"image_url":item["url"],"artist":"ODM / medals.org.uk catalogue image","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
    records.append({"id":rid,"family":family,"country_zh":"孟加拉国","name":name,"original":raw["original_name"],"date":date,"variant":variant,"views":views,"source_ids":[raw["source_id"]],"image_kind":"object_photo","html_eligible":True})

(ROOT / "data/volumes/bangladesh_medals_org_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"孟加拉国 · ODM","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT / "data/volumes/bangladesh_medals_org_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":[],"excluded_candidates":[{"kind":"ribbon_only","count":41,"reason":"绶带图不作为章体图示"}]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images)},ensure_ascii=False))
