from __future__ import annotations

import hashlib
import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/books/ireland_defence_forces_medals_2010.pdf"
SOURCE_URL = "https://www.military.ie/media/c0uhlm5x/df_medals_2010.pdf"
SOURCE_ID = "IE-DF-MEDALS-2010"
RAW_IMAGE_DIR = ROOT / "assets/raw/ireland_defence_forces_medals_2010"
IMAGE_DIR = ROOT / "assets/images/ireland_defence_forces_medals_2010"
RAW_CANDIDATE_PATH = ROOT / "data/raw_candidates/ireland/defence_forces_medals_2010.jsonl"
VOLUME_PATH = ROOT / "data/volumes/ireland_defence_forces_medals_2010.json"
MANIFEST_PATH = ROOT / "data/volumes/ireland_defence_forces_medals_2010_manifest.json"
MATRIX_PATH = ROOT / "data/source_atlas/ireland_defence_forces_medals_2010_source_matrix.json"
CHECKPOINT_PATH = ROOT / "data/checkpoints/ireland_defence_forces_medals_2010.json"
UNPICTURED_PATH = ROOT / "data/unpictured/ireland_defence_forces_medals_2010.json"
CONTACT_PATH = ROOT / "data/image_harvest/ireland_defence_forces_medals_2010/selected-objects-contact.jpg"

# On these three pages the mission clasp is a separate PDF layer.  The base
# embedded object therefore omits the identifying clasp; crop the fully rendered
# page instead and retain the exact pixel box.
PAGE_CROP_OVERRIDES: dict[tuple[int, int], tuple[int, int, int, int]] = {
    (75, 3): (565, 360, 800, 760),
    (77, 3): (565, 430, 800, 815),
    (78, 3): (565, 430, 800, 815),
}


@dataclass
class ViewSpec:
    page: int
    image_index: int
    label: str


@dataclass
class RecordSpec:
    family: str
    authority: str
    name: str
    original: str
    date: str
    variant: str
    views: list[ViewSpec]
    aliases: list[str] = field(default_factory=list)
    notes: str = ""


records: list[RecordSpec] = []


def add(
    family: str,
    authority: str,
    name: str,
    original: str,
    date: str,
    variant: str,
    page: int,
    image_indexes: list[int],
    labels: list[str] | None = None,
    aliases: list[str] | None = None,
    notes: str = "",
) -> None:
    if labels is None:
        labels = ["完整正面", "同页所示完整背面"][: len(image_indexes)]
    records.append(
        RecordSpec(
            family=family,
            authority=authority,
            name=name,
            original=original,
            date=date,
            variant=variant,
            views=[ViewSpec(page, index, label) for index, label in zip(image_indexes, labels)],
            aliases=aliases or [],
            notes=notes,
        )
    )


# Irish Defence Forces medals: one family per award, with classes, bars and service periods as variants.
add("IE-MIL-GALLANTRY", "爱尔兰国防军", "军事英勇奖章", "An Bonn Míleata Calmachta / The Military Medal for Gallantry", "1944年设立", "荣誉级（With Honour）；银质", 12, [0, 1])
add("IE-MIL-GALLANTRY", "爱尔兰国防军", "军事英勇奖章", "An Bonn Míleata Calmachta / The Military Medal for Gallantry", "1944年设立", "卓异级（With Distinction）；铜质", 13, [0, 1])
add("IE-MIL-GALLANTRY", "爱尔兰国防军", "军事英勇奖章", "An Bonn Míleata Calmachta / The Military Medal for Gallantry", "1944年设立", "功绩级（With Merit）；铜质", 14, [0, 1])

add("IE-DIST-SERVICE", "爱尔兰国防军", "卓越服役奖章", "An Bonn Seirbhíse Dearscna / The Distinguished Service Medal", "1964年2月18日设立", "荣誉级（With Honour）；银质", 16, [0, 1])
add("IE-DIST-SERVICE", "爱尔兰国防军", "卓越服役奖章", "An Bonn Seirbhíse Dearscna / The Distinguished Service Medal", "1964年2月18日设立", "卓异级（With Distinction）；铜质", 17, [0, 1])
add("IE-DIST-SERVICE", "爱尔兰国防军", "卓越服役奖章", "An Bonn Seirbhíse Dearscna / The Distinguished Service Medal", "1964年2月18日设立", "功绩级（With Merit）；铜质", 18, [0, 1])

