import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "data/volumes/russia_bulk_pack1_2026-09-26.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "data/volumes/russia_bulk_pack1_2026-09-26_manifest.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/russia_pack1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAMES = {
    "RUS-IMP-ORD-01": ("圣安德烈使徒勋章", "Орден Святого Андрея Первозванного", "1698年设立"),
    "RUS-IMP-ORD-05": ("圣乔治勋章", "Орден Святого Георгия", "1769年设立"),
    "RUS-IMP-MED-RUSSO-JAPANESE": ("日俄战争纪念奖章", "Медаль «В память русско-японской войны»", "1906年设立；纪念1904–1905年战争"),
    "USSR-ORD-01": ("列宁勋章", "Орден Ленина", "1930年设立"),
    "USSR-ORD-04": ("红旗勋章", "Орден Красного Знамени", "苏联章种1924年设立；其前身可追溯至1918年"),
    "USSR-ORD-05": ("苏沃洛夫勋章", "Орден Суворова", "1942年设立"),
    "USSR-MED-04": ("勇敢奖章", "Медаль «За отвагу»", "1938年设立"),
    "RUS-FED-MED-01": ("勇敢奖章", "Медаль «За отвагу»", "1994年设立"),
    "RUS-FED-MED-02": ("英勇奖章", "Медаль «За храбрость»", "2023年3月23日设立"),
}
PERIOD = {
    "RUS-IMP": "russian_empire",
    "USSR": "soviet_union",
    "RUS-FED": "russian_federation",
}
images_by_id = {x["image_id"]: x for x in MAN["images"]}
families = {x["family_id"]: x for x in SRC["families"]}
records_by_period = {value: [] for value in PERIOD.values()}
manifest_images_by_period = {value: [] for value in PERIOD.values()}

for variant in SRC["variants"]:
    fid = variant["family_id"]
    name, original, date = NAMES[fid]
    period = next(value for prefix, value in PERIOD.items() if fid.startswith(prefix))
    views = []
    for image_id in variant["image_ids"]:
        image = images_by_id[image_id]
        source_path = ROOT / image["local_path"]
        target = OUT_DIR / (image_id.lower() + source_path.suffix.lower())
        shutil.copy2(source_path, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest.lower() != image["sha256"].lower():
            raise ValueError(f"checksum mismatch: {image_id}")
        label = "完整" + ("官方图式" if variant["image_type"] == "官方图式" else "实物图")
        if len(variant["image_ids"]) > 1:
            label += "（独立视图；不保证为同一实物）"
        key = image_id + "-VIEW"
        views.append({"key": key, "label": label})
        manifest_images_by_period[period].append({
            "view_key": key, "local_path": target.relative_to(ROOT).as_posix(),
            "source_page": image["source_page_url"], "direct_image_url": image["original_file_url"],
            "width": image["width_px"], "height": image["height_px"], "sha256": digest,
            "license": image["license_as_shown_on_page"], "creator": image["creator_or_author"],
        })
    note = variant["label_zh"] + "；" + variant["image_type"]
    if "低清" in variant["variant_status"]:
        note += "；低清参考"
    if "UNSPECIFIED" in variant["variant_id"]:
        note += "；具体时期版型待考，暂归入同名章种"
    records_by_period[period].append({
        "id": variant["variant_id"], "family": fid, "name": name, "original": original,
        "date": date, "variant": note, "views": views,
        "source_ids": ["russia-bulk-pack1", *families[fid]["evidence"]],
    })

TITLES = {
    "russian_empire": "俄罗斯帝国：来源优先首包",
    "soviet_union": "苏联：来源优先首包",
    "russian_federation": "俄罗斯联邦：来源优先首包",
}
for period, records in records_by_period.items():
    volume_path = ROOT / f"data/volumes/{period}_pack1.json"
    manifest_path = ROOT / f"data/volumes/{period}_pack1_manifest.json"
    volume = {
        "as_of": "2026-09-26", "volume": TITLES[period],
        "scope": "俄罗斯三时期来源优先首包中的对应授奖主体；同一章种的等级与版型保持在同一family。",
        "records": records,
        "notes": ["具体版型未确定的实物按同名章种收录并明确标待考，不拆成新的独立章种。"],
    }
    manifest = {
        "as_of": "2026-09-26", "volume": TITLES[period],
        "records_file": volume_path.relative_to(ROOT).as_posix(),
        "image_directory": "assets/images/russia_pack1/",
        "counts": {"distinct_award_families": len({x["family"] for x in records}), "variant_rows": len(records), "complete_image_files": len(manifest_images_by_period[period])},
        "images": manifest_images_by_period[period],
    }
    volume_path.write_text(json.dumps(volume, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {"families": len({x['family'] for x in v}), "variants": len(v), "images": len(manifest_images_by_period[k])} for k, v in records_by_period.items()}, ensure_ascii=False))
