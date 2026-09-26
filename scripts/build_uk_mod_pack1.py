import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tmp/uk_us_bulk_20260926/data/volumes/uk_mod_medal_guide_candidate_volume.json"
OUT_DIR = ROOT / "assets/images/uk_mod_pack1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ZH = {
    "GB-UK-ATLANTIC-STAR": "大西洋星章",
    "GB-UK-GULF-MEDAL-1990-1991": "海湾战争奖章（1990–1991）",
    "GB-UK-CONSPICUOUS-GALLANTRY-CROSS-CGC": "杰出英勇十字勋章",
    "GB-UK-KING-S-COMMENDATION-FOR-BRAVERY": "国王英勇嘉奖",
    "GB-UK-ELIZABETH-CROSS": "伊丽莎白十字章",
    "GB-UK-DISTINGUISHED-FLYING-CROSS-DFC": "杰出飞行十字勋章",
    "GB-UK-MENTION-IN-DESPATCHES": "传令嘉奖佩饰",
    "GB-UK-AIR-FORCE-CROSS-AFC": "空军十字勋章",
    "GB-UK-1939-TO-1945-STAR": "1939–1945年星章",
    "GB-UK-AFRICA-STAR": "非洲星章",
    "GB-UK-OPERATIONAL-SERVICE-MEDAL-AFGHANISTAN": "作战服务奖章",
    "GB-UK-OPERATIONAL-SERVICE-MEDAL-DEMOCRATIC-REPUBLIC-OF-CONGO": "作战服务奖章",
    "GB-UK-OPERATIONAL-SERVICE-MEDAL-SIERRA-LEONE": "作战服务奖章",
    "GB-UK-RAF-LSGC-MEDAL": "皇家空军长期服务与良好品行奖章",
    "GB-UK-KING-S-COMMENDATION-FOR-VALUABLE-SERVICE": "国王有价值服务嘉奖",
    "GB-UK-FRANCE-AND-GERMANY-STAR": "法国与德国星章",
    "GB-UK-KINGS-CORONATION-MEDAL-2023": "查尔斯三世加冕奖章",
    "GB-UK-ARMY-LSGC-MEDAL": "陆军长期服务与良好品行奖章",
    "GB-UK-PLATINUM-JUBILEE-MEDAL-2022": "伊丽莎白二世白金禧年奖章",
    "GB-UK-AFRICA-GENERAL-SERVICE-MEDAL": "非洲一般服务奖章",
    "GB-UK-KING-S-COMMENDATION-FOR-BRAVERY-IN-THE-AIR": "国王空中英勇嘉奖",
    "GB-UK-ROYAL-RED-CROSS": "皇家红十字勋章",
    "GB-UK-NAVAL-GENERAL-SERVICE-MEDAL-1915": "海军一般服务奖章（1915）",
    "GB-UK-ACCUMULATED-CAMPAIGN-SERVICE-MEDAL": "累计战役服务奖章",
    "GB-UK-KOREA-MEDAL": "朝鲜战争奖章",
    "GB-UK-EBOLA-MEDAL": "埃博拉疫情服务奖章",
    "GB-UK-DIAMOND-JUBILEE-MEDAL-2012": "伊丽莎白二世钻石禧年奖章",
    "GB-UK-GEORGE-MEDAL-GM": "乔治奖章",
    "GB-UK-KING-S-VOLUNTEER-RESERVES-MEDAL-KVRM": "国王志愿预备役奖章",
    "GB-UK-BURMA-STAR": "缅甸星章",
    "GB-UK-ITALY-STAR": "意大利星章",
    "GB-UK-PACIFIC-STAR-MALAYA-SINGAPORE-AND-THE-PACIFIC-OCEAN": "太平洋星章",
    "GB-UK-KING-S-GALLANTRY-MEDAL-KGM": "国王英勇奖章",
    "GB-UK-GEORGE-CROSS-GC": "乔治十字勋章",
    "GB-UK-ARCTIC-STAR": "北极星章",
    "GB-UK-DEFENCE-MEDAL": "国防奖章",
    "GB-UK-VICTORIA-CROSS-VC": "维多利亚十字勋章",
    "GB-UK-GOLDEN-JUBILEE-MEDAL-2002": "伊丽莎白二世金禧年奖章",
    "GB-UK-CADET-FORCES-MEDAL": "学员部队奖章",
    "GB-UK-SILVER-JUBILEE-MEDAL-1977": "伊丽莎白二世银禧年奖章",
    "GB-UK-DISTINGUISHED-SERVICE-CROSS-DSC": "杰出服务十字勋章",
    "GB-UK-ROYAL-NAVAL-LSGC-MEDAL": "皇家海军长期服务与良好品行奖章",
    "GB-UK-IRAQ-MEDAL": "伊拉克奖章",
    "GB-UK-VOLUNTEER-RESERVES-SERVICE-MEDAL": "志愿预备役服务奖章",
    "GB-UK-AIR-CREW-EUROPE-STAR": "欧洲空勤星章",
    "GB-UK-MILITARY-CROSS-MC": "军功十字勋章",
    "GB-UK-SOUTH-ATLANTIC-MEDAL": "南大西洋奖章",
    "GB-UK-WAR-MEDAL-1939-TO-1945": "1939–1945年战争奖章",
}