add("IE-GOOD-CONDUCT", "爱尔兰国防军", "良好品行奖章", "An Bonn Dea-Iompair / The Good Conduct Medal", "1987年9月16日至1990年1月30日授予", "铜质；现已停授", 19, [0, 1])

add("IE-SERVICE", "爱尔兰国防军", "服役奖章", "An Bonn Seirbhíse / The Service Medal", "设立日期待考；2010年官方图册所载", "士官与士兵十年服役；纯圣帕特里克蓝绶带", 20, [0, 1])
add("IE-SERVICE", "爱尔兰国防军", "服役奖章", "An Bonn Seirbhíse / The Service Medal", "设立日期待考；2010年官方图册所载", "军官十五年服役／士官与士兵十五年服役；中央金色条纹绶带", 21, [0], ["完整正面"])
add("IE-SERVICE", "爱尔兰国防军", "服役奖章", "An Bonn Seirbhíse / The Service Medal", "设立日期待考；2010年官方图册所载", "军官二十年服役／士官与士兵十五年服役；加铜质服役条", 21, [1], ["完整正面"])

add("IE-FCA-SM-SERVICE", "爱尔兰国防军", "地方防卫军与海上志愿军服役奖章", "An Bonn Seirbhíse (FCÁ agus SM) / The Service Medal (FCÁ and SM)", "1961年6月设立", "七年服役；无服役条", 22, [0, 1])
add("IE-FCA-SM-SERVICE", "爱尔兰国防军", "地方防卫军与海上志愿军服役奖章", "An Bonn Seirbhíse (FCÁ agus SM) / The Service Medal (FCÁ and SM)", "1961年6月设立", "十二年服役；一道服役条", 23, [0], ["完整正面"])
add("IE-FCA-SM-SERVICE", "爱尔兰国防军", "地方防卫军与海上志愿军服役奖章", "An Bonn Seirbhíse (FCÁ agus SM) / The Service Medal (FCÁ and SM)", "1961年6月设立", "二十一年服役；两道服役条，上条数字“21”", 23, [1], ["完整正面"])

add("IE-EMERGENCY-SERVICE", "爱尔兰国防军及爱尔兰国家应急服务机构", "紧急状态服役奖章", "An Bonn Seirbhíse Éigeandála / The Emergency Service Medal", "1944年10月设立；认可1939年9月3日至1946年3月31日服役", "国防军／地方防卫军代表型；红绶带中央两道白纹", 24, [0, 1])
add("IE-EMERGENCY-SERVICE", "爱尔兰国防军及爱尔兰国家应急服务机构", "紧急状态服役奖章", "An Bonn Seirbhíse Éigeandála / The Emergency Service Medal", "1944年10月设立；认可1939年9月3日至1946年3月31日服役", "其他机构代表型；红绶带中央一道白纹", 25, [0], ["完整正面"])
add("IE-EMERGENCY-SERVICE", "爱尔兰国防军及爱尔兰国家应急服务机构", "紧急状态服役奖章", "An Bonn Seirbhíse Éigeandála / The Emergency Service Medal", "1944年10月设立；认可1939年9月3日至1946年3月31日服役", "其他机构代表型；加1939—1946额外两年服役条", 25, [1], ["完整正面"])

add("IE-UN-PEACEKEEPERS", "爱尔兰国防军", "联合国维和人员奖章", "An Bonn Chosantóirí Síochána na Náisiún Aontaithe / The United Nations Peacekeepers Medal", "1989年设立", "银质；爱尔兰国防军海外维和服役奖章", 26, [0, 1])
add("IE-MILITARY-STAR", "爱尔兰国防军", "军事之星", "An Réalt Míleata / The Military Star", "设立日期待考；追溯适用于1958年6月28日后符合条件者", "铜质八角星；追授阵亡人员", 27, [0, 1])


