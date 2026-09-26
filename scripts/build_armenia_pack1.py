"""Build a first Armenia country volume from the complete official-design files on Commons.

Names and award status are checked against the Armenian Presidency's current
Orders and Medals pages.  Commons supplies the locally cached complete designs.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-local-research/1.0 (offline catalogue)"
OUT_DIR = ROOT / "assets/images/armenia_pack1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (file title, stable family suffix, Chinese name, English/Armenian working name, variant)
ITEMS = [
    ("Order National Hero of Armenia.svg", "MOTHERLAND", "祖国勋章", "The Order of Motherland / Հայրենիքի շքանշան", "国家最高荣誉所佩勋章；官方图式"),
    ("Order of Glory Armenia.svg", "GLORY", "光荣勋章", "The Order of Glory / Փառքի շքանշան", "官方图式"),
    ("Order of Tigran the Great.svg", "TIGRAN", "提格兰大帝勋章", "The Order Tigran the Great / Տիգրան Մեծ շքանշան", "官方图式"),
    ("Order of the Combat Cross Armenia.svg", "COMBAT-CROSS", "战斗十字勋章", "The Order of the Combat Cross / Մարտական խաչ", "文件页所示等级；官方图式"),
    ("Vardan Mamikonian.svg", "VARDAN", "圣瓦尔丹·马米科尼扬勋章", "The Order St. Vardan Mamikonian / Սուրբ Վարդան Մամիկոնյանի շքանշան", "官方图式"),
    ("Mashtosmedal.svg", "MASHTOTS", "圣梅斯罗普·马什托茨勋章", "The Order of St. Mesrop Mashtots / Սուրբ Մեսրոպ Մաշտոցի շքանշան", "官方图式"),
    ("Order of Honor Armenia.svg", "HONOUR", "荣誉勋章", "The Order of Honor / Պատվո շքանշան", "官方图式"),
    ("Order Services to the Fatherland Armenia.svg", "SERVICES-FATHERLAND", "为祖国服务勋章", "Order for Services to the Motherland / Հայրենիքին մատուցած ծառայությունների համար", "文件页所示等级；官方图式"),
    ("Order of Friendship (Armenia).svg", "FRIENDSHIP", "友谊勋章", "Order of Friendship / Բարեկամության շքանշան", "官方图式"),
    ("Medal For Courage Armenia.svg", "COURAGE", "勇气奖章", "The Medal of Courage / Արիության մեդալ", "官方图式"),
    ("Medal for Combat Service Armenia.svg", "COMBAT-SERVICE", "战斗服务奖章", "The Medal for Combat Service / Մարտական ծառայության մեդալ", "官方图式"),
    ("Medal of Services to the Motherland 2 Armenia.svg", "SERVICES-MEDAL", "为祖国服务奖章", "The Medal of Services to the Motherland / Հայրենիքին մատուցած ծառայությունների համար մեդալ", "二等；官方图式"),
    ("Mkhitar Gosh Medal.svg", "MKHITAR-GOSH", "姆希塔尔·戈什奖章", "The Medal of Mkhitar Gosh / Մխիթար Գոշի մեդալ", "官方图式"),
    ("Mkhitar Heratsi Medal.svg", "MKHITAR-HERATSI", "姆希塔尔·赫拉齐奖章", "The Medal of Mkhitar Heratsi / Մխիթար Հերացու մեդալ", "官方图式"),
    ("Anania Shirakatsi Medal.svg", "ANANIA", "阿纳尼亚·希拉卡齐奖章", "The Medal of Anania Shirakatsi / Անանիա Շիրակացու մեդալ", "官方图式"),
    ("Order of Movses Khorenatsi.svg", "MOVSES", "莫夫谢斯·霍列纳齐奖章", "The Medal of Movses Khorenatsi / Մովսես Խորենացու մեդալ", "官方图式"),
]


def image_info(title: str) -> dict:
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": 2,
        "prop": "imageinfo", "titles": "File:" + title,
        "iiprop": "url|size|sha1|mime|extmetadata", "iiurlwidth": 1800,
    })
    req = urllib.request.Request(API + "?" + params, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        page = json.load(response)["query"]["pages"][0]
    if "missing" in page or not page.get("imageinfo"):
        raise RuntimeError(f"Commons file missing: {title}")
    return page["imageinfo"][0]


old_manifest_path = ROOT / "data/volumes/armenia_pack1_manifest.json"
old_images = ({item["source_id"]: item for item in json.loads(old_manifest_path.read_text(encoding="utf-8")).get("images", [])}
              if old_manifest_path.is_file() else {})
records, images, raw = [], [], []
for index, (title, suffix, name, original, variant) in enumerate(ITEMS, 1):
    source_id = f"commons-armenia-{index:02d}"
    out = OUT_DIR / f"arm-{index:02d}.png"
    cached = old_images.get(source_id)
    if cached and out.is_file():
        source_url = cached["source_original_url"]
        license_name = cached.get("license", "Commons文件页所示许可")
    else:
        info = image_info(title)
        source_url = info["url"]
        download_url = info.get("thumburl", source_url)
        req = urllib.request.Request(download_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as response:
            out.write_bytes(response.read())
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "Commons文件页所示许可")
    with Image.open(out) as im:
        im.verify()
    with Image.open(out) as im:
        width, height = im.size
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    record_id = f"ARM-{suffix}-01"
    view_key = f"{record_id}-FRONT"
    records.append({
        "id": record_id, "family": f"ARM-{suffix}", "country_zh": "亚美尼亚",
        "name": name, "original": original,
        "date": "亚美尼亚共和国时期；初设日期待考",
        "variant": variant, "views": [{"key": view_key, "label": "官方图式"}],
        "source_ids": [source_id], "image_kind": "official_design", "html_eligible": True,
    })
    local_path = out.relative_to(ROOT).as_posix()
    images.append({
        "view_key": view_key, "local_path": local_path, "source_id": source_id,
        "download_status": "downloaded_complete_official_design",
        "source_page_url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title.replace(" ", "_"), safe="/:()'"),
        "source_original_url": source_url, "license": license_name,
        "width": width, "height": height, "sha256": digest,
    })
    raw.append({
        "source_id": source_id, "country_zh": "亚美尼亚", "file_title": "File:" + title,
        "file_page_url": images[-1]["source_page_url"], "original_url": source_url,
        "width": width, "height": height, "license": license_name,
        "presidency_reference": "https://www.president.am/en/orders/" if "勋章" in name else "https://www.president.am/en/medals/",
        "status": "INGESTED_OFFICIAL_DESIGN",
    })
    time.sleep(0.8)

# Two Commons designs are plates containing both statutory grades.  Preserve
# the source plate above, but publish each complete badge as its own local crop
# so a row never ambiguously represents two grades.
for base_id, crops in {
    "ARM-COMBAT-CROSS-01": [
        ("ARM-COMBAT-CROSS-2-01", "二级；官方图式", (0.00, 0.00, 0.50, 1.00)),
        ("ARM-COMBAT-CROSS-1-01", "一级；官方图式", (0.50, 0.00, 1.00, 1.00)),
    ],
    "ARM-SERVICES-FATHERLAND-01": [
        ("ARM-SERVICES-FATHERLAND-1-01", "一等；官方图式", (0.00, 0.00, 1.00, 0.50)),
        ("ARM-SERVICES-FATHERLAND-2-01", "二等；官方图式", (0.00, 0.50, 1.00, 1.00)),
    ],
}.items():
    base_record = next(record for record in records if record["id"] == base_id)
    base_image = next(image for image in images if image["view_key"] == base_record["views"][0]["key"])
    records.remove(base_record)
    images.remove(base_image)
    source_path = ROOT / base_image["local_path"]
    with Image.open(source_path) as source:
        width, height = source.size
        for suffix_index, (record_id, variant, bounds) in enumerate(crops, 1):
            box = (int(width * bounds[0]), int(height * bounds[1]), int(width * bounds[2]), int(height * bounds[3]))
            cropped = source.crop(box)
            out = source_path.with_name(source_path.stem + f"-grade-{suffix_index}.png")
            cropped.save(out, "PNG")
            view_key = record_id + "-FRONT"
            record = dict(base_record)
            record.update({"id": record_id, "variant": variant, "views": [{"key": view_key, "label": "官方图式"}]})
            records.append(record)
            derived = dict(base_image)
            derived.update({
                "view_key": view_key, "local_path": out.relative_to(ROOT).as_posix(),
                "download_status": "complete_grade_crop_from_official_design_plate",
                "width": cropped.width, "height": cropped.height,
                "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
            })
            images.append(derived)

records.sort(key=lambda record: record["id"])
images.sort(key=lambda image: image["view_key"])

(ROOT / "data/volumes/armenia_pack1.json").write_text(
    json.dumps({"as_of": "2026-09-26", "records": records}, ensure_ascii=False, indent=2), encoding="utf-8"
)
(ROOT / "data/volumes/armenia_pack1_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-26", "images": images, "unpictured_candidates": []}, ensure_ascii=False, indent=2), encoding="utf-8"
)
(ROOT / "data/raw_candidates/commons_armenia_pack1.jsonl").write_text(
    "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in raw), encoding="utf-8"
)
print(json.dumps({"records": len(records), "images": len(images), "country": "亚美尼亚"}, ensure_ascii=False))