DATES = {
    "GB-UK-ATLANTIC-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-GULF-MEDAL-1990-1991": "1990–1991",
    "GB-UK-CONSPICUOUS-GALLANTRY-CROSS-CGC": "1993年设立",
    "GB-UK-ELIZABETH-CROSS": "2009年设立",
    "GB-UK-DISTINGUISHED-FLYING-CROSS-DFC": "1918年设立",
    "GB-UK-AIR-FORCE-CROSS-AFC": "1918年设立",
    "GB-UK-1939-TO-1945-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-AFRICA-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-FRANCE-AND-GERMANY-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-KINGS-CORONATION-MEDAL-2023": "2023",
    "GB-UK-PLATINUM-JUBILEE-MEDAL-2022": "2022",
    "GB-UK-ROYAL-RED-CROSS": "1883年设立；图示二等",
    "GB-UK-NAVAL-GENERAL-SERVICE-MEDAL-1915": "1915年设立",
    "GB-UK-KOREA-MEDAL": "1950–1953",
    "GB-UK-EBOLA-MEDAL": "2015年设立",
    "GB-UK-DIAMOND-JUBILEE-MEDAL-2012": "2012",
    "GB-UK-GEORGE-MEDAL-GM": "1940年设立",
    "GB-UK-BURMA-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-ITALY-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-PACIFIC-STAR-MALAYA-SINGAPORE-AND-THE-PACIFIC-OCEAN": "第二次世界大战时期（1939–1945）",
    "GB-UK-GEORGE-CROSS-GC": "1940年设立",
    "GB-UK-ARCTIC-STAR": "2012年设立；奖励第二次世界大战北极航线服役",
    "GB-UK-DEFENCE-MEDAL": "第二次世界大战时期（1939–1945）",
    "GB-UK-VICTORIA-CROSS-VC": "1856年设立",
    "GB-UK-GOLDEN-JUBILEE-MEDAL-2002": "2002",
    "GB-UK-CADET-FORCES-MEDAL": "1950年设立",
    "GB-UK-SILVER-JUBILEE-MEDAL-1977": "1977",
    "GB-UK-DISTINGUISHED-SERVICE-CROSS-DSC": "1901年设立",
    "GB-UK-IRAQ-MEDAL": "2003年设立",
    "GB-UK-AIR-CREW-EUROPE-STAR": "第二次世界大战时期（1939–1945）",
    "GB-UK-MILITARY-CROSS-MC": "1914年设立",
    "GB-UK-SOUTH-ATLANTIC-MEDAL": "1982年设立",
    "GB-UK-WAR-MEDAL-1939-TO-1945": "第二次世界大战时期（1939–1945）",
}

def clean(text):
    return (text or "").replace("鈥?", "—").replace("鈥檚", "’s").replace("閳ユ獨", "’s")