# UN Medal: mission ribbons remain variants of one United Nations Medal family.
un_variants = [
    (31, "UNTSO", "联合国停战监督组织任务型", "United Nations Truce Supervision Organisation", "1948年"),
    (32, "UNMOGIP", "联合国驻印度和巴基斯坦军事观察组任务型", "United Nations Military Observer Group India-Pakistan", "1949年"),
    (33, "UNOGIL", "联合国黎巴嫩观察组任务型", "United Nations Observer Group in Lebanon", "1958年"),
    (34, "ONUC", "联合国刚果行动任务型；1963年后绿色主纹绶带", "United Nations Operation in the Congo", "1960年；图示1963年后绶带"),
    (35, "UNTEA/UNSF", "联合国西新几内亚临时行政当局／安全部队任务型", "United Nations Temporary Executive Authority / United Nations Security Force in West New Guinea", "1962年"),
    (36, "UNFICYP", "联合国驻塞浦路斯维持和平部队任务型", "United Nations Peacekeeping Force in Cyprus", "1964年"),
    (37, "UNIPOM", "联合国印度－巴基斯坦观察团任务型", "United Nations India-Pakistan Observation Mission", "1965年"),
    (38, "UNEF II", "联合国第二期紧急部队任务型", "United Nations Emergency Force II", "1973年"),
    (39, "UNDOF", "联合国脱离接触观察员部队任务型", "United Nations Disengagement Observer Force", "1974年"),
    (40, "UNIFIL", "联合国驻黎巴嫩临时部队任务型", "United Nations Interim Force in Lebanon", "1978年"),
    (41, "UNHQ", "联合国总部服务任务型", "United Nations Headquarters New York", "1979年"),
    (42, "UNIIMOG", "联合国伊朗－伊拉克军事观察团任务型", "United Nations Iran-Iraq Military Observer Group", "1988年"),
    (43, "UNTAG", "联合国过渡时期援助团任务型", "United Nations Transition Assistance Group", "1989年"),
    (44, "ONUCA", "联合国中美洲观察团任务型", "United Nations Observer Group in Central America", "1989年"),
    (45, "UNAVEM II", "联合国第二期安哥拉核查团任务型", "United Nations Angola Verification Mission II", "1991年"),
    (46, "UNSCOM", "联合国特别委员会任务型", "United Nations Special Commission", "1991年"),
    (47, "MINURSO", "联合国西撒哈拉全民投票特派团任务型", "United Nations Mission for the Referendum in Western Sahara", "1991年"),
    (48, "UNIKOM", "联合国伊拉克－科威特观察团任务型", "United Nations Iraq-Kuwait Observer Mission", "1991年"),
    (49, "UNAMIC", "联合国柬埔寨先遣团任务型", "United Nations Advance Mission in Cambodia", "1991年"),
    (50, "ONUSAL", "联合国萨尔瓦多观察团任务型", "United Nations Observer Mission in El Salvador", "1991年"),
    (51, "UNTAC", "联合国柬埔寨过渡时期权力机构任务型", "United Nations Transitional Authority in Cambodia", "1992年"),
    (52, "UNPROFOR", "联合国保护部队任务型", "United Nations Protection Force", "1992年"),
    (53, "UNOSOM II", "联合国第二期索马里行动任务型", "United Nations Operation in Somalia II", "1992—1993年"),
    (54, "UNSMA", "联合国阿富汗特别团任务型", "United Nations Special Mission in Afghanistan", "1993年"),
    (55, "UNMIH", "联合国海地特派团任务型", "United Nations Mission in Haiti", "1993年"),
    (56, "UNAMIR", "联合国卢旺达援助团任务型", "United Nations Assistance Mission for Rwanda", "1994年"),
    (57, "UNPREDEP", "联合国预防性部署部队任务型", "United Nations Preventive Deployment Force", "1995年"),
    (58, "UNMOP", "联合国普雷维拉卡观察团任务型", "United Nations Mission of Observers in Prevlaka", "1996年"),
    (59, "UNTAES", "联合国东斯拉沃尼亚过渡行政当局任务型", "United Nations Transitional Administration for Eastern Slavonia, Baranja and Western Sirmium", "1996年"),
    (60, "UNMIK", "联合国科索沃临时行政当局特派团任务型", "United Nations Interim Administration Mission in Kosovo", "1999年"),
    (61, "UNAMET/UNTAET/UNMISET", "联合国东帝汶三任务共用绶带型", "United Nations Assistance Mission in East Timor / Transitional Administration in East Timor / Mission of Support in East Timor", "1999—2002年"),
    (62, "MONUC", "联合国刚果民主共和国特派团任务型", "United Nations Organization Mission in the Democratic Republic of the Congo", "2000年"),
    (63, "UNMEE", "联合国埃塞俄比亚和厄立特里亚特派团任务型", "United Nations Mission in Ethiopia and Eritrea", "2000年"),
    (64, "UNMIL", "联合国利比里亚特派团任务型", "United Nations Mission in Liberia", "2003年"),
    (65, "MINUCI/ONUCI", "联合国科特迪瓦特派团／行动任务型；图示ONUCI较窄中央三色纹", "United Nations Mission / Operation in Côte d’Ivoire", "2003—2004年"),
    (66, "MINURCAT II", "联合国中非共和国和乍得特派团第二期任务型", "United Nations Mission in the Central African Republic and Chad II", "2009年"),
]
for page, acronym, variant, mission, date in un_variants:
    add(
        "UN-MEDAL",
        "联合国",
        "联合国奖章",
        "United Nations Medal",
        date,
        f"{variant}（{acronym}）；铜质标准章体，任务专用绶带",
        page,
        [1, 0],
        ["完整正面", "同页所示完整背面"],
        [mission, acronym],
    )

