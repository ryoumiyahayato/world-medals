import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "tmp/uk_us_bulk_20260926/us_batch1"
SRC = json.loads((BATCH / "data/volumes/us_nhhc_candidate_volume_20260926.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "assets/images/us_nhhc_pack1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAME_OVERRIDES = {
    "US-SMM-1901": "特别优异服役奖章",
}
VARIANT_ZH = {
    "US-BSM-1944-V-PLAIN": "标准悬挂式；正面",
    "US-DFC-1926-V-STANDARD": "标准悬挂式十字章；正面",
    "US-PH-1932-V-OBVERSE": "1932年后奖章式；正面",
    "US-SSM-1932-V-STANDARD": "1932年改制奖章式；正面",
    "US-NGCM-1869-V-TYPE-I": "I型马耳他十字式",
    "US-MANILA-BAY-1898-V-AH-FOY": "USS Olympia水兵Ah Foy受授实物；正背面",
    "US-SAMPSON-1901-V-NEW-YORK": "U.S.S. New York舰名扣饰型；Feinbloom藏品正背面",
    "US-SMM-1901-V-BRONZE": "铜质悬挂十字式；正面",
}

records, images = [], []
for family in SRC["award_families"]:
    for variant in family["variants"]:
        image_records = [x for x in variant.get("image_records", []) if x.get("decoded")]
        if not image_records:
            continue
        views = []
        for index, image in enumerate(image_records, start=1):
            source = BATCH / image["local_path"]
            target = OUT_DIR / (variant["variant_id"].lower() + f"-{index}" + source.suffix.lower())
            shutil.copy2(source, target)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest.lower() != image["sha256"].lower():
                raise ValueError(f"checksum mismatch: {source}")
            key = variant["variant_id"] + f"-VIEW-{index}"
            label = image.get("view") or ("完整正面" if index == 1 else "完整背面")
            views.append({"key": key, "label": "完整实物图·" + label})
            images.append({
                "view_key": key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": image["source_page"], "direct_image_url": image["direct_image_url"],
                "width": image["width_px"], "height": image["height_px"], "sha256": digest,
                "rights": image["rights_status"],
            })
        records.append({
            "id": variant["variant_id"], "family": family["award_family_id"],
            "name": NAME_OVERRIDES.get(family["award_family_id"], family["chinese_name"]),
            "original": variant["source_name"], "date": variant["date_or_period"],
            "variant": VARIANT_ZH.get(variant["variant_id"], variant["variant_name"]) + "；美国海军历史与遗产司令部／国家档案来源",
            "views": views, "source_ids": family["source_ids"],
        })

volume = {
    "as_of": "2026-09-26", "volume": "美国联邦军事奖励：NHHC/NARA首包",
    "scope": "美国海军历史与遗产司令部可见目录37个直系页面及4个补充馆藏／档案页面的首批正式差集。",
    "records": records,
    "notes": [
        "同一章种的前身、设计改制、舰名扣饰和具体受授实物保持在family下作为variant；不按图片数量增加章种。",
        "仅纳入完整章体；颁授仪式照、横幅、裁切图及尚未辨明版型的低清图继续留在候选区。",
    ],
}
manifest = {
    "as_of": "2026-09-26", "volume": volume["volume"],
    "records_file": "data/volumes/us_nhhc_pack1.json", "image_directory": "assets/images/us_nhhc_pack1/",
    "counts": {"distinct_award_families": len({x["family"] for x in records}), "variant_rows": len(records), "complete_image_files": len(images)},
    "images": images, "source_coverage": SRC["source_coverage"],
}
(ROOT / "data/volumes/us_nhhc_pack1.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "data/volumes/us_nhhc_pack1_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest["counts"], ensure_ascii=False))
