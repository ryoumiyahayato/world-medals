from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-09-29"
BATCH = "luxembourg_official_book_2007"
PDF_LOCAL = "sources/books/luxembourg_honorary_distinctions_2007_en.pdf"
PDF_URL = "https://sip.gouvernement.lu/dam-assets/publications/brochure-livre/minist-etat/sip/brochure/Distinctions_honorifique/Distinctions_honorifiques-EN.pdf"
PUBLICATION_URL = "https://gouvernement.lu/fr/publications.gouv2024_sip%2Bfr%2Bpublications%2Bminist-etat%2Bsip%2Bbrochure%2BDistinctions_honorifique.html"
COURT_URL = "https://monarchie.lu/en/luxembourg-monarchy/les-ordres"
RAW_DIR = ROOT / "assets/raw/luxembourg_official_book_2007"
OUT_DIR = ROOT / "assets/images/luxembourg_official_book_2007"
OUT_DIR.mkdir(parents=True, exist_ok=True)


FAMILIES = {
    "LU-GOLD-LION": {
        "name": "拿骚王室金狮勋章",
        "original": "Ordre du Lion d'Or de la Maison de Nassau / Order of the Gold Lion of the House of Nassau",
        "date": "1858年3月31日设立；1905年恢复为拿骚两支王室共有勋章",
    },
    "LU-ADOLPH-NASSAU": {
        "name": "拿骚阿道夫民事与军事功绩勋章",
        "original": "Ordre du Mérite civil et militaire d'Adolphe de Nassau / Order of Civil and Military Merit of Adolph of Nassau",
        "date": "1858年5月8日设立；1890年在卢森堡恢复；现行八级名称自1927年",
    },
    "LU-OAK-CROWN": {
        "name": "橡树冠勋章",
        "original": "Ordre de la Couronne de chêne / Order of the Oak Crown",
        "date": "1841年12月29日设立；1858年形成五级并附功绩奖章；1872年镀金银质奖章取代金质奖章",
    },
    "LU-ORDER-MERIT": {
        "name": "卢森堡大公国功绩勋章",
        "original": "Ordre de Mérite du Grand-Duché de Luxembourg / Order of Merit of the Grand Duchy of Luxembourg",
        "date": "1961年1月23日设立",
    },
}


