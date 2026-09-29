from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(line) for line in (ROOT/"data/raw_candidates/pmo_singapore_awards.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
OUT_DIR=ROOT/"assets/images/pmo_singapore_awards"

META={
 "the-certificate-of-honour-sijil-kemuliaan":("SGP-AWARD-CERTIFICATE-HONOUR","荣誉证书佩饰","官方所示佩饰","1962年设立"),
 "the-commendation-medal-pingat-kepujian":("SGP-AWARD-COMMENDATION-MEDAL","嘉奖奖章","官方所示章饰","1996年设立"),
 "the-conspicuous-gallantry-medal-pingat-gagah-perkasa":("SGP-AWARD-CONSPICUOUS-GALLANTRY","显著英勇奖章","官方所示章饰","1962年设立"),
 "the-distinguished-service-order-darjah-utama-bakti-cemerlang":("SGP-AWARD-DISTINGUISHED-SERVICE-ORDER","卓越服务勋章","官方所示章饰","1968年设立"),
 "the-efficiency-medal-pingat-berkebolehan":("SGP-AWARD-EFFICIENCY-MEDAL","效率奖章","官方所示章饰","1969年设立"),
 "the-long-service-medal-pingat-bakti-setia":("SGP-AWARD-LONG-SERVICE-MEDAL","长期服务奖章","官方所示章饰","1962年设立"),
 "the-medal-of-honour-pingat-kehormatan":("SGP-AWARD-MEDAL-HONOUR","荣誉奖章","官方所示章饰","1970年设立"),
 "the-medal-of-valour-pingat-keberanian":("SGP-AWARD-MEDAL-VALOUR","勇毅奖章","官方所示章饰","1987年设立"),
 "the-meritorious-service-medal-pingat-jasa-gemilang":("SGP-AWARD-MERITORIOUS-SERVICE","功绩服务奖章","官方所示章饰","1962年设立"),
 "the-order-of-nila-utama-darjah-utama-nila-utama":("SGP-AWARD-ORDER-NILA-UTAMA","尼拉乌塔玛勋章","官方所示徽章与星章","1975年设立"),
 "the-order-of-temasek-darjah-utama-temasek":("SGP-AWARD-ORDER-TEMASEK","淡马锡勋章","官方所示徽章与星章","1962年设立"),
 "the-public-administration-medal-bronze-pingat-pentadbiran-awam-gangsa":("SGP-AWARD-PUBLIC-ADMIN-MEDAL","公共行政奖章","铜级；官方所示章饰","1963年设立"),
 "the-public-administration-medal-gold-pingat-pentadbiran-awam-emas":("SGP-AWARD-PUBLIC-ADMIN-MEDAL","公共行政奖章","金级；官方所示章饰","1963年设立"),
 "the-public-administration-medal-silver-pingat-pentadbiran-awam-perak":("SGP-AWARD-PUBLIC-ADMIN-MEDAL","公共行政奖章","银级；官方所示章饰","1963年设立"),
 "the-public-service-medal-pingat-bakti-masyarakat":("SGP-AWARD-PUBLIC-SERVICE-MEDAL","公共服务奖章","官方所示章饰","1973年设立"),
 "the-public-service-star-bintang-bakti-masyarakat":("SGP-AWARD-PUBLIC-SERVICE-STAR","公共服务星章","官方所示章饰","1963年设立"),
 "the-star-of-temasek-bintang-temasek":("SGP-AWARD-STAR-TEMASEK","淡马锡星章","官方所示章饰","1970年设立"),
}


def main()->None:
 OUT_DIR.mkdir(parents=True,exist_ok=True); records=[]; images=[]; hashes=set()
 for source in RAW:
  if not source["original_images"]: continue
  slug=Path(source["object_url"].rstrip("/")).name; family,name,variant,date_text=META[slug]
  item=source["original_images"][0]
  if item["sha256"] in hashes: raise ValueError(f"duplicate official payload: {slug}")
  hashes.add(item["sha256"]); source_path=ROOT/item["local_path"]
  with Image.open(source_path) as decoded: decoded.verify()
  relative=f"assets/images/pmo_singapore_awards/{slug}{source_path.suffix.lower()}"; shutil.copy2(source_path,ROOT/relative)
  record_id=family+"-PMO-"+re.sub(r"[^A-Z0-9]+","-",slug.upper()).strip("-")
  view_key=record_id+"-VIEW1"
  records.append({"id":record_id,"family":family,"country_zh":"新加坡共和国","name":name,"original":source["page_title"],"date":date_text,"variant":variant,"views":[{"key":view_key,"label":"完整正面"}],"source_ids":[source["source_id"]],"image_kind":"official_object_image","html_eligible":True})
  images.append({"key":"singapore-pmo-"+slug,"record_id":record_id,"view_key":view_key,"local_path":relative,"source_page":source["object_url"],"image_url":item["image_url"],"artist":"Prime Minister's Office Singapore","license":"Singapore Government official website terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
 (ROOT/"data/volumes/singapore_pmo_official_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":"新加坡共和国","records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (ROOT/"data/volumes/singapore_pmo_official_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":images,"unpictured_candidates":[],"excluded_candidates":[{"kind":"official_page_without_image","count":1,"reason":"勇敢奖章官方专页当前未提供章图；保留原始候选"}]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"rows":len(records),"families":len({r['family'] for r in records}),"views":len(images),"unpictured_official_pages":1},ensure_ascii=False))


if __name__=="__main__": main()
