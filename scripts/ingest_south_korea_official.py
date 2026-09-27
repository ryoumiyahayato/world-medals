"""Build the South Korea official orders/decorations volume from sanghun.go.kr plates.

The official order plates are preserved in the earlier East Asia source batch.  This
script extracts one complete labelled panel per official grade without inventing
detail, and copies the twelve official decoration plates without resampling.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ORDER_SOURCE = ROOT / "assets/images/east_asia_gap_round1_2026-09-26"
MEDAL_SOURCE = ROOT / "sources/cache/sanghun_korea/images"
OUTPUT = ROOT / "assets/images/south_korea_official_complete_2026-09-27"
VOLUME = ROOT / "data/volumes/south_korea_official_complete_2026-09-27.json"
MANIFEST = ROOT / "data/volumes/south_korea_official_complete_2026-09-27_manifest.json"
RAW = ROOT / "data/raw_candidates/sanghun_south_korea_official.jsonl"

ORDER_PAGE = "https://www.sanghun.go.kr/nation/hunjangDetail.html"
MEDAL_PAGE = "https://www.sanghun.go.kr/nation/pojangDetail.html"
HISTORY_PAGE = "https://www.sanghun.go.kr/nation/information/posangInfo1.do"
OVERVIEW_PAGE = "https://www.sanghun.go.kr/nation/information/posangInfo3.do"
ORDER_INDEX_PAGE = "https://www.sanghun.go.kr/nation/hunjang.html"
MEDAL_INDEX_PAGE = "https://www.sanghun.go.kr/nation/pojang.html"


orders = [
    ("ROK-ORD-01", "无穷花大勋章", "무궁화대훈장", "Grand Order of Mugunghwa", "eas-gap-01.jpg", [
        ("无等级", "무궁화대훈장", "Grand Order of Mugunghwa"),
    ]),
    ("ROK-ORD-02", "建国勋章", "건국훈장", "Order of Merit for National Foundation", "eas-gap-02.jpg", [
        ("一等·大韩民国章", "대한민국장", "Republic of Korea Medal"),
        ("二等·大统领章", "대통령장", "Presidential Medal"),
        ("三等·独立章", "독립장", "Independence Medal"),
        ("四等·爱国章", "애국장", "Patriotic Medal"),
        ("五等·爱族章", "애족장", "National Medal"),
    ]),
    ("ROK-ORD-03", "国民勋章", "국민훈장", "Order of Civil Merit", "eas-gap-03.jpg", [
        ("一等·无穷花章", "무궁화장", "Mugunghwa Medal"),
        ("二等·牡丹章", "모란장", "Moran Medal"),
        ("三等·冬柏章", "동백장", "Dongbaek Medal"),
        ("四等·木莲章", "목련장", "Mongnyeon Medal"),
        ("五等·石榴章", "석류장", "Seongnyu Medal"),
    ]),
    ("ROK-ORD-04", "武功勋章", "무공훈장", "Order of Military Merit", "eas-gap-04.jpg", [
        ("一等·太极", "태극", "Taegeuk"), ("二等·乙支", "을지", "Eulji"),
        ("三等·忠武", "충무", "Chungmu"), ("四等·花郎", "화랑", "Hwarang"),
        ("五等·仁宪", "인헌", "Inheon"),
    ]),
    ("ROK-ORD-05", "勤政勋章", "근정훈장", "Order of Service Merit", "eas-gap-05.jpg", [
        ("一等·青条", "청조", "Blue Stripes"), ("二等·黄条", "황조", "Yellow Stripes"),
        ("三等·红条", "홍조", "Red Stripes"), ("四等·绿条", "녹조", "Green Stripes"),
        ("五等·玉条", "옥조", "Aquamarine Stripes"),
    ]),
    ("ROK-ORD-06", "保国勋章", "보국훈장", "Order of National Security Merit", "eas-gap-06.jpg", [
        ("一等·统一章", "통일장", "Tongil Medal"), ("二等·国仙章", "국선장", "Gukseon Medal"),
        ("三等·天授章", "천수장", "Cheonsu Medal"), ("四等·三一章", "삼일장", "Samil Medal"),
        ("五等·光复章", "광복장", "Gwangbok Medal"),
    ]),
    ("ROK-ORD-07", "修交勋章", "수교훈장", "Order of Diplomatic Service Merit", "eas-gap-07.jpg", [
        ("一等·光化大章", "광화대장", "Grand Gwanghwa Medal"),
        ("一等·光化章", "광화장", "Gwanghwa Medal"),
        ("二等·兴仁章", "흥인장", "Heungin Medal"),
        ("三等·崇礼章", "숭례장", "Sungnye Medal"),
        ("四等·彰义章", "창의장", "Changui Medal"),
        ("五等·肃靖章", "숙정장", "Sukjeong Medal"),
    ]),
    ("ROK-ORD-08", "产业勋章", "산업훈장", "Order of Industrial Service Merit", "eas-gap-08.jpg", [
        ("一等·金塔", "금탑", "Gold Tower"), ("二等·银塔", "은탑", "Silver Tower"),
        ("三等·铜塔", "동탑", "Bronze Tower"), ("四等·铁塔", "철탑", "Iron Tower"),
        ("五等·锡塔", "석탑", "Tin Tower"),
    ]),
    ("ROK-ORD-09", "新村勋章", "새마을훈장", "Order of Saemaeul Service Merit", "eas-gap-09.jpg", [
        ("一等·自立章", "자립장", "Jarib Medal"), ("二等·自助章", "자조장", "Jajo Medal"),
        ("三等·协同章", "협동장", "Hyeopdong Medal"), ("四等·勤勉章", "근면장", "Geunmyeon Medal"),
        ("五等·努力章", "노력장", "Noryeok Medal"),
    ]),
    ("ROK-ORD-10", "文化勋章", "문화훈장", "Order of Culture Merit", "eas-gap-10.jpg", [
        ("一等·金冠", "금관", "Geumgwan"), ("二等·银冠", "은관", "Eungwan"),
        ("三等·宝冠", "보관", "Bogwan"), ("四等·玉冠", "옥관", "Okgwan"),
        ("五等·花冠", "화관", "Hwagwan"),
    ]),
    ("ROK-ORD-11", "体育勋章", "체육훈장", "Order of Sport Merit", "eas-gap-11.jpg", [
        ("一等·青龙章", "청룡장", "Cheongnyong Medal"), ("二等·猛虎章", "맹호장", "Maengho Medal"),
        ("三等·巨象章", "거상장", "Geosang Medal"), ("四等·白马章", "백마장", "Baengma Medal"),
        ("五等·麒麟章", "기린장", "Girin Medal"),
    ]),
    ("ROK-ORD-12", "科学技术勋章", "과학기술훈장", "Order of Science and Technology Merit", "eas-gap-12.jpg", [
        ("一等·创造章", "창조장", "Changjo Medal"), ("二等·革新章", "혁신장", "Hyeoksin Medal"),
        ("三等·雄飞章", "웅비장", "Ungbi Medal"), ("四等·跃进章", "도약장", "Doyak Medal"),
        ("五等·进步章", "진보장", "Jinbo Medal"),
    ]),
]

official_order_files = ["011", "012", "013", "014", "015", "016_1", "021_1", "027_1", "032_1", "037_1", "042_1", "047_1"]

medals = [
    ("ROK-MED-01", "建国褒章", "건국포장", "National Foundation Medal", 52),
    ("ROK-MED-02", "国民褒章", "국민포장", "Civil Merit Medal", 53),
    ("ROK-MED-03", "武功褒章", "무공포장", "Military Merit Medal", 54),
    ("ROK-MED-04", "勤政褒章", "근정포장", "Service Merit Medal", 55),
    ("ROK-MED-05", "保国褒章", "보국포장", "National Security Medal", 56),
    ("ROK-MED-06", "预备军褒章", "예비군포장", "Reserve Forces Medal", 57),
    ("ROK-MED-07", "修交褒章", "수교포장", "Diplomatic Service Medal", 58),
    ("ROK-MED-08", "产业褒章", "산업포장", "Industrial Service Medal", 59),
    ("ROK-MED-09", "新村褒章", "새마을포장", "Saemaeul Service Medal", 60),
    ("ROK-MED-10", "文化褒章", "문화포장", "Culture Merit Medal", 61),
    ("ROK-MED-11", "体育褒章", "체육포장", "Sport Merit Medal", 62),
    ("ROK-MED-12", "科学技术褒章", "과학기술포장", "Science and Technology Medal", 63),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crops(count: int) -> list[tuple[int, int, int, int]]:
    if count == 1:
        return [(0, 0, 614, 970)]
    if count == 5:
        return [
            (0, 0, 614, 725), (0, 725, 614, 1145), (0, 1145, 614, 1565),
            (0, 1565, 307, 1810), (307, 1565, 614, 1810),
        ]
    if count == 6:
        return [
            (0, 0, 614, 725), (0, 725, 614, 1135), (0, 1135, 614, 1557),
            (0, 1557, 614, 1975), (0, 1975, 307, 2210), (307, 1975, 614, 2210),
        ]
    raise ValueError(count)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    VOLUME.parent.mkdir(parents=True, exist_ok=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    images: list[dict] = []
    candidates: list[dict] = []

    for family_index, (family, name, original, english, source_name, variants) in enumerate(orders, 1):
        source = ORDER_SOURCE / source_name
        with Image.open(source) as plate:
            if plate.width != 614:
                raise ValueError(f"Unexpected plate width: {source} {plate.size}")
            for variant_index, ((variant, variant_original, variant_english), box) in enumerate(zip(variants, crops(len(variants))), 1):
                out = OUTPUT / f"{family.lower()}-v{variant_index:02d}.jpg"
                panel = plate.crop(box)
                panel.save(out, quality=95, subsampling=0)
                key = f"ROK-OFFICIAL-{family_index:02d}-{variant_index:02d}"
                rid = f"{family}-OFFICIAL-V{variant_index:02d}"
                official_file = official_order_files[family_index - 1]
                records.append({
                    "id": rid,
                    "family": family,
                    "country_zh": "韩国",
                    "name": name,
                    "original": f"{original}；{variant_original} / {english} · {variant_english}",
                    "date": "大韩民国现行制式（截至2026年）",
                    "variant": f"{variant}；官方图式",
                    "views": [{"key": key, "label": "官方图式"}],
                    "source_ids": [ORDER_PAGE, f"https://www.sanghun.go.kr/nation/images/contents/m_img_{official_file}.jpg"],
                    "supersedes_id": f"{family}-V01" if variant_index == 1 else None,
                })
                images.append({
                    "view_key": key,
                    "local_path": out.relative_to(ROOT).as_posix(),
                    "source_page_url": ORDER_PAGE,
                    "original_file_url": records[-1]["source_ids"][1],
                    "source_plate_local_path": source.relative_to(ROOT).as_posix(),
                    "crop_box": list(box),
                    "image_nature": "official_diagram_crop",
                    "sha256": sha256(out),
                    "bytes": out.stat().st_size,
                    "width": panel.width,
                    "height": panel.height,
                })
                candidates.append({
                    "source_id": key,
                    "source": "Republic of Korea Awards and Decorations",
                    "source_page_url": ORDER_PAGE,
                    "title": f"{original} - {variant_original}",
                    "chinese_work_name": f"{name}·{variant}",
                    "original_name": f"{original}·{variant_original}",
                    "english_name": f"{english} · {variant_english}",
                    "category": "order",
                    "status": "INGESTED",
                })

    for index, (family, name, original, english, number) in enumerate(medals, 1):
        source = MEDAL_SOURCE / f"m_img_{number:03d}.jpg"
        if not source.is_file():
            source.parent.mkdir(parents=True, exist_ok=True)
            image_url = f"https://www.sanghun.go.kr/nation/images/contents/m_img_{number:03d}.jpg"
            request = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            source.write_bytes(urllib.request.urlopen(request, timeout=30).read())
        out = OUTPUT / f"{family.lower()}-v01.jpg"
        shutil.copyfile(source, out)
        key = f"ROK-OFFICIAL-MED-{index:02d}"
        image_url = f"https://www.sanghun.go.kr/nation/images/contents/m_img_{number:03d}.jpg"
        records.append({
            "id": f"{family}-V01", "family": family, "country_zh": "韩国",
            "name": name, "original": f"{original} / {english}",
            "date": "大韩民国现行制式（截至2026年）",
            "variant": "不分等级；官方图式",
            "views": [{"key": key, "label": "官方图式"}],
            "source_ids": [MEDAL_PAGE, image_url],
        })
        with Image.open(out) as image:
            width, height = image.size
            image.verify()
        images.append({
            "view_key": key, "local_path": out.relative_to(ROOT).as_posix(),
            "source_page_url": MEDAL_PAGE, "original_file_url": image_url,
            "source_plate_local_path": source.relative_to(ROOT).as_posix(),
            "image_nature": "official_diagram", "sha256": sha256(out),
            "bytes": out.stat().st_size, "width": width, "height": height,
        })
        candidates.append({
            "source_id": key, "source": "Republic of Korea Awards and Decorations",
            "source_page_url": MEDAL_PAGE, "title": original,
            "chinese_work_name": name, "original_name": original,
            "english_name": english, "category": "medal", "status": "INGESTED",
        })

    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27", "volume": "韩国官方现行勋章与褒章完整目录",
        "scope": "韩国政府 상훈 官方目录：12类勋章的全部现行等级／名目，以及12种褒章。",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27", "volume": "韩国官方现行勋章与褒章完整目录",
        "sources": [ORDER_INDEX_PAGE, ORDER_PAGE, MEDAL_INDEX_PAGE, MEDAL_PAGE, HISTORY_PAGE, OVERVIEW_PAGE],
        "images": images,
        "coverage": {
            "planned_sources": 6, "completed_sources": 6, "partial_sources": 0,
            "not_started_sources": 0, "award_families": len({r["family"] for r in records}),
            "variant_rows": len(records), "local_complete_images": len(images),
            "unresolved_candidates": 0,
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RAW.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in candidates), encoding="utf-8")
    print(f"wrote {len(records)} rows, {len(images)} images, {len(candidates)} candidates")


if __name__ == "__main__":
    main()