add("UN-DAG-HAMMARSKJOLD", "联合国", "达格·哈马舍尔德奖章", "Dag Hammarskjöld Medal", "1997年7月22日设立", "追授因维和行动殉职人员；玻璃晶体与金属片组合", 67, [0], ["完整正面／整体图"])


# European Community / European Union medals.
add("EU-ECMM", "欧洲共同体", "欧洲共同体监察团奖章", "European Community Monitor Mission Medal", "1991年起", "银色合金；图示“EC Monitor Mission”铭文型", 72, [1, 0])
add("EU-EUMM", "欧洲联盟", "欧洲联盟监察团奖章", "European Union Monitoring Mission Medal", "2000—2007年", "银色合金；EU中央铭文型", 73, [1, 0])

esdp_variants = [
    (75, "ARTEMIS", "2003年", True, True),
    (76, "ALTHEA", "2004年", True, False),
    (77, "AMIS", "2005—2007年", True, True),
    (78, "AMM", "2005—2006年", True, True),
    (79, "EUFOR RD CONGO", "2006年", True, True),
    (80, "EUFOR TCHAD/RCA", "2008—2009年", True, True),
    (81, "ATALANTA", "2008年起", False, True),
]
for page, clasp, date, has_force, has_support in esdp_variants:
    if has_force:
        indexes = [1, 0] if page == 75 else [1]
        labels = ["完整正面", "同页所示完整背面"] if page == 75 else ["完整正面"]
        add(
            "EU-ESDP-SERVICE",
            "欧洲联盟",
            "欧洲安全与防务政策服役奖章",
            "European Security and Defence Policy Service Medal",
            date,
            f"任务区／部队总部型；蓝黄绶带；“{clasp}”任务扣饰",
            page,
            indexes,
            labels,
        )
    if has_support:
        indexes = [3, 2] if page == 75 else ([1, 0] if page == 81 else [3])
        labels = ["完整正面", "同页所示完整背面"] if page in (75, 81) else ["完整正面"]
        add(
            "EU-ESDP-SERVICE",
            "欧洲联盟",
            "欧洲安全与防务政策服役奖章",
            "European Security and Defence Policy Service Medal",
            date,
            f"作战总部／计划支援型；蓝白绶带；“{clasp}”任务扣饰",
            page,
            indexes,
            labels,
        )