def public_family(fid, variant_name):
    if fid.startswith("GB-UK-OPERATIONAL-SERVICE-MEDAL-"):
        return "GB-UK-OPERATIONAL-SERVICE-MEDAL"
    if fid == "GB-UK-GENERAL-SERVICE-MEDAL":
        if "1918" in variant_name:
            return "GB-UK-GENERAL-SERVICE-MEDAL-1918"
        if "1962" in variant_name:
            return "GB-UK-GENERAL-SERVICE-MEDAL-1962"
        return "GB-UK-GENERAL-SERVICE-MEDAL-2008"
    return fid

def chinese_name(fid, variant_name):
    if fid == "GB-UK-GENERAL-SERVICE-MEDAL":
        return "一般服务奖章（" + ("1918" if "1918" in variant_name else "1962" if "1962" in variant_name else "2008") + "）"
    return ZH[fid]

data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
records, images = [], []
for family in data["award_families"]:
    fid = family["award_family_id"]
    for variant in family["variants"]:
        accepted = [x for x in variant.get("image_records", []) if x.get("eligible_as_complete_illustration")]
        if not accepted:
            continue
        image = accepted[0]
        source_path = ROOT / image["local_path"]
        suffix = source_path.suffix.lower() or ".jpg"
        target_name = variant["variant_id"].lower().replace("-v-", "--") + suffix
        target = OUT_DIR / target_name
        shutil.copy2(source_path, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest.lower() != image["sha256"].lower():
            raise ValueError(f"checksum mismatch: {source_path}")
        variant_name = clean(variant["variant_name"])
        pfamily = public_family(fid, variant_name)
        name = chinese_name(fid, variant_name)
        date = DATES.get(fid, "制度日期待核；英国国防部现行指南收录")
        if fid == "GB-UK-GENERAL-SERVICE-MEDAL":
            date = variant_name.replace("General Service Medal ", "")
        theatre = ""
        if pfamily == "GB-UK-OPERATIONAL-SERVICE-MEDAL":
            theatre = variant_name.replace("Operational Service Medal — ", "")
        label = (theatre + "战区型；" if theatre else "") + "英国国防部页面所示完整章体；官方页面参考图；低清参考"
        if "Class II" in variant_name:
            label = "二等；英国国防部页面所示完整章体；官方页面参考图；低清参考"
        if "Kenya Clasp" in variant_name:
            label = "肯尼亚扣饰型；英国国防部页面所示完整章体；官方页面参考图；低清参考"
        key = variant["variant_id"] + "-IMAGE"
        records.append({
            "id": variant["variant_id"], "family": pfamily, "name": name,
            "original": clean(variant["source_name"]), "date": date, "variant": label,
            "views": [{"key": key, "label": "完整章体（英国国防部官方页面参考图）"}],
            "source_ids": ["uk-mod-medal-guide"],
        })
        images.append({
            "view_key": key, "local_path": target.relative_to(ROOT).as_posix(),
            "source_page": data["source_page"], "direct_image_url": image["direct_image_url"],
            "width": image["width_px"], "height": image["height_px"], "sha256": digest,
            "rights": image["rights_status"],
        })

volume = {
    "as_of": "2026-09-26", "volume": "英国：国防部勋奖章指南首包",
    "scope": "英国国防部现行指南整页扫描；仅纳入已逐图确认章体完整的条目。",
    "records": records,
    "notes": [
        "同一章种的等级、时期版型、战区型、扣饰和微型章归入同一family；不按图片数量虚增章种。",
        "三种Operational Service Medal战区型归入同一章种；三代General Service Medal因制度上为不同授奖章种而分开。",
        "来源图用于离线研究图鉴；不据官方页面照片保证所摄实物真伪或材质。",
    ],
}
manifest = {
    "volume": volume["volume"], "as_of": "2026-09-26",
    "records_file": "data/volumes/uk_mod_pack1.json",
    "image_directory": "assets/images/uk_mod_pack1/",
    "counts": {
        "distinct_award_families": len({x["family"] for x in records}),
        "variant_rows": len(records), "complete_image_files": len(images),
    },
    "images": images,
    "source_coverage": data["source_coverage"],
    "rejected_incomplete_images": data["counts"]["rejected_incomplete_images"],
}
(ROOT / "data/volumes/uk_mod_pack1.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "data/volumes/uk_mod_pack1_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest["counts"], ensure_ascii=False))
