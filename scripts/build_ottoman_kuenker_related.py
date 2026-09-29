"""Build the Kuenker 299 related-awards appendix for lots 7383-7413."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "tmp/pdfs/kuenker299_embedded"
ASSETS = ROOT / "assets/images/ottoman_kuenker299_related"
VOLUME = ROOT / "data/volumes/ottoman_kuenker299_related.json"
MANIFEST = ROOT / "data/volumes/ottoman_kuenker299_related_manifest.json"

# lot, page, image indices, family, Chinese name, original name, date, precise disposition
LOTS = [
    (7383,233,[7,6],"OTT-REL-KADIKOY-SCHOOL","卡德柯伊奥斯曼团结学校奖牌","Kadıköy İttihad-ı Osmanî Mektebi Madalyası","1910","学校奖牌；银质；非佩戴式"),
    (7384,233,[5,4],"OTT-REL-KADIKOY-SCHOOL","卡德柯伊奥斯曼团结学校奖牌","Kadıköy İttihad-ı Osmanî Mektebi Madalyası","1910","学校奖牌；青铜质；非佩戴式"),
    (7385,233,[10,11],"OTT-REL-GALATASARAY-FOUNDING","加拉塔萨雷足球队成立纪念章","Galatasaray Futbol Takımı Hatıra Madalyası","1905","体育团体纪念章；青铜质；30毫米；非佩戴式"),
    (7386,233,[2,3],"OTT-REL-FLOWER-FESTIVAL","花卉节济贫功绩奖章","Kadıköy Fukaraperver Cemiyeti Madalyası","1917","慈善组织奖章；银质；吊环残缺；无绶带"),
    (7387,234,[7,6],"OTT-REL-SPORTS-ASSOCIATION","奥斯曼体育协会功绩奖章","İttihad-ı Spor Madalyası","1917","体育协会奖章；银质；原绶带与横扣"),
    (7388,234,[5,4],"OTT-REL-PETIT-LYON-CONSTITUTION","小里昂宪政颁布纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；镀金青铜；非佩戴式；法文铭文"),
    (7389,234,[2,3],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜；无环无绶带"),
    (7390,234,[10,11],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜版型；无环无绶带"),
    (7391,234,[9,8],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜版型；无环无绶带"),
    (7392,235,[6,7],"OTT-REL-BALKAN-MEDAL","巴尔干非官方纪念章","Balkan Madalyası","约1908-1912","非官方纪念章；铝质；28.6毫米；带绶带与横扣"),
    (7393,235,[5,4],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；镀银青铜；希腊文铭文；小绶带"),
    (7394,235,[9,8],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜；珐琅横扣与别针"),
    (7395,235,[3,2],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜版型；无环无绶带"),
    (7396,235,[11,10],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；青铜版型；无环无绶带"),
    (7397,236,[2,3],"OTT-REL-UNOFFICIAL-CONSTITUTION","宪政颁布非官方纪念章","Meşrûtiyyet İlânı Madalyası","1908","非官方纪念章；银质；无环无绶带"),
    (7398,236,[4,5],"OTT-REL-WEDDING-1918","婚礼纪念章","Tarih-i Akdi Nikâh Madalyası","1918-09-06","私人婚礼纪念章；铝质；无环无绶带"),
    (7399,236,[6,7],"OTT-REL-ALI-PASHA","阿里帕夏委制未知纪念章","Tepedelenli Ali Paşa Madalyası","约1807","非官方委制纪念章；金质；29.4毫米；身份归属待考"),
    (7400,236,[9,8],"OTT-REL-PILOT-BADGE","奥斯曼飞行员章","Osmanlı Pilot Brövesi","约1916","资格章；奥斯曼制造；银质局部镀金；原盒"),
    (7401,237,[5,4],"OTT-REL-PILOT-BADGE","奥斯曼飞行员章","Osmanlı Pilot Brövesi","约1916","资格章；可能奥地利制造；贱金属局部珐琅"),
    (7402,237,[9,8],"OTT-REL-MEHMED-V-ACCESSION","穆罕默德五世即位非官方纪念章","Cülûs Madalyası","1909","非官方纪念章；青铜；无环无绶带"),
    (7403,237,[7,6],"OTT-REL-MEHMED-V-ACCESSION","穆罕默德五世即位非官方纪念章","Cülûs Madalyası","1909","非官方纪念章；镀金青铜；非佩戴式"),
    (7404,237,[3,2],"OTT-REL-MEHMED-V-ACCESSION","穆罕默德五世即位非官方纪念章","Cülûs Madalyası","1909","非官方纪念章；青铜版型；无环无绶带"),
    (7405,237,[11,10],"OTT-REL-MEHMED-V-ACCESSION","穆罕默德五世即位非官方纪念章","Cülûs Madalyası","1909","非官方纪念章；铜质；局部英文铭文；无绶带"),
    (7407,238,[3,2],"OTT-REL-GERMAN-CRAFTSMEN","君士坦丁堡德国手工业协会五十周年纪念章","Deutscher Handwerker-Verein Konstantinopel Jubiläumsmedaille","1911","协会纪念章；镀金贱金属；无绶带"),
    (7408,238,[7,6],"OTT-REL-SHKODRA-JESUIT","斯库台圣方济各·沙勿略耶稣会学院功绩奖章","Verdienstmedaille des Jesuitenkollegs St. Franz Xaver zu Shkodra","19世纪末","宗教学校功绩奖章；银质花丝与粒金；局部镀金；玻璃石饰"),
    (7409,239,[3,2],"OTT-REL-CONSTANTINOPLE-BUDAPEST","君士坦丁堡—布达佩斯纪念章","Erinnerung Konstantinopel Budapest","约1896","城市展陈相关纪念章；青铜；无环无绶带"),
    (7410,239,[5,4],"OTT-REL-FAIK-BEY-CYCLING","法伊克贝伊自行车赛奖章","Professor Faik Bey Radrennen-Medaille","约1905以后","加拉塔萨雷体育赛事奖章；青铜；无绶带"),
    (7411,239,[7,6],"OTT-REL-FAIK-BEY-GYMNASTICS","法伊克贝伊体操纪念章","Professor Faik Bey Erinnerungsmedaille für Gymnastik","约1905以后","体育纪念章；青铜；配绶带"),
    (7412,240,[3,2,4],"OTT-REL-ASSEMBLY-BADGE","奥斯曼国民议会议员章","Meclis-i Meb'ûsân-ı Osmanî Azalarına Mahsus Görüce Alâmeti","1916-1919","身份章；第三会期；奥斯曼造币厂；镀金白色金属与金、珐琅；原绶带与原盒"),
    (7413,240,[6,5],"OTT-REL-TALAT-PASHA","塔拉特帕夏纪念章","Talât Paşa Madalyası","1917","人物纪念章；青铜铸造；76.3毫米；非佩戴式；A. Oppler签名"),
]


def extracted(page: int, index: int) -> Path:
    matches = sorted((EXTRACTED / f"page_{page:03d}").glob(f"{index:02d}_*"))
    if len(matches) != 1:
        raise RuntimeError((page, index, matches))
    return matches[0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    records, images = [], []
    for lot, page, indices, family, name, original, date, variant in LOTS:
        record_id = f"OK299-REL-{lot}"
        views = []
        for number, index in enumerate(indices):
            side = "front" if number == 0 else ("back" if number == 1 else f"view{number + 1}")
            label = "正面完整实物图" if number == 0 else ("背面完整实物图" if number == 1 else "配套佩饰完整实物图")
            src = extracted(page, index)
            dst = ASSETS / f"lot_{lot}_{side}{src.suffix.lower()}"
            shutil.copy2(src, dst)
            with Image.open(dst) as image:
                width, height = image.size
                image.verify()
            key = f"{record_id}-{side.upper()}"
            views.append({"key": key, "label": label})
            images.append({
                "view_key": key,
                "local_path": dst.relative_to(ROOT).as_posix(),
                "source_id": f"kuenker299-lot-{lot}",
                "download_status": "extracted_and_decoded",
                "source_page_url": f"https://kuenker.s3.eu-central-1.amazonaws.com/media/31/1d/22/1736866624/299_kuenker-katalog_web.pdf#page={page}",
                "source_original_url": f"embedded image in Kuenker Auction 299 PDF, page {page}, image {index}",
                "license": "Kuenker Auction 299 catalogue photograph; local research use only",
                "width": width,
                "height": height,
                "sha256": digest(dst),
                "pdf_page": page,
                "lot": lot,
                "side": side,
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
        "volume": "奥斯曼帝国：Künker 299相关奖励与纪念佩饰",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "Künker Auction 299, The Ottoman Collection Part 2",
        "source_pdf": "sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf",
        "pages_processed": list(range(233, 241)),
        "lots_ingested": [item[0] for item in LOTS],
        "classification": "related_gallery",
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} related records and {len(images)} images")


if __name__ == "__main__":
    main()
