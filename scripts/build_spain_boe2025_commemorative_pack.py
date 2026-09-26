from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tmp/pdfs/spain_boe2025_extracted"
OUT = ROOT / "assets/images/spain_boe2025_commemorative"
VOLUME = ROOT / "data/volumes/spain_boe2025_commemorative_pack1.json"
MANIFEST = ROOT / "data/volumes/spain_boe2025_commemorative_pack1_manifest.json"
SOURCE_ID = "es_boe_military_book_2025_commemorative_chapter"
SOURCE_PAGE = "https://www.boe.es/biblioteca_juridica/publicacion.php?id=PUB-DH-2025-364"


def row(family, name, original, date, detail, images):
    return {
        "id": f"{family}-V01",
        "family": family,
        "country_zh": "西班牙王国",
        "issuer": "西班牙相应历史政权与军政机关",
        "name": name,
        "original": original,
        "date": date,
        "variant": f"{detail}；历史专题图录照片·2025；低清参考",
        "views": [
            {"key": f"{family}-V01-VIEW-{i+1}", "label": label}
            for i, (_, label) in enumerate(images)
        ],
        "source_ids": [SOURCE_ID],
        "image_kind": "catalogue_photo",
        "html_eligible": True,
        "internal_notes": f"BOE 2025专题著作第6章；PDF第{images[0][0].split('_')[1]}页；仅用于本地研究图鉴。",
        "_images": images,
    }