# record suffix, family, variant, [(source image, view label, output suffix)], PDF page
ROWS = [
    ("001", "LU-GOLD-LION", "单一等级佩章；正背面；官方政府图册实物图·低清参考", [("page-04-image-01.jpg", "佩章完整正面"), ("page-04-image-02.jpg", "同式佩章完整背面")], 4),
    ("002", "LU-GOLD-LION", "单一等级星章；官方政府图册实物图·低清参考", [("page-04-image-03.jpg", "星章完整正面")], 4),
    ("003", "LU-ADOLPH-NASSAU", "大十字级·民事型佩章；正背面；官方政府图册实物图·低清参考", [("page-05-image-01.jpg", "佩章完整正面"), ("page-05-image-02.jpg", "同式佩章完整背面")], 5),
    ("004", "LU-ADOLPH-NASSAU", "大十字级·民事型星章；官方政府图册实物图·低清参考", [("page-05-image-03.jpg", "星章完整正面")], 5),
    ("005", "LU-ADOLPH-NASSAU", "大十字级·军事型加剑佩章；正背面；官方政府图册实物图·低清参考", [("page-06-image-04.jpg", "加剑佩章完整正面"), ("page-06-image-05.jpg", "同式加剑佩章完整背面")], 6),
    ("006", "LU-ADOLPH-NASSAU", "大十字级·军事型加剑星章；官方政府图册实物图·低清参考", [("page-06-image-02.jpg", "加剑星章完整正面")], 6),
    ("007", "LU-ADOLPH-NASSAU", "大军官级佩章；官方政府图册实物图·低清参考", [("page-06-image-03.jpg", "佩章完整正面")], 6),
    ("008", "LU-ADOLPH-NASSAU", "大军官级星章；官方政府图册实物图·低清参考", [("page-06-image-01.jpg", "星章完整正面")], 6),
    ("009", "LU-ADOLPH-NASSAU", "王冠司令级佩章；官方政府图册实物图·低清参考", [("page-07-image-04.jpg", "佩章完整正面")], 7),
    ("010", "LU-ADOLPH-NASSAU", "司令级佩章；官方政府图册实物图·低清参考", [("page-07-image-03.jpg", "佩章完整正面")], 7),
    ("011", "LU-ADOLPH-NASSAU", "女士荣誉十字；等同司令级；官方政府图册实物图·低清参考", [("page-07-image-01.jpg", "女士荣誉十字完整正面")], 7),
    ("012", "LU-ADOLPH-NASSAU", "王冠军官级佩章；官方政府图册实物图·低清参考", [("page-07-image-05.jpg", "佩章完整正面")], 7),
    ("013", "LU-ADOLPH-NASSAU", "军官级佩章；结上玫瑰花结；官方政府图册实物图·低清参考", [("page-07-image-02.jpg", "佩章完整正面")], 7),
    ("014", "LU-ADOLPH-NASSAU", "王冠骑士级佩章；图册页首误排作王冠军官级，依八级体系及无玫瑰结形制校正；官方政府图册实物图·低清参考", [("page-08-image-06.jpg", "佩章完整正面")], 8),
    ("015", "LU-ADOLPH-NASSAU", "骑士级佩章；图册页首误排作军官级，依八级体系及无玫瑰结形制校正；官方政府图册实物图·低清参考", [("page-08-image-07.jpg", "佩章完整正面")], 8),
    ("016", "LU-ADOLPH-NASSAU", "附属金十字章；官方政府图册实物图·低清参考", [("page-08-image-01.jpg", "十字章完整正面")], 8),
    ("017", "LU-ADOLPH-NASSAU", "附属银十字章；官方政府图册实物图·低清参考", [("page-08-image-02.jpg", "十字章完整正面")], 8),
    ("018", "LU-ADOLPH-NASSAU", "附属金奖章；官方政府图册实物图·低清参考", [("page-08-image-03.jpg", "奖章完整正面")], 8),
    ("019", "LU-ADOLPH-NASSAU", "附属银奖章；官方政府图册实物图·低清参考", [("page-08-image-04.jpg", "奖章完整正面")], 8),
    ("020", "LU-ADOLPH-NASSAU", "附属铜奖章；官方政府图册实物图·低清参考", [("page-08-image-05.jpg", "奖章完整正面")], 8),
    ("021", "LU-OAK-CROWN", "大十字级佩章；官方政府图册实物图·低清参考", [("page-09-image-01.jpg", "佩章完整正面")], 9),
    ("022", "LU-OAK-CROWN", "大十字级星章；官方政府图册实物图·低清参考", [("page-09-image-02.jpg", "星章完整正面")], 9),
    ("023", "LU-OAK-CROWN", "大军官级佩章；官方政府图册实物图·低清参考", [("page-10-image-02.jpg", "佩章完整正面")], 10),
    ("024", "LU-OAK-CROWN", "大军官级星章；官方政府图册实物图·低清参考", [("page-10-image-03.jpg", "星章完整正面")], 10),
    ("025", "LU-OAK-CROWN", "司令级佩章；官方政府图册实物图·低清参考", [("page-10-image-01.jpg", "佩章完整正面")], 10),
    ("026", "LU-OAK-CROWN", "军官级佩章；结上玫瑰花结；官方政府图册实物图·低清参考", [("page-11-image-03.jpg", "佩章完整正面")], 11),
    ("027", "LU-OAK-CROWN", "骑士级佩章；官方政府图册实物图·低清参考", [("page-11-image-01.jpg", "佩章完整正面")], 11),
    ("028", "LU-OAK-CROWN", "附属镀金银质功绩奖章；官方政府图册实物图·低清参考", [("page-11-image-04.jpg", "奖章完整正面")], 11),
    ("029", "LU-OAK-CROWN", "附属银质功绩奖章；官方政府图册实物图·低清参考", [("page-11-image-02.jpg", "奖章完整正面")], 11),
    ("030", "LU-OAK-CROWN", "附属铜质功绩奖章；官方政府图册实物图·低清参考", [("page-11-image-05.jpg", "奖章完整正面")], 11),
    ("031", "LU-ORDER-MERIT", "大十字级佩章；正背面；官方政府图册实物图·低清参考", [("page-12-image-01.jpg", "佩章完整正面"), ("page-12-image-03.jpg", "同式佩章完整背面")], 12),
    ("032", "LU-ORDER-MERIT", "大十字级星章；官方政府图册实物图·低清参考", [("page-12-image-02.jpg", "星章完整正面")], 12),
    ("033", "LU-ORDER-MERIT", "大军官级佩章；官方政府图册实物图·低清参考", [("page-13-image-02.jpg", "佩章完整正面")], 13),
    ("034", "LU-ORDER-MERIT", "大军官级星章；官方政府图册实物图·低清参考", [("page-13-image-01.jpg", "星章完整正面")], 13),
    ("035", "LU-ORDER-MERIT", "司令级佩章；官方政府图册实物图·低清参考", [("page-13-image-03.jpg", "佩章完整正面")], 13),
    ("036", "LU-ORDER-MERIT", "军官级佩章；结上玫瑰花结；官方政府图册实物图·低清参考", [("page-14-image-03.jpg", "佩章完整正面")], 14),
    ("037", "LU-ORDER-MERIT", "骑士级佩章；官方政府图册实物图·低清参考", [("page-14-image-01.jpg", "佩章完整正面")], 14),
    ("038", "LU-ORDER-MERIT", "附属镀金银质奖章；官方政府图册实物图·低清参考", [("page-14-image-02.jpg", "奖章完整正面")], 14),
]


