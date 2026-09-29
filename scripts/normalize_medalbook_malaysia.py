from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT=Path(__file__).resolve().parents[1]
RAW=[json.loads(line) for line in (ROOT/"data/raw_candidates/medalbook_malaysia.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
SWEEP=json.loads((ROOT/"data/source_sweeps/medalbook_malaysia_images_2026-09-28.json").read_text(encoding="utf-8"))
OUT_DIR=ROOT/"assets/images/medalbook_malaysia"

# index: (scope stem, country label, family, Chinese name, variant, date, image numbers)
ROWS={
0:("malaysia_federal","马来西亚联邦","MYS-FED-ACTIVE-SERVICE","现役服务奖章","章饰；正背","1960年设立",[1,3]),
17:("malaysia_federal","马来西亚联邦","MYS-FED-LOYALTY-CROWN","效忠马来西亚王冠勋章","指挥官级；正背","1966年设立",[2,1]),
20:("malaysia_federal","马来西亚联邦","MYS-FED-LOYALTY-CROWN","效忠马来西亚王冠勋章","大指挥官级挂章","1966年设立",[1]),
21:("malaysia_federal","马来西亚联邦","MYS-FED-LOYALTY-CROWN","效忠马来西亚王冠勋章","大指挥官级星章","1966年设立",[1]),
42:("malaysia_federal","马来西亚联邦","MYS-FED-CROWN-REALM","王国王冠勋章","项链章","1958年设立",[1]),
43:("malaysia_federal","马来西亚联邦","MYS-FED-DEFENDER-REALM","护国勋章","指挥官级挂章","1958年设立",[1]),
44:("malaysia_federal","马来西亚联邦","MYS-FED-DEFENDER-REALM","护国勋章","指挥官级星章","1958年设立",[1]),
49:("malaysia_federal","马来西亚联邦","MYS-FED-DEFENDER-REALM","护国勋章","成员级；正背","1958年设立",[4,2]),
51:("malaysia_federal","马来西亚联邦","MYS-FED-DEFENDER-REALM","护国勋章","银质奖章；正背","1958年设立",[1,2]),
102:("sabah","沙巴州","MYS-SABAH-KINABALU","神山勋章","大指挥官级项链章","1963年设立",[1]),
108:("sarawak","砂拉越州","MYS-SARAWAK-DISTINGUISHED-SERVICE","卓越服务奖章","一级","设立时间待考",[1]),
109:("sarawak","砂拉越州","MYS-SARAWAK-DISTINGUISHED-SERVICE","卓越服务奖章","二级","设立时间待考",[1]),
111:("sarawak","砂拉越州","MYS-SARAWAK-FAITHFUL-MERITORIOUS","忠诚功绩服务奖章","章饰；正背","设立时间待考",[2,4]),
171:("sarawak","砂拉越州","MYS-SARAWAK-STAR","砂拉越之星至高勋章","成员级；正背","1973年设立",[4,2]),
174:("sarawak","砂拉越州","MYS-SARAWAK-STAR","砂拉越之星至高勋章","军官级；正背","1973年设立",[3,2]),
189:("johor","柔佛苏丹国","MYS-JOHOR-ABU-BAKAR-MEDAL","苏丹阿布·巴卡尔奖章","章饰","1886年设立",[1]),
202:("johor","柔佛苏丹国","MYS-JOHOR-LOYALTY-SULTAN-ISMAIL","苏丹伊斯迈效忠至高勋章","伙伴级；正背","1974年设立",[2,1]),
209:("johor","柔佛苏丹国","MYS-JOHOR-CROWN","柔佛王冠勋章","骑士指挥官级挂章；正背","1886年设立",[4,7]),
212:("johor","柔佛苏丹国","MYS-JOHOR-CROWN","柔佛王冠勋章","骑士大指挥官级星章；正背","1886年设立",[2,4]),
217:("johor","柔佛苏丹国","MYS-JOHOR-ROYAL-FAMILY","柔佛王家家族勋章","大指挥官级挂章与星章合图","1886年设立",[1]),
219:("johor","柔佛苏丹国","MYS-JOHOR-ROYAL-FAMILY","柔佛王家家族勋章","大指挥官级项链章","1886年设立",[1]),
238:("kedah","吉打苏丹国","MYS-KEDAH-DISTINGUISHED-SERVICE-STAR","吉打卓越服务星章","章饰","1952年设立",[1]),
271:("kedah","吉打苏丹国","MYS-KEDAH-ROYAL-FAMILY","吉打王家家族勋章","挂章","1964年设立",[1]),
272:("kedah","吉打苏丹国","MYS-KEDAH-ROYAL-FAMILY","吉打王家家族勋章","星章","1964年设立",[1]),
273:("kedah","吉打苏丹国","MYS-KEDAH-ROYAL-FAMILY","吉打王家家族勋章","项链章","1964年设立",[1]),
303:("kelantan","吉兰丹苏丹国","MYS-KELANTAN-CROWN","吉兰丹王冠至显赫勋章","骑士大指挥官级星章","1916年设立",[1]),
304:("kelantan","吉兰丹苏丹国","MYS-KELANTAN-CROWN","吉兰丹王冠至显赫勋章","骑士大指挥官级项链章","1916年设立",[2]),
404:("pahang","彭亨苏丹国","MYS-PAHANG-CROWN","彭亨王冠尊贵勋章","骑士伙伴级星章","1968年设立",[1]),
409:("pahang","彭亨苏丹国","MYS-PAHANG-CROWN-INDRA-FAMILY","彭亨因陀罗王冠至尊家族勋章","一级挂章；正背","1967年设立",[1,3]),
458:("perak","霹雳苏丹国","MYS-PERAK-CURA-SI-MANJA-KINI","古拉西曼佳基尼至显赫勋章","I型（1969–1989）·大骑士项链章","1969年设立；I型使用至1989年",[1]),
}


def main()->None:
 OUT_DIR.mkdir(parents=True,exist_ok=True)
 items={(x["record_index"],x["image_index"]):x for x in SWEEP["items"] if x["status"]=="downloaded"}
 volumes=defaultdict(lambda:{"records":[],"images":[]}); hashes=set()
 for index,(stem,country,family,name,variant,date_text,picks) in ROWS.items():
  source=RAW[index]; record_id=f"{family}-MEDALBOOK-{index:03d}"; views=[]
  for order,image_no in enumerate(picks,1):
   item=items[(index,image_no)]
   if item["sha256"] in hashes: raise ValueError(f"duplicate selected payload {index}:{image_no}")
   hashes.add(item["sha256"]); source_path=ROOT/item["local_path"]
   with Image.open(source_path) as decoded: decoded.verify()
   relative=f"assets/images/medalbook_malaysia/{index:03d}_{image_no:02d}{source_path.suffix.lower()}"; shutil.copy2(source_path,ROOT/relative)
   view_key=f"{record_id}-VIEW{order}"; views.append({"key":view_key,"label":"完整正面" if order==1 else "完整背面"})
   volumes[stem]["images"].append({"key":f"malaysia-medalbook-{index:03d}-{image_no:02d}","record_id":record_id,"view_key":view_key,"local_path":relative,"source_page":source["page_url"],"image_url":item["url"],"artist":"MedalBook catalogue object photograph","license":"Source terms apply; retained for offline research catalogue","dimensions":[item["width"],item["height"]],"bytes":item["bytes"],"sha256":item["sha256"],"decoded":True,"visually_checked":True})
  volumes[stem]["country"]=country
  volumes[stem]["records"].append({"id":record_id,"family":family,"country_zh":country,"name":name,"original":source["page_title"],"date":date_text,"variant":variant,"views":views,"source_ids":[source["source_id"]],"image_kind":"object_photo","html_eligible":True})
 for stem,data in volumes.items():
  (ROOT/f"data/volumes/{stem}_medalbook_variants.json").write_text(json.dumps({"as_of":"2026-09-28","volume":data["country"],"records":data["records"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  (ROOT/f"data/volumes/{stem}_medalbook_variants_manifest.json").write_text(json.dumps({"as_of":"2026-09-28","images":data["images"],"unpictured_candidates":[],"excluded_candidates":[]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({stem:{"rows":len(data["records"]),"families":len({r['family'] for r in data["records"]}),"views":len(data["images"])} for stem,data in volumes.items()},ensure_ascii=False))


if __name__=="__main__": main()
