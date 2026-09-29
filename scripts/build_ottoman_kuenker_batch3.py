"""Build the third Ottoman Kuenker 299 ingestion batch.

This batch covers the early medal plates and the 1877-1893 sequence.  Rows
represent meaningful grades, issues or mounting variants; duplicate named
specimens of the same type are deliberately omitted.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "tmp/pdfs/kuenker299_embedded"
ASSETS = ROOT / "assets/images/ottoman_kuenker299_batch3"
VOLUME = ROOT / "data/volumes/ottoman_kuenker299_batch3.json"
MANIFEST = ROOT / "data/volumes/ottoman_kuenker299_batch3_manifest.json"


# lot, PDF page, front image index, back image index, family, Chinese name,
# original name, date, image-specific variant.
LOTS = [
    (7182,157,4,6,"OTT-SIKKE-CEDID","新式钱币铸造纪念章","Sikke-i Cedid Madalyası","1754","金质；椭圆形；链式悬挂；30.8×39.6毫米"),
    (7183,158,2,3,"OTT-EGYPT-1801","埃及战役奖章","Vaka-i Misriye Madalyası","1801","一级大型金质；53.7毫米；链式悬挂"),
    (7184,159,2,3,"OTT-EGYPT-1801","埃及战役奖章","Vaka-i Misriye Madalyası","1801","二级金质；41.8毫米；英式佩戴装具"),
    (7185,160,2,3,"OTT-EGYPT-1801","埃及战役奖章","Vaka-i Misriye Madalyası","1801","二级金质；48.4毫米；链式悬挂"),
    (7186,160,4,5,"OTT-EGYPT-1801","埃及战役奖章","Vaka-i Misriye Madalyası","1801","四级金质；36.4毫米；链式悬挂"),
    (7188,162,2,3,"OTT-OTTOMAN-CRESCENT-1808","奥斯曼新月奖章","Hilâl-i Osmanî Madalyası","约1808","银质；41.9毫米；非佩戴式"),
    (7189,162,7,8,"OTT-CAMI-NUSRET","胜利清真寺纪念章","Câmi-i Nusret Madalyası","1831","大型金质；28.9毫米；佩戴式"),
    (7190,162,4,6,"OTT-CAMI-NUSRET","胜利清真寺纪念章","Câmi-i Nusret Madalyası","1831","大型银质；29.1毫米；英式佩戴装具与原绶带"),
    (7191,163,7,8,"OTT-CAMI-NUSRET","胜利清真寺纪念章","Câmi-i Nusret Madalyası","1831","银质；佩戴式；红色绶带"),
    (7194,163,9,10,"OTT-HUNKAR-ISKELESI","许恩卡尔伊斯凯莱西条约纪念章","Hünkâr İskelesi Madalyası","1833","金质；28.5毫米；非佩戴式"),
    (7195,164,4,5,"OTT-HUNKAR-ISKELESI","许恩卡尔伊斯凯莱西条约纪念章","Hünkâr İskelesi Madalyası","1833","银质；29.7毫米；非佩戴式"),
    (7196,164,2,3,"OTT-HADIM-HAREMEYN","两圣地服务奖章","Hâdimü'l-Haremeyni'ş-Şerefeyn Madalyası","1837","银质条形；19.6×40.5毫米；非佩戴式"),
    (7197,164,6,7,"OTT-IFTIHAR-ORDER","伊夫蒂哈尔勋章","Nişan-ı İftihar","1831年型","军事功绩挂章；鎏金银质；镶45枚玫瑰切割钻石"),
    (7198,166,2,3,"OTT-ACRE","阿克里战役奖章","Akka Madalyası","1840","金质；英式佩戴装具；ACRE横条"),
    (7200,167,6,7,"OTT-ACRE","阿克里战役奖章","Akka Madalyası","1840","银质；佩戴式；红色绶带"),
    (7201,167,2,3,"OTT-ACRE","阿克里战役奖章","Akka Madalyası","1840","银质；非佩戴式"),
    (7202,167,4,5,"OTT-ACRE","阿克里战役奖章","Akka Madalyası","1840","青铜质；非佩戴式"),
    (7203,167,8,9,"OTT-TASHIH-AYAR","新币制校正纪念章","Tashih-i Ayar Sikke Madalyası","1844","大型银质；非佩戴式"),
    (7252,185,2,3,"OTT-RUSSO-TURKISH-WAR-1877","俄土战争奖章","Rus Harbi Madalyası","1877-1878","第一版；银质；花饰图格拉；非佩戴式"),
    (7253,185,4,5,"OTT-RUSSO-TURKISH-WAR-1877","俄土战争奖章","Rus Harbi Madalyası","1877-1878","第二版；银质；El Gazi图格拉；非佩戴式"),
    (7258,187,2,3,"OTT-MONTENEGRO","黑山战役奖章","Karadağ Madalyası","1862","银质；非佩戴式"),
    (7259,187,4,5,"OTT-PLEVNA","普列夫纳战役奖章","Plevne Madalyası","1877","银质；佩戴式；原绶带与花结"),
    (7261,188,6,7,"OTT-IMTIYAZ-MEDAL","大伊姆蒂亚兹奖章","Büyük İmtiyaz Madalyası","1883","金质；佩戴式；1887年授予题名"),
    (7263,189,6,7,"OTT-IMTIYAZ-MEDAL","大伊姆蒂亚兹奖章","Büyük İmtiyaz Madalyası","1883","银质；横分红绿绶带；佩戴式"),
    (7267,190,7,8,"OTT-IFTIHAR-MEDAL","伊夫蒂哈尔（工业）奖章","İftihâr / Sanayi Madalyası","1884-1922","第四型金质；第一版宽月桂环；非佩戴式"),
    (7268,191,2,3,"OTT-IFTIHAR-MEDAL","伊夫蒂哈尔（工业）奖章","İftihâr / Sanayi Madalyası","1884-1922","第四型金质；第二版窄月桂环；宽绶带扣"),
    (7269,192,2,3,"OTT-IFTIHAR-MEDAL","伊夫蒂哈尔（工业）奖章","İftihâr / Sanayi Madalyası","1884-1922","第四型银质；第一版宽月桂环；佩戴式"),
    (7274,193,6,7,"OTT-IFTIHAR-MEDAL","伊夫蒂哈尔（工业）奖章","İftihâr / Sanayi Madalyası","1884-1922","第四型银质；第一版宽月桂环；Kanal（苏伊士运河）横条"),
    (7276,193,8,9,"OTT-IFTIHAR-MEDAL","伊夫蒂哈尔（工业）奖章","İftihâr / Sanayi Madalyası","1884-1922","第四型银质；第二版窄月桂环；Çanakkale横条"),
    (7280,195,4,5,"OTT-WILHELM-II-COMMEMORATIVE","德皇威廉二世访问君士坦丁堡纪念章","Alman Mülâkâtı Madalyası","1889","银级；德式大勋表弓形绶带"),
    (7281,195,2,3,"OTT-WILHELM-II-COMMEMORATIVE","德皇威廉二世访问君士坦丁堡纪念章","Alman Mülâkâtı Madalyası","1889","青铜级；铜质；移除悬环；非佩戴式"),
    (7282,195,8,9,"OTT-CRETE-1890","第二次克里特战役奖章","Cedîd Girid Madalyası","1890","金级；金质；无悬环"),
    (7283,195,6,7,"OTT-CRETE-1890","第二次克里特战役奖章","Cedîd Girid Madalyası","1890","银级；银质；窄绶带"),
    (7287,196,6,7,"OTT-LIYAKAT","功绩奖章","Liyakât Madalyası","1890年设立","金级；金质；非佩戴式"),
    (7292,198,6,7,"OTT-YEMEN-1892","也门战役奖章","Cedid Yemen Madalyası","1902年设立；纪年1273/1310","金级；第二版；红底三绿条绶带"),
    (7293,199,2,3,"OTT-YEMEN-1892","也门战役奖章","Cedid Yemen Madalyası","1902年设立；纪年1273","银级；第一版；佩戴横条"),
    (7295,199,8,9,"OTT-YEMEN-1892","也门战役奖章","Cedid Yemen Madalyası","1902年设立；纪年1273/1310","银级；第二版；红底绿边绶带与佩戴横条"),
    (7296,199,6,7,"OTT-AGRI-INDUSTRY","农业与工业奖章","Zira'at ve Sınâ'at Madalyası","1893","金质；44.3毫米；非佩戴式"),
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
    records, images = [], []
    for lot, page, front_index, back_index, family, name, original, date, variant in LOTS:
        record_id = f"OK299-{lot}"
        views = []
        for side, label, index in (("FRONT", "正面完整实物图", front_index), ("BACK", "背面完整实物图", back_index)):
            source = extracted(page, index)
            destination = ASSETS / f"lot_{lot}_{side.lower()}{source.suffix.lower()}"
            shutil.copy2(source, destination)
            with Image.open(destination) as im:
                width, height = im.size
                im.verify()
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
                "width": width, "height": height, "sha256": digest(destination),
                "pdf_page": page, "lot": lot, "side": side.lower(),
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "奥斯曼帝国",
            "name": name, "original": original, "date": date,
            "variant": f"{variant}；Künker 299图录实物照 · 2017",
            "views": views, "source_ids": [f"kuenker299-lot-{lot}"],
            "image_kind": "object_photo", "html_eligible": True,
        })

    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "奥斯曼帝国：Künker 299专题拍卖差集第三批", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "source": "Künker Auction 299, The Ottoman Collection Part 2", "source_pdf": "sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf", "pages_processed": sorted({row[1] for row in LOTS}), "lots_ingested": [row[0] for row in LOTS], "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} records and {len(images)} images")


if __name__ == "__main__":
    main()