RECORDS = [
    row("ESP-BAILEN-MEDAL", "拜伦战役奖章", "Medalla de Bailén", "1808年独立战争战役奖励", "馆藏实物；完整章体、悬挂结构与绶带", [("page_126_image_00.png", "完整正面")]),
    row("ESP-FRENCH-SQUADRON-SURRENDER-MEDAL", "法国舰队投降纪念奖章", "Medalla de la rendición de la Escuadra francesa", "1808年独立战争时期", "馆藏实物；完整圆章、悬挂结构与绶带", [("page_126_image_01.png", "完整正面")]),
    row("ESP-NORTH-DISTINCTION-CROSS", "北方军团杰出十字章", "Cruz de distinción del Norte", "1808–1814年独立战争时期", "完整十字、王冠、月桂悬挂与绶带", [("page_126_image_02.png", "完整正面")]),
    row("ESP-SAPPERS-DEPARTURE-CROSS", "工兵出走纪念十字章", "Cruz de la salida de los Zapadores", "1817年设立；纪念1808年行动", "完整王冠十字章与绶带", [("page_126_image_03.png", "完整正面")]),
    row("ESP-IRUN-DISTINCTION-MEDAL", "伊伦杰出奖章", "Medalla de distinción de Irún", "1837年设立；第一次卡洛斯战争", "完整实物正面、悬挂结构与绶带", [("page_129_image_00.png", "完整正面")]),
    row("ESP-TERUEL-DEFENCE-MEDAL", "特鲁埃尔保卫奖章", "Medalla de la defensa de Teruel", "1874年设立；卡洛斯战争", "完整实物正面与绶带", [("page_129_image_01.png", "完整正面")]),
    row("ESP-MONTEJURRA-MEDAL", "蒙特胡拉奖章", "Medalla de Montejurra", "1873年；卡洛斯派奖励", "完整十字形章体、悬挂结构与绶带", [("page_129_image_02.png", "完整正面")]),
    row("ESP-VIZCAYA-MEDAL", "比斯开奖章", "Medalla de Vizcaya", "1874年；卡洛斯派奖励", "完整实物正面、悬挂结构与绶带", [("page_129_image_03.png", "完整正面")]),
    row("ESP-EPIDEMICS-DISTINCTION-CROSS", "防疫杰出十字章", "Cruz de distinción de Epidemias", "1829年设立", "完整十字章、月桂悬挂与绶带", [("page_129_image_04.png", "完整正面")]),
    row("ESP-NUMANCIA-CIRCUMNAVIGATION-MEDAL", "努曼西亚号环球航行奖章", "Medalla de la circunnavegación de la Numancia", "1868年设立；纪念1865–1867年航行", "完整实物正面与绶带", [("page_129_image_05.png", "完整正面")]),
    row("ESP-NAUTILUS-CIRCUMNAVIGATION-MEDAL", "鹦鹉螺号环球航行奖章", "Medalla de la circunnavegación de la Nautilus", "1894年设立；纪念1892–1894年航行", "完整实物正面与绶带", [("page_129_image_06.png", "完整正面")]),
    row("ESP-ALFONSO-XIII-OATH-MEDAL", "阿方索十三世宣誓纪念章", "Medalla de la jura de Alfonso XIII", "1902年设立", "完整实物正面、悬挂结构与绶带", [("page_129_image_07.png", "完整正面")]),
    row("ESP-ZARAGOZA-SIEGES-CENTENARY-MEDAL", "萨拉戈萨围城百年纪念章", "Medalla de los sitios de Zaragoza", "1908–1914年百年纪念章系列", "银级／协作者型；完整实物正面与绶带", [("page_130_image_00.png", "完整正面")]),
    row("ESP-CADIZ-CONSTITUTION-CENTENARY-MEDAL", "1812年宪法与加的斯围城百年纪念章", "Medalla de la Constitución de 1812 y sitio de Cádiz", "1908–1914年百年纪念章系列", "铜级／参与者型；完整实物正面与绶带", [("page_130_image_01.png", "完整正面")]),
    row("ESP-CIUDAD-RODRIGO-SIEGE-CENTENARY-MEDAL", "罗德里戈城围城百年纪念章", "Medalla del sitio de Ciudad Rodrigo", "1908–1914年百年纪念章系列", "银级；完整实物正面与绶带", [("page_130_image_02.png", "完整正面")]),
    row("ESP-CHICLANA-BATTLE-CENTENARY-MEDAL", "奇克拉纳战役百年纪念章", "Medalla de la batalla de Chiclana", "1908–1914年百年纪念章系列", "银级；完整十字形章体、月桂悬挂与绶带", [("page_130_image_03.png", "完整正面")]),
    row("ESP-GERONA-SIEGES-CENTENARY-MEDAL", "赫罗纳围城百年纪念章", "Medalla de los sitios de Gerona", "1908–1914年百年纪念章系列", "银级／保卫者型；完整实物正面与绶带", [("page_132_image_00.png", "完整正面")]),
    row("ESP-BRIHUEGA-VILLAVICIOSA-CENTENARY-MEDAL", "布里韦加轰炸与比利亚维西奥萨战役纪念章", "Medalla del bombardeo y asalto de Brihuega y de la batalla de Villaviciosa", "1908–1914年历史纪念章系列", "银级；完整实物正面与绶带", [("page_132_image_01.png", "完整正面")]),
    row("ESP-VIGO-RECONQUEST-CENTENARY-MEDAL", "维戈收复百年纪念章", "Medalla de la reconquista de Vigo", "1908–1914年百年纪念章系列", "铜级；完整实物正面与绶带", [("page_132_image_02.png", "完整正面")]),
    row("ESP-VITORIA-BATTLE-CENTENARY-MEDAL", "维多利亚战役百年纪念章", "Medalla de la batalla de Vitoria", "1908–1914年百年纪念章系列", "银级；完整十字章、王冠与绶带", [("page_132_image_03.png", "完整正面")]),
    row("ESP-LEPANTO-IV-CENTENARY-MEDAL", "勒班陀战役四百周年纪念章", "Medalla conmemorativa del IV Centenario de la Batalla de Lepanto", "1971年设立", "同一章种完整正背面", [("page_132_image_04.png", "正面"), ("page_132_image_05.png", "背面")]),
    row("ESP-OPERATION-BALMIS-MEDAL", "巴尔米斯行动纪念章", "Medalla conmemorativa de la operación Balmis", "2020-07-28设立", "2020式；同一实物完整正背面", [("page_133_image_01.png", "正面"), ("page_133_image_02.png", "背面")]),
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
                "view_key": record["views"][i - 1]["key"],
                "label": label,
                "local_path": dest.relative_to(ROOT).as_posix(),
                "source_page": SOURCE_PAGE,
                "source_pdf": "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf",
                "source_pdf_page": int(src_name.split("_")[1]),
                "width": width,
                "height": height,
                "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "rights": "BOE 2025 volume states CC BY-NC-ND 4.0; individual photographs may have additional rights. Offline research catalogue only.",
            })
        public.append(record)
    payload = {"as_of": "2026-09-26", "volume": "西班牙历史纪念奖励（BOE 2025专题图录）", "records": public}
    families = len({r["family"] for r in public})
    manifest = {
        "volume": payload["volume"], "as_of": payload["as_of"],
        "records_file": VOLUME.relative_to(ROOT).as_posix(),
        "image_directory": OUT.relative_to(ROOT).as_posix() + "/",
        "counts": {"distinct_award_families": families, "variant_rows": len(public), "complete_image_files": len(images), "physical_photo_views": len(images)},
        "source": {"source_id": SOURCE_ID, "title": "Las órdenes y condecoraciones militares del Reino de España", "institution": "Agencia Estatal Boletín Oficial del Estado", "year": 2025, "catalogue_url": SOURCE_PAGE, "processed_pdf_pages": [126, 129, 130, 132, 133], "rights_note": "Offline research use; retain source credits and the volume's CC BY-NC-ND notice."},
        "images": images,
    }
    VOLUME.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {families} families, {len(public)} variants, {len(images)} images")


if __name__ == "__main__":
    main()
