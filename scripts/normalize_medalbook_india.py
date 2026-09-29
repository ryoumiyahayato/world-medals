"""Normalize the complete MedalBook India sweep by actual awarding polity.

The selection below is based on a visual review of all twelve local contact
sheets.  Rows without a complete, decodable object image remain in the
unpictured appendix rather than being promoted into the public catalogue.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / "data/raw_candidates/medalbook_india.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
IMAGES = json.loads((ROOT / "data/source_sweeps/medalbook_india_images_2026-09-28.json").read_text(encoding="utf-8"))["items"]
IMAGE_BY_KEY = {(x["record_index"], x["image_index"]): x for x in IMAGES if x["status"] == "downloaded"}
OUT_DIR = ROOT / "assets/images/medalbook_india"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IND = "印度共和国（1950–）"
AZH = "自由印度临时政府（1943–1945）"
BAH = "巴哈瓦尔布尔土邦（1802–1955）"
BAR = "巴罗达土邦"
BIK = "比卡内尔土邦"
GWA = "瓜廖尔土邦"
JAK = "查谟—克什米尔土邦"
PAT = "帕蒂亚拉土邦"
SIK = "锡克帝国（1799–1849）"

# index: polity, Chinese working name, family, date, exact pictured variant,
# selected image numbers.  Image numbering follows the source sweep manifest.
ROWS = {
  0:(IND,"二十年长期服役奖章","IND-MEDAL-LS-20","1971年设立","奖章",[2]),
  1:(IND,"独立二十五周年纪念章","IND-MEDAL-INDEP-25","1972年","纪念章",[3,4]),
  3:(IND,"独立五十周年纪念章","IND-MEDAL-INDEP-50","1997年","纪念章",[3]),
  4:(IND,"九年长期服役奖章","IND-MEDAL-LS-9","1971年设立","奖章",[4,3]),
  15:(IND,"一般勤务奖章","IND-MEDAL-GENERAL-SERVICE-1947","1947年设立","带扣版",[2,3]),
  17:(IND,"高海拔勤务奖章","IND-MEDAL-HIGH-ALTITUDE","1986年设立","奖章",[3,5]),
  21:(IND,"独立纪念章","IND-MEDAL-INDEPENDENCE-1950","1950年","奖章",[3,2]),
  23:(IND,"兵工厂四十年服务奖章","IND-MEDAL-ORDNANCE-40","日期待考","奖章",[4,3]),
  26:(IND,"长期服役与良好品行奖章","IND-MEDAL-LSGC","1957年设立","奖章",[1,2]),
  31:(IND,"海军奖章","IND-MEDAL-NAUSENA","1960年设立","正背合图",[1]),
  32:(IND,"帕拉克拉姆行动奖章","IND-MEDAL-OP-PARAKRAM","2001年设立","奖章",[4,5]),
  33:(IND,"维杰行动奖章","IND-MEDAL-OP-VIJAY","2001年设立","奖章",[2,4]),
  42:(IND,"西方之星","IND-STAR-PASCHIMI","1971年设立","星章",[1,2]),
  45:(IND,"警察特别勤务奖章","IND-MEDAL-POLICE-SPECIAL","1962年设立","带扣版",[1,4]),
  46:(IND,"东方之星","IND-STAR-POORVI","1971年设立","星章",[2,3]),
  57:(IND,"防卫奖章","IND-MEDAL-RAKSHA-1965","1965年设立","奖章",[3,4]),
  58:(IND,"军役奖章","IND-MEDAL-SAINYA-SEVA","1960年设立","正背合图",[1]),
  59:(IND,"战役服务星章","IND-STAR-SAMAR-SEVA","1965年设立","星章",[2,1]),
  60:(IND,"战争奖章","IND-MEDAL-SANGRAM","1971年设立","奖章",[3,2]),
  63:(IND,"陆军奖章","IND-MEDAL-SENA","1960年设立","奖章",[1,2]),

  77:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","文职组·二级印度英雄星章",[3,2]),
  78:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","文职组·一级战斗领袖星章",[3,5]),
  80:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","文职组·三级祖国烈士金质奖章",[5,4]),
  82:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","文职组·印度之虎大星章",[3,7]),
  83:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","军事组·二级印度英雄星章",[1,2]),
  84:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","军事组·一级战斗领袖星章",[4,5]),
  86:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","军事组·三级祖国烈士金质奖章",[3,2]),
  88:(AZH,"自由印度勋章","AZH-ORDER-TIGER-INDIA","1942年设立","军事组·印度之虎大星章；低清参考",[1]),

  89:(BAH,"加冕纪念章","BAH-MEDAL-CORONATION-1930","1930年","奖章",[2,1]),
  92:(BAH,"巴哈瓦尔布尔—巴基斯坦结盟纪念章","BAH-MEDAL-ALLIANCE-1947","1947年","奖章；低清参考",[1]),
  99:(BAH,"民事长期服务奖章","BAH-MEDAL-CIVIL-LS","约1924年","奖章",[2,5]),
  107:(BAH,"金禧纪念章","BAH-MEDAL-GOLDEN-JUBILEE","1955年","二级·铜质",[2,5]),
  108:(BAH,"金禧纪念章","BAH-MEDAL-GOLDEN-JUBILEE","1955年","三级·白色金属",[4,5]),
  110:(BAH,"第一次世界大战星章","BAH-STAR-GREAT-WAR","1920年设立","1914–1919型",[2,1]),
  112:(BAH,"独立纪念章","BAH-MEDAL-INDEPENDENCE-1947","1947年","奖章",[1,2]),
  113:(BAH,"就任纪念章","BAH-MEDAL-INSTALLATION-1925","1925年","三级·铜质",[4,3]),
  115:(BAH,"就任纪念章","BAH-MEDAL-INSTALLATION-1925","1925年","二级·银质",[2,4]),
  119:(BAH,"军事一般勤务奖章","BAH-MEDAL-MIL-GS","1924年设立","奖章",[2,7]),
  123:(BAH,"海外勤务奖章","BAH-MEDAL-OVERSEAS-WWII","1945年设立","1939–1945型",[2,1]),
  127:(BAH,"银禧纪念章","BAH-MEDAL-SILVER-JUBILEE","1931年","奖章",[1,3]),
  128:(BAH,"胜利星章","BAH-STAR-VICTORY-WWII","1939–1945年","星章",[1,3]),
  129:(BAH,"志愿军团奖章","BAH-MEDAL-VOLUNTEER-CORPS","日期待考","二级·铜质",[1,2]),
  130:(BAH,"志愿军团奖章","BAH-MEDAL-VOLUNTEER-CORPS","日期待考","一级·银质",[1,4]),
  131:(BAH,"工人服务／工程功绩奖章","BAH-MEDAL-WORKS-MERIT","日期待考","奖章",[1,2]),
  135:(BAH,"阿巴西亚勋章","BAH-ORDER-ABASSIA","约1920–1930年设立","二级大军官·颈章",[1]),
  136:(BAH,"阿巴西亚勋章","BAH-ORDER-ABASSIA","约1920–1930年设立","三级指挥官",[2,4]),
  137:(BAH,"阿巴西亚勋章","BAH-ORDER-ABASSIA","约1920–1930年设立","四级成员章；低清参考",[1]),
  139:(BAH,"哈鲁尼亚勋章","BAH-ORDER-HAROONIA","1903年设立","一级大指挥官",[1]),
  143:(BAH,"哈鲁尼亚勋章","BAH-ORDER-HAROONIA","1903年设立","三级指挥官；低清参考",[1]),
  144:(BAH,"哈鲁尼亚勋章","BAH-ORDER-HAROONIA","1903年设立","四级成员章；低清参考",[1]),
  145:(BAH,"哈鲁尼亚勋章","BAH-ORDER-HAROONIA","1903年设立","五级成员章；低清参考",[1]),
  148:(BAH,"萨特莱杰殊勋章","BAH-ORDER-SATLEJ","约1920–1930年设立","二级大军官",[1]),
  150:(BAH,"萨特莱杰殊勋章","BAH-ORDER-SATLEJ","约1920–1930年设立","三级指挥官",[1]),

  167:(BAR,"国家宝石／布施奖章","BAR-MEDAL-RAJYARATNA","1922年设立","一级·金质·Danamoorti",[1,2]),
  221:(BIK,"金禧纪念章","BIK-MEDAL-GOLDEN-JUBILEE","1937年","银质；正背合图",[1]),
  245:(BIK,"荣誉之星勋章","BIK-ORDER-STAR-HONOUR","1947年设立","一级大指挥官·星章",[1]),
  246:(BIK,"荣誉之星勋章","BIK-ORDER-STAR-HONOUR","1947年设立","一级大指挥官·绶章",[1]),
  289:(GWA,"瓜廖尔奖章","GWA-MEDAL","1912年设立","铜质；正背合图",[1]),
  349:(JAK,"战争奖章","JAK-MEDAL-WAR-WWI","1914–1918年","铜质",[1]),
  419:(PAT,"克里希纳勋章","PAT-ORDER-KRISHNA","约1933年","章饰",[4,3]),
  421:(PAT,"克里希纳勋章","PAT-ORDER-KRISHNA","约1933年","链饰",[2]),
  422:(PAT,"功绩勋章","PAT-ORDER-MERIT","约1933年","文职组·一级大十字章",[1]),
  423:(PAT,"功绩勋章","PAT-ORDER-MERIT","约1933年","文职组·一级大十字星章",[1]),
  428:(PAT,"功绩勋章","PAT-ORDER-MERIT","约1933年","军事组·一级大十字章",[1]),
  429:(PAT,"功绩勋章","PAT-ORDER-MERIT","约1933年","军事组·一级大十字星章",[1]),
  448:(PAT,"王室家族勋章","PAT-ROYAL-FAMILY-ORDER","20世纪初","链饰",[3]),
  449:(PAT,"王室家族勋章","PAT-ROYAL-FAMILY-ORDER","20世纪初","大十字章",[3,5]),
  450:(PAT,"王室家族勋章","PAT-ROYAL-FAMILY-ORDER","20世纪初","大十字星章",[4,5]),
  467:(SIK,"旁遮普吉星勋章","SIK-ORDER-PROPITIOUS-STAR-PUNJAB","约1837年","二级章饰",[1,3]),
}

records, manifest, used_hashes = [], [], set()
for idx, (country, name, family, date, variant, picks) in ROWS.items():
    raw = RAW[idx]
    rid = f"IND-MB-{idx:03d}-V01"
    views = []
    for number, image_index in enumerate(picks, 1):
        item = IMAGE_BY_KEY[(idx, image_index)]
        if item["sha256"] in used_hashes:
            raise ValueError(f"duplicate selected image payload: {idx}:{image_index}")
        used_hashes.add(item["sha256"])
        ext = Path(item["local_path"]).suffix.lower() or ".jpg"
        local_rel = f"assets/images/medalbook_india/{idx:03d}_{image_index:02d}{ext}"
        shutil.copy2(ROOT / item["local_path"], ROOT / local_rel)
        view_key = f"IND-MB-{idx:03d}-VIEW{number}"
        views.append({"key": view_key, "label": "完整正面" if number == 1 else "完整背面"})
        manifest.append({
            "key": f"ind-mb-{idx:03d}-{image_index:02d}", "record_id": rid,
            "view_key": view_key, "local_path": local_rel,
            "source_page": raw["page_url"], "image_url": item["url"],
            "artist": "MedalBook catalogue image",
            "license": "Source terms apply; retained for offline research catalogue",
            "dimensions": [item["width"], item["height"]], "bytes": item["bytes"],
            "sha256": item["sha256"], "decoded": True, "visually_checked": True,
        })
    records.append({
        "id": rid, "family": family, "country_zh": country, "name": name,
        "original": raw["original_name"], "date": date, "variant": variant,
        "views": views, "source_ids": [raw["source_id"]],
        "image_kind": "object_photo", "html_eligible": True,
    })

unpictured = [
    {"source_id": row["source_id"], "name": row["page_title"], "date": "待考",
     "page_url": row["page_url"], "status": "有记载未配图"}
    for index, row in enumerate(RAW) if index not in ROWS
]
(ROOT / "data/volumes/india_medalbook_variants.json").write_text(
    json.dumps({"as_of": "2026-09-28", "volume": "印度及历史授予主体 · MedalBook", "records": records}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(ROOT / "data/volumes/india_medalbook_variants_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-28", "images": manifest, "unpictured_candidates": unpictured}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({
    "records": len(records), "families": len({r["family"] for r in records}),
    "views": len(manifest), "unpictured": len(unpictured),
    "polities": len({r["country_zh"] for r in records}),
}, ensure_ascii=False))
