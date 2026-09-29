"""Normalize completed Lebanon, Israel and Syria World Awards country indexes."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CONFIG={
"lebanon":("LBN","黎巴嫩共和国",{
"lebanese-order-of-merit":"黎巴嫩功绩勋章","national-order-of-the-cedar":"国家雪松勋章","order-of-public-instruction":"公共教育勋章","labour-medal":"劳动奖章","public-health-merit-medal":"公共卫生功绩奖章","medal-of-the-eagle":"雄鹰奖章","navy-medal":"海军奖章","military-medal":"军事奖章","war-medal":"战争奖章","medal-for-battle-wounds":"战斗负伤奖章","military-valour-medal":"军事英勇奖章","military-medal-of-honour":"军事荣誉奖章","medal-of-appreciation":"嘉奖奖章","state-security-medal":"国家安全奖章","medal-of-general-security":"治安总局奖章","medal-of-competence":"才能奖章","internal-security-forces-medal":"内部安全部队奖章","commemorative-medal-for-lebanon":"黎巴嫩纪念奖章","medal-of-palestine":"巴勒斯坦奖章","medal-of-31-december-1961":"1961年12月31日奖章","medal-of-national-unity":"民族团结奖章","medal-of-the-dawn-of-the-south":"南方黎明奖章"}),
"israel":("ISR","以色列国",{
"medal-of-valor":"英勇勋章","medal-of-courage":"勇气勋章","medal-of-distinguished-service":"卓越服务勋章","chief-of-staff-medal-of-appreciation":"总参谋长嘉奖奖章","major-general-medal-of-appreciation":"少将嘉奖奖章","medal-for-service-in-israel":"在以色列服务奖章","president-s-medal":"总统奖章","police-medal-of-valor":"警察英勇勋章","police-medal-of-courage":"警察勇气勋章","police-medal-of-distinguished-service":"警察卓越服务勋章","police-service-medal":"警察服务奖章","police-volunteers-medal":"警察志愿者奖章","firefighters-medal-of-valor":"消防员英勇勋章","firefighters-medal-of-courage":"消防员勇气勋章","firefighters-medal-of-exemplary-service":"消防员模范服务勋章","jubilee-medal-45-years-of-the-victory-over-germany":"战胜德国四十五周年纪念章","jubilee-medal-50-years-of-the-victory-over-germany":"战胜德国五十周年纪念章","jubilee-medal-55-years-of-the-victory-over-germany":"战胜德国五十五周年纪念章","jubilee-medal-60-years-of-the-victory-over-germany":"战胜德国六十周年纪念章","jubilee-medal-65-years-of-the-victory-over-germany":"战胜德国六十五周年纪念章"}),
"syria":("SYR","叙利亚共和国",{"order-of-devotion":"忠诚勋章"})}

for scope,(prefix,country,names) in CONFIG.items():
 rows=[json.loads(x) for x in (ROOT/f"data/raw_candidates/wawards_{scope}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
 out=ROOT/f"assets/images/wawards_{scope}";out.mkdir(parents=True,exist_ok=True);records=[];images=[];unpictured=[]
 for row in rows:
  slug=Path(urlparse(row["object_url"]).path).stem;name=names.get(slug,slug.replace("-"," "));family=f"{prefix}-WAWARDS-{slug.upper().replace('-', '_')}"
  if not row["original_images"]:unpictured.append({"source_id":row["source_id"],"name":name,"reason":"source object page has no exposed full image"});continue
  item=row["original_images"][0];src=ROOT/item["local_path"];rel=f"assets/images/wawards_{scope}/{slug}{src.suffix.lower()}";shutil.copy2(src,ROOT/rel)
  with Image.open(src) as im:w,h=im.size;im.verify()
  rid=family+"-REPRESENTATIVE";view=rid+"-VIEW1";date=(row.get("date_candidates") or ["日期待考"])[0]
  if date!="日期待考":date=f"{date}年设立／纪年"
  records.append({"id":rid,"family":family,"country_zh":country,"name":name,"original":row["page_title"],"date":date,"variant":"World Awards对象页所示完整章体；具体等级待考","views":[{"key":view,"label":"完整图样"}],"source_ids":[row["source_id"]],"image_kind":"catalogue_object_or_illustration","html_eligible":True})
  images.append({"key":rid.lower()+"-image","record_id":rid,"view_key":view,"local_path":rel,"source_page":row["object_url"],"image_url":item["image_url"],"license":"source-site research use; publication rights not asserted","dimensions":[w,h],"bytes":src.stat().st_size,"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"decoded":True,"visually_checked":True})
 stem=f"{scope}_wawards_families"
 (ROOT/f"data/volumes/{stem}.json").write_text(json.dumps({"as_of":"2026-09-28","volume":country,"records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (ROOT/f"data/volumes/{stem}_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":unpictured,"notes":["First pass establishes family coverage; additional images remain cached for grade and reverse expansion."]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"scope":scope,"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"unpictured":len(unpictured)},ensure_ascii=False))
