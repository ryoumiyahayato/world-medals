import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-09-29"
SOURCE_ID = "mondvor_ussr_order_index"
BOOK_ID = "putnikov_orders_medals_ussr_1990"
BOOK_PAGES = {
    "USSR-ORD-01": [7],
    "USSR-ORD-02": [7],
    "USSR-ORD-03": [12],
    "USSR-ORD-04": [13],
    "USSR-ORD-05": [15],
    "USSR-ORD-06": [16],
    "USSR-ORD-07": [17],
    "USSR-ORD-08": [18],
    "USSR-ORD-09": [14],
    "USSR-ORD-10": [14],
    "USSR-ORD-11": [20],
    "USSR-ORD-12": [19],
    "USSR-ORD-13": [8],
    "USSR-ORD-14": [9],
    "USSR-ORD-15": [10],
    "USSR-ORD-16": [21, 22],
    "USSR-ORD-17": [23],
    "USSR-ORD-19": [11, 21, 22],
    "USSR-ORD-20": [21],
    "USSR-ORD-21": [11],
    "RSFSR-ORD-01": [5],
}
RAW_PATH = ROOT / "data/raw_candidates/mondvor_soviet_orders_2026-09-29.jsonl"
CRAWL_PATH = ROOT / "sources/cache/mondvor_soviet_orders/crawl_inventory_2026-09-29.json"
VOLUME_PATH = ROOT / "data/volumes/mondvor_soviet_orders_2026-09-29.json"
MANIFEST_PATH = ROOT / "data/volumes/mondvor_soviet_orders_2026-09-29_manifest.json"
MATRIX_PATH = ROOT / "data/source_atlas/soviet_orders_source_matrix.json"
CHECKPOINT_PATH = ROOT / "data/checkpoints/mondvor_soviet_orders_2026-09-29.json"
IMAGE_QUEUE_PATH = ROOT / "data/queues/mondvor_soviet_orders_image_permission_queue_2026-09-29.json"
MERGE_QUEUE_PATH = ROOT / "data/queues/mondvor_soviet_orders_merge_queue_2026-09-29.json"

FAMILY_META = {
    "USSR-ORD-01": ("列宁勋章", "Орден Ленина", "Order of Lenin"),
    "USSR-ORD-02": ("十月革命勋章", "Орден Октябрьской Революции", "Order of the October Revolution"),
    "USSR-ORD-03": ("胜利勋章", "Орден «Победа»", "Order of Victory"),
    "USSR-ORD-04": ("红旗勋章", "Орден Красного Знамени", "Order of the Red Banner"),
    "USSR-ORD-05": ("苏沃洛夫勋章", "Орден Суворова", "Order of Suvorov"),
    "USSR-ORD-06": ("库图佐夫勋章", "Орден Кутузова", "Order of Kutuzov"),
    "USSR-ORD-07": ("波格丹·赫梅利尼茨基勋章", "Орден Богдана Хмельницкого", "Order of Bohdan Khmelnytsky"),
    "USSR-ORD-08": ("亚历山大·涅夫斯基勋章", "Орден Александра Невского", "Order of Alexander Nevsky"),
    "USSR-ORD-09": ("乌沙科夫勋章", "Орден Ушакова", "Order of Ushakov"),
    "USSR-ORD-10": ("纳希莫夫勋章", "Орден Нахимова", "Order of Nakhimov"),
    "USSR-ORD-11": ("红星勋章", "Орден Красной Звезды", "Order of the Red Star"),
    "USSR-ORD-12": ("卫国战争勋章", "Орден Отечественной войны", "Order of the Patriotic War"),
    "USSR-ORD-13": ("劳动红旗勋章", "Орден Трудового Красного Знамени", "Order of the Red Banner of Labour"),
    "USSR-ORD-14": ("各族人民友谊勋章", "Орден Дружбы народов", "Order of Friendship of Peoples"),
    "USSR-ORD-15": ("荣誉勋章", "Орден «Знак Почёта»", "Order of the Badge of Honour"),
    "USSR-ORD-16": ("光荣勋章", "Орден Славы", "Order of Glory"),
    "USSR-ORD-17": ("母亲光荣勋章", "Орден «Материнская слава»", "Order of Maternal Glory"),
    "USSR-ORD-19": ("劳动光荣勋章", "Орден Трудовой Славы", "Order of Labour Glory"),
    "USSR-ORD-20": ("在苏联武装力量中为祖国服务勋章", "Орден «За службу Родине в Вооружённых Силах СССР»", "Order for Service to the Homeland in the Armed Forces of the USSR"),
    "USSR-ORD-21": ("个人英勇勋章", "Орден «За личное мужество»", "Order for Personal Courage"),
    "RSFSR-ORD-01": ("红旗勋章（俄罗斯苏维埃联邦社会主义共和国）", "Орден Красного Знамени РСФСР", "Order of the Red Banner of the RSFSR"),
}

