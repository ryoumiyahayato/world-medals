import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "data/staging/europe_central_west_2026-09-26"
SRC = json.loads((STAGE / "normalized_draft/italy_kingdom_seed_volume.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets/images/italy_crown_pack1"
OUT.mkdir(parents=True, exist_ok=True)

records, images = [], []
for variant in SRC["variants"]:
    source = STAGE / variant["local_file"]
    target = OUT / variant["filename"].lower()
    shutil.copy2(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != variant["sha256"]:
        raise ValueError(variant["variant_id"])
    key = variant["variant_id"] + "-VIEW"
    records.append({
        "id": variant["variant_id"], "family": SRC["family_id"], "name": SRC["name_zh"],
        "original": SRC["name_original"],
        "date": "1868年2月20日设立；1868年3月22日生效",
        "variant": variant["grade_note_zh"],
        "views": [{"key": key, "label": "历史官方图版·1868"}],
        "source_ids": ["italy-rd-4251-1868", variant["file_page"]],
    })
    images.append({
        "view_key": key, "local_path": target.relative_to(ROOT).as_posix(),
        "source_page": variant["file_page"], "direct_image_url": variant["original_file"],
        "width": variant["width"], "height": variant["height"], "sha256": digest,
        "license": variant["license"],
    })

volume = {
    "as_of": "2026-09-26", "volume": "意大利王国：意大利王冠勋章首包",
    "scope": "1868年设立法令及其历史官方图版；所有等级图式归入同一独立章种。",
    "records": records,
    "notes": ["骑士、官员、指挥官、大官、大绶级十字章和星章均为意大利王冠勋章的等级／版型，不拆为独立章种。"],
}
manifest = {
    "as_of": "2026-09-26", "volume": volume["volume"],
    "records_file": "data/volumes/italy_crown_pack1.json", "image_directory": "assets/images/italy_crown_pack1/",
    "counts": {"distinct_award_families": 1, "variant_rows": len(records), "complete_image_files": len(images), "historical_official_plates": len(images)},
    "images": images,
    "source_coverage": "MedalBook意大利王国/撒丁王国目录5/5分页及343/343对象页已扫描；商业图片仅作候选线索。",
}
(ROOT / "data/volumes/italy_crown_pack1.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "data/volumes/italy_crown_pack1_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest["counts"], ensure_ascii=False))
