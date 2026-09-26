from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tmp/pdfs/spain_boe2025_extracted"
OUT = ROOT / "assets/images/spain_boe2025_campaigns"
VOLUME = ROOT / "data/volumes/spain_boe2025_campaigns_pack1.json"
MANIFEST = ROOT / "data/volumes/spain_boe2025_campaigns_pack1_manifest.json"

SOURCE_ID = "es_boe_military_book_2025_campaign_chapters"
SOURCE_PAGE = "https://www.boe.es/biblioteca_juridica/publicacion.php?id=PUB-DH-2025-364"


def variant(family: str, suffix: str, name: str, original: str, date: str, detail: str, images: list[tuple[str, str]]) -> dict:
    return {
        "id": f"{family}-{suffix}",
        "family": family,
        "country_zh": "西班牙王国",
        "issuer": "西班牙王国／相应历史政权与军政机关",
        "name": name,
        "original": original,
        "date": date,
        "variant": f"{detail}；专题图录照片·2025；低清参考",
        "views": [{"key": f"{family}-{suffix}-VIEW-{i+1}", "label": label} for i, (_, label) in enumerate(images)],
        "source_ids": [SOURCE_ID],
        "image_kind": "catalogue_photo",
        "html_eligible": True,
        "internal_notes": "BOE 2025专题著作的完整章体照片；原PDF第{}页。仅用于本地研究图鉴，保留来源与权利限制。".format(images[0][0].split("_")[1]),
        "_images": images,
    }