ROMANS = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
AUX_NAME = re.compile(r"(?:Kav|Gaz|Frag|Vint|Number|Prob|Resp|T\d+|Z\d+)", re.I)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def roman_or_digit(raw):
    raw = raw.upper().strip().rstrip(".,;:)")
    return ROMANS.get(raw, int(raw) if raw.isdigit() else raw)


def extract_labels(context):
    text = re.sub(r"\s+", " ", context or "")
    caption = re.search(r"(?i)(?:фотографии|фотография|фото)\s+(?:ордена|медали|знака)\s*(?:№|N|No\.?|)", text)
    if caption:
        text = text[max(0, caption.start() - 210) : caption.start() + 20]
    else:
        text = text[-210:]
    labels = {}
    for key, pattern in (
        ("type", r"(?i)\bТип\s*([IVX]{1,5}|\d{1,2})\b"),
        ("variant", r"(?i)\bВариант\s*([IVX]{1,5}|\d{1,2})\b"),
        ("variety", r"(?i)\bРазновидность\s*([\d]{1,2}[а-яa-z]?)\b"),
        ("degree", r"(?i)\b(I{1,3}|IV|V|[1-3])\s*(?:степени|степень|класс(?:а)?)\b"),
    ):
        matches = list(re.finditer(pattern, text))
        if matches:
            raw = matches[-1].group(1)
            value = roman_or_digit(raw)
            if key == "variety":
                value = raw.lower()
            labels[key] = value
    return labels, text


def normalize_existing_variant(value):
    text = value or ""
    labels = {}
    patterns = (
        ("type", r"(?i)\b(?:type|тип)\s*(I{1,3}|IV|V|[1-5])\b"),
        ("variant", r"(?i)\b(?:variant|вариант)\s*(I{1,3}|IV|V|[1-5])\b"),
        ("variety", r"(?i)\b(?:variety|разновидность)\s*([\d]{1,2}[a-zа-я]?)\b"),
        ("degree", r"(?i)\b(I{1,3}|IV|V|[1-3])\s*(?:class|degree|степени|степень|класс)\b"),
    )
    for key, pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw = match.group(1)
            labels[key] = raw.lower() if key == "variety" else roman_or_digit(raw)
    return labels


def variant_key(labels):
    return tuple((key, labels[key]) for key in ("type", "variant", "variety", "degree") if key in labels)


def display_label(labels):
    result = []
    if "type" in labels:
        result.append(f"第{labels['type']}型")
    if "variant" in labels:
        result.append(f"版本{labels['variant']}")
    if "variety" in labels:
        result.append(f"细分型{labels['variety']}")
    if "degree" in labels:
        result.append(f"{labels['degree']}级")
    return "；".join(result)


def candidate_id(family, labels):
    parts = [family, "V-MV"]
    for key, prefix in (("type", "T"), ("variant", "V"), ("variety", "R"), ("degree", "G")):
        if key in labels:
            value = str(labels[key]).upper().replace(" ", "")
            parts.append(prefix + value)
    return "-".join(parts)


def image_base(name):
    stem = Path(name).stem
    if re.search(r"R$", stem, re.I):
        return stem[:-1], True
    return stem, False


def is_non_object_image(name, context):
    if AUX_NAME.search(name or ""):
        return True
    if re.search(r"(?i)(?:дубликат|копия|копия ордена)", context or ""):
        return True
    return False


def object_number(context, name):
    match = re.search(r"(?i)(?:ордена|медали|знака)\s*(?:№|N|No\.?)\s*([\d]+)", context or "")
    if match:
        return match.group(1)
    match = re.search(r"(\d{2,})", Path(name).stem)
    return match.group(1) if match else None


def polities(family, filename, context):
    if family == "USSR-ORD-04" and (filename.upper().startswith("ORBANRS") or "РСФСР" in (context or "")):
        return "RSFSR-ORD-01", "俄罗斯苏维埃联邦社会主义共和国"
    return family, "苏联"


