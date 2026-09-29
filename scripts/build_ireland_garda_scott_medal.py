from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-09-29"
BATCH = "ireland_garda_scott_medal_2023"
PDF = ROOT / "sources/books/ireland_garda_scott_medal_awards_2023.pdf"
PDF_URL = "https://www.garda.ie/en/about-us/our-departments/office-of-corporate-communications/news-media/scott-medal-award-ceremony-booklet-2023.pdf"
PAGE_URL = "https://www.garda.ie/en/about-us/our-history/the-scott-medal/"
RAW_GROUP = ROOT / "assets/raw/ireland_garda_scott_medal_2023/page-19-image-01.jpg"
OUT_DIR = ROOT / "assets/images/ireland_garda_scott_medal_2023"
PAGE_DIR = ROOT / "sources/pages/ireland_garda_scott_medal_2023"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PAGE_DIR.mkdir(parents=True, exist_ok=True)


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# Render the complete PDF page containing the three-grade plate for visual provenance.
doc = pdfium.PdfDocument(str(PDF))
page = doc[18]  # one-based PDF page 19
rendered = page.render(scale=2.5).to_pil()
rendered.save(PAGE_DIR / "page-19.png")

group = Image.open(RAW_GROUP).convert("RGB")
crops = [
    ("gold", "金级", (176, 0, 351, 305)),
    ("silver", "银级", (34, 0, 205, 305)),
    ("bronze", "铜级", (317, 0, 508, 305)),
]

records = []
images = []
raw = []
for idx, (slug, grade, box) in enumerate(crops, 1):
    rid = f"IE-GARDA-SCOTT-{idx:02d}"
    out = OUT_DIR / f"scott-medal-{slug}-official-2023.jpg"
    group.crop(box).save(out, quality=96, subsampling=0)
    with Image.open(out) as im:
        im.verify()
    with Image.open(out) as im:
        width, height = im.size
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    view_key = f"{rid}-V01"
    records.append({
        "id": rid,
        "family": "IE-GARDA-SCOTT-MEDAL",
        "name": "斯科特英勇奖章",
        "original": "An Bonn Scott / Scott Medal",
        "date": "1923年设立；1924年首次颁发",
        "variant": f"{grade}；爱尔兰国家警察官方2023年三等级图版裁图；低清参考",
        "views": [{"key": view_key, "label": "完整正面实物照"}],
        "source_ids": ["IE-GARDA-SCOTT-HISTORY", "IE-GARDA-SCOTT-BOOKLET-2023"],
    })
    images.append({
        "view_key": view_key,
        "local_path": out.relative_to(ROOT).as_posix(),
        "source_page": f"{PDF_URL}#page=19",
        "image_page": f"{PDF_URL}#page=19",
        "original_url": PDF_URL,
        "source_object": "official booklet PDF page 19, image object Im0; crop box " + ",".join(map(str, box)),
        "width": width,
        "height": height,
        "bytes": out.stat().st_size,
        "sha256": sha,
        "content_type": "image/jpeg",
        "image_kind": "官方实物合照裁取的完整单枚正面；低清参考",
        "author_or_institution": "An Garda Síochána",
        "license": "未见逐图开放许可；本地研究使用",
        "pdf_page": 19,
        "crop_box_pixels": list(box),
        "source_embedded_image": RAW_GROUP.relative_to(ROOT).as_posix(),
    })
    raw.append({
        "source_id": "IE-GARDA-SCOTT-BOOKLET-2023",
        "page_title": "History of the Scott Medal",
        "original_name": "An Bonn Scott / Scott Medal",
        "name_zh": "斯科特英勇奖章",
        "date_candidate": "1923年设立；1924年首次颁发",
        "category": "police_bravery_medal",
        "grade_or_material_clue": grade,
        "object_page": PAGE_URL,
        "image_page": f"{PDF_URL}#page=19",
        "original_image_urls": [PDF_URL],
        "local_source_page": "sources/pages/ireland_garda_scott_medal_2023/page-19.png",
        "local_embedded_image": RAW_GROUP.relative_to(ROOT).as_posix(),
        "crop_box_pixels": list(box),
        "notes": "官方图版同时展示金、银、铜三级；从完整三章合照按单枚轮廓裁取，未插值。",
        "status": "merged_pictured",
        "accessed": AS_OF,
    })