RECORDS = [
    variant("ESP-AFRICA-1860", "SILVER", "非洲战役奖章", "Medalla de África", "1860年设立", "银质型；王冠悬挂", [("page_138_image_00.png", "完整正面")]),
    variant("ESP-PACIFIC-CALLAO-1866", "BRONZE", "太平洋战役（卡亚俄）奖章", "Medalla de la campaña del Pacífico o del Callao", "1866年设立", "铜质章；红色绶带", [("page_138_image_01.png", "完整正面")]),
    variant("ESP-JOLO-CROSS-1851", "BADGE", "霍洛十字章", "Cruz de Joló", "1851年设立", "白色珐琅十字；图录所示章型", [("page_138_image_02.png", "完整正面")]),
    variant("ESP-JOLO-CAMPAIGN-1876", "BRONZE", "霍洛战役奖章", "Medalla de la campaña de Joló", "1876年设立", "铜质单级；王冠与月桂悬挂", [("page_138_image_03.png", "完整正面")]),
    variant("ESP-CUBA-CAMPAIGN-1873", "FIELD", "古巴战役奖章", "Medalla de la campaña de Cuba", "1873年设立", "战地服役型；红色绶带中央黑条", [("page_138_image_04.png", "完整正面")]),
    variant("ESP-CUBA-CAMPAIGN-1873", "DEPENDENCIES", "古巴战役奖章", "Medalla de la campaña de Cuba", "1873年设立", "后方机关三年服役型；白色绶带中央黑条", [("page_138_image_05.png", "完整正面")]),
    variant("ESP-MINDANAO-CAMPAIGNS", "1890-1895", "棉兰老战役奖章", "Medalla de las campañas de Mindanao", "1895年设立；纪念1890-1891及1894-1895战役", "双战役扣型", [("page_139_image_00.png", "完整正面")]),
    variant("ESP-PHILIPPINES-CAMPAIGN-1898", "BADGE", "菲律宾战役奖章", "Medalla de la campaña de Filipinas", "1898年设立", "盾形章；图示带战役扣", [("page_139_image_01.png", "完整正面")]),
    variant("ESP-LUZON-CAMPAIGN-1898", "BRONZE", "吕宋战役奖章", "Medalla de campaña de Luzón", "1898年设立；纪念1896-1897战役", "铜质圆章", [("page_139_image_02.png", "完整正面")]),
    variant("ESP-CUBA-ISLAND-CAMPAIGN-1899", "REGULAR-WOUNDED", "古巴岛战役奖章", "Medalla de la Campaña de la isla de Cuba", "1899年设立；纪念1895-1898战役", "陆海军正规部队型；绶带附伤员红色交叉饰", [("page_140_image_00.png", "完整正面")]),
    variant("ESP-CUBA-ISLAND-CAMPAIGN-1899", "VOLUNTEER", "古巴岛战役奖章", "Medalla de la Campaña de la isla de Cuba", "1899年设立；纪念1895-1898战役", "古巴志愿部队型", [("page_140_image_01.png", "完整正面")]),
    variant("ESP-CUBA-VOLUNTEER-CORPS-1871", "SILVER", "古巴岛志愿军团奖章", "Medalla de los cuerpos voluntarios de la isla de Cuba", "1871年设立", "银质椭圆章；王冠悬挂", [("page_140_image_02.png", "完整正面")]),
    variant("ESP-PUERTO-RICO-VOLUNTEERS-1880", "SILVER", "波多黎各志愿者奖章", "Medalla de los Voluntarios de Puerto Rico", "1880年设立", "银质椭圆章；图示带扣", [("page_141_image_00.png", "完整正面")]),
    variant("ESP-CUBA-VOLUNTEERS-CONSTANCY-1883", "TEN-YEARS", "古巴岛志愿者恒久服役奖章", "Medalla de la constancia de los voluntarios de la isla de Cuba", "1883年设立", "十年服役扣型", [("page_141_image_01.png", "完整正面")]),
    variant("ESP-FILIPINO-NATIVE-VOLUNTEERS-1897", "SILVERED-COPPER", "菲律宾土著志愿者奖章", "Medalla de los voluntarios indígenas de Filipinas", "1897年设立", "镀银铜质椭圆章", [("page_141_image_02.png", "完整正面")]),
    variant("ESP-ALFONSO-XII-MEDAL-1875", "CAMPAIGN", "阿方索十二世奖章", "Medalla de Alfonso XII", "1875年设立", "银质或镀银型；图示带战役扣", [("page_143_image_00.png", "完整正面")]),
    variant("ESP-CIVIL-WAR-MEDAL-1873-1874", "CAMPAIGN", "1873-1874年内战奖章", "Medalla de la Guerra Civil 1873-1874", "1876年设立", "圆章；红色绶带中央黄条", [("page_143_image_01.png", "完整正面")]),
    variant("ESP-MELILLA-MEDAL-1910", "WOUNDED", "梅利利亚奖章", "Medalla de Melilla", "1910年设立", "伤员绶带红色交叉饰型", [("page_145_image_00.png", "正面"), ("page_145_image_01.png", "背面")]),
    variant("ESP-AFRICA-MEDAL-1915", "WESTERN-ZONE", "非洲奖章", "Medalla de África", "1915年改称", "西部战区绿色绶带型", [("page_145_image_02.png", "完整正面")]),
    variant("ESP-MOROCCO-MILITARY-MEDAL-1916", "WOUNDED", "摩洛哥军事奖章", "Medalla Militar de Marruecos", "1916年改称", "伤员绶带红色交叉饰型", [("page_145_image_03.png", "完整正面")]),
    variant("ESP-SANTIAGO-CAVITE-MEDAL-1923", "SANTIAGO", "圣地亚哥-卡维特奖章", "Medalla de Santiago de Cuba y Cavite", "1923年设立；纪念1898年海战", "图示圣地亚哥扣型", [("page_146_image_00.png", "完整正面")]),
    variant("ESP-CAMPAIGNS-COMMEMORATIVE-1931", "WOUNDED", "战役纪念奖章", "Medalla conmemorativa de las campañas", "1931年设立", "第二共和国型；绶带附伤员交叉饰", [("page_146_image_01.png", "完整正面")]),
    variant("ESP-CAMPAIGN-1936-1939", "FRONTLINE", "1936-1939年战役奖章", "Medalla de la Campaña 1936-1939", "1937年设立", "前线服役型；黑边绶带", [("page_146_image_02.png", "完整正面")]),
    variant("ESP-RUSSIA-CAMPAIGN-1943", "WOUNDED", "俄罗斯战役奖章", "Medalla de la Campaña de Rusia", "1943年设立", "伤员绶带交叉饰型", [("page_148_image_02.png", "完整正面")]),
    variant("ESP-IFNI-SAHARA-MEDAL-1958", "ENAMELLED", "伊夫尼-撒哈拉奖章", "Medalla de Ifni-Sahara", "1958年设立", "军官等有色珐琅型；图录同件正背", [("page_148_image_00.png", "正面"), ("page_148_image_01.png", "背面")]),
    variant("ESP-SAHARA-MEDAL-1977", "COMBAT-WOUNDED", "撒哈拉奖章", "Medalla del Sahara", "1977年设立", "战区蓝黑白绶带；附伤员交叉饰", [("page_148_image_03.png", "完整正面")]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images_manifest = []
    public_records = []
    for record in RECORDS:
        image_specs = record.pop("_images")
        for index, (src_name, label) in enumerate(image_specs, 1):
            src = SRC / src_name
            dest_name = f"{record['id'].lower().replace('_', '-')}-{index}.png"
            dest = OUT / dest_name
            shutil.copyfile(src, dest)
            with Image.open(dest) as image:
                width, height = image.size
                image.verify()
            digest = hashlib.sha256(dest.read_bytes()).hexdigest()
            key = record["views"][index - 1]["key"]
            images_manifest.append({
                "view_key": key,
                "label": label,
                "local_path": dest.relative_to(ROOT).as_posix(),
                "source_page": SOURCE_PAGE,
                "source_pdf": "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf",
                "source_pdf_page": int(src_name.split("_")[1]),
                "width": width,
                "height": height,
                "sha256": digest,
                "rights": "BOE 2025 volume states CC BY-NC-ND 4.0; individual photographs may have additional rights. Retained for offline research catalogue only.",
            })
        public_records.append(record)

    volume = {
        "as_of": "2026-09-26",
        "volume": "西班牙历史战役与海外服役勋奖章（BOE 2025专题图录）",
        "scope": "BOE 2025整本专题著作第6、7及10章的成组图版；本包只纳入名称、日期与具体图像可明确对应的完整章体。",
        "records": public_records,
    }
    families = len({record["family"] for record in public_records})
    manifest = {
        "volume": volume["volume"],
        "as_of": volume["as_of"],
        "records_file": VOLUME.relative_to(ROOT).as_posix(),
        "image_directory": OUT.relative_to(ROOT).as_posix() + "/",
        "counts": {
            "distinct_award_families": families,
            "variant_rows": len(public_records),
            "complete_image_files": len(images_manifest),
            "physical_photo_views": len(images_manifest),
        },
        "source": {
            "source_id": SOURCE_ID,
            "title": "Las órdenes y condecoraciones militares del Reino de España",
            "institution": "Agencia Estatal Boletín Oficial del Estado",
            "year": 2025,
            "catalogue_url": SOURCE_PAGE,
            "local_pdf": "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf",
            "processed_pdf_pages": [138, 139, 140, 141, 143, 145, 146, 148],
            "rights_note": "Offline research use. Preserve attribution and the PDF's CC BY-NC-ND 4.0 notice; individual image credits remain in the source pages.",
        },
        "images": images_manifest,
    }
    VOLUME.write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {families} families, {len(public_records)} variants, {len(images_manifest)} images")


if __name__ == "__main__":
    main()