# UN-mandated but non-UN awards.
add("ICFY-MEDAL", "前南斯拉夫问题国际会议", "前南斯拉夫问题国际会议奖章", "International Conference on the Former Yugoslavia Medal", "1992年起", "监察任务服役奖章", 84, [0, 1])
add("NATO-MEDAL", "北大西洋公约组织", "北约奖章", "NATO Medal", "1997年起", "SFOR；“Former Yugoslavia”扣饰", 85, [1, 0])
add("NATO-MEDAL", "北大西洋公约组织", "北约奖章", "NATO Medal", "1999年起", "KFOR；“Kosovo”扣饰", 86, [1, 0])
add("INTERFET-MEDAL", "东帝汶国际部队", "东帝汶国际部队奖章", "International Force East Timor Medal / INTERFET Medal", "1999—2000年", "标准型", 87, [0, 1])
add("NATO-MEDAL", "北大西洋公约组织", "北约奖章", "NATO Medal", "2002年起", "非第五条款奖章；巴尔干服役扣饰", 88, [1, 0])
add("NATO-MEDAL", "北大西洋公约组织", "北约奖章", "NATO Medal", "2002年起", "非第五条款奖章；ISAF扣饰", 90, [1, 0])


# Irish revolutionary / War of Independence awards.
add("IE-1916-MEDAL", "爱尔兰", "1916年奖章", "An Bonn 1916 / The 1916 Medal", "为1916年4月23日起复活节起义参战者设", "标准型；铜质", 94, [0, 1])
add("IE-1917-1921-SERVICE", "爱尔兰", "1917—1921年服役奖章", "An Bonn Seirbhíse (1917-1921) / The Service Medal (1917-1921)", "表彰1917—1921年独立斗争服役", "带“Comrac”战斗服役条型", 95, [1, 0])
add("IE-1916-SURVIVORS", "爱尔兰", "1916年幸存者奖章", "An Bonn Marthanóirí 1916 / The 1916 Survivors' Medal", "1966年设立", "银鎏金；仅授予仍在世的1916年复活节起义参与者", 96, [0, 1])
add("IE-TRUCE-ANNIVERSARY", "爱尔兰", "停战周年纪念奖章（1921）", "An Bonn Cuimhneacháin Sos Cogaidh (1921) / The Truce (1921) Anniversary Medal", "1971年设立", "铜质；授予1971年7月11日仍在世且已获1917—1921年服役奖章者", 97, [0, 1])


unpictured: list[dict[str, Any]] = [
    {
        "family": "IE-1917-1921-SERVICE",
        "name": "1917—1921年服役奖章",
        "original": "The Service Medal (1917-1921)",
        "variant": "无战斗服役条型",
        "pdf_page": 95,
        "reason": "官方图册文字明确列为第二类别，但本页只配带条型完整实物图。",
    },
    {
        "family": "UN-MEDAL",
        "name": "联合国奖章",
        "original": "United Nations Medal - ONUC",
        "variant": "ONUC 1960—1963早期型；UNTSO式绶带加“CONGO”扣饰",
        "pdf_page": 34,
        "reason": "本页仅给绶带／扣饰局部图，依项目规则不作为正文完整章体图。",
    },
    {
        "family": "EU-ECMM",
        "name": "欧洲共同体监察团奖章",
        "original": "European Community Monitor Mission Medal",
        "variant": "“EC Task Force”中央铭文型",
        "pdf_page": 72,
        "reason": "文字说明存在该铭文型，但本页完整实物图为另一铭文型。",
    },
]

emergency_issues = [
    "Na Fórsaí Cosanta（常备陆军、空军与海军）",
    "An Slua Muirí（海上志愿预备役）",
    "An Fórsa Cosanta Áitiúil（地方防卫军）",
    "Fórsa na nÓglach（第二线预备役专业人员）",
    "26ú Cathlán（第26营）",
    "Seirbhís Áltranais an Airm（陆军护理服务）",
    "An tSeirbhís Séiplíneachta（随军牧师服务）",
    "Caomhnóirí Áitiúla（地方保安部队）",
    "爱尔兰红十字会志愿援助科",
    "爱尔兰红十字会急救科",
    "防空袭预防组织",
]
for issue in emergency_issues:
    unpictured.append(
        {
            "family": "IE-EMERGENCY-SERVICE",
            "name": "紧急状态服役奖章",
            "original": "The Emergency Service Medal",
            "variant": f"机构背铭版：{issue}",
            "pdf_page": 25,
            "reason": "图册列明十一种机构背铭，但仅配两种绶带组的代表性正面和一枚未逐项标识的背面。",
        }
    )


