"""Build a large Italy package from the already-completed MedalBook source sweep.

This script deliberately selects distinct formal/state award families.  It does not
rescan listing pages and it does not promote grades, obverse/reverse views, ribbons,
or unit souvenir pieces to separate families.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/staging/europe_central_west_2026-09-26/raw_candidates/medalbook_italy_kingdom.jsonl"
OUT = ROOT / "assets/images/italy_medalbook_pack4_2026-09-26"
OUT.mkdir(parents=True, exist_ok=True)

# family key -> Chinese working name.  These are distinct state/formal award
# families; known earlier packs and the unofficial divisional souvenir crosses
# are intentionally absent.
SELECTED = {
    "IT-SAR-KOI-AERONAUTIC-VALOUR-MEDAL": "航空勇敢勋章",
    "IT-SAR-KOI-AIR-FORCE-LONG-SERVICE-MEDAL": "空军长期服役奖章",
    "IT-SAR-KOI-CHINA-CAMPAIGN-MEDAL": "中国战役奖章",
    "IT-SAR-KOI-COMMEMORATIVE-MEDAL-FOR-MILITARY-CAMPAIGNS-IN-EAST-AFRICA": "东非军事战役纪念章",
    "IT-SAR-KOI-COMMEMORATIVE-MEDAL-FOR-THE-ALBANIA-CAMPAIGN": "阿尔巴尼亚战役纪念章",
    "IT-SAR-KOI-COMMEMORATIVE-MEDAL-FOR-THE-EXPEDITION-TO-FIUME": "阜姆远征纪念章",
    "IT-SAR-KOI-COMMEMORATIVE-MEDAL-FOR-THE-ITALY-BRAZIL-ATLANTIC-CROSSING": "意大利—巴西大西洋飞越纪念章",
    "IT-SAR-KOI-COMMEMORATIVE-MEDAL-FOR-THE-LIBYA-CAMPAIGNS": "利比亚战役纪念章",
    "IT-SAR-KOI-COMMEMORATIVE-MERIT-FOR-THE-MESSINA-EARTHQUAKE": "墨西拿地震功绩纪念章",
    "IT-SAR-KOI-CROSS-FOR-MILITARY-VALOUR": "军事勇敢十字章",
    "IT-SAR-KOI-ITALIAN-RED-CROSS-MEDAL-OF-MERIT": "意大利红十字会功绩奖章",
    "IT-SAR-KOI-LONG-SERVICE-CROSS": "长期服役十字章",
    "IT-SAR-KOI-MEDAL-FOR-THE-AFRICA-CAMPAIGN": "非洲战役奖章",
    "IT-SAR-KOI-MEDAL-FOR-THE-CRIMEA-CAMPAIGN": "克里米亚战役奖章",
    "IT-SAR-KOI-MEDAL-FOR-THE-LIBERATION-OF-SICILY": "西西里解放奖章",
    "IT-SAR-KOI-MEDAL-FOR-THE-WAR-OF-INDEPENDENCE-AND-THE-UNIFICATION-OF-ITALY": "独立战争与意大利统一奖章",
    "IT-SAR-KOI-MEDAL-FOR-WAR-DISABLED": "战争伤残人员奖章",
    "IT-SAR-KOI-MEDAL-OF-HONOUR-FOR-MOTHERS-OF-LARGE-FAMILIES": "多子女母亲荣誉奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-FOR-AIR-FORCE-PIONEERS": "空军先驱功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-FOR-LONG-SERVICE-IN-THE-ROYAL-GUARD-OF-FINANCE": "皇家财政卫队长期服役功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-FOR-PUBLIC-HEALTH": "公共卫生功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-FOR-SERVICE-IN-NATIONAL-FIRE-BRIGADES": "国家消防队服役功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-FOR-VOLUNTEERS": "志愿人员功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-MERIT-OF-LONG-COMMAND-OF-THE-ROYAL-ARMY": "皇家陆军长期指挥功绩奖章",
    "IT-SAR-KOI-MEDAL-OF-NATIONAL-GRATITUDE-TO-MOTHERS-OF-THE-FALLEN": "国家致阵亡者母亲感恩奖章",
    "IT-SAR-KOI-MERIT-CROSS-FOR-LONG-SERVICE-IN-THE-FINANCIAL-POLICE": "财政警察长期服役功绩十字章",
    "IT-SAR-KOI-MERIT-OF-MEDAL-FOR-THE-MARSICA-EARTHQUAKE": "马尔西卡地震功绩奖章",
    "IT-SAR-KOI-MILITARY-MERIT-MAURITIANA-MEDAL": "毛里齐亚纳军事功绩奖章",
    "IT-SAR-KOI-NAVAL-MEDAL-OF-HONOUR-FOR-LONG-SERVICE": "海军长期服役荣誉奖章",
    "IT-SAR-KOI-PANTHEON-MEDAL-FOR-THE-HONOUR-GUARD": "万神殿荣誉卫队奖章",
    "IT-SAR-KOI-RED-CROSS-MEDAL-FOR-VOLUNTARY-NURSES": "红十字会志愿护士奖章",
    "IT-SAR-KOI-ROYAL-HOUSE-REMEMBRANCE-MEDAL": "王室纪念奖章",
    "IT-SAR-KOI-STAR-OF-RURAL-MERIT": "乡村功绩星章",
    "IT-SAR-KOI-CIVIL-ORDER-OF-SAVOY": "萨伏依民事勋章",
    "IT-SAR-KOI-TYPE-I-1815-1855": "萨伏依军事勋章",
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def institution_date(text: str) -> str:
    match = re.search(r"date of institution\s+(.{1,100}?)(?:makers|History)", text, re.I | re.S)
    if not match:
        return "设立日期待考"
    value = re.sub(r"\s+", " ", match.group(1)).strip(" .")
    value = re.sub(r"\s+remarks.*$", "", value, flags=re.I)
    return f"目录所记设立日期：{value}" if value else "设立日期待考"


rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
grouped: dict[str, list[dict]] = {}
for row in rows:
    grouped.setdefault(row["family_key_candidate"], []).append(row)

records = []
images = []
sources = []
used_hashes: set[str] = set()

for number, (family_key, name_zh) in enumerate(SELECTED.items(), 9):
    candidates = grouped.get(family_key, [])
    # Pick the first precise variant that actually has object images.
    selected = next((r for r in candidates if any("/attachments/" in x.get("url", "") and x.get("alt") for x in r.get("image_candidates", []))), None)
    if not selected:
        raise RuntimeError(f"No illustrated candidate for {family_key}")
    attachments = [x for x in selected["image_candidates"] if "/attachments/" in x.get("url", "") and x.get("alt")]
    # Prefer an explicit obverse/reverse pair; otherwise retain only the first
    # full object view.  A ribbon-only candidate is never accepted here.
    ordered = sorted(attachments, key=lambda x: (0 if re.search(r"obverse|front", x.get("alt", ""), re.I) else 1 if re.search(r"reverse|back", x.get("alt", ""), re.I) else 2))
    chosen = []
    for item in ordered:
        if re.search(r"ribbon\s*(only)?$|ribbon bar", item.get("alt", ""), re.I):
            continue
        side = "front" if re.search(r"obverse|front", item.get("alt", ""), re.I) else "back" if re.search(r"reverse|back", item.get("alt", ""), re.I) else "view"
        if any(x[0] == side for x in chosen):
            continue
        chosen.append((side, item))
        if len(chosen) == 2:
            break
    if not chosen:
        raise RuntimeError(f"No acceptable object view for {family_key}")

    family_id = f"IT-KOI-{number:03d}"
    variant_id = f"{family_id}-V01"
    views = []
    for view_no, (side, item) in enumerate(chosen, 1):
        url = item["url"]
        suffix = Path(unquote(urlparse(url).path)).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            suffix = ".jpg"
        target = OUT / f"{variant_id.lower()}-{view_no}{suffix}"
        if not target.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 world-medals research catalogue"})
            with urllib.request.urlopen(request, timeout=45) as response:
                target.write_bytes(response.read())
        with Image.open(target) as im:
            im.verify()
        with Image.open(target) as im:
            width, height = im.size
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        # Duplicates within the same package usually mean the wrong generic
        # catalogue image, so fail rather than silently reusing it.
        if digest in used_hashes:
            raise RuntimeError(f"Duplicate image payload in pack: {url}")
        used_hashes.add(digest)
        view_key = f"{variant_id}-VIEW-{view_no}"
        label = "完整实物图·正面" if side == "front" else "完整实物图·背面" if side == "back" else "完整实物图"
        views.append({"key": view_key, "label": label})
        images.append({
            "view_key": view_key,
            "local_path": target.relative_to(ROOT).as_posix(),
            "source_page": selected["source_page"],
            "direct_image_url": url,
            "width": width,
            "height": height,
            "sha256": digest,
            "rights": "商业专题目录图片；仅保留作本地研究图鉴，未主张公开再利用许可。",
        })
    variant_title = selected["variant_name_candidate"]
    records.append({
        "id": variant_id,
        "family": family_id,
        "name": name_zh,
        "original": variant_title,
        "date": institution_date(selected["object_page_text_excerpt"]),
        "variant": f"{variant_title}；目录所示具体等级／版型；章体完整；商业目录图像，仅限本地研究",
        "views": views,
        "source_ids": ["medalbook_italy_kingdom_complete_sweep"],
    })
    sources.append({
        "family": family_id,
        "candidate_family_key": family_key,
        "source_page": selected["source_page"],
        "source_excerpt": selected["object_page_text_excerpt"][:1200],
        "accessed": selected.get("accessed", "2026-09-26"),
    })

volume = {
    "as_of": "2026-09-26",
    "volume": "撒丁王国／意大利王国：MedalBook目录正式奖励第四包",
    "scope": "复用已完成的5页、343对象页整库扫描；本包只取正式国家或法定机构奖励，不含部队私人纪念章。",
    "records": records,
    "notes": [
        "同一勋奖章的等级、材质和正背面保持在同一family／variant下，不按图片数增加章种。",
        "正文只采用完整章体视图；单独绶带、勋略和通用站点图片均被脚本排除。",
    ],
}
manifest = {
    "as_of": "2026-09-26",
    "volume": volume["volume"],
    "records_file": "data/volumes/italy_medalbook_pack4_2026-09-26.json",
    "image_directory": "assets/images/italy_medalbook_pack4_2026-09-26/",
    "counts": {"distinct_award_families": len({r["family"] for r in records}), "variant_rows": len(records), "complete_image_files": len(images)},
    "images": images,
    "source_coverage": "MedalBook Kingdom of Sardinia & Kingdom of Italy existing complete sweep: 5/5 listing pages and 343/343 distinct object pages; 35 additional formal-family groups normalized in this package.",
}

(ROOT / "data/volumes/italy_medalbook_pack4_2026-09-26.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/italy_medalbook_pack4_2026-09-26_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/italy_medalbook_pack4_2026-09-26_sources.json").write_text(json.dumps({"as_of": "2026-09-26", "sources": sources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest["counts"], ensure_ascii=False))
