from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tmp/pdfs/spain_boe2025_extracted"
OUT = ROOT / "assets/images/spain_boe2025_discontinued"
VOLUME = ROOT / "data/volumes/spain_boe2025_discontinued_pack1.json"
MANIFEST = ROOT / "data/volumes/spain_boe2025_discontinued_pack1_manifest.json"
SOURCE_ID = "es_boe_military_book_2025_discontinued_chapter"
SOURCE_PAGE = "https://www.boe.es/biblioteca_juridica/publicacion.php?id=PUB-DH-2025-364"


def row(family, suffix, name, original, date, detail, images):
    return {
        "id": f"{family}-{suffix}", "family": family, "country_zh": "西班牙王国",
        "issuer": "西班牙王国／相应历史政权与军政机关", "name": name,
        "original": original, "date": date,
        "variant": f"{detail}；专题图录照片·2025；低清参考",
        "views": [{"key": f"{family}-{suffix}-VIEW-{i+1}", "label": label} for i, (_, label) in enumerate(images)],
        "source_ids": [SOURCE_ID], "image_kind": "catalogue_photo", "html_eligible": True,
        "internal_notes": f"BOE 2025专题著作第10章；原PDF第{images[0][0].split('_')[1]}页。仅用于本地研究图鉴。",
        "_images": images,
    }


