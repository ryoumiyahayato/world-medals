"""Generate the reviewed MENA round-7 volume from cached Commons review images."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT_IMAGES = ROOT / "assets/images/mena_round7"
OUT_IMAGES.mkdir(parents=True, exist_ok=True)

SOURCES = [
    (ROOT / "data/normalized_drafts/mena_bulk_round7_candidates.json", ROOT / "assets/raw/mena_round7_review"),
    (ROOT / "data/normalized_drafts/mena_core_deep_round7_candidates.json", ROOT / "assets/raw/mena_core_deep_round7_review"),
]
SUDAN_MEDALBOOK = ROOT / "data/raw_candidates/medalbook_sudan.jsonl"
ISABELLA_REFERENCE = ROOT / "assets/raw/user_provided_round7/isabella_republic_user_reference.png"
ANNUNCIATION_REFERENCE = ROOT / "assets/raw/user_provided_round7/annunciation_star_user_reference.png"

REJECT = re.compile(
    r"(ribbon|ruban|bar\.png|bar\.svg|portrait|ceremony|wearing|awarded by|museum.+awards|assortment|"
    r"NARA|Iranian orders|Frederick Hammersley|Şefik Aker|DSC00051|CairoRodaKalthumMedals|"
    r"Abde.?l-Nasser|Conseiller|litho|miniatures of orders|Döyüş medalları|Order1993|"
    r"1941-1945-yillardagi|Bahrain|Ultra Mirage|Air Force Hawk|JSOC|Mekteb|"
    r"medal, decoration \(AM|The Abyssinian \(Ethiopian\)|Twee Turkse|Rib\. Bar|"
    r"document|certificate|passport|awards of|front and rear photo|"
    r"Ibrahim.+Akk|إبراهيم باشا|presidents of Azerbaijan and Turkey|Mekteb-i Muelkiye|"
    r"Green Scarab|FC College|V.t.n .vlad.|\\u0417\\u0432\\u0435\\u0437\\u0434\\u0430\. \\u041f\\u0430\\u043a\\u0438\\u0441\\u0442\\u0430\\u043d|"
    r"\\u041d\\u0430\\u0434\\u043f\\u0438\\u0441\\u044c \\u043d\\u0430 \\u043f\\u043b\\u0430\\u043d\\u043a\\u0435)", re.I
)
BACK = re.compile(r"(back|reverse|rev\.|orqa|keerzijde|rückseite|реверс|other side)", re.I)
GENERIC = re.compile(r"^(Orders|Medals|Military decorations|Orders, decorations)", re.I)
BROAD_FAMILIES = {
    "Medal of Honors of Iran - Imperial Era", "Medal of Honors of Iran - Islamic Republic Era",
    "1933 Defence Force awards", "1956 Sudan independence related awards", "1969 cop d’état related awards",
    "SVG orders, decorations and medals of Azerbaijan", "Badges of honorary titles of Azerbaijan",
    "Badges of Kazakhstan", "Badges of honorary titles of Uzbekistan",
}

FAMILY_ZH = {
    "Order of the Medjidie": "麦吉迪勋章", "Order of Osmanieh": "奥斯曼勋章",
    "Gallipoli Star": "奥斯曼战争奖章（加里波利星）", "Turkish Crimea Medal": "克里米亚战争奖章",
    "Order of the Crescent": "新月勋章", "Order of Glory (Ottoman Empire)": "荣耀勋章",
    "Order of Honour (Ottoman Empire)": "荣誉勋章", "İftikhar Order": "慈善勋章",
    "Imtiyaz Medal": "伊姆蒂亚兹奖章", "Liyakat Medal": "利亚卡特奖章",
    "Order of the Lion and the Sun": "狮子与太阳勋章", "Order of the Nile": "尼罗河勋章",
    "Khedive's Star": "赫迪夫星章", "Order of Muhammad Ali": "穆罕默德·阿里勋章",
    "Order of Independence (Egypt)": "埃及独立勋章", "Order of the Republic (Egypt)": "埃及共和国勋章",
    "Order of Ismail": "伊斯梅尔勋章", "Order of Merit (Egypt)": "埃及功绩勋章",
    "Order of the Two Niles": "两尼罗河勋章", "Order of Merit of the Sudanese Republic": "苏丹共和国功绩勋章",
    "Order of Bravery (Sudan)": "苏丹英勇勋章", "Order of the Republic (Sudan)": "苏丹共和国勋章",
    "Order of Distinction (Sudan)": "苏丹卓越勋章", "Order of Military Accomplishment": "苏丹军事功绩勋章",
    "Order of Production (Sudan)": "苏丹生产功绩勋章", "Order of Science, Literature and Arts": "苏丹科学文学艺术勋章",
    "Medal of Honors of Iran - Imperial Era": "伊朗帝国荣誉奖章",
    "Medal of Honors of Iran - Islamic Republic Era": "伊朗伊斯兰共和国荣誉奖章",
}

def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", "-", value).strip("-")[:70] or hashlib.sha1(value.encode()).hexdigest()[:12].upper()

def display_name(row: dict) -> str:
    if row.get("_display_name"):
        return row["_display_name"]
    hint = row["family_hint"]
    if hint in FAMILY_ZH:
        return FAMILY_ZH[hint]
    title = re.sub(r"\.[^.]+$", "", row["file_title"][5:])
    title = re.sub(r"[-_+ ]*removebg[-_ ]preview", "", title, flags=re.I)
    title = re.sub(r"\s*\((?:obverse|front|cropped)\)", "", title, flags=re.I)
    translations = [
        (r"^Order of ", ""), (r"^Medal of ", ""), (r" Medal$", ""), (r" Order$", ""),
        (r"1st Class", "一等"), (r"2nd Class", "二等"), (r"3rd Class", "三等"),
        (r"4th class", "四等"), (r"5th class", "五等"),
    ]
    worked = title
    for pattern, replacement in translations:
        worked = re.sub(pattern, replacement, worked, flags=re.I)
    suffix = "勋章" if "order" in title.casefold() else "奖章"
    return f"{row['country_zh']}“{worked.strip()}”{suffix}"

def family_key(row: dict) -> str:
    if row.get("_family_key"):
        return row["_family_key"]
    hint = row["family_hint"]
    title = row.get("file_title", "")
    ottoman_existing = {
        "Gallipoli Star": "OTT-WAR", "Imtiyaz Medal": "OTT-IMTIYAZ-MEDAL",
        "Liyakat Medal": "OTT-LIYAKAT", "Order of Honour (Ottoman Empire)": "OTT-IFTIHAR-ORDER",
        "Order of Osmanieh": "OTT-OSM", "Order of the Medjidie": "OTT-MEDJ",
        "Turkish Crimea Medal": "OTT-CRIMEA", "Şefkat Order": "OTT-SEFKAT",
    }
    if hint in ottoman_existing:
        return ottoman_existing[hint]
    folded = (hint + " " + title).casefold()
    if "bosna madaly" in folded:
        return "OTT-BOSNIA-1850"
    if "yemen" in folded and ("1892" in folded or "1310" in folded):
        return "OTT-YEMEN-1892"
    if "kanûn-u esâsî" in folded:
        return "OTT-CONSTITUTION"
    if "jiladat" in folded:
        return "MENA7-IRAN-JILADAT"
    if "medal of pleiad" in folded:
        return "MENA7-IRAN-MEDAL-OF-PLEIADES"
    if "order of pleiad" in folded:
        return "MENA7-IRAN-ORDER-OF-PLEIADES"
    if "imom buxoriy ordeni" in folded:
        return "MENA7-UZBEKISTAN-IMOM-BUKHARI-ORDER"
    if row.get("country_zh") == "苏丹":
        if "army distinguished service medal" in folded:
            return "MENA7-ARMY-DISTINGUISHED-SERVICE-MEDAL"
        if "civil accomplishment" in folded:
            return "MENA7-ORDER-OF-CIVIL-ACCOMPLISHMENT"
        if "order of the republic" in folded or "order of the republic sudan" in folded:
            return "MENA7-SUDAN-ORDER-OF-THE-REPUBLIC"
        if "order of the two niles" in folded or "el-nilen" in folded:
            return "MENA7-ORDER-OF-THE-TWO-NILES"
        if "khedives sudan medal" in folded:
            return "MENA7-KHEDIVES-SUDAN-MEDAL"
    if row.get("country_zh") == "埃及":
        if "وسام الجمهورية" in folded:
            return "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT"
        if "وسام الاستحقاق" in folded:
            return "MENA7-ORDER-OF-MERIT-EGYPT"
    if "sitra-e-jurat" in folded:
        return "MENA7-SITARA-E-JURAT"
    if hint not in BROAD_FAMILIES and (hint in FAMILY_ZH or not GENERIC.search(hint)):
        base = hint
    else:
        base = re.sub(r"\.[^.]+$", "", row["file_title"][5:])
        base = re.sub(r"\b(?:1st|2nd|3rd|4th|5th|first|second|third|fourth|fifth)\s+(?:class|grade)\b", "", base, flags=re.I)
        base = re.sub(r"\b(?:gold|silver|bronze)\b", "", base, flags=re.I)
        base = re.sub(r"[-_+ ]*removebg[-_ ]preview", "", base, flags=re.I)
    return "MENA7-" + slug(row["country_zh"] + "-" + base)

def variant_text(row: dict) -> tuple[str, str]:
    if row.get("_variant"):
        return row["_variant"], row.get("_kind", "完整实物图")
    title = re.sub(r"\.[^.]+$", "", row["file_title"][5:])
    kind = "历史图录插图" if re.search(r"Gritzner|Perrot|1820|Meyers", title, re.I) else ("公开图式" if row.get("mime") == "image/svg+xml" else "完整实物图")
    details = []
    for pattern, label in [(r"1st Class|I(?:st)? class|Eerste Klasse", "一等"), (r"2nd Class|II(?:e)? Klasse|Tweede Klasse", "二等"),
                           (r"3rd Class|III(?:e)? Klasse", "三等"), (r"4th Class|IV|Vierde Klasse", "四等"),
                           (r"5th Class|Vijfde Klasse", "五等"), (r"Grand Cross", "大十字级"),
                           (r"Officer", "军官级"), (r"Commander", "指挥官级"), (r"milit", "军功组"),
                           (r"civil", "文官组"), (r"gold", "金质／金色版"), (r"silver", "银质／银色版"), (r"bronze", "铜质／铜色版")]:
        if re.search(pattern, title, re.I): details.append(label)
    if re.search(r"replica|copy|reproduction", title, re.I):
        details.append("复制品／Copy")
    if not details: details.append("文件页所示版型；具体等级待考")
    return "；".join(dict.fromkeys(details)) + f"；{kind}；低清完整参考图（原图地址已存档）", kind

all_rows = []
for data_path, image_dir in SOURCES:
    for row in json.loads(data_path.read_text(encoding="utf-8"))["records"]:
        local = image_dir / f"{row['candidate_id']}.png"
        if not local.is_file(): continue
        title = row["file_title"] + " " + row["family_hint"]
        if REJECT.search(title) or BACK.search(row["file_title"]): continue
        with Image.open(local) as im:
            width, height = im.size
            im.verify()
        # Horizontal ribbon bars and isolated ribbon devices are reference
        # material, not complete award objects for the third column.
        if width / max(height, 1) > 3.2:
            continue
        all_rows.append((row, local))

# MedalBook Sudan was harvested before this Commons batch.  It is deliberately
# folded in here because leaving its 77 locally cached object photographs out of
# the formaliser hid eleven otherwise missing Sudanese award families.
sudan_name_zh = {
    "Army Distinguished Service Medal": "苏丹陆军杰出服务奖章",
    "Khedives Sudan Medal, 1897": "赫迪夫苏丹奖章（1897年型）",
    "Khedives Sudan Medal, 1908": "赫迪夫苏丹奖章（1908年型）",
    "Long Service and Good Conduct Medal, for Police": "苏丹警察长期服务与良好品行奖章",
    "Medal for Gallantry": "苏丹英勇奖章",
    "Medal for Merit, I Class": "苏丹功绩奖章",
    "Medal for Merit, III Class": "苏丹功绩奖章",
    "Prison Long and Distinguished Service Medal": "苏丹监狱长期杰出服务奖章",
    "Order of Civil Accomplishment": "苏丹民事成就勋章",
    "Order of Long and Distinguished Service": "苏丹长期杰出服务勋章",
    "Order of Loyal Son of Sudan": "苏丹忠诚之子勋章",
    "Order of Regional Government": "苏丹地方政府勋章",
    "Order of Sport, in Silver": "苏丹体育勋章",
    "Order of the Republic, II Class": "苏丹共和国勋章",
    "Order of the Republic, II Class Breast Star": "苏丹共和国勋章",
    "Order of the Two Niles, Commander": "两尼罗河勋章",
    "Order of the Two Niles, Grand Cross": "两尼罗河勋章",
    "Order of the Two Niles, Grand Cross Breast Star": "两尼罗河勋章",
    "Order of the Two Niles, Knight": "两尼罗河勋章",
}
sudan_best_view = {
    "Army Distinguished Service Medal": 1,
    "Medal for Merit, III Class": 1,
    "Order of Loyal Son of Sudan": 2,
    "Order of Sport, in Silver": 1,
    "Order of the Two Niles, Commander": 1,
    "Order of the Two Niles, Knight": 1,
}
if SUDAN_MEDALBOOK.is_file():
    for raw in SUDAN_MEDALBOOK.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        item = json.loads(raw)
        pictures = item.get("local_raw_images", [])
        if not pictures:
            continue
        index = min(sudan_best_view.get(item["page_title"], 0), len(pictures) - 1)
        local = ROOT / pictures[index]
        if not local.is_file():
            continue
        title = item["page_title"]
        family_title = re.sub(r",?\s+(?:I|II|III|IV|V) Class(?: Breast Star)?$", "", title)
        family_title = re.sub(r",?\s+(?:Commander|Grand Cross(?: Breast Star)?|Knight)$", "", family_title)
        details = []
        for token, label in [("I Class", "一等"), ("II Class", "二等"), ("III Class", "三等"),
                             ("Commander", "指挥官级"), ("Grand Cross", "大十字级"),
                             ("Breast Star", "星章"), ("Knight", "骑士级"), ("in Silver", "银质版")]:
            if token in title:
                details.append(label)
        row = {
            "candidate_id": item["source_id"], "country_zh": "苏丹", "family_hint": family_title,
            "file_title": "File:" + title + ".jpg", "sha1": hashlib.sha1(local.read_bytes()).hexdigest(),
            "file_page_url": item["page_url"], "original_url": item.get("original_image_urls", [None])[index],
            "license_short_name": "来源页未声明开放许可", "artist": "MedalBook / listed dealer image",
            "object_name": title, "image_description": item.get("notes"), "_display_name": sudan_name_zh[title],
            "_family_key": "MENA7-" + slug("苏丹-" + family_title),
            "_variant": "；".join(details or ["来源页所示版型；具体等级待考"]) + "；完整实物图",
            "_kind": "完整实物图", "_date": (str(item["date_candidates"][0]) + "年型") if item.get("date_candidates") else "制度日期待考",
            "_source_type": "MedalBook Sudan catalogue",
        }
        all_rows.append((row, local))

# The user supplied this restored reference.  The identity is supported by the
# Spanish official regulation/history and the Republican-era MedalBook entry,
# but the pixels remain labelled as a user-provided restoration rather than an
# original auction or museum photograph.
if ISABELLA_REFERENCE.is_file():
    all_rows.append(({
        "candidate_id": "user-isabella-republic-20260926", "country_zh": "西班牙第二共和国",
        "family_hint": "Order of Isabella the Catholic", "file_title": "File:Order of Isabella the Catholic Republican star.png",
        "sha1": hashlib.sha1(ISABELLA_REFERENCE.read_bytes()).hexdigest(),
        "file_page_url": "https://www.exteriores.gob.es/es/ServiciosAlCiudadano/PublicacionesOficiales/Orden%20de%20Isabel%20la%20Cat%C3%B3lica.%20Reglamento.%20Resumen%20hist%C3%B3rico.pdf",
        "original_url": None, "license_short_name": "用户提供；原始影像权利待核", "artist": "用户提供",
        "object_name": "Order of Isabella the Catholic, Republican-era insignia",
        "image_description": "Motto and Republican-era identity cross-checked; exact maker remains unresolved.",
        "_display_name": "天主教伊莎贝拉勋章（西班牙第二共和国型）",
        "_family_key": "MENA7-SPAIN-ORDER-OF-ISABELLA-THE-CATHOLIC",
        "_variant": "共和国时期星章版型；制造商待考；用户提供高清修复参考图",
        "_kind": "用户提供修复参考图", "_date": "1931–1938年型", "_source_type": "user_reference_with_official_identity_check",
    }, ISABELLA_REFERENCE))

if ANNUNCIATION_REFERENCE.is_file():
    all_rows.append(({
        "candidate_id": "user-annunciation-star-20260926", "country_zh": "意大利／萨佛依王朝",
        "family_hint": "Supreme Order of the Most Holy Annunciation", "file_title": "File:Supreme Order of the Most Holy Annunciation breast star.png",
        "sha1": hashlib.sha1(ANNUNCIATION_REFERENCE.read_bytes()).hexdigest(),
        "file_page_url": "https://americanhistory.si.edu/collections/object/nmah_962684",
        "original_url": None, "license_short_name": "用户提供；原始影像权利待核", "artist": "用户提供",
        "object_name": "Supreme Order of the Most Holy Annunciation breast star",
        "image_description": "Annunciation scene and FERT letters cross-checked against museum and specialist catalogue descriptions; exact maker and object date unresolved.",
        "_display_name": "至圣报喜最高勋章",
        "_family_key": "MENA7-ITALY-SUPREME-ORDER-MOST-HOLY-ANNUNCIATION",
        "_variant": "骑士星章；F·E·R·T字样；制造商与本件年代待考；用户提供高清修复参考图",
        "_kind": "用户提供修复参考图", "_date": "1362年设立；星章制式1680年起；本件年代待考",
        "_source_type": "user_reference_with_museum_identity_check",
    }, ANNUNCIATION_REFERENCE))

# Correct source-tree leakage before any country filtering or rendering.  A
# Commons category path is discovery evidence, not proof of the issuing state.
for row, _local in all_rows:
    title = (row.get("file_title", "") + " " + row.get("family_hint", "")).casefold()
    if "siege of khartum" in title:
        row["country_zh"] = "苏丹"
    elif "khedive the order of justice" in title:
        row["country_zh"] = "埃及"
    elif "distinctive medal of ottoman army" in title:
        row["country_zh"] = "奥斯曼帝国"

priority = {"奥斯曼帝国": 0, "埃及": 1, "苏丹": 2, "伊朗／波斯": 3, "土耳其共和国": 4,
            "伊拉克": 5, "叙利亚": 6, "阿曼": 7, "沙特阿拉伯": 8, "阿富汗": 9,
            "巴基斯坦": 10, "摩洛哥": 11, "阿尔及利亚": 12, "阿塞拜疆": 13,
            "哈萨克斯坦": 14, "乌兹别克斯坦": 15, "西班牙第二共和国": 16,
            "意大利／萨佛依王朝": 17}
all_rows.sort(key=lambda pair: (priority.get(pair[0]["country_zh"], 99), family_key(pair[0]),
                                0 if pair[0].get("_source_type") == "MedalBook Sudan catalogue" else 1,
                                pair[0]["file_title"]))

country_caps = {"奥斯曼帝国": 35, "埃及": 30, "苏丹": 30, "伊朗／波斯": 38, "土耳其共和国": 12,
                "伊拉克": 4, "叙利亚": 7, "也门": 1, "科威特": 3, "阿曼": 3, "沙特阿拉伯": 3,
                "阿富汗": 5, "巴基斯坦": 7, "摩洛哥": 7, "阿尔及利亚": 4, "突尼斯": 2,
                "阿塞拜疆": 18, "哈萨克斯坦": 10, "乌兹别克斯坦": 10}
seen = set(); accepted = []; country_counts = Counter(); family_counts = Counter()

def accept(row: dict, local: Path) -> None:
    duplicate = (row.get("sha1"), row["file_title"].casefold())
    seen.add(duplicate)
    country_counts[row["country_zh"]] += 1
    family_counts[family_key(row)] += 1
    accepted.append((row, local))

# Pass 1: one complete image for every distinct family.  This prevents a famous
# order with many maker/grade photographs from crowding out smaller systems.
for row, local in all_rows:
    duplicate = (row.get("sha1"), row["file_title"].casefold())
    fam = family_key(row)
    if duplicate in seen or family_counts[fam]:
        continue
    accept(row, local)

# Pass 2: add meaningful grade/maker/design variants without exceeding a modest
# per-family cap.  The first pass is never subject to country caps.
for row, local in all_rows:
    if len(accepted) >= 230:
        break
    duplicate = (row.get("sha1"), row["file_title"].casefold())
    fam = family_key(row)
    cap = 18 if row["family_hint"] == "Order of the Lion and the Sun" else 5
    if duplicate in seen or family_counts[fam] >= cap:
        continue
    accept(row, local)

records, images, sources = [], [], {}
for index, (row, local) in enumerate(accepted, 1):
    view_key = f"MENA7-{index:03d}-FRONT"
    dest = OUT_IMAGES / f"{row['candidate_id']}.png"
    if not dest.is_file():
        with Image.open(local) as src:
            src.convert("RGBA" if src.mode in ("RGBA", "LA") else "RGB").save(dest, "PNG")
    name = display_name(row); variant, kind = variant_text(row)
    title = re.sub(r"\.[^.]+$", "", row["file_title"][5:])
    years = re.findall(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)", title)
    date = row.get("_date") or ((years[0] + "年图示／纪年；制度日期待考") if years else "制度日期待考")
    family = family_key(row)
    record_id = family + "-" + row["candidate_id"].split("-")[-1].upper()
    records.append({"id": record_id, "family": family, "country_zh": row["country_zh"], "name": name, "original": title, "date": date,
                    "variant": variant, "views": [{"key": view_key, "label": kind}],
                    "source_ids": [row["candidate_id"]], "image_kind": "historical_illustration" if kind == "历史图录插图" else ("design" if kind == "公开图式" else ("restored_reference" if "修复参考" in kind else "object_photo")),
                    "html_eligible": True})
    with Image.open(dest) as rendered:
        actual_width, actual_height = rendered.size
    images.append({"view_key": view_key, "local_path": str(dest.relative_to(ROOT)).replace("\\", "/"),
                   "source_id": row["candidate_id"], "download_status": "cached_complete_local_image",
                   "source_original_url": row.get("original_url"), "license": row.get("license_short_name"),
                   "width": actual_width, "height": actual_height})
    sources[row["candidate_id"]] = {"page": row["file_page_url"], "image_url": row.get("original_url"),
                                    "file_title": row["file_title"], "object_name": row.get("object_name"),
                                    "image_description": row.get("image_description"), "license": row.get("license_short_name"),
                                    "artist": row.get("artist"), "source_type": row.get("_source_type", "Wikimedia Commons"),
                                    "accessed": "2026-09-26", "local_review_file": str(dest.relative_to(ROOT)).replace("\\", "/")}

volume = ROOT / "data/volumes/mena_round7_2026-09-26.json"
manifest = ROOT / "data/volumes/mena_round7_manifest_2026-09-26.json"
source_file = ROOT / "data/volumes/mena_round7_sources_2026-09-26.json"
volume.write_text(json.dumps({"as_of": "2026-09-26", "volume": "中东与穆斯林国家批量扩充第7轮", "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
manifest.write_text(json.dumps({"as_of": "2026-09-26", "images": images, "unpictured_candidates": []}, ensure_ascii=False, indent=2), encoding="utf-8")
source_file.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
checkpoint = {"as_of": "2026-09-26", "accepted_rows": len(records), "independent_families": len({r['family'] for r in records}),
              "by_country": dict(Counter(row["country_zh"] for row, _ in accepted)), "pictures": len(images),
              "available_reviewed_by_country": dict(Counter(row["country_zh"] for row, _ in all_rows)),
              "available_reviewed_families": len({family_key(row) for row, _ in all_rows}),
              "reviewed_cached_candidates": len(all_rows), "note": "Each family first receives one visually reviewed complete local image; further rows are meaningful variants. Commons rows retain original URLs/licences; MedalBook Sudan rows use its locally cached object photographs. The Isabella row is explicitly labelled as a user-provided restored reference."}
(ROOT / "data/checkpoints/mena_round7_formalization_2026-09-26.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(checkpoint, ensure_ascii=False, indent=2))