def short_id(family, labels):
    return candidate_id(family, labels)


def select_round_robin(candidates, max_per_family=6):
    grouped = defaultdict(list)
    for item in candidates:
        grouped[item["family"]].append(item)
    for family_items in grouped.values():
        family_items.sort(
            key=lambda x: (
                0 if "type" in x["labels"] else 1,
                0 if "degree" in x["labels"] else 1,
                len(x["labels"]),
                x["photo_number"] or "",
                x["front"]["source_file_name"],
            )
        )
    selected = []
    round_no = 0
    families = sorted(grouped)
    while any(round_no < len(grouped[f]) for f in families) and round_no < max_per_family:
        for family in families:
            if round_no < len(grouped[family]):
                selected.append(grouped[family][round_no])
        round_no += 1
    return selected


def main():
    crawl = read_json(CRAWL_PATH)
    pages = [json.loads(line) for line in RAW_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    images = defaultdict(dict)
    page_by_url = {}
    for page in pages:
        page_by_url[page["object_page_url"]] = page
        family = page["candidate_family_id"]
        for image in page.get("image_inventory", []):
            images[family].setdefault(image["source_file_name"], image)

    existing_records = defaultdict(list)
    for file in (ROOT / "data/volumes").glob("*.json"):
        try:
            volume = read_json(file)
        except Exception:
            continue
        if not isinstance(volume, dict):
            continue
        stored_records = volume.get("records", [])
        if not isinstance(stored_records, list):
            continue
        for row in stored_records:
            family = row.get("family", "")
            if family.startswith(("USSR-ORD-", "RSFSR-ORD-")):
                existing_records[family].append(row)
    existing_keys = defaultdict(set)
    existing_dates = {}
    for family, rows in existing_records.items():
        for row in rows:
            existing_keys[family].add(variant_key(normalize_existing_variant(row.get("variant"))))
            if row.get("date"):
                existing_dates.setdefault(family, row["date"])

    all_groups = {}
    excluded_auxiliary = 0
    for source_family, family_images in images.items():
        for filename, reverse in family_images.items():
            base, is_reverse = image_base(filename)
            if not is_reverse or base + Path(filename).suffix not in family_images:
                continue
            front = family_images[base + Path(filename).suffix]
            context = reverse.get("page_context", "")
            final_family, polity = polities(source_family, filename, context)
            if is_non_object_image(filename, context) or is_non_object_image(front["source_file_name"], front.get("page_context", "")):
                excluded_auxiliary += 1
                continue
            labels, label_context = extract_labels(context)
            if not labels:
                labels, label_context = extract_labels(front.get("page_context", ""))
            if not labels:
                continue
            key = (final_family, variant_key(labels))
            candidate = {
                "family": final_family,
                "source_family": source_family,
                "polity": polity,
                "labels": labels,
                "front": front,
                "reverse": reverse,
                "label_context": label_context,
                "page_url": reverse.get("source_page_url") or front.get("source_page_url"),
                "photo_number": object_number(context, filename),
            }
            score = min(
                int(re.search(r"\((\d+) bytes\)", (front.get("alt_and_byte_hint") or "")).group(1)) if re.search(r"\((\d+) bytes\)", (front.get("alt_and_byte_hint") or "")) else 0,
                int(re.search(r"\((\d+) bytes\)", (reverse.get("alt_and_byte_hint") or "")).group(1)) if re.search(r"\((\d+) bytes\)", (reverse.get("alt_and_byte_hint") or "")) else 0,
            )
            previous = all_groups.get(key)
            if previous is None or score > previous["byte_score"]:
                candidate["byte_score"] = score
                all_groups[key] = candidate

    # Rows already present at the same degree/type level are excluded only when
    # the site presents exactly the same specificity; more detailed issues stay.
    differential = []
    for (family, key), candidate in all_groups.items():
        if key and key in existing_keys[family]:
            continue
        name, original, english = FAMILY_META[family]
        candidate.update({"name": name, "original": original, "english": english})
        differential.append(candidate)
    selected = select_round_robin(differential, max_per_family=6)

    volume_records = []
    referenced_images = []
    for candidate in selected:
        family = candidate["family"]
        labels = candidate["labels"]
        name, original, english = FAMILY_META[family]
        info = display_label(labels)
        number = candidate["photo_number"]
        note = f"Mondvor 页面分类：{info}。"
        if number:
            note += f"页面图注对应编号 {number}。"
        note += "这是专题站使用的实物版型分类，是否与正式法令型式相同仍待核。"
        front = candidate["front"]
        reverse = candidate["reverse"]
        item_id = short_id(family, labels)
        date = "1918年设立（РСФСР）" if family == "RSFSR-ORD-01" else existing_dates.get(family, "设立日期待考")
        views = []
        for view_label, image in (("正面候选", front), ("背面候选（文件名后缀 R）", reverse)):
            ref = {
                "source_page_url": image.get("source_page_url") or candidate["page_url"],
                "original_image_url": image["source_image_url"],
                "source_file_name": image["source_file_name"],
                "view_label_candidate": view_label,
                "source_caption_context": image.get("page_context"),
                "rights_status": "许可未确认；不下载、不嵌入、不计入完整图片。",
                "local_path": None,
                "decoded": False,
            }
            views.append(ref)
            referenced_images.append(ref)
        excerpt = re.sub(r"\s+", " ", candidate["label_context"]).strip()[:360]
        book_pages = BOOK_PAGES.get(family, [])
        book_crosscheck = {
            "source_id": BOOK_ID,
            "pages": book_pages,
            "role": "printed English-language catalog/title cross-check only; does not validate Mondvor's specimen type labels or image identity",
        }
        if family == "USSR-ORD-15":
            book_crosscheck.update({
                "catalogue_heading_en": "Order of Honour",
                "name_difference_note": "Putnikov's p.10 English heading differs from Mondvor's Badge of Honour title; retain both source forms until the 1988 statutory rename/chronology is verified.",
            })
        if family == "RSFSR-ORD-01":
            book_crosscheck.update({
                "facts_supported": ["RSFSR predecessor attribution", "establishment date candidate"],
                "excerpt_en": "established the Order of the Red Banner of the RSFSR ... on September 16, 1918",
            })
        volume_records.append(
            {
                "id": item_id,
                "family": family,
                "name": name,
                "original": original,
                "english": english,
                "date": date,
                "variant": note,
                "views": [],
                "image_candidates": views,
                "source_ids": [SOURCE_ID],
                "related_source_refs": [book_crosscheck],
                "source_page_url": candidate["page_url"],
                "source_excerpt_ru": excerpt,
                "source_classification": labels,
                "awarding_polity_candidate": candidate["polity"],
                "status": "candidate_image_permission_pending",
                "merge_note": "版型候选由原页图注、编号与相邻正文生成；未下载/目检图片，禁止作为正文完整图。",
            }
        )

    volume = {
        "as_of": AS_OF,
        "volume": "苏联勋章：Mondvor 目录版型差集（图片权利待处理）",
        "scope": "苏联 ordpage.htm 的20个入口勋章页及其同名数字分页；俄罗斯苏维埃联邦社会主义共和国红旗勋章前身单独保留授予主体候选。",
        "source": SOURCE_ID,
        "records": volume_records,
        "notes": [
            "此文件是内部合并草稿，不是可浏览正文卷。",
            "源站页面说明的具体分类和实物图注均保留；类型是否属于法定版别需要继续核对。",
            "源站图片复用权限未确认，因此没有下载或嵌入任何照片；image_candidates 仅为来源页引用，不计完整图片。",
            "来源首页的 Hero/medal/badge 目录与本批 ordpage 分开；最高称号、母亲英雄等目录须由跨目录任务另作 family 差集。",
        ],
    }
    VOLUME_PATH.parent.mkdir(parents=True, exist_ok=True)
    VOLUME_PATH.write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts_by_family = defaultdict(int)
    for row in volume_records:
        counts_by_family[row["family"]] += 1
    unique_ref_urls = sorted({row["original_image_url"] for row in referenced_images})
    manifest = {
        "as_of": AS_OF,
        "volume": volume["volume"],
        "records_file": VOLUME_PATH.relative_to(ROOT).as_posix(),
        "image_directory": "sources/cache/mondvor_soviet_orders/images/ (empty; restricted source images not downloaded)",
        "source_scope": {
            "index_entries": len(crawl.get("index_entries", [])),
            "article_pages_swept": crawl.get("page_count", 0),
            "distinct_families_in_index": len({row["family"] for row in crawl.get("index_entries", [])}),
            "unique_image_references_in_article_pages": crawl.get("image_reference_count", 0),
        },
        "counts": {
            "distinct_family_candidates": len(counts_by_family),
            "variant_rows_after_exact_key_difference": len(volume_records),
            "variant_rows_by_family": dict(sorted(counts_by_family.items())),
            "complete_local_image_files": 0,
            "unique_image_urls_waiting_for_permission": len(unique_ref_urls),
            "decoded_local_images": 0,
            "unresolved_candidates": max(0, len(all_groups) - len(differential)),
        },
        "rights_review": {
            "status": "permission_pending",
            "note": "Mondvor 页尾/站点复用限制未取得许可，图像只记录URL、页面和图注上下文；未下载、解码或嵌入。",
        },
        "difference_method": "20篇对象页及所有同名数字分页；用 family + 页面显式 type/variant/variety/degree 标签做候选归并；排除与既有 volume 完全相同的标签键；同一标签组选优字节提示最高的一件作代表，不据不同照片重复建行。",
        "volume_status": "internal_review_draft_not_body_ready",
        "images": referenced_images,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    matrix = {
        "schema_version": "2.0",
        "as_of": AS_OF,
        "scope_id": "soviet_orders_mondvor",
        "scope_label": "USSR and linked RSFSR predecessor order articles on Mondvor",
        "sources": [
            {
                "source_id": SOURCE_ID,
                "source_name": "Mondvor — ОРДЕНА СССР",
                "base_url": "https://mondvor.narod.ru/ordpage.htm",
                "source_type": "specialist_site",
                "languages": ["ru"],
                "regions_or_polities": ["苏联", "俄罗斯苏维埃联邦社会主义共和国（红旗勋章前身页面线索）"],
                "date_coverage": "主目录苏联勋章1922–1991；红旗勋章文章含RSFSR前身线索（1918年起）",
                "content_coverage": "入口页20条；递归读取全部20个对象页及其同名前缀数字分页，共64篇正文页；提取页面题名、日期候选、类型/级别、厂标/序号/螺柱/螺母线索及图片图注。",
                "has_images": True,
                "image_quality_notes": "64篇正文页中发现1000个唯一原站图片引用；经文件名和图注识别到数百组可能的同编号正背对象照片。页面的图片许可/复用条件未确认，未下载、未解码、不得计为正文图。",
                "has_pagination": True,
                "pagination_notes": "同名数字后缀页面：OLenin 4页、ORBan 8页、OPatWar 7页、ORStar 7页、OSlava 5页、ORbnLab 4页、OZnPoch 5页及其他相应页；共64篇对象页。",
                "download_method": "原站公开HTML以有限顺序请求和本地页面缓存；照片仅留直接URL与图注引用，等待许可复核。",
                "priority": 1,
                "status": "partial",
                "last_checked": AS_OF,
                "coverage_result": f"20个目录入口均递归完成，64篇对象页完整缓存；形成{len(volume_records)}个去重版型候选，{len(unique_ref_urls)}个被选图像URL仍待权利处理；可入正文完整图片为0。",
                "local_cache": "sources/cache/mondvor_soviet_orders/pages/",
                "raw_candidates": RAW_PATH.relative_to(ROOT).as_posix(),
                "volume_draft": VOLUME_PATH.relative_to(ROOT).as_posix(),
                "manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
                "rights": "原站限制文字/图片的再用；尚未获得复制许可。不得将缓存引用视作已授权图片。",
                "coverage_boundary": "只覆盖ordpage勋章目录；heropage、medpage、badgepage由跨目录来源任务另扫。",
                "next_action": "继续和其余三目录及Putnikov 1990英文图录交叉核对；从授权来源补齐代表版型照片，或在取得权利后下载这批原图。",
            },
            {
                "source_id": BOOK_ID,
                "source_name": "Georgi A. Putnikov, Orders and Medals of the USSR",
                "bibliographic_citation": "Moscow: Novosti, 1990; English edition. 41-page local PDF supplied in project sources.",
                "source_type": "reference_book",
                "languages": ["en", "ru (title page)"] ,
                "regions_or_polities": ["苏联", "俄罗斯苏维埃联邦社会主义共和国（前身说明）"],
                "date_coverage": "全书叙述苏联奖励制度；勋章目录式章节见PDF第5、7–23页，最高称号见第24–25页，奖章见第26–41页。",
                "content_coverage": "已对41页OCR逐页提取并按题名与勋章目录交叉核对；勋章英文目录名及设立日期线索见第7–23页。第5页明确提及RSFSR红旗勋章设立日期。",
                "has_images": True,
                "image_quality_notes": "原书含图版/照片；本批仅将页码用于名称与制度线索交叉核对，没有裁取或导入书中图片。",
                "has_pagination": False,
                "download_method": "本地已有PDF及已缓存OCR文本；未重复下载。",
                "priority": 1,
                "status": "partial",
                "last_checked": AS_OF,
                "coverage_result": "41页均完成OCR文本提取；苏联勋章条目约覆盖第7–23页，需由跨目录任务对最高称号与奖章条目继续并表。",
                "local_cache": "sources/books/ordersandmedalsoftheussr.pdf",
                "ocr_text_cache": "sources/pages/ordersandmedalsoftheussr_ocr_extract.txt",
                "rights": "本地参考资料；本批只保存书目、页码和短摘要，不将书页图片作为可公开图片素材。",
                "coverage_boundary": "交叉核对该书所载苏联勋章名称与日期线索；不独立证明Mondvor具体实物版型或实物照片身份。",
                "next_action": "与Mondvor其余三目录及后续图录来源完成名称差异/遗漏核对。",
            },
        ],
        "coverage": {"planned": 2, "completed": 0, "partial": 2, "blocked": 0, "not_started": 0},
        "next_action": "跨目录合并；图片权利确认前不构建正文图片行。",
    }
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_PATH.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checkpoint = {
        "as_of": AS_OF,
        "batch": "mondvor_soviet_orders_2026-09-29",
        "source_method": "SOURCE_FIRST_BULK_INGESTION",
        "source_coverage": {"planned_source_scopes": 1, "completed_source_scopes": 0, "partial_source_scopes": 1, "not_started_source_scopes": 0},
        "source_pages": {"directory_entries": len(crawl.get("index_entries", [])), "article_pages_swept": crawl.get("page_count", 0), "unique_image_references": crawl.get("image_reference_count", 0)},
        "variant_differential": {"unique_family_candidates": len(counts_by_family), "variant_rows": len(volume_records), "exact_duplicate_groups_excluded": max(0, len(all_groups) - len(differential)), "selected_image_urls_pending_permission": len(unique_ref_urls)},
        "images": {"complete_local_image_files": 0, "decoded_local_images": 0, "not_downloaded_reason": "原站复用许可未确认，尊重页面限制。"},
        "next_action": "合并Putnikov 1990与Mondvor其余目录交叉表；图片使用授权来源替代，或在获得权利后再回填。",
        "files": [RAW_PATH.relative_to(ROOT).as_posix(), VOLUME_PATH.relative_to(ROOT).as_posix(), MANIFEST_PATH.relative_to(ROOT).as_posix(), MATRIX_PATH.relative_to(ROOT).as_posix()],
    }
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    image_queue = {
        "as_of": AS_OF,
        "scope_id": "soviet_orders_mondvor",
        "status": "permission_pending",
        "source_image_reference_count": len(unique_ref_urls),
        "selected_variant_rows": [
            {"variant_id": row["id"], "family": row["family"], "source_page_url": row["source_page_url"], "image_urls": [x["original_image_url"] for x in row["image_candidates"]], "status": "do_not_download_until_permission_confirmed"}
            for row in volume_records
        ],
    }
    IMAGE_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMAGE_QUEUE_PATH.write_text(json.dumps(image_queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    merge_queue = {
        "as_of": AS_OF,
        "scope_id": "soviet_orders_mondvor",
        "status": "pending_cross_source_review",
        "candidate_volume": VOLUME_PATH.relative_to(ROOT).as_posix(),
        "manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "tasks": [
            "核对蒙古/英语译名与目录分类；仅合并同一授予主体和实体章种。",
            "将RSFSR时期红旗勋章与1924年后苏联红旗勋章分开归属。",
            "复核Mondvor的type/variant层级是否与正式法定等级一致。",
            "不要把image_candidates计作本地图或正文完整图。",
        ],
    }
    MERGE_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MERGE_QUEUE_PATH.write_text(json.dumps(merge_queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"pages={len(pages)} families_in_draft={len(counts_by_family)} "
        f"variant_rows={len(volume_records)} candidate_groups={len(all_groups)} "
        f"complete_images=0 image_urls_pending={len(unique_ref_urls)}"
    )
    for family, count in sorted(counts_by_family.items()):
        print(f"{family}: {count}")


if __name__ == "__main__":
    main()