def ensure_dirs() -> None:
    for path in (
        RAW_IMAGE_DIR,
        IMAGE_DIR,
        RAW_CANDIDATE_PATH.parent,
        VOLUME_PATH.parent,
        MATRIX_PATH.parent,
        CHECKPOINT_PATH.parent,
        UNPICTURED_PATH.parent,
        CONTACT_PATH.parent,
    ):
        path.mkdir(parents=True, exist_ok=True)
    for directory in (RAW_IMAGE_DIR, IMAGE_DIR):
        for path in directory.iterdir():
            if path.is_file():
                path.unlink()


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        image.verify()
    return {
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "content_type": mimetypes.guess_type(path.name)[0] or "image/png",
    }


def main() -> None:
    ensure_dirs()
    reader = PdfReader(PDF)
    out_records: list[dict[str, Any]] = []
    manifest_images: list[dict[str, Any]] = []
    raw_candidates: list[dict[str, Any]] = []
    selected_paths: list[Path] = []
    seen_payloads: dict[str, str] = {}

    for sequence, spec in enumerate(records, start=1):
        record_id = f"IE-DF-2010-{sequence:03d}"
        views: list[dict[str, str]] = []
        for view_no, view in enumerate(spec.views, start=1):
            page_images = list(reader.pages[view.page - 1].images)
            source_image = page_images[view.image_index]
            source_ext = Path(source_image.name).suffix.lower() or ".bin"
            raw_name = f"p{view.page:03d}-obj{view.image_index:02d}-{record_id.lower()}-v{view_no:02d}{source_ext}"
            raw_path = RAW_IMAGE_DIR / raw_name
            raw_path.write_bytes(source_image.data)
            output_name = f"{record_id.lower()}-v{view_no:02d}.png"
            output_path = IMAGE_DIR / output_name
            crop_box = PAGE_CROP_OVERRIDES.get((view.page, view.image_index))
            if crop_box:
                rendered_page = ROOT / f"sources/pages/ireland_defence_forces_medals_2010/page-{view.page:03d}.jpg"
                image = Image.open(rendered_page).convert("RGBA").crop(crop_box)
            else:
                image = source_image.image.convert("RGBA")
            image.save(output_path, format="PNG", optimize=True)
            info = file_info(output_path)
            view_key = f"{record_id}-V{view_no:02d}"
            prior_view = seen_payloads.get(info["sha256"])
            if prior_view:
                output_path.unlink()
                continue
            seen_payloads[info["sha256"]] = view_key
            views.append({"key": view_key, "label": view.label})
            manifest_images.append(
                {
                    "view_key": view_key,
                    "local_path": output_path.relative_to(ROOT).as_posix(),
                    "raw_path": raw_path.relative_to(ROOT).as_posix(),
                    "source_page": f"{SOURCE_URL}#page={view.page}",
                    "image_page": f"{SOURCE_URL}#page={view.page}",
                    "original_url": SOURCE_URL,
                    "source_object": f"official PDF page {view.page}; embedded image object index {view.image_index} ({source_image.name})",
                    "pdf_page": view.page,
                    "crop_box": list(crop_box) if crop_box else None,
                    "extraction": "rendered page crop preserving composite clasp layer" if crop_box else "embedded image object; no page crop",
                    "image_kind": "爱尔兰国防军官方图册内嵌完整实物图；2010；低清参考",
                    "author_or_institution": "Óglaigh na hÉireann / Irish Defence Forces",
                    "license": "官方公开图册；未见逐图开放许可；本地研究使用",
                    **info,
                }
            )
            selected_paths.append(output_path)

        out_records.append(
            {
                "id": record_id,
                "family": spec.family,
                "awarding_authority": spec.authority,
                "name": spec.name,
                "original": spec.original,
                "date": spec.date,
                "variant": f"{spec.variant}；官方图册实物图·低清参考",
                "views": views,
                "source_ids": [SOURCE_ID],
            }
        )
        raw_candidates.append(
            {
                "source_id": SOURCE_ID,
                "candidate_id": record_id,
                "page_title": spec.original,
                "original_name": spec.original,
                "aliases": spec.aliases,
                "chinese_name": spec.name,
                "awarding_authority": spec.authority,
                "date_candidate": spec.date,
                "category": "formal_medal_or_decoration",
                "family_draft": spec.family,
                "grade_material_clues": spec.variant,
                "object_page": f"{SOURCE_URL}#page={spec.views[0].page}",
                "image_page": f"{SOURCE_URL}#page={spec.views[0].page}",
                "original_image_address": [
                    f"pdf-embedded:p{view.page}:object-index-{view.image_index}" for view in spec.views
                ],
                "local_images": [item["local_path"] for item in manifest_images if item["view_key"].startswith(record_id + "-")],
                "notes": spec.notes or "官方图册逐页核对；同种奖章的等级、任务绶带或扣饰归在同一family。",
                "status": "pictured_complete_object",
            }
        )

    for offset, candidate in enumerate(unpictured, start=1):
        raw_candidates.append(
            {
                "source_id": SOURCE_ID,
                "candidate_id": f"IE-DF-2010-U{offset:03d}",
                "page_title": candidate["original"],
                "original_name": candidate["original"],
                "aliases": [],
                "chinese_name": candidate["name"],
                "awarding_authority": "依family归属",
                "date_candidate": "见正文family日期",
                "category": "formal_medal_or_decoration",
                "family_draft": candidate["family"],
                "grade_material_clues": candidate["variant"],
                "object_page": f"{SOURCE_URL}#page={candidate['pdf_page']}",
                "image_page": None,
                "original_image_address": [],
                "local_images": [],
                "notes": candidate["reason"],
                "status": "recorded_unpictured",
            }
        )

    RAW_CANDIDATE_PATH.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in raw_candidates),
        encoding="utf-8",
    )
    save_json(
        VOLUME_PATH,
        {
            "as_of": "2026-09-29",
            "volume": "爱尔兰国防军2010年官方勋奖章图册整册归并草稿",
            "records": out_records,
            "unpictured_candidates": unpictured,
        },
    )
    save_json(
        MANIFEST_PATH,
        {
            "as_of": "2026-09-29",
            "source_id": SOURCE_ID,
            "source_pdf": PDF.relative_to(ROOT).as_posix(),
            "source_url": SOURCE_URL,
            "images": manifest_images,
            "validation": {
                "record_count": len(out_records),
                "family_count": len({item["family"] for item in out_records}),
                "decoded_image_count": len(manifest_images),
                "all_images_exist": all((ROOT / item["local_path"]).is_file() for item in manifest_images),
                "all_decoded": True,
                "unpictured_candidate_count": len(unpictured),
            },
        },
    )
    save_json(UNPICTURED_PATH, {"as_of": "2026-09-29", "source_id": SOURCE_ID, "items": unpictured})
    save_json(
        MATRIX_PATH,
        {
            "source_atlas_id": "ireland_defence_forces_medals_2010_source_matrix",
            "as_of": "2026-09-29",
            "scope": "爱尔兰国防军官方2010年勋奖章图册所载爱尔兰、联合国、欧盟、北约及授权任务正式奖章",
            "sources": [
                {
                    "id": SOURCE_ID,
                    "type": "official_defence_forces_book",
                    "language": "en/ga",
                    "scope": "全书109页；爱尔兰国防军奖章、联合国任务奖章、欧洲共同体／欧盟奖章、联合国授权任务奖章、独立战争奖章",
                    "date_coverage": "1916—2010",
                    "image_capability": f"{len(manifest_images)}张从PDF内嵌对象提取并转为PNG的完整实物图",
                    "pagination": "109-page PDF; pages 1-109 exhausted",
                    "download_method": "official direct PDF; full text extraction; page rendering; embedded image extraction",
                    "priority": 1,
                    "status": "completed_entire_book",
                    "last_checked": "2026-09-29",
                    "coverage_boundary": "第10—27页爱尔兰国防军奖章；第29—68页联合国奖章；第71—81页欧洲共同体／欧盟奖章；第83—91页联合国授权任务；第93—97页独立战争奖章；其余为封面、目录、佩戴规则、索引和参考。",
                }
            ],
            "counts": {"planned": 1, "completed": 1, "partial": 0, "blocked": 0, "not_started": 0},
            "next_action": "由主任务按授予机构分别归并到爱尔兰、联合国、欧洲联盟和北约分区，并对2010年以后新增或更名的奖章另作现行制度更新。",
        },
    )

    # Contact sheet for a final, row-level visual audit of every selected object image.
    thumb_w, thumb_h, label_h, columns = 190, 230, 28, 8
    rows = (len(selected_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (thumb_w * columns, (thumb_h + label_h) * rows), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(selected_paths):
        image = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", image.size, "white")
        bg.alpha_composite(image)
        rgb = bg.convert("RGB")
        rgb.thumbnail((thumb_w - 8, thumb_h - 8), Image.Resampling.LANCZOS)
        col, row = index % columns, index // columns
        x = col * thumb_w + (thumb_w - rgb.width) // 2
        y = row * (thumb_h + label_h) + label_h
        sheet.paste(rgb, (x, y))
        draw.text((col * thumb_w + 4, row * (thumb_h + label_h) + 5), path.stem, fill="black", font=font)
    sheet.save(CONTACT_PATH, quality=90)

    save_json(
        CHECKPOINT_PATH,
        {
            "checkpoint_id": "ireland_defence_forces_medals_2010",
            "as_of": "2026-09-29",
            "scope": "爱尔兰国防军官方《Medals of the Irish Defence Forces》2010年第一版整册扫描",
            "plan": [
                "穷尽官方PDF全部109页并保存逐页文本",
                "渲染全部109页并检查章节、对象页与排除页",
                "按授予机构与family归并等级、服役条、任务绶带和扣饰",
                "从PDF内嵌对象提取完整章体并保存页码、对象索引和原始文件",
                "登记文字明确但只有绶带局部或未配完整章体的版型",
            ],
            "source_counts": {"planned": 1, "completed": 1, "partial": 0, "blocked": 0, "not_started": 0},
            "counts": {
                "raw_candidates": len(raw_candidates),
                "merged_families": len({item["family"] for item in out_records}),
                "variants": len(out_records),
                "decoded_local_images": len(manifest_images),
                "unpictured_candidates": len(unpictured),
                "unresolved_candidates": 0,
            },
            "files": [
                RAW_CANDIDATE_PATH.relative_to(ROOT).as_posix(),
                VOLUME_PATH.relative_to(ROOT).as_posix(),
                MANIFEST_PATH.relative_to(ROOT).as_posix(),
                MATRIX_PATH.relative_to(ROOT).as_posix(),
                UNPICTURED_PATH.relative_to(ROOT).as_posix(),
                IMAGE_DIR.relative_to(ROOT).as_posix() + "/",
                RAW_IMAGE_DIR.relative_to(ROOT).as_posix() + "/",
                PDF.relative_to(ROOT).as_posix(),
                "sources/pages/ireland_defence_forces_medals_2010/",
                CONTACT_PATH.relative_to(ROOT).as_posix(),
            ],
            "status": "official_book_exhausted_isolated_draft_ready",
            "next_action": "主任务审阅contact sheet后按授予机构合并，不把联合国、欧盟或北约奖章误归爱尔兰国家奖励。",
            "review": {
                "rendered_pages_reviewed": 109,
                "excluded": ["仅绶带图", "勋略", "佩戴照", "肖像", "证书", "封面拼图", "裁断章体"],
                "rights": "官方公开图册未见逐图开放许可；本地研究使用，保留来源与页码。",
            },
        },
    )
    print(
        json.dumps(
            {
                "records": len(out_records),
                "families": len({item["family"] for item in out_records}),
                "images": len(manifest_images),
                "unpictured": len(unpictured),
                "raw_candidates": len(raw_candidates),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
