"""Build the second Ottoman Kuenker 299 ingestion batch.

Every selected lot has been checked against the page text and the embedded
front/back photographs.  Repeated specimens of the same variant are omitted.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "tmp/pdfs/kuenker299_embedded"
ASSETS = ROOT / "assets/images/ottoman_kuenker299_batch2"
VOLUME = ROOT / "data/volumes/ottoman_kuenker299_batch2.json"
MANIFEST = ROOT / "data/volumes/ottoman_kuenker299_batch2_manifest.json"


# lot, page, front image number, back image number, family, Chinese name,
# original name, date, variant
LOTS = [
    (7204,168,2,3,"OTT-TASHIH-AYAR","新币制校正纪念章","Tashih-i Ayar Sikke Madalyası","1844","小型；银质；38.3毫米；非佩戴式"),
    (7205,168,4,5,"OTT-TASHIH-AYAR","新币制校正纪念章","Tashih-i Ayar Sikke Madalyası","1844","大型；青铜质；50.4毫米；非佩戴式"),
    (7206,168,6,7,"OTT-TASHIH-AYAR","新币制校正纪念章","Tashih-i Ayar Sikke Madalyası","1844","小型；青铜质；38.5毫米；非佩戴式"),
    (7207,168,8,9,"OTT-KURDISTAN","库尔德斯坦战役奖章","Kürdistan Madalyası","1847","大型银质；29.6毫米；非佩戴式"),
    (7208,169,4,5,"OTT-KURDISTAN","库尔德斯坦战役奖章","Kürdistan Madalyası","1847","小型金质；26.5毫米；英式佩戴装具"),
    (7209,169,2,3,"OTT-KURDISTAN","库尔德斯坦战役奖章","Kürdistan Madalyası","1847","小型银质；26.6毫米；佩戴式"),
    (7210,169,8,9,"OTT-KURDISTAN","库尔德斯坦战役奖章","Kürdistan Madalyası","1847","小型银质；26.4毫米；无环"),
    (7211,169,6,7,"OTT-KURDISTAN","库尔德斯坦战役奖章","Kürdistan Madalyası","1847","小型银质；26.8毫米；非佩戴式"),
    (7212,170,2,3,"OTT-YEMEN-1846","1846年也门战役奖章","Hıtta-ı Yemaniye Madalyası","1852年设立（纪念1846年战役）","银质；非佩戴式"),
    (7213,170,4,5,"OTT-YEMEN-1846","1846年也门战役奖章","Hıtta-ı Yemaniye Madalyası","1852年设立（纪念1846年战役）","青铜质；非佩戴式"),
    (7214,170,6,7,"OTT-RUSDIYE","鲁什迪耶学校优等生奖章","Mekteb-i Rüşdiye Madalyası","1847","一等；鎏金银质；42.2×43.2毫米；颈授"),
    (7243,180,2,3,"OTT-TAKDIR-HUNER","才能表彰奖章","Takdîr-i Hüner Madalyası","约1858年设立","金质；佩戴式；原绶带"),
    (7244,180,4,5,"OTT-TAKDIR-HUNER","才能表彰奖章","Takdîr-i Hüner Madalyası","约1858年设立","银级名义；铜质试铸；非佩戴式"),
    (7245,180,6,7,"OTT-TAKDIR-HUNER","才能表彰奖章","Takdîr-i Hüner Madalyası","约1858年设立","青铜级；铜质；非佩戴式"),
    (7246,181,2,3,"OTT-HIRFET-SANAT-TICARET","手工业、工业与商业功绩奖章","Sergi-i Umumî-i Osmanî Hirfet Sanat Ticaret Madalyası","约1866","银质；44.7毫米；非佩戴式"),
    (7247,182,2,3,"OTT-NISAN-ENDAHT","射击奖章","Nişan-Endâht Madalyası","1863","银质；36.8毫米；非佩戴式"),
    (7248,182,4,5,"OTT-CHOLERA","霍乱防疫奖章","Kolera Madalyası","1865","银质；佩戴式；原绶带"),
    (7297,200,2,3,"OTT-AGRI-INDUSTRY","农业与工业奖章","Zira'at ve Sınâ'at Madalyası","1893","银质；44.4毫米；非佩戴式"),
    (7298,200,4,5,"OTT-AGRI-INDUSTRY","农业与工业奖章","Zira'at ve Sınâ'at Madalyası","1893","银质；佩戴式；原绶带"),
    (7299,200,6,7,"OTT-AGRI-INDUSTRY","农业与工业奖章","Zira'at ve Sınâ'at Madalyası","1893","青铜质；44.3毫米；非佩戴式"),
    (7301,201,2,3,"OTT-EARTHQUAKE-1894","1894年大地震救济基金纪念章","Hareket-i Arz İâne Madalyası","1894","大型银质；34.8毫米；佩戴式；特拉布宗行业团体题名"),
    (7302,201,4,5,"OTT-EARTHQUAKE-1894","1894年大地震救济基金纪念章","Hareket-i Arz İâne Madalyası","1894","小型银质；28.1毫米；佩戴式；阿里夫帕夏题名"),
    (7304,202,2,3,"OTT-ANADOLU-EPIDEMIC","安纳托利亚疫灾救济基金奖章","Anadolu Musâbînine İâne Madalyası","1895","银质；29.7毫米；无环"),
    (7305,202,4,5,"OTT-TESISAT-ASKERIYYE","军备基金捐助奖章","Te'sîsât-i Askeriyye İâne Madalyası","1895","银质；29.8毫米；佩戴式"),
    (7306,202,6,7,"OTT-TESISAT-ASKERIYYE","军备基金捐助奖章","Te'sîsât-i Askeriyye İâne Madalyası","1895","铝质；27毫米；佩戴式；原绶带"),
    (7310,204,2,3,"OTT-SEHID-EVLAD-MALUL","军人遗孤与伤员救济展览功绩章","Şehid Evlad ve Malül Askere İâne Sergisi Madalyası","1897","小型银质；60.3毫米；非佩戴式"),
    (7311,204,4,5,"OTT-SEHID-EVLAD-MALUL","军人遗孤与伤员救济展览功绩章","Şehid Evlad ve Malül Askere İâne Sergisi Madalyası","1897","小型镍质；26.9毫米；非佩戴式；原盒"),
    (7313,204,8,9,"OTT-MAARIF-BADGE","教育功绩徽章","Ma'ârif Madalyası","1899年设立；图示1902年授予件","银质徽章；行政／军事学院毕业奖励；背刻授予文"),
    (7323,208,2,3,"OTT-HARIR-MUSABAKA","蚕桑养殖竞赛奖章","Harir Müsabakası Madalyası","1904","银质；35毫米；佩戴式；原绶带"),
    (7324,208,4,5,"OTT-HARIR-MUSABAKA","蚕桑养殖竞赛奖章","Harir Müsabakası Madalyası","1904","青铜质；34.9毫米；非佩戴式"),
    (7325,208,7,8,"OTT-HEJAZ-MAAN","汉志铁路马安站启用纪念章","Hicâz Demiryolu Ma'ân Mevki'i Küşâd Madalyası","1904","小型镍质；佩戴式；红色绶带"),
    (7327,209,4,5,"OTT-HEJAZ-MEDINA","汉志铁路麦地那站启用纪念章","Hicâz Demiryolu Medine-i Münevvere Mevki'i Madalyası","1908","银质；无环"),
    (7335,212,2,3,"OTT-MESRUTIYET-MONUMENT","宪政纪念碑落成纪念章","Hâtıra-i Âbide-i Meşrûtiyet Madalyası","1911","银质；正式佩戴式；背面1328年题名"),
    (7336,212,6,7,"OTT-HAMIDIYE-CRUISER","哈米迪耶巡洋舰奖章","Hamidiye Kruvazör-i Hümâyûnu Madalyası","1913","鎏金残存青铜质；佩戴式"),
    (7353,219,2,3,"OTT-RED-CRESCENT","奥斯曼红新月奖章","Hilâl-i Ahmer Madalyası","约1914起第二版","青铜级；无年份佩戴横条；原绶带与原盒"),
    (7354,219,4,5,"OTT-MUDAFAA-MILLIYE","国防委员会功绩奖章","Müdafaa-i Milliye Cemiyeti Biçki Yurdu Madalyası","1914","银质；绶带装具与背针；无绶带"),
]


def extracted(page: int, index: int) -> Path:
    matches = sorted((EXTRACTED / f"page_{page:03d}").glob(f"{index:02d}_*"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one image for page {page}, index {index}: {matches}")
    return matches[0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    records = []
    images = []
    for lot, page, front_index, back_index, family, name, original, date, variant in LOTS:
        record_id = f"OK299-{lot}"
        views = []
        for side, label, index in (
            ("FRONT", "正面完整实物图", front_index),
            ("BACK", "背面完整实物图", back_index),
        ):
            source = extracted(page, index)
            suffix = source.suffix.lower()
            destination = ASSETS / f"lot_{lot}_{side.lower()}{suffix}"
            shutil.copy2(source, destination)
            with Image.open(destination) as image:
                width, height = image.size
                image.verify()
            view_key = f"{record_id}-{side}"
            views.append({"key": view_key, "label": label})
            images.append({
                "view_key": view_key,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "source_id": f"kuenker299-lot-{lot}",
                "download_status": "extracted_and_decoded",
                "source_page_url": f"https://kuenker.s3.eu-central-1.amazonaws.com/media/31/1d/22/1736866624/299_kuenker-katalog_web.pdf#page={page}",
                "source_original_url": f"embedded image in Kuenker Auction 299 PDF, page {page}, image {index}",
                "license": "Kuenker Auction 299 catalogue photograph; local research use only",
                "width": width,
                "height": height,
                "sha256": digest(destination),
                "pdf_page": page,
                "lot": lot,
                "side": side.lower(),
            })
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": "奥斯曼帝国",
            "name": name,
            "original": original,
            "date": date,
            "variant": f"{variant}；Künker 299图录实物照 · 2017",
            "views": views,
            "source_ids": [f"kuenker299-lot-{lot}"],
            "image_kind": "object_photo",
            "html_eligible": True,
        })

    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：Künker 299专题拍卖差集第二批",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Künker Auction 299, The Ottoman Collection Part 2",
        "source_pdf": "sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf",
        "pages_processed": sorted({row[1] for row in LOTS}),
        "lots_ingested": [row[0] for row in LOTS],
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} records and {len(images)} images")


if __name__ == "__main__":
    main()
