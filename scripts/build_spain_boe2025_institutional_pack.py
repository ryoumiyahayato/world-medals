from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tmp/pdfs/spain_boe2025_extracted"
OUT = ROOT / "assets/images/spain_boe2025_institutional"
VOLUME = ROOT / "data/volumes/spain_boe2025_institutional_pack1.json"
MANIFEST = ROOT / "data/volumes/spain_boe2025_institutional_pack1_manifest.json"
SOURCE_ID = "es_boe_military_book_2025_institutional_chapters"
SOURCE_PAGE = "https://www.boe.es/biblioteca_juridica/publicacion.php?id=PUB-DH-2025-364"


def row(family, suffix, name, original, date, detail, images, issuer):
    return {
        "id": f"{family}-{suffix}", "family": family, "country_zh": "西班牙王国",
        "issuer": issuer, "name": name, "original": original, "date": date,
        "variant": f"{detail}；历史专题图录照片·2025；低清参考",
        "views": [{"key": f"{family}-{suffix}-VIEW-{i+1}", "label": label} for i, (_, label) in enumerate(images)],
        "source_ids": [SOURCE_ID], "image_kind": "catalogue_photo", "html_eligible": True,
        "internal_notes": f"BOE 2025专题著作第11／12章；PDF第{images[0][0].split('_')[1]}页；仅用于本地研究图鉴。",
        "_images": images,
    }