UNPICTURED = [
    ("LU-RESISTANCE-ORDER", "抵抗勋章", "Ordre de la Résistance / Order of the Resistance"),
    ("LU-NATIONAL-RECOGNITION-MEDAL", "国家认同奖章", "Médaille de la Reconnaissance nationale / Medal of National Recognition"),
    ("LU-SPORT-MERIT-ORDER", "体育功绩奖章国家勋章", "Ordre national de la Médaille du Mérite sportif / National Order of the Medal of Merit for Sport"),
    ("LU-BLOOD-DONATION-MERIT", "献血功绩奖章", "Médaille du Mérite pour le don du sang / Medal of Merit for Blood Donation"),
    ("LU-EMERGENCY-SERVICES-MERIT", "应急服务功绩奖章", "Médaille du Mérite des services de secours / Medal of Merit of Emergency Services"),
    ("LU-ARMY-POLICE-SERVICE-CROSS", "陆军与警察服役十字章", "Croix de service pour l'armée et la police / Service Cross for the Army and Police"),
    ("LU-CUSTOMS-SERVICE-CROSS", "海关人员服役十字章", "Croix de service pour les agents des douanes / Service Cross for Customs Officials"),
    ("LU-PENAL-SERVICE-CROSS", "监狱与保安人员服役十字章", "Croix de service pour gardiens et agents des établissements pénitentiaires / Service Cross for Security Guards and Penal Officers"),
    ("LU-WATER-FOREST-SERVICE-CROSS", "水务与林业人员服役十字章", "Croix de service pour les agents des Eaux et Forêts / Service Cross for Water and Forest Service Officials"),
]


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