volume = {"as_of": AS_OF, "volume": "爱尔兰国家警察正式英勇奖励", "records": records}
manifest = {
    "as_of": AS_OF,
    "volume": "爱尔兰国家警察正式英勇奖励",
    "batch_id": BATCH,
    "sources": [
        {
            "source_id": "IE-GARDA-SCOTT-HISTORY",
            "source_name": "An Garda Síochána — The Scott Medal",
            "base_url": PAGE_URL,
            "source_type": "official_national_police_history",
            "languages": ["en"],
            "status": "completed_visible_page",
            "content_coverage": "1923年创设背景、章面说明、授予条件与现行颁发机构。",
        },
        {
            "source_id": "IE-GARDA-SCOTT-BOOKLET-2023",
            "source_name": "Scott Medal Award Ceremony Booklet 2023",
            "base_url": PDF_URL,
            "local_copy": PDF.relative_to(ROOT).as_posix(),
            "source_type": "official_national_police_ceremony_booklet",
            "languages": ["en"],
            "status": "completed_relevant_24_page_booklet",
            "content_coverage": "第19页金、银、铜三级完整实物合照及三级授予标准。",
        },
    ],
    "images": images,
    "validation": {"record_count": 3, "family_count": 1, "decoded_image_count": 3, "all_images_exist": True, "all_decoded": True},
}
dump(ROOT / f"data/volumes/{BATCH}.json", volume)
dump(ROOT / f"data/volumes/{BATCH}_manifest.json", manifest)
raw_path = ROOT / f"data/raw_candidates/{BATCH}.jsonl"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in raw), encoding="utf-8")

matrix = {
    "source_atlas_id": "ireland_garda_source_matrix",
    "as_of": AS_OF,
    "scope": "爱尔兰国家警察正式勋奖章",
    "sources": [
        {"id": "IE-GARDA-SCOTT-HISTORY", "type": "official_national_police_history", "language": "en", "scope": "斯科特英勇奖章制度与形制", "date_coverage": "1923—现行", "image_capability": "单枚低清图", "pagination": "none", "download_method": "public page and direct image", "priority": 1, "status": "completed_visible_page", "last_checked": AS_OF},
        {"id": "IE-GARDA-SCOTT-BOOKLET-2023", "type": "official_ceremony_booklet", "language": "en", "scope": "斯科特奖章金银铜三级", "date_coverage": "1923—2023", "image_capability": "三级完整正面合照", "pagination": "24-page PDF", "download_method": "direct public PDF; embedded image extraction", "priority": 1, "status": "completed_relevant_booklet", "last_checked": AS_OF},
        {"id": "IE-GARDA-OTHER-AWARDS", "type": "official_national_police", "language": "en/ga", "scope": "国家警察其他正式奖章与长期服务奖励", "date_coverage": "待扫", "image_capability": "unknown", "pagination": "unknown", "download_method": "site and publications sweep pending", "priority": 2, "status": "not_started", "last_checked": AS_OF},
    ],
    "counts": {"planned": 3, "completed": 2, "partial": 0, "blocked": 0, "not_started": 1},
    "next_action": "穷尽国家警察其他正式奖章和服役奖励；与国防军官方整册结果合并为爱尔兰总卷。",
}
dump(ROOT / "data/source_atlas/ireland_garda_source_matrix.json", matrix)

checkpoint = {
    "checkpoint_id": BATCH,
    "as_of": AS_OF,
    "scope": "爱尔兰国家警察斯科特英勇奖章三级",
    "plan": ["核对国家警察官方历史页", "检查24页2023颁奖册", "提取第19页三级完整实物合照", "按等级裁取并归入同一family", "等待主任务合并HTML"],
    "source_counts": matrix["counts"],
    "counts": {"raw_candidates": 3, "merged_families": 1, "variants": 3, "decoded_local_images": 3, "unpictured_candidates": 0, "unresolved_candidates": 0},
    "files": [f"data/raw_candidates/{BATCH}.jsonl", f"data/volumes/{BATCH}.json", f"data/volumes/{BATCH}_manifest.json", "data/source_atlas/ireland_garda_source_matrix.json", "assets/images/ireland_garda_scott_medal_2023/", "sources/pages/ireland_garda_scott_medal_2023/page-19.png", PDF.relative_to(ROOT).as_posix()],
    "status": "official_three_grade_plate_normalized_pending_html_merge",
    "next_action": "主任务视觉检查三个裁图并合并爱尔兰分区；随后接入国防军整册批次。",
}
dump(ROOT / f"data/checkpoints/{BATCH}.json", checkpoint)

print(json.dumps({"records": 3, "families": 1, "images": 3, "page_render": "sources/pages/ireland_garda_scott_medal_2023/page-19.png"}, ensure_ascii=False))