RECORDS = [
    row("ESP-GUARDIA-CIVIL-MERIT-ORDER", "GRAND-CROSS", "国民警卫队功绩勋章", "Orden del Mérito de la Guardia Civil", "1976-05-29设立；2012年增设大十字", "大十字级胸星", [("page_225_image_00.png", "完整正面")], "西班牙内政部／国民警卫队"),
    row("ESP-GUARDIA-CIVIL-MERIT-ORDER", "GOLD-CROSS", "国民警卫队功绩勋章", "Orden del Mérito de la Guardia Civil", "1976-05-29设立", "金十字级胸星", [("page_225_image_01.png", "完整正面")], "西班牙内政部／国民警卫队"),
    row("ESP-GUARDIA-CIVIL-MERIT-ORDER", "SILVER-CROSS", "国民警卫队功绩勋章", "Orden del Mérito de la Guardia Civil", "1976-05-29设立", "银十字级胸星", [("page_225_image_02.png", "完整正面")], "西班牙内政部／国民警卫队"),
    row("ESP-GUARDIA-CIVIL-MERIT-ORDER", "RED-DISTINCTION", "国民警卫队功绩勋章", "Orden del Mérito de la Guardia Civil", "1976-05-29设立", "红色标识十字；同一实物正背面", [("page_225_image_03.png", "正面"), ("page_225_image_04.png", "背面")], "西班牙内政部／国民警卫队"),
    row("ESP-GUARDIA-CIVIL-MERIT-ORDER", "WHITE-DISTINCTION", "国民警卫队功绩勋章", "Orden del Mérito de la Guardia Civil", "1976-05-29设立", "白色标识十字", [("page_225_image_05.png", "完整正面")], "西班牙内政部／国民警卫队"),
    row("ESP-FIDELITAS-CROSS", "FIRST-CLASS", "菲德利塔斯十字章", "Cruz Fidélitas", "2007-07-25设立；2013年修订", "一等／牌章（Placa）", [("page_233_image_00.png", "完整正面")], "西班牙军中教长区"),
    row("ESP-FIDELITAS-CROSS", "SECOND-CLASS", "菲德利塔斯十字章", "Cruz Fidélitas", "2007-07-25设立；2013年修订", "二等／司令级颈章（Encomienda）", [("page_233_image_01.png", "完整正面")], "西班牙军中教长区"),
    row("ESP-FIDELITAS-CROSS", "THIRD-CLASS", "菲德利塔斯十字章", "Cruz Fidélitas", "2007-07-25设立；2013年修订", "三等十字章", [("page_233_image_02.png", "完整正面")], "西班牙军中教长区"),
    row("ESP-FIDELITAS-CROSS", "HONOUR-CROSS", "菲德利塔斯十字章", "Cruz Fidélitas", "2007-07-25设立；2013年修订", "荣誉十字章", [("page_233_image_03.png", "完整正面")], "西班牙军中教长区"),
    row("ESP-VIRGIN-PILAR-GUARDIA-CIVIL-CENTENARY", "STANDARD", "皮拉尔圣母任国民警卫队主保百年纪念章", "Medalla conmemorativa del Centenario de la Proclamación de la Virgen del Pilar como Patrona de la Guardia Civil", "2012-10-12设立", "标准型；完整章体、王冠、悬挂结构与绶带", [("page_235_image_00.png", "完整正面")], "西班牙军中教长区"),
    row("ESP-SAINT-TERESA-INTENDANCE-CENTENARY", "STANDARD", "圣德肋撒任陆军军需部队主保百年纪念十字章", "Cruz conmemorativa del Centenario de Santa Teresa de Jesús como Patrona del Cuerpo y Tropas de Intendencia", "2014-10-15设立", "标准十字章；同一实物正背面；来源称十字／司令章两种佩戴方式属于同一纪念十字章", [("page_236_image_00.png", "正面"), ("page_236_image_01.png", "背面")], "西班牙军中教长区"),
    row("ESP-SAINT-BARBARA-ARTILLERY-QUINCENTENARY", "STANDARD", "圣芭芭拉任炮兵主保五百周年纪念章", "Medalla conmemorativa del Quinto Centenario de la Proclamación de Santa Bárbara como Patrona del Arma de Artillería", "2021-12-04设立", "标准型；完整椭圆章体、王冠、炮饰与红黑绶带", [("page_237_image_00.png", "完整正面")], "西班牙军中教长区"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    public, images = [], []
    for record in RECORDS:
        specs = record.pop("_images")
        for i, (src_name, label) in enumerate(specs, 1):
            src = SRC / src_name
            dest = OUT / f"{record['id'].lower()}-{i}.png"
            shutil.copyfile(src, dest)
            with Image.open(dest) as image:
                width, height = image.size
                image.verify()
            images.append({"view_key": record["views"][i-1]["key"], "label": label, "local_path": dest.relative_to(ROOT).as_posix(), "source_page": SOURCE_PAGE, "source_pdf": "sources/books/spain/boe_2025_las_ordenes_y_condecoraciones_militares_del_reino_de_espana.pdf", "source_pdf_page": int(src_name.split("_")[1]), "width": width, "height": height, "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(), "rights": "BOE 2025 volume states CC BY-NC-ND 4.0; individual photographs may have additional rights. Offline research catalogue only."})
        public.append(record)
    payload = {"as_of": "2026-09-26", "volume": "西班牙机构与军中教长区奖励（BOE 2025专题图录）", "records": public}
    families = len({r["family"] for r in public})
    manifest = {"volume": payload["volume"], "as_of": payload["as_of"], "records_file": VOLUME.relative_to(ROOT).as_posix(), "image_directory": OUT.relative_to(ROOT).as_posix() + "/", "counts": {"distinct_award_families": families, "variant_rows": len(public), "complete_image_files": len(images), "physical_photo_views": len(images)}, "source": {"source_id": SOURCE_ID, "title": "Las órdenes y condecoraciones militares del Reino de España", "institution": "Agencia Estatal Boletín Oficial del Estado", "year": 2025, "catalogue_url": SOURCE_PAGE, "processed_pdf_pages": [222, 223, 224, 225, 231, 232, 233, 234, 235, 236, 237, 238], "rights_note": "Offline research use; retain source credits and the volume's CC BY-NC-ND notice."}, "images": images}
    VOLUME.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {families} families, {len(public)} variants, {len(images)} images")


if __name__ == "__main__":
    main()