records = []
manifest_images = []
raw_lines = []
for suffix, family_id, variant, images, page in ROWS:
    rid = f"LU-OFF-{suffix}"
    fam = FAMILIES[family_id]
    views = []
    for index, (src_name, label) in enumerate(images, 1):
        src = RAW_DIR / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        out_name = f"{rid.lower()}-{index:02d}.jpg"
        dst = OUT_DIR / out_name
        shutil.copy2(src, dst)
        with Image.open(dst) as im:
            im.verify()
        with Image.open(dst) as im:
            width, height = im.size
        sha = hashlib.sha256(dst.read_bytes()).hexdigest()
        view_key = f"{rid}-V{index:02d}"
        views.append({"key": view_key, "label": label})
        manifest_images.append({
            "view_key": view_key,
            "local_path": dst.relative_to(ROOT).as_posix(),
            "source_page": f"{PDF_URL}#page={page}",
            "image_page": f"{PDF_URL}#page={page}",
            "original_url": PDF_URL,
            "source_object": f"official brochure page {page}; embedded image {src_name}",
            "width": width,
            "height": height,
            "bytes": dst.stat().st_size,
            "sha256": sha,
            "content_type": "image/jpeg",
            "image_kind": "卢森堡政府官方图册内嵌完整实物图；低清参考",
            "author_or_institution": "Information and Press Service of the Luxembourg Government / Ministry of State / Grand Ducal Palace; photographs: Christof Weber",
            "license": "未见逐图开放许可；本地研究使用",
            "pdf_page": page,
        })
    record = {
        "id": rid,
        "family": family_id,
        "name": fam["name"],
        "original": fam["original"],
        "date": fam["date"],
        "variant": variant,
        "views": views,
        "source_ids": ["LU-GOV-HONOURS-BOOK-2007", "LU-GRAND-DUCAL-COURT-ORDERS"],
    }
    records.append(record)
    raw_lines.append({
        "source_id": "LU-GOV-HONOURS-BOOK-2007",
        "page_title": fam["original"],
        "original_name": fam["original"],
        "name_zh": fam["name"],
        "date_candidate": fam["date"],
        "category": "formal_order_or_annexed_decoration",
        "grade_or_material_clue": variant,
        "object_page": f"{PDF_URL}#page={page}",
        "image_page": f"{PDF_URL}#page={page}",
        "original_image_urls": [PDF_URL for _ in images],
        "local_embedded_images": [f"assets/raw/luxembourg_official_book_2007/{name}" for name, _ in images],
        "notes": "官方图册页级映射；图版中章体完整，但原始内嵌图分辨率较低。",
        "status": "merged_pictured",
        "accessed": AS_OF,
    })

for family, name, original in UNPICTURED:
    raw_lines.append({
        "source_id": "LU-GOV-HONOURS-BOOK-2007",
        "page_title": "Other orders, medals, crosses and insignia",
        "original_name": original,
        "name_zh": name,
        "date_candidate": "待考",
        "category": "formal_award_unpictured",
        "grade_or_material_clue": "待考",
        "object_page": f"{PDF_URL}#page=15",
        "image_page": None,
        "original_image_urls": [],
        "notes": "卢森堡政府官方图册第15页列名但未提供章体图；登记至有记载未配图附录。",
        "status": "recorded_unpictured",
        "accessed": AS_OF,
    })

volume = {"as_of": AS_OF, "volume": "卢森堡大公国主要勋章体系", "records": records}
manifest = {
    "as_of": AS_OF,
    "volume": "卢森堡大公国主要勋章体系",
    "batch_id": BATCH,
    "sources": [
        {
            "source_id": "LU-GOV-HONOURS-BOOK-2007",
            "source_name": "Honorary distinctions of the Grand Duchy of Luxembourg",
            "base_url": PUBLICATION_URL,
            "download_url": PDF_URL,
            "local_copy": PDF_LOCAL,
            "source_type": "official_government_brochure",
            "languages": ["en"],
            "status": "completed_entire_20_page_book",
            "content_coverage": "四个主要勋章体系的历史、等级、佩章与星章图版，以及第15页所列其他正式勋章、奖章和服役十字章。",
        },
        {
            "source_id": "LU-GRAND-DUCAL-COURT-ORDERS",
            "source_name": "Luxembourg Monarchy — Orders",
            "base_url": COURT_URL,
            "source_type": "official_grand_ducal_court",
            "languages": ["en", "fr", "de", "lb"],
            "status": "completed_visible_orders_page",
            "content_coverage": "现行四个主要勋章的正式名称、设立日期、等级和制度复核。",
        },
    ],
    "images": manifest_images,
    "validation": {
        "record_count": len(records),
        "family_count": len({r["family"] for r in records}),
        "decoded_image_count": len(manifest_images),
        "all_images_exist": True,
        "all_decoded": True,
        "unpictured_candidate_count": len(UNPICTURED),
    },
}

dump(ROOT / f"data/volumes/{BATCH}.json", volume)
dump(ROOT / f"data/volumes/{BATCH}_manifest.json", manifest)

raw_path = ROOT / f"data/raw_candidates/{BATCH}.jsonl"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in raw_lines), encoding="utf-8")

