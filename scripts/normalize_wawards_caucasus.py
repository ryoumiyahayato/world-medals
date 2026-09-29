"""Normalize Georgia and the net-new Armenia differential from completed Wawards indexes."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CONFIG={
"georgia":("GEO","格鲁吉亚",{
"order-of-the-national-hero-of-georgia":"格鲁吉亚民族英雄勋章","st-george-s-order-of-victory":"圣乔治胜利勋章","order-of-david-the-builder":"建国者大卫勋章","order-of-queen-tamara":"塔玛尔女王勋章","presidential-order-of-excellence":"总统卓越勋章","order-of-st-nicholas":"圣尼古拉勋章","order-of-the-golden-fleece":"金羊毛勋章","order-of-vakhtang-gorgasali":"瓦赫唐·戈尔加萨利勋章","order-of-honor":"荣誉勋章","medal-for-civil-sacrifice":"公民奉献奖章","medal-of-military-valour":"军事英勇奖章","medal-of-military-honour":"军事荣誉奖章","medal-of-honour":"荣誉奖章","ministry-of-the-interior-medal-of-bravery":"内务部英勇奖章","ministry-of-the-interior-distinguished-service-medal":"内务部卓越服务奖章","ministry-of-the-interior-medal-for-impeccable-service":"内务部无瑕服务奖章","ministry-of-defense-medal-for-impeccable-service":"国防部无瑕服务奖章","medal-for-devotion-to-the-motherland":"献身祖国奖章","medal-kakutsa-cholokashvili":"卡库察·乔洛卡什维利奖章","medal-general-kvinitadze":"克维尼塔泽将军奖章","lifesaving-medal":"救生奖章","medal-for-peacekeeping-operations":"维和行动奖章","medal-general-mazniashvili":"马兹尼阿什维利将军奖章","medal-for-courage-in-the-struggle-against-disaster":"抗灾勇气奖章","medal-giorgi-antsukhelidze":"乔治·安楚赫利泽奖章","medal-didgori-cross":"迪德戈里十字奖章","medal-80-years-of-internal-troops":"内卫部队八十周年奖章","jubilee-medal-65-years-of-victory-over-fascism":"战胜法西斯六十五周年纪念章","jubilee-medal-70-years-of-victory-over-fascism":"战胜法西斯七十周年纪念章","jubilee-medal-75-years-of-victory-over-fascism":"战胜法西斯七十五周年纪念章"},set(),"georgia_wawards_families"),
"armenia":("ARM-WA","亚美尼亚共和国",{
"medal-for-excellent-maintenance-of-public-order":"维护公共秩序优异奖章","medal-of-gratitude":"感恩奖章","medal-of-merit-in-work":"劳动功绩奖章","medal-of-parental-glory":"父母荣光奖章","medal-for-fair-service":"廉正服务奖章","medal-of-marshal-baghramyan":"巴格拉米扬元帅奖章","medal-of-drastamat-kanayan":"德拉斯塔马特·卡纳扬奖章","medal-of-garegin-nzdeh":"加列金·恩日德奖章","medal-of-nelson-stepanyan":"涅尔松·斯捷潘尼扬奖章","medal-of-vazgen-sargsyan":"瓦兹根·萨尔基相奖章","medal-of-admiral-isakov":"伊萨科夫海军上将奖章","medal-of-andranik-ozanyan":"安德拉尼克·奥扎尼扬奖章","medal-for-combat-duty":"战斗勤务奖章","jubilee-medal-20-years-of-armed-forces":"武装力量二十周年纪念章","medal-for-heroism":"英雄行为奖章","medal-for-strengthening-law-and-order":"加强法治秩序奖章","medal-for-strengthening-cooperation":"加强合作奖章","medal-for-protection-of-law":"法律保护奖章","medal-for-combat-support":"战斗保障奖章","police-medal-for-long-service":"警察长期服务奖章"},
{"national-hero-of-armenia","order-of-glory","order-of-tigran-the-great","order-of-the-combat-cross","order-st-vardan-mamikonian","order-of-st-mesrop-mashtots","order-of-honor","order-for-services-to-the-motherland","order-of-friendship","medal-for-courage","medal-for-combat-service","medal-of-services-to-the-motherland","medal-of-mkhitar-gosh","medal-of-mkhitar-heratsi","medal-of-anania-shirakatsi","medal-of-movses-khorenatsi"},"armenia_wawards_differential")}
for scope,(prefix,country,names,skip,stem) in CONFIG.items():
 rows=[json.loads(x) for x in (ROOT/f"data/raw_candidates/wawards_{scope}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()];out=ROOT/f"assets/images/{stem}";out.mkdir(parents=True,exist_ok=True);records=[];images=[]
 for row in rows:
  slug=Path(urlparse(row["object_url"]).path).stem
  if slug in skip:continue
  if slug not in names:continue
  family=f"{prefix}-{slug.upper().replace('-', '_')}";item=row["original_images"][0];src=ROOT/item["local_path"];rel=f"assets/images/{stem}/{slug}{src.suffix.lower()}";shutil.copy2(src,ROOT/rel)
  with Image.open(src) as im:w,h=im.size;im.verify()
  rid=family+"-REPRESENTATIVE";view=rid+"-VIEW1";date=(row.get("date_candidates") or ["日期待考"])[0]
  if date!="日期待考":date=f"{date}年设立／纪年"
  records.append({"id":rid,"family":family,"country_zh":country,"name":names[slug],"original":row["page_title"],"date":date,"variant":"World Awards对象页所示完整章体；具体等级待考","views":[{"key":view,"label":"完整图样"}],"source_ids":[row["source_id"]],"image_kind":"catalogue_object_or_illustration","html_eligible":True})
  images.append({"key":rid.lower()+"-image","record_id":rid,"view_key":view,"local_path":rel,"source_page":row["object_url"],"image_url":item["image_url"],"license":"source-site research use; publication rights not asserted","dimensions":[w,h],"bytes":src.stat().st_size,"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"decoded":True,"visually_checked":True})
 (ROOT/f"data/volumes/{stem}.json").write_text(json.dumps({"as_of":"2026-09-28","volume":country,"records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (ROOT/f"data/volumes/{stem}_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":[],"notes":["Armenia output is a differential against the existing 16-family volume; source images for overlapping families remain cached."]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"scope":scope,"source_rows":len(rows),"formal_rows":len(records),"families":len({r['family'] for r in records}),"skipped_existing":len(rows)-len(records)},ensure_ascii=False))
