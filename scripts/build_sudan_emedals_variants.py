"""Publish reviewed Republic of Sudan variants from eMedals."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/raw/sudan_emedals"
DEST = ROOT / "assets/images/sudan_emedals"
VOLUME = ROOT / "data/volumes/sudan_emedals_variants.json"
MANIFEST = ROOT / "data/volumes/sudan_emedals_variants_manifest.json"
RIGHTS = "eMedals sales archive photograph; retained for offline research catalogue use subject to source terms"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    images: list[dict] = []

    def make_crop(source_name: str, target_name: str, box: tuple[int, int, int, int]) -> str:
        target = RAW / target_name
        with Image.open(RAW / source_name) as image:
            image.crop(box).save(target, quality=95)
        return target_name

    def add_record(*, record_id: str, family: str, name: str, original: str, date: str,
                   variant: str, source_id: str, source_page: str,
                   selected: list[tuple[str, str, str] | tuple[str, str, str, str]], supersedes_id: str | None = None) -> None:
        views = []
        for number, selection in enumerate(selected, start=1):
            source_name, target_name, label = selection[:3]
            source_original_name = selection[3] if len(selection) == 4 else source_name
            source = RAW / source_name
            target = DEST / target_name
            shutil.copy2(source, target)
            with Image.open(target) as image:
                width, height = image.size
                image.verify()
            key = f"{record_id}-VIEW-{number}"
            views.append({"key": key, "label": label})
            images.append({
                "key": key, "record_id": record_id, "view_key": key,
                "local_path": target.relative_to(ROOT).as_posix(),
                "source_id": source_id, "source_page": source_page,
                "source_original_url": f"https://www.emedals.com/cdn/shop/files/{source_original_name}?width=1946",
                "image_kind": "object_photo", "width": width, "height": height,
                "sha256": digest(target),
                "visual_check": "complete named grade/component retained; no ribbon-only or cropped preview image",
                "rights_note": RIGHTS,
            })
        record = {
            "id": record_id, "family": family, "country_zh": "苏丹", "name": name,
            "original": original, "date": date, "variant": variant, "views": views,
            "source_ids": [source_id], "image_kind": "object_photo", "html_eligible": True,
        }
        if supersedes_id:
            record["supersedes_id"] = supersedes_id
        records.append(record)

    add_record(
        record_id="SDN-EMEDALS-W6054-POLICE-LDSM",
        family="MENA7-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL-FOR-POLICE",
        name="长期优秀服务奖章", original="Police Long and Distinguished Service Medal",
        date="苏丹共和国时期",
        variant="警察版；银质；原绶带；边缘标记 SILVER；直径36.2毫米；同一实物完整正反面",
        source_id="emedals-w6054",
        source_page="https://www.emedals.com/products/sudan-republic-a-police-long-and-distinguished-service-medal-w6054",
        selected=[("m19_18988.jpg", "police_long_distinguished_service_1.jpg", "完整实物正面"),
                  ("m19_18989.jpg", "police_long_distinguished_service_2.jpg", "完整实物背面")],
    )
    add_record(
        record_id="SDN-EMEDALS-W6057-ARMY-LDSM",
        family="MENA7-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL-FOR-POLICE",
        name="长期优秀服务奖章", original="Army Long and Distinguished Service Medal",
        date="苏丹共和国时期",
        variant="陆军版；银质；原黑白条纹绶带；边缘标记 SILVER；直径36.2毫米；同一实物完整正反面",
        source_id="emedals-w6057",
        source_page="https://www.emedals.com/products/sudan-republic-an-army-long-and-distinguished-service-medal-w6057",
        selected=[("m19_19001.jpg", "army_long_distinguished_service_1.jpg", "完整实物正面"),
                  ("m19_19002.jpg", "army_long_distinguished_service_2.jpg", "完整实物背面")],
        supersedes_id="SDN-MB-PENDING-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL-FOR-ARMY",
    )
    add_record(
        record_id="SDN-EMEDALS-W0031-REPUBLIC-I-STAR",
        family="MENA7-ORDER-OF-THE-REPUBLIC",
        name="苏丹共和国勋章", original="Order of the Republic",
        date="1961年11月16日设立；约1960年代制造",
        variant="一等大绶星章；银质珐琅；Garrard伦敦制；直径96毫米；同一实物完整正反面",
        source_id="emedals-w0031",
        source_page="https://www.emedals.com/products/sudan-order-of-the-republic-w0031",
        selected=[("io126002.jpg", "order_republic_i_star_front.jpg", "一等星章完整正面"),
                  ("io126001.jpg", "order_republic_i_star_reverse.jpg", "一等星章完整背面")],
        supersedes_id="SDN-MB-PENDING-ORDER-OF-THE-REPUBLIC-I-CLASS",
    )
    add_record(
        record_id="SDN-EMEDALS-M0620-13-REPUBLIC-II-SET",
        family="MENA7-ORDER-OF-THE-REPUBLIC",
        name="苏丹共和国勋章", original="Order of the Republic, Grand Officer's Set",
        date="1961年11月16日设立；约1960年代制造",
        variant="二等大军官套组；Garrard制；颈章完整正反面及星章完整正面",
        source_id="emedals-m0620-13",
        source_page="https://www.emedals.com/products/sudan-republic-an-order-of-the-republic-grand-officers-set-by-garrard-co-c1960-m0620-13",
        selected=[("MNC4529_6e286626-5268-4dc4-bbe9-13091e698664.jpg", "order_republic_ii_badge_front.jpg", "二等颈章完整正面"),
                  ("MNC4531_6e54e9fb-e9a3-413b-b209-5e6f7d22ca31.jpg", "order_republic_ii_badge_reverse.jpg", "二等颈章完整背面"),
                  ("MNC4532_f65f5a12-35a0-4f4b-89cc-798024783dbd.jpg", "order_republic_ii_star_front.jpg", "二等星章完整正面")],
    )
    add_record(
        record_id="SDN-EMEDALS-W8564-REPUBLIC-III-COMMANDER",
        family="MENA7-ORDER-OF-THE-REPUBLIC",
        name="苏丹共和国勋章", original="Order of the Republic, Commander",
        date="1961年11月16日设立；约1960年代制造",
        variant="三等指挥官颈章；Garrard制；60.9×86.5毫米；原绶带；同一实物完整正反面",
        source_id="emedals-w8564",
        source_page="https://www.emedals.com/products/sudan-republic-an-order-of-the-republic-commander-by-garrard-co-c1960-w8564",
        selected=[("eMedals_W8564_7.jpg", "order_republic_iii_front.jpg", "三等颈章完整正面"),
                  ("eMedals_W8564_9.jpg", "order_republic_iii_reverse.jpg", "三等颈章完整背面")],
        supersedes_id="SDN-MB-PENDING-ORDER-OF-THE-REPUBLIC-III-CLASS",
    )

    add_record(
        record_id="SDN-EMEDALS-W1625-REPUBLIC-I-STAR-1959",
        family="MENA7-ORDER-OF-THE-REPUBLIC",
        name="苏丹共和国勋章", original="Order of the Sudanese Republic",
        date="1959年制造；1961年11月16日正式设立",
        variant="一等大绶星章；银质珐琅；Garrard & Co. Ltd伯明翰制；1959年英国检验印；直径96毫米；同一实物完整正反面",
        source_id="emedals-w1625",
        source_page="https://www.emedals.com/products/an-english-made-order-of-the-sudanese-republic-w1625",
        selected=[("W1625_04.jpg", "order_republic_i_star_1959_front.jpg", "1959年制一等星章完整正面"),
                  ("W1625_05.jpg", "order_republic_i_star_1959_reverse.jpg", "1959年制一等星章完整背面")],
    )

    conscientious = [
        ("I", "金色一级（银鎏金）", (45, 35, 355, 725)),
        ("II", "银色二级（磨砂银）", (345, 35, 655, 725)),
        ("III", "铜色三级（铜质）", (640, 35, 955, 725)),
    ]
    for number, (roman, variant_text, box) in enumerate(conscientious, start=1):
        front = make_crop("W7547RL1_01.jpg", f"W7547RL1_{roman}_front_crop.jpg", box)
        reverse = make_crop("W7547RL1_02.jpg", f"W7547RL1_{roman}_reverse_crop.jpg", box)
        add_record(
            record_id=f"SDN-EMEDALS-W7547-CONSCIENTIOUS-{roman}",
            family="SDN-MB-CONSCIENTIOUS-WORK-MEDAL",
            name="尽职工作奖章", original="Medal for Conscientious Work / وسام العمل الجاد",
            date="苏丹共和国时期",
            variant=f"{variant_text}；直径36.5毫米；由同一套组三章合照裁取；本章完整正反面",
            source_id="emedals-w7547rl1",
            source_page="https://www.emedals.com/products/sudan-republic-a-set-of-three-medals-for-conscientious-work-w7547rl1",
            selected=[(front, f"conscientious_{number}_front.jpg", f"{variant_text}完整正面", "ai1_0969_1.jpg"),
                      (reverse, f"conscientious_{number}_reverse.jpg", f"{variant_text}完整背面", "ai1_0970_1.jpg")],
            supersedes_id=f"SDN-MB-PENDING-MEDAL-FOR-CONSCIENTIOUS-WORK-{roman}-CLASS",
        )

    add_record(
        record_id="SDN-EMEDALS-W6371-SPORT-II",
        family="MENA7-ORDER-OF-SPORT-IN-SILVER",
        name="体育勋章", original="Order of Sport",
        date="苏丹共和国时期",
        variant="二等功绩章；银质；45.5×62毫米（含国徽悬挂）；原绶带；同一实物完整正反面",
        source_id="emedals-w6371",
        source_page="https://www.emedals.com/products/sudan-republic-an-order-of-sport-ii-class-merit-medal-w6371",
        selected=[("W6371_01.jpg", "order_sport_ii_front.jpg", "二等功绩章完整正面"),
                  ("W6371_03.jpg", "order_sport_ii_reverse.jpg", "二等功绩章完整背面")],
    )

    add_record(
        record_id="SDN-EMEDALS-W8804-TWO-NILES-I-SPINK",
        family="MENA7-ORDER-OF-THE-TWO-NILES",
        name="两尼罗河勋章", original="Order of the Two Niles / وسام النيلين",
        date="1961年11月16日设立；约1965年版",
        variant="一等大绶章；银质珐琅；Spink & Son制式；58.56×83毫米；原颈绶；同一实物完整正反面",
        source_id="emedals-w8804",
        source_page="https://www.emedals.com/products/sudan-republic-order-of-the-two-niles-i-class-grand-badge-by-spink-son-ltd-c1965-w8804",
        selected=[("W8804_01.jpg", "two_niles_i_spink_front.jpg", "一等大绶章完整正面"),
                  ("W8804_02.jpg", "two_niles_i_spink_reverse.jpg", "一等大绶章完整背面")],
    )

    police_order_boxes = {
        "FULL": ((145, 20, 575, 735), (145, 20, 575, 735), "全尺寸章", "40.7×53毫米"),
        "MINI": ((535, 135, 755, 620), (535, 120, 755, 610), "微型章", "20×28.5毫米"),
    }
    for code, (front_box, reverse_box, label, size) in police_order_boxes.items():
        front = make_crop("W6190_02.jpg", f"W6190_{code}_front_crop.jpg", front_box)
        reverse = make_crop("W6190_03.jpg", f"W6190_{code}_reverse_crop.jpg", reverse_box)
        add_record(
            record_id=f"SDN-EMEDALS-W6190-POLICE-LDSO-{code}",
            family="SDN-EMEDALS-FAM-POLICE-LONG-DISTINGUISHED-SERVICE-ORDER",
            name="警察长期杰出服务勋章", original="Police Long and Distinguished Service Order",
            date="苏丹共和国时期",
            variant=f"{label}；银质徽章配银鎏金星底；{size}；原绶带；由同一套组合照裁取；完整正反面",
            source_id="emedals-w6190",
            source_page="https://www.emedals.com/products/sudan-republic-police-long-and-distinguished-service-order-w6190",
            selected=[(front, f"police_ldso_{code.lower()}_front.jpg", f"{label}完整正面", "m19_21194.jpg"),
                      (reverse, f"police_ldso_{code.lower()}_reverse.jpg", f"{label}完整背面", "m19_21195.jpg")],
        )

    grouped_orders = [
        ("CIVIL", "MENA7-ORDER-OF-CIVIL-ACCOMPLISHMENT", "苏丹民事成就勋章", "Order of Civil Accomplishment",
         "Spink & Son伦敦制；鎏金铜与多色珐琅；96.3×96.2毫米；原绶带", (0, 0, 520, 750)),
        ("POLITICAL", "SDN-WAWARDS-ORDER-OF-POLITICAL-ACCOMPLISHMENT", "政治成就勋章", "Order of Political Accomplishment",
         "英国制造式（来源未标厂）；银质、黑色珐琅及鎏金中央圆盘；约100×120毫米（含悬挂横杆）", (475, 0, 1000, 750)),
    ]
    for code, family, name, original, details, box in grouped_orders:
        front = make_crop("M0620-10_02.jpg", f"M0620-10_{code}_front_crop.jpg", box)
        reverse = make_crop("M0620-10_03.jpg", f"M0620-10_{code}_reverse_crop.jpg", box)
        add_record(
            record_id=f"SDN-EMEDALS-M0620-10-{code}",
            family=family, name=name, original=original,
            date="苏丹共和国时期",
            variant=f"{details}；由两章合照裁取；同一实物完整正反面",
            source_id="emedals-m0620-10",
            source_page="https://www.emedals.com/products/two-orders-and-decorations-m0620-10",
            selected=[(front, f"m0620_10_{code.lower()}_front.jpg", "完整实物正面", "MNC4450_ffd32d50-46d8-46a9-88da-a7abd77478da.jpg"),
                      (reverse, f"m0620_10_{code.lower()}_reverse.jpg", "完整实物背面", "MNC4452_ab2f3d50-b050-4158-a508-7fa6a1bff1d2.jpg")],
        )

    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹：eMedals实物档案", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "source": "eMedals Sudan item pages", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"published {len(records)} Sudan eMedals variants with {len(images)} complete object views")


if __name__ == "__main__":
    main()