# Append the exact official page-15 names to the shared unpictured appendix without altering unrelated records.
unpictured_path = ROOT / "data/unpictured.json"
unpictured = json.loads(unpictured_path.read_text(encoding="utf-8"))
known = {x.get("family") for x in unpictured}
for family, name, original in UNPICTURED:
    if family not in known:
        unpictured.append({
            "family": family,
            "name": name,
            "original": original,
            "date": "待考",
            "known_grade": "卢森堡政府官方图册第15页列名；具体等级待考",
            "category": "主编",
            "source_ids": ["LU-GOV-HONOURS-BOOK-2007"],
            "reason": "官方图册列入正式勋章、奖章或服役十字章体系，但该图册未提供章体图；待取得可追溯完整正面后进入正文。",
        })
dump(unpictured_path, unpictured)

matrix = {
    "source_atlas_id": "luxembourg_source_matrix",
    "as_of": AS_OF,
    "scope": "卢森堡大公国现行及历史正式勋赏体系",
    "sources": [
        {
            "id": "LU-GOV-HONOURS-BOOK-2007",
            "type": "official_government_brochure",
            "language": "en",
            "scope": "四个主要勋章全部等级与附属章；其他正式勋章、奖章和服役十字章名录",
            "date_coverage": "1841—2007",
            "image_capability": "42张完整低清官方图册实物图",
            "pagination": "20-page PDF",
            "download_method": "direct public PDF; embedded image extraction",
            "priority": 1,
            "status": "completed_entire_book",
            "last_checked": AS_OF,
            "coverage_boundary": "正文第4—14页四个主要勋章；第15页其他奖励仅列名无图；第16—20页为佩戴、归还、法源、书目与版权页。",
        },
        {
            "id": "LU-GRAND-DUCAL-COURT-ORDERS",
            "type": "official_grand_ducal_court",
            "language": "en/fr/de/lb",
            "scope": "四个主要勋章现行制度",
            "date_coverage": "1841—现行",
            "image_capability": "页面图未用于本批",
            "pagination": "none",
            "download_method": "web review",
            "priority": 1,
            "status": "completed_visible_page",
            "last_checked": AS_OF,
        },
        {
            "id": "LU-NATIONAL-MUSEUM-COLLECTIONS",
            "type": "national_museum_collection",
            "language": "fr/de/lb",
            "scope": "历史版型与第15页无图奖励",
            "date_coverage": "待扫",
            "image_capability": "可能",
            "pagination": "unknown",
            "download_method": "object search pending",
            "priority": 2,
            "status": "not_started",
            "last_checked": AS_OF,
        },
    ],
    "counts": {"planned": 3, "completed": 2, "partial": 0, "blocked": 0, "not_started": 1},
    "next_action": "为第15页列出的九个无图正式奖励补完整实物图，并扩展四个主要勋章的历史版型和军用加剑各级。",
}
dump(ROOT / "data/source_atlas/luxembourg_source_matrix.json", matrix)

checkpoint = {
    "checkpoint_id": BATCH,
    "as_of": AS_OF,
    "scope": "卢森堡政府官方勋赏图册整本扫描与四个主要勋章归并",
    "plan": ["穷尽20页政府官方图册", "映射第4—14页42张内嵌完整对象图", "归并为四个family和具体等级/部件行", "登记第15页有记载未配图奖励", "合并离线HTML"],
    "source_counts": matrix["counts"],
    "counts": {
        "raw_candidates": len(raw_lines),
        "merged_families": len(FAMILIES),
        "variants": len(records),
        "decoded_local_images": len(manifest_images),
        "unpictured_candidates": len(UNPICTURED),
        "unresolved_candidates": 0,
    },
    "files": [
        f"data/raw_candidates/{BATCH}.jsonl",
        f"data/volumes/{BATCH}.json",
        f"data/volumes/{BATCH}_manifest.json",
        "data/source_atlas/luxembourg_source_matrix.json",
        "data/unpictured.json",
        "assets/images/luxembourg_official_book_2007/",
        PDF_LOCAL,
    ],
    "status": "official_book_normalized_pending_html_merge",
    "next_action": "主任务视觉复核38行，并合并离线HTML；随后补第15页九个无图奖励与历史版型。",
}
dump(ROOT / f"data/checkpoints/{BATCH}.json", checkpoint)

print(json.dumps({
    "records": len(records),
    "families": len(FAMILIES),
    "images": len(manifest_images),
    "raw_candidates": len(raw_lines),
    "unpictured": len(UNPICTURED),
}, ensure_ascii=False))
