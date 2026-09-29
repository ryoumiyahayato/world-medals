"""Normalize the completed Belarus, Lithuania and Latvia World Awards sweeps.

This is deliberately an isolated volume writer.  It copies every decoded image
exposed by each object page into a volume-owned image directory and keeps all
of the views on the same award family record; the public site can then decide
how to render the set without losing source variants.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

NAMES = {
    "belarus": {
        "hero-of-belarus": "白俄罗斯英雄称号",
        "order-of-the-fatherland": "祖国勋章",
        "order-for-promotion-of-peace-and-friendship": "促进和平与友谊勋章",
        "order-of-military-glory": "军事荣誉勋章",
        "order-of-labor-glory": "劳动光荣勋章",
        "order-for-service-to-the-homeland": "服务祖国勋章",
        "order-for-personal-courage": "个人英勇勋章",
        "order-of-friendship-of-peoples": "人民友谊勋章",
        "order-of-honor": "荣誉勋章",
        "order-of-francysk-skaryna": "弗朗齐斯克·斯卡里纳勋章",
        "order-of-mother": "母亲勋章",
        "medal-for-bravery": "勇敢奖章",
        "medal-for-saved-life": "生命救援奖章",
        "medal-for-distinction-in-military-service": "军事服役优异奖章",
        "medal-for-distinction-in-the-maintenance-of-public-order": "维护公共秩序优异奖章",
        "medal-for-distinction-in-the-state-border-protection": "国家边境保卫优异奖章",
        "medal-for-distinction-in-prevention-and-elimination-of-emergencies": "预防和消除紧急情况优异奖章",
        "medal-for-labour-merits": "劳动功绩奖章",
        "medal-of-francysk-skaryna": "弗朗齐斯克·斯卡里纳奖章",
        "medal-for-impeccable-service": "无瑕服役奖章",
        "jubilee-medal-80-years-of-belarusian-police": "白俄罗斯警察80周年纪念奖章",
        "jubilee-medal-90-years-of-belarusian-police": "白俄罗斯警察90周年纪念奖章",
        "jubilee-medal-80-years-of-the-state-security-committee": "国家安全委员会80周年纪念奖章",
        "jubilee-medal-90-years-of-the-state-security-bodies": "国家安全机关90周年纪念奖章",
        "jubilee-medal-80-years-of-the-armed-forces": "武装力量80周年纪念奖章",
        "jubilee-medal-90-years-of-the-armed-forces": "武装力量90周年纪念奖章",
        "jubilee-medal-80-years-of-the-border-troops": "边防部队80周年纪念奖章",
        "jubilee-medal-90-years-of-border-guard": "边防部队90周年纪念奖章",
        "jubilee-medal-150-years-of-fire-service": "消防部门150周年纪念奖章",
        "jubilee-medal-160-years-of-fire-service": "消防部门160周年纪念奖章",
        "jubilee-medal-100-years-of-the-trade-union-movement-of-belarus": "白俄罗斯工会运动100周年纪念奖章",
        "jubilee-medal-110-years-of-the-trade-union-movement-of-belarus": "白俄罗斯工会运动110周年纪念奖章",
        "jubilee-medal-10th-anniversary-of-the-withdrawal-of-the-soviet-army-from-afghanistan": "苏军撤出阿富汗10周年纪念奖章",
        "jubilee-medal-20th-anniversary-of-the-withdrawal-of-the-soviet-army-from-afghanistan": "苏军撤出阿富汗20周年纪念奖章",
        "jubilee-medal-115-years-of-the-trade-union-movement-of-belarus": "白俄罗斯工会运动115周年纪念奖章",
        "medal-100-years-of-agricultural-and-food-public-administration": "农业和食品公共管理100周年奖章",
        "jubilee-medal-20-years-of-the-presidents-security-service": "总统安全局成立20周年纪念奖章",
        "jubilee-medal-95-years-of-army-signal-troops": "武装力量通信兵95周年纪念奖章",
    },
    "lithuania": {
        "vytis-cross": "维蒂斯十字勋章",
        "order-of-vytautas-the-great": "维陶塔斯大帝勋章",
        "order-of-the-vytis-cross": "维蒂斯十字勋章",
        "order-of-the-lithuanian-grand-duke-gediminas": "立陶宛大公格迪米纳斯勋章",
        "order-for-merits-to-lithuania": "立陶宛功绩勋章",
        "life-saving-cross": "救生十字勋章",
        "medal-of-the-order-of-vytautas-the-great": "维陶塔斯大帝勋章奖章",
        "medal-of-the-order-of-the-lithuanian-grand-duke-gediminas": "立陶宛大公格迪米纳斯勋章奖章",
        "medal-of-the-order-of-the-cross-of-vytis": "维蒂斯十字勋章奖章",
        "medal-of-the-order-for-merits-to-lithuania": "立陶宛功绩勋章奖章",
        "medal-of-the-volunteers-founders-of-the-army": "建军志愿者奖章",
        "medal-of-lithuanian-independence": "立陶宛独立奖章",
        "medal-of-the-pioneers-of-the-army": "建军先驱奖章",
        "medal-of-the-liberation-of-klaipeda": "克莱佩达解放奖章",
        "medal-of-13-january": "一月十三日奖章",
        "medal-of-darius-and-girenas": "达里乌斯与吉雷纳斯奖章",
        "riflemen-s-star-decoration": "步枪手之星佩饰",
        "riflemen-s-star-medal": "步枪手之星奖章",
        "national-defence-system-medal-for-merits": "国防系统功绩奖章",
        "national-defence-system-medal-for-merits-for-civilians": "国防系统平民功绩奖章",
        "national-defence-system-medal-for-distinction": "国防系统优异奖章",
        "national-defence-system-general-jonas-zemaitis-medal": "国防系统约纳斯·热马蒂斯将军奖章",
        "national-defence-system-medal-for-international-operations": "国防系统国际行动奖章",
        "national-defence-system-medal-of-nato-accession": "国防系统加入北约奖章",
        "armed-forces-medal-for-merits": "武装力量功绩奖章",
        "armed-forces-medal-for-distinction": "武装力量优异奖章",
        "armed-forces-wound-medal": "武装力量负伤奖章",
        "armed-forces-medal-for-mutual-support": "武装力量相互支援奖章",
        "armed-forces-medal-for-distinguished-service": "武装力量杰出服役奖章",
        "armed-forces-medal-for-exemplary-service": "武装力量模范服役奖章",
        "armed-forces-medal-for-exemplary-volunteer-service": "武装力量模范志愿服役奖章",
        "medal-100-years-of-the-restoration-of-the-lithuanian-armed-forces": "立陶宛武装力量恢复100周年奖章",
        "police-guardian-angel-medal": "警察守护天使奖章",
        "police-medal-of-merit": "警察功绩奖章",
        "police-medal-for-impeccable-service": "警察无瑕服役奖章",
        "police-medal-for-duty-performed-in-1991": "警察1991年履职奖章",
        "order-of-the-labour-star": "劳动之星勋章",
        "medal-of-the-labour-star": "劳动之星奖章",
        "firemen-cross": "消防员十字勋章",
        "badge-help-to-the-near": "助人徽章",
        "cross-help-to-the-near": "助人十字勋章",
        "medal-help-to-the-near": "助人奖章",
    },
    "latvia": {
        "order-of-three-stars": "三星勋章",
        "order-of-viesturs": "维斯图尔斯勋章",
        "cross-of-recognition": "荣誉十字勋章",
        "military-order-of-lacplesis": "拉奇普莱西斯军事勋章",
        "order-of-the-red-cross": "红十字勋章",
        "liberation-war-commemorative-medal": "解放战争纪念奖章",
        "medal-of-honourary-recognition": "荣誉认可奖章",
        "medal-for-contribution-to-the-development-of-the-armed-forces": "武装力量发展贡献奖章",
        "commemorative-medal-for-the-promotion-of-latvia-s-accession-to-nato": "促进拉脱维亚加入北约纪念奖章",
        "commemorative-medal-nato-summit-2006": "2006年北约峰会纪念奖章",
        "medal-for-contributions-to-the-development-of-the-security-service": "安全机关发展贡献奖章",
    },
}

CONFIG = {
    "belarus": ("BLR", "白俄罗斯共和国"),
    "lithuania": ("LTU", "立陶宛共和国"),
    "latvia": ("LVA", "拉脱维亚共和国"),
}

# The Wawards object pages frequently expose certificates, cases and portraits
# alongside the medal.  Only these image numbers are admitted to the pictured
# volume.  An empty list means that the page is retained as a candidate with no
# pictured row (there is no standalone complete award image).
KEEP = {
    # Explicit lists are intentional: every raw object page is reviewed so a
    # certificate, presentation case, portrait or ribbon-only image can never
    # enter a pictured row merely because it happened to be the last image.
    "belarus": {
        "hero-of-belarus": [1],
        "order-of-the-fatherland": [1, 2],
        "order-for-promotion-of-peace-and-friendship": [1],
        "order-of-military-glory": [1],
        "order-of-labor-glory": [1],
        "order-for-service-to-the-homeland": [1, 2],
        "order-for-personal-courage": [1],
        "order-of-friendship-of-peoples": [1, 2],
        "order-of-honor": [1],
        "order-of-francysk-skaryna": [1, 2],
        "order-of-mother": [1, 2, 3, 4],
        "medal-for-bravery": [1, 2, 3],
        "medal-for-saved-life": [1, 2],
        "medal-for-distinction-in-military-service": [1, 2],
        "medal-for-distinction-in-the-maintenance-of-public-order": [1, 2, 3],
        "medal-for-distinction-in-the-state-border-protection": [1, 2],
        "medal-for-distinction-in-prevention-and-elimination-of-emergencies": [1, 2],
        "medal-for-labour-merits": [1, 2],
        "medal-of-francysk-skaryna": [1, 2, 3],
        "medal-for-impeccable-service": [1, 2, 3, 4, 5],
        "jubilee-medal-80-years-of-belarusian-police": [1, 2, 3],
        "jubilee-medal-90-years-of-belarusian-police": [1, 2, 3],
        "jubilee-medal-80-years-of-the-state-security-committee": [1, 2, 3],
        "jubilee-medal-90-years-of-the-state-security-bodies": [1, 2, 3],
        "jubilee-medal-80-years-of-the-armed-forces": [1, 2],
        "jubilee-medal-90-years-of-the-armed-forces": [1, 2],
        "jubilee-medal-80-years-of-the-border-troops": [1, 2, 3],
        "jubilee-medal-90-years-of-border-guard": [1, 2],
        "jubilee-medal-150-years-of-fire-service": [1, 2],
        "jubilee-medal-160-years-of-fire-service": [1, 2, 3],
        "jubilee-medal-100-years-of-the-trade-union-movement-of-belarus": [1, 2],
        "jubilee-medal-110-years-of-the-trade-union-movement-of-belarus": [1, 2],
        "jubilee-medal-10th-anniversary-of-the-withdrawal-of-the-soviet-army-from-afghanistan": [1, 2],
        "jubilee-medal-20th-anniversary-of-the-withdrawal-of-the-soviet-army-from-afghanistan": [1, 2],
        "jubilee-medal-115-years-of-the-trade-union-movement-of-belarus": [1],
        "medal-100-years-of-agricultural-and-food-public-administration": [1],
        "jubilee-medal-20-years-of-the-presidents-security-service": [1, 2],
        "jubilee-medal-95-years-of-army-signal-troops": [1, 2],
    },
    "lithuania": {
        "vytis-cross": [1, 2, 3, 4],
        "order-of-vytautas-the-great": [1, 2, 3, 4, 5, 6, 7],
        "order-of-the-vytis-cross": [1, 2, 3, 4, 5, 6, 7, 8],
        "order-of-the-lithuanian-grand-duke-gediminas": [1, 2, 3, 4, 5],
        "order-for-merits-to-lithuania": [1, 2],
        "life-saving-cross": [1, 2, 3],
        "medal-of-the-order-of-vytautas-the-great": [1, 2, 4],
        "medal-of-the-order-of-the-lithuanian-grand-duke-gediminas": [1, 2, 4, 5, 6],
        "medal-of-the-order-of-the-cross-of-vytis": [1],
        "medal-of-the-order-for-merits-to-lithuania": [1],
        "medal-of-the-volunteers-founders-of-the-army": [1, 2, 3, 4],
        "medal-of-lithuanian-independence": [1, 2, 3],
        "medal-of-the-pioneers-of-the-army": [1, 2],
        "medal-of-the-liberation-of-klaipeda": [1, 2],
        "medal-of-13-january": [1, 2],
        "medal-of-darius-and-girenas": [1, 2, 4, 5],
        "riflemen-s-star-decoration": [1, 2, 4, 5],
        "riflemen-s-star-medal": [1, 2, 4, 5],
        "national-defence-system-medal-for-merits": [],
        "national-defence-system-medal-for-merits-for-civilians": [1],
        "national-defence-system-medal-for-distinction": [1, 2],
        "national-defence-system-general-jonas-zemaitis-medal": [1],
        "national-defence-system-medal-for-international-operations": [1],
        "national-defence-system-medal-of-nato-accession": [1],
        "armed-forces-medal-for-merits": [1, 2],
        "armed-forces-medal-for-distinction": [1],
        "armed-forces-wound-medal": [1],
        "armed-forces-medal-for-mutual-support": [1, 2],
        "armed-forces-medal-for-distinguished-service": [1, 2],
        "armed-forces-medal-for-exemplary-service": [1, 2],
        "armed-forces-medal-for-exemplary-volunteer-service": [1, 2],
        "medal-100-years-of-the-restoration-of-the-lithuanian-armed-forces": [],
        "police-guardian-angel-medal": [1, 2],
        "police-medal-of-merit": [1],
        "police-medal-for-impeccable-service": [1],
        "police-medal-for-duty-performed-in-1991": [1],
        "order-of-the-labour-star": [1, 2],
        "medal-of-the-labour-star": [1, 2],
        "firemen-cross": [1],
        "badge-help-to-the-near": [1, 2],
        "cross-help-to-the-near": [1, 2, 3],
        "medal-help-to-the-near": [1, 2],
    },
    "latvia": {
        "order-of-three-stars": [2, 3, 5, 6, 7, 8, 9, 10, 14, 15],
        "order-of-viesturs": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "cross-of-recognition": [1, 2, 3, 4, 5, 7, 8],
        "military-order-of-lacplesis": [2, 3, 4],
        "order-of-the-red-cross": [1, 2, 3, 4, 5, 6, 7, 8],
        "liberation-war-commemorative-medal": [1, 2],
        "medal-of-honourary-recognition": [1, 2],
        "medal-for-contribution-to-the-development-of-the-armed-forces": [1, 2],
        "commemorative-medal-for-the-promotion-of-latvia-s-accession-to-nato": [1, 2],
        "commemorative-medal-nato-summit-2006": [1, 2],
        "medal-for-contributions-to-the-development-of-the-security-service": [1, 2],
    },
}


def display_date(candidates: list[str]) -> str:
    vals = [str(x) for x in candidates if str(x).isdigit()]
    if not vals:
        return "日期待考"
    unique = list(dict.fromkeys(vals))
    if len(unique) == 1:
        return f"{unique[0]}年设立／纪年"
    return f"{unique[0]}年设立；另载{ '、'.join(unique[1:]) }年"


def normalize(scope: str) -> dict[str, int]:
    prefix, country = CONFIG[scope]
    raw_path = ROOT / f"data/raw_candidates/wawards_{scope}.jsonl"
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    stem = f"{scope}_wawards_families"
    image_root = ROOT / f"assets/images/{stem}"
    image_root.mkdir(parents=True, exist_ok=True)
    # The directory is generated solely by this normalizer.  Remove stale
    # certificate/case copies left by an earlier unfiltered pass so the volume
    # directory cannot be mistaken for the published image set.
    for stale in image_root.iterdir():
        if stale.is_file():
            stale.unlink()
    records: list[dict] = []
    images: list[dict] = []
    unpictured: list[dict] = []
    for row in rows:
        slug = Path(urlparse(row["object_url"]).path).stem
        family = f"{prefix}-WA-{slug.upper().replace('-', '_')}"
        record_id = f"{family}-REPRESENTATIVE"
        selected_numbers = KEEP.get(scope, {}).get(slug, [n for n in range(1, len(row.get("original_images", [])) + 1)])
        selected = [row["original_images"][n - 1] for n in selected_numbers if 1 <= n <= len(row.get("original_images", []))]
        if not selected:
            unpictured.append({
                "source_id": row["source_id"],
                "name": NAMES[scope].get(slug, row["page_title"]),
                "date": display_date(row.get("date_candidates", [])),
                "page_url": row["object_url"],
                "status": "有记载但对象页没有独立完整章体图（仅证书／盒／合图）",
            })
            continue
        views = []
        for number, item in enumerate(selected, 1):
            source = ROOT / item["local_path"]
            if not source.is_file():
                raise FileNotFoundError(source)
            with Image.open(source) as im:
                im.verify()
            with Image.open(source) as im:
                width, height = im.size
            suffix = source.suffix.lower() or ".jpg"
            destination = image_root / f"{slug}_{number:02d}{suffix}"
            shutil.copy2(source, destination)
            view_key = f"{record_id}-VIEW{number}"
            views.append({"key": view_key, "label": "完整图样" if number == 1 else f"完整图样·{number}"})
            payload = destination.read_bytes()
            images.append({
                "key": f"{record_id.lower()}-image-{number:02d}",
                "record_id": record_id,
                "view_key": view_key,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "source_page": row["object_url"],
                "image_url": item["image_url"],
                "license": "source-site research use; publication rights not asserted",
                "dimensions": [width, height],
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True,
                "visually_checked": True,
            })
        if not views:
            raise ValueError(f"No complete image for {row['source_id']}")
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": country,
            "name": NAMES[scope].get(slug, row["page_title"]),
            "original": row["page_title"],
            "date": display_date(row.get("date_candidates", [])),
            "variant": "World Awards对象页完整图样组；具体等级／版别待考",
            "views": views,
            "source_ids": [row["source_id"]],
            "image_kind": "catalogue_object_or_illustration",
            "html_eligible": True,
        })
    volume = {"as_of": "2026-09-28", "volume": country, "records": records}
    manifest = {"as_of": "2026-09-28", "images": images, "unpictured_candidates": unpictured}
    (ROOT / f"data/volumes/{stem}.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / f"data/volumes/{stem}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"scope": scope, "object_pages": len(rows), "pictured_families": len(records), "unpictured": len(unpictured), "variants": len(images)}


if __name__ == "__main__":
    for scope in ("belarus", "lithuania", "latvia"):
        print(json.dumps(normalize(scope), ensure_ascii=False))