RECORDS = [
    row("ESP-NAVY-DISTINCTION-CROSS", "OFFICER", "海军杰出十字章（王家冠冕）", "Cruz de Distinción de la Marina o Diadema Real", "1816年设立；1866年前使用", "军官金质白珐琅型；王冠与锚悬挂", [("page_206_image_00.png", "完整正面")]),
    row("ESP-MARIA-ISABEL-LUISA-CROSS", "SILVER", "玛丽亚·伊莎贝尔·路易莎十字章", "Cruz de María Isabel Luisa", "1833年设立；1868年废止", "士兵银质型", [("page_207_image_01.png", "完整正面")]),
    row("ESP-MARIA-ISABEL-LUISA-CROSS", "GOLD", "玛丽亚·伊莎贝尔·路易莎十字章", "Cruz de María Isabel Luisa", "1833年设立；1868年废止", "晋升军官后换用金质／鎏金型", [("page_207_image_02.png", "完整正面")]),
    row("ESP-MILITARY-ORDER-MARIA-CRISTINA", "FIRST-ROYAL", "玛丽亚·克里斯蒂娜皇家军事勋章", "Real y Militar Orden de María Cristina", "1890年设立；1931年废止", "一等十字；王冠与百合版", [("page_209_image_00.png", "完整正面")]),
    row("ESP-MILITARY-ORDER-MARIA-CRISTINA", "SECOND-ROYAL", "玛丽亚·克里斯蒂娜皇家军事勋章", "Real y Militar Orden de María Cristina", "1890年设立；1931年废止", "二等十字；王冠与百合版", [("page_209_image_01.png", "完整正面")]),
    row("ESP-MILITARY-ORDER-MARIA-CRISTINA", "FIRST-REPUBLIC", "玛丽亚·克里斯蒂娜皇家军事勋章", "Real y Militar Orden de María Cristina", "1931年共和国改式", "一等十字；壁冠、城堡与狮子改式", [("page_209_image_02.png", "完整正面")]),
    row("ESP-MILITARY-ORDER-MARIA-CRISTINA", "SECOND-REPUBLIC", "玛丽亚·克里斯蒂娜皇家军事勋章", "Real y Militar Orden de María Cristina", "1931年共和国改式", "二等十字；壁冠、城堡与狮子改式", [("page_209_image_03.png", "完整正面")]),
    row("ESP-NAVAL-ORDER-MARIA-CRISTINA", "FIRST", "玛丽亚·克里斯蒂娜皇家海军勋章", "Real y Militar Orden Naval de María Cristina", "1891年设立；1931年废止", "一等十字；锚饰海军型", [("page_210_image_00.png", "完整正面")]),
    row("ESP-NAVAL-MEDAL-1918", "MODEL-1918", "海军奖章", "Medalla Naval", "1918年设立；1971年废止", "1918型；个人章", [("page_211_image_00.png", "完整正面")]),
    row("ESP-NAVAL-CANNON-SHOOTING-MEDAL", "1922-1931", "海军火炮射击奖章", "Medalla para Premio de Tiro con Cañón", "1922年设立；1941年废止", "1922-1931王冠型；图示带射击扣", [("page_213_image_00.png", "完整正面")]),
    row("ESP-AIR-MEDAL-1926", "MODELS-1926-1931", "航空奖章", "Medalla Aérea", "1926年设立；1971年废止", "1926、1928及1931三种早期模型同图对照", [("page_214_image_00.png", "三种完整模型图")]),
    row("ESP-AIR-MEDAL-1926", "MODEL-1945", "航空奖章", "Medalla Aérea", "1945年改式", "1945和平时期型", [("page_215_image_00.png", "完整正面")]),
    row("ESP-AIR-MEDAL-1926", "MODEL-1970", "航空奖章", "Medalla Aérea", "1970年改式；1971年废止", "1970和平时期型", [("page_215_image_01.png", "完整正面")]),
    row("ESP-MOROCCO-PEACE-MEDAL", "STANDARD", "摩洛哥和平奖章", "Medalla de la Paz de Marruecos", "1927年设立；2003年废止", "标准型；同件正背面", [("page_216_image_00.png", "正面"), ("page_216_image_01.png", "背面")]),
    row("ESP-BLOOD-DONOR-MEDAL", "1955", "献血者奖章", "Medalla de los donantes de sangre", "1937年设立；1989年前后停授", "1955式文字型", [("page_217_image_00.png", "完整正面")]),
    row("ESP-WAR-DISABLED-MEDAL", "1938", "祖国战争伤残军人奖章", "Medalla de Mutilados", "1938年设立；1980年后逐步失效", "1938型；带1936年7月18日题记", [("page_218_image_01.png", "完整正面")]),
    row("ESP-MOROCCAN-MILITARY-CONSTANCY-ORDER", "PLAQUE", "摩洛哥保护地军事恒久服役勋章", "Orden Militar de la Constancia", "1946年设立；1956年随保护地结束", "胸星／牌章（Placa）；西属摩洛哥哈里发军队奖励", [("page_219_image_01.png", "完整正面")]),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    images = []
    public = []
    for record in RECORDS:
        specs = record.pop("_images")
        for i, (src_name, label) in enumerate(specs, 1):
            src = SRC / src_name
            dest = OUT / f"{record['id'].lower()}-{i}.png"
            shutil.copyfile(src, dest)
            with Image.open(dest) as image:
                width, height = image.size
                image.verify()
            images.append({
                "view_key": record["views"][i-1]["key"], "label": label,
                "local_path": dest.relative_to(ROOT).as_posix(), "source_page": SOURCE_PAGE,
                "source_pdf": "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf",
                "source_pdf_page": int(src_name.split("_")[1]), "width": width, "height": height,
                "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "rights": "BOE 2025 volume states CC BY-NC-ND 4.0; individual photographs may have additional rights. Offline research catalogue only.",
            })
        public.append(record)
    payload = {"as_of": "2026-09-26", "volume": "西班牙已废止军事奖励（BOE 2025专题图录）", "records": public}
    families = len({r["family"] for r in public})
    manifest = {
        "volume": payload["volume"], "as_of": payload["as_of"],
        "records_file": VOLUME.relative_to(ROOT).as_posix(), "image_directory": OUT.relative_to(ROOT).as_posix()+"/",
        "counts": {"distinct_award_families": families, "variant_rows": len(public), "complete_image_files": len(images), "physical_photo_views": len(images)},
        "source": {"source_id": SOURCE_ID, "title": "Las órdenes y condecoraciones militares del Reino de España", "institution": "Agencia Estatal Boletín Oficial del Estado", "year": 2025, "catalogue_url": SOURCE_PAGE, "processed_pdf_pages": [206,207,209,210,211,213,214,215,216,217,218,219], "rights_note": "Offline research use; retain all source credits and CC BY-NC-ND notice."},
        "images": images,
    }
    VOLUME.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"built {families} families, {len(public)} variants, {len(images)} images")


if __name__ == "__main__":
    main()
