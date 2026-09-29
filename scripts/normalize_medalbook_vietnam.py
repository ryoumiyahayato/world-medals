"""Normalize the complete MedalBook Vietnam sweep by historical awarding polity."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_vietnam.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_vietnam_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_vietnam"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DRV = "越南民主共和国（1945–1976）"
SVN = "越南共和国（1955–1975）"
STATE = "越南国／越南共和国（1950–1975）"
ANNAM = "阮朝／安南保护国（1884–1945）"
TAI = "法属印度支那 · 傣联邦"
SRV = "越南社会主义共和国（1976–）"

# index: polity, Chinese name, family, date, variant, selected images, image nature.
# All selected frames were visually checked on eleven local contact sheets.
ROWS = {
  4:(DRV,"战斗英雄奖章","DRV-MEDAL-GLORIOUS-FIGHTER","1961年设立","奖章；目录图样",[1],"catalogue_illustration"),
  14:(DRV,"越南友谊纪念章","DRV-DECORATION-FRIENDSHIP","约1960年","纪念章",[5,2],"object_photo"),
  21:(TAI,"民事功绩勋章","TAI-ORDER-CIVIL-MERIT","约1890–1950年","军官级",[1,3],"object_photo"),
  25:(DRV,"战功勋章","DRV-ORDER-FEAT","1947年设立","一级；历史图录插图",[1],"historical_catalogue"),
  28:(DRV,"金星勋章","DRV-SRV-ORDER-GOLD-STAR","1947–2003年式","旧式；目录图样",[1],"catalogue_illustration"),
  29:(SRV,"金星勋章","DRV-SRV-ORDER-GOLD-STAR","2003年起","现行式；目录图样",[1],"catalogue_illustration"),
  30:(DRV,"胡志明勋章","DRV-SRV-ORDER-HO-CHI-MINH","1947年设立","第一型·一级；目录图样",[1],"catalogue_illustration"),
  39:(DRV,"军功勋章","DRV-ORDER-MILITARY-EXPLOIT","1947年设立","一级；历史图录插图",[1],"historical_catalogue"),
  42:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","指挥官级",[2,1],"object_photo"),
  43:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","大十字级章饰",[1,4],"object_photo"),
  44:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","大十字级星章",[1,2],"object_photo"),
  45:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","大军官级章饰；历史图录插图",[1],"historical_catalogue"),
  46:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","大军官级星章",[1,2],"object_photo"),
  47:(STATE,"越南国家勋章","VNS-ORDER-NATIONAL","1950年设立","骑士级",[4,2],"object_photo"),
  49:(DRV,"自由勋章","DRV-ORDER-FREEDOM","1954年设立","勋章",[2,1],"object_photo"),
  50:(DRV,"独立勋章","DRV-SRV-ORDER-INDEPENDENCE","1947年设立","一级；历史图录插图",[1],"historical_catalogue"),
  52:(DRV,"独立勋章","DRV-SRV-ORDER-INDEPENDENCE","1947年设立","三级",[2,1],"object_photo"),
  62:(DRV,"解放战士勋章","DRV-ORDER-SOLDIER-LIBERATION","1966年设立","一级",[1,2],"object_photo"),
  63:(DRV,"解放战士勋章","DRV-ORDER-SOLDIER-LIBERATION","1966年设立","二级",[2,3],"object_photo"),
  65:(ANNAM,"大南龙星","ANNAM-ORDER-DRAGON","1886年设立","指挥官级",[2,3],"object_photo"),
  66:(ANNAM,"大南龙星","ANNAM-ORDER-DRAGON","1886年设立","大十字级章饰",[1],"object_photo"),
  67:(ANNAM,"大南龙星","ANNAM-ORDER-DRAGON","1886年设立","大十字级星章",[3,1],"object_photo"),
  70:(ANNAM,"大南龙星","ANNAM-ORDER-DRAGON","1886年设立","骑士级",[1,3],"object_photo"),
  71:(ANNAM,"大南龙星","ANNAM-ORDER-DRAGON","1886年设立","军官级",[2,1],"object_photo"),
  72:(ANNAM,"金磬章","ANNAM-ORDER-KIM-KHANH","1889年设立","一等一品",[2],"object_photo"),
  74:(ANNAM,"金磬章","ANNAM-ORDER-KIM-KHANH","1889年设立","二等；历史图录插图",[1],"historical_catalogue"),
  75:(ANNAM,"金磬章","ANNAM-ORDER-KIM-KHANH","1889年设立","三等；历史图录插图",[1],"historical_catalogue"),
  78:(SVN,"农业服务奖章","SVN-MEDAL-AGRICULTURAL-SERVICE","1967年设立","一级",[1,4],"object_photo"),
  80:(SVN,"空军北伐奖章","SVN-MEDAL-AIR-NORTHERN-EXPEDITION","1966年设立","奖章",[2,1],"object_photo"),
  81:(SVN,"空军英勇奖章","SVN-MEDAL-AIR-GALLANTRY","1955–1975年","奖章",[4,5],"object_photo"),
  83:(SVN,"空军服务奖章","SVN-MEDAL-AIR-SERVICE","1964年设立","二级",[3,2],"object_photo"),
  84:(SVN,"武装部队荣誉奖章","SVN-MEDAL-ARMED-FORCES-HONOUR","1953年设立","一级",[2,4],"object_photo"),
  85:(SVN,"武装部队荣誉奖章","SVN-MEDAL-ARMED-FORCES-HONOUR","1953年设立","二级",[3,1],"object_photo"),
  86:(SVN,"彰美奖章","SVN-MEDAL-CHUONG-MY","1955–1975年","一级",[2,4],"object_photo"),
  88:(SVN,"民事行动奖章","SVN-MEDAL-CIVIL-ACTIONS","1964年设立","一级",[3,1],"object_photo"),
  89:(SVN,"民事行动奖章","SVN-MEDAL-CIVIL-ACTIONS","1964年设立","二级；历史图录插图",[1],"historical_catalogue"),
  93:(SVN,"尽职服务奖章","SVN-MEDAL-DEDICATED-SERVICE","1967年设立","二级",[3,1],"object_photo"),
  100:(SVN,"善行奖章","SVN-MEDAL-GOOD-CONDUCT","1964年设立","一级；历史图录插图",[1],"historical_catalogue"),
  106:(SVN,"危险服务奖章","SVN-MEDAL-HAZARDOUS-SERVICE","1964年设立","历史图录插图",[1],"historical_catalogue"),
  109:(SVN,"劳动奖章","SVN-MEDAL-LABOUR","1967年设立","一级；目录图样",[1],"catalogue_illustration"),
  111:(SVN,"劳动奖章","SVN-MEDAL-LABOUR","1967年设立","三级",[2,1],"object_photo"),
  112:(SVN,"领导奖章","SVN-MEDAL-LEADERSHIP","1964年设立","历史图录插图",[1],"historical_catalogue"),
  113:(SVN,"救生奖章","SVN-MEDAL-LIFE-SAVING","1964年设立","历史图录插图",[1],"historical_catalogue"),
  114:(SVN,"忠诚奖章","SVN-MEDAL-LOYALTY","1964年设立","历史图录插图",[1],"historical_catalogue"),
  117:(SVN,"空军功绩服务奖章","SVN-MEDAL-MERITORIOUS-AIR","1964年设立","奖章",[3,1],"object_photo"),
  118:(SVN,"陆军功绩服务奖章","SVN-MEDAL-MERITORIOUS-ARMY","1964年设立","奖章",[4,3],"object_photo"),
  119:(SVN,"海军功绩服务奖章","SVN-MEDAL-MERITORIOUS-NAVY","1964年设立","历史图录插图",[1],"historical_catalogue"),
  120:(SVN,"军事功绩奖章","SVN-MEDAL-MILITARY-MERIT","1950年设立","奖章",[2,3],"object_photo"),
  122:(SVN,"海军英勇十字章","SVN-CROSS-NAVY-GALLANTRY","1955–1975年","十字章",[1,3],"object_photo"),
  128:(SVN,"警察荣誉奖章","SVN-MEDAL-POLICE-HONOUR","1955–1975年","三级",[3,1],"object_photo"),
  132:(SVN,"警察功绩奖章","SVN-MEDAL-POLICE-MERIT","1955–1975年","二级",[4,1],"object_photo"),
  133:(SVN,"心理战奖章","SVN-MEDAL-PSYCHOLOGICAL-WARFARE","1967年设立","一级",[2,4],"object_photo"),
  142:(SVN,"特别服务奖章","SVN-MEDAL-SPECIAL-SERVICE","1974年设立","历史图录插图",[1],"historical_catalogue"),
  143:(SVN,"参谋服务奖章","SVN-MEDAL-STAFF-SERVICE","1964年设立","一级",[2,3],"object_photo"),
  144:(SVN,"参谋服务奖章","SVN-MEDAL-STAFF-SERVICE","1964年设立","二级",[2,1],"object_photo"),
  145:(SVN,"技术服务奖章","SVN-MEDAL-TECHNICAL-SERVICE","1964年设立","一级",[4,2],"object_photo"),
  146:(SVN,"技术服务奖章","SVN-MEDAL-TECHNICAL-SERVICE","1964年设立","二级",[4,3],"object_photo"),
  147:(SVN,"训练服务奖章","SVN-MEDAL-TRAINING-SERVICE","1964年设立","一级；历史图录插图",[1],"historical_catalogue"),
  148:(SVN,"训练服务奖章","SVN-MEDAL-TRAINING-SERVICE","1964年设立","二级",[3,1],"object_photo"),
  152:(SVN,"越南战役奖章","SVN-MEDAL-VIETNAM-CAMPAIGN","1960年设立","1960年带扣版",[1,2],"object_photo"),
  153:(SVN,"越南英勇十字章","SVN-CROSS-GALLANTRY","1950年设立","十字章",[4,2],"object_photo"),
  154:(SVN,"负伤奖章","SVN-MEDAL-WOUND","1953年设立","奖章",[1,4],"object_photo"),
  157:(SVN,"空军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-AIR","1964年设立","一级",[1,4],"object_photo"),
  158:(SVN,"空军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-AIR","1964年设立","二级",[3,2],"object_photo"),
  159:(SVN,"陆军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-ARMY","1964年设立","一级；历史图录插图",[1],"historical_catalogue"),
  160:(SVN,"陆军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-ARMY","1964年设立","二级；历史图录插图",[1],"historical_catalogue"),
  161:(SVN,"海军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-NAVY","1964年设立","一级；历史图录插图",[1],"historical_catalogue"),
  162:(SVN,"海军杰出服务勋章","SVN-ORDER-DISTINGUISHED-SERVICE-NAVY","1964年设立","二级；历史图录插图",[1],"historical_catalogue"),
  164:(SRV,"决胜军旗奖章","SRV-MEDAL-DETERMINED-WIN-FLAG","1984年设立","目录图样",[1],"catalogue_illustration"),
  166:(SRV,"国家安全奖章","SRV-MEDAL-NATIONAL-SECURITY","2003年设立","目录图样",[1],"catalogue_illustration"),
  167:(SRV,"友谊奖章","SRV-MEDAL-FRIENDSHIP","2003年式","目录图样",[1],"catalogue_illustration"),
  168:(SRV,"越南英雄母亲奖章","SRV-MEDAL-HEROIC-MOTHER","1994年设立","目录图样",[1],"catalogue_illustration"),
  172:(SRV,"英勇勋章","SRV-ORDER-BRAVERY","2003年式","目录图样",[1],"catalogue_illustration"),
  173:(SRV,"保卫祖国勋章","SRV-ORDER-FATHERLAND-DEFENCE","2003年式","目录图样",[1],"catalogue_illustration"),
  174:(SRV,"友谊勋章","SRV-ORDER-FRIENDSHIP","2003年式","目录图样",[1],"catalogue_illustration"),
  175:(SRV,"民族大团结勋章","SRV-ORDER-GREAT-NATIONAL-UNITY","2003年式","目录图样",[1],"catalogue_illustration"),
}

records, manifest, used_hashes = [], [], set()
for idx, (country,name,family,date,variant,picks,image_kind) in ROWS.items():
    raw=RAW[idx]; rid=f"VNM-MB-{idx:03d}-V01"; views=[]
    for n,image_index in enumerate(picks,1):
        item=IMAGE_BY_KEY[(idx,image_index)]
        if item["sha256"] in used_hashes: raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext=Path(item["local_path"]).suffix.lower() or ".jpg"; local_rel=f"assets/images/medalbook_vietnam/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT/item["local_path"],ROOT/local_rel)
        view_key=f"VNM-MB-{idx:03d}-VIEW{n}"; views.append({"key":view_key,"label":"完整正面" if n==1 else "完整背面"})
        manifest.append({"key":f"vnm-mb-{idx:03d}-{image_index:02d}","record_id":rid,"view_key":view_key,"local_path":local_rel,
          "source_page":raw["page_url"],"image_url":item["url"],"artist":"MedalBook catalogue image",
          "license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],
          "sha256":item["sha256"],"decoded":True,"visually_checked":True})
    records.append({"id":rid,"family":family,"country_zh":country,"name":name,"original":raw["original_name"],"date":date,"variant":variant,
      "views":views,"source_ids":[raw["source_id"]],"image_kind":image_kind,"html_eligible":True})

unpictured=[{"source_id":r["source_id"],"name":r["page_title"],"date":"待考","page_url":r["page_url"],"status":"有记载未配图"}
             for i,r in enumerate(RAW) if i not in ROWS]
(ROOT/"data/volumes/vietnam_medalbook_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"越南各历史授予政权 · MedalBook","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"data/volumes/vietnam_medalbook_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":manifest,"unpictured_candidates":unpictured},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"records":len(records),"families":len({r['family'] for r in records}),"views":len(manifest),"unpictured":len(unpictured),"polities":len({r['country_zh'] for r in records})},ensure_ascii=False))
