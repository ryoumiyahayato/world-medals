from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src_volume = ROOT / "data/volumes/finland_orders_pack1_2026-09-26.json"
src_manifest = ROOT / "data/volumes/finland_orders_pack1_2026-09-26_manifest.json"
out_volume = ROOT / "data/volumes/finland_orders_pack1.json"
out_manifest = ROOT / "data/volumes/finland_orders_pack1_manifest.json"


def main() -> None:
    volume = json.loads(src_volume.read_text(encoding="utf-8"))
    manifest = json.loads(src_manifest.read_text(encoding="utf-8"))
    image_by_path = {item["volume_path"]: item for item in manifest["images"]}
    records = []
    images = []
    for source_row in volume["rows"]:
        name_date = source_row["name_date"].split("；")
        name = name_date[0]
        original = name_date[1] if len(name_date) > 1 else ""
        date = "；".join(name_date[2:]) if len(name_date) > 2 else "日期待考"
        view_key = source_row["variant_id"] + "-IMAGE"
        records.append({
            "id": source_row["variant_id"],
            "family": source_row["award_family_id"],
            "country_zh": "芬兰共和国",
            "issuer": source_row["issuer"],
            "name": name,
            "original": original,
            "date": date,
            "variant": f"{source_row['grade_variant']}；{source_row['image_kind']}",
            "views": [{"key": view_key, "label": "官方图式" if "官方图式" in source_row["image_kind"] else "完整正面"}],
            "source_ids": source_row["source_ids"],
            "image_kind": "official_design" if "官方图式" in source_row["image_kind"] else "specimen_photo",
            "html_eligible": True,
            "internal_notes": source_row["image_credit"],
        })
        meta = image_by_path[source_row["image"]]
        images.append({
            "view_key": view_key,
            "local_path": source_row["image"],
            "source_page": meta["source_page"],
            "direct_image_url": meta.get("original_url"),
            "width": meta["dimensions_px"][0],
            "height": meta["dimensions_px"][1],
            "sha256": meta["sha256"],
            "rights": f"{meta['license']}; {meta['license_note']}",
        })
    normalized_volume = {
        "as_of": volume["as_of"],
        "volume": "芬兰共和国国家勋团首包",
        "scope": volume["scope"],
        "records": records,
    }
    normalized_manifest = {
        "volume": normalized_volume["volume"],
        "as_of": volume["as_of"],
        "records_file": out_volume.relative_to(ROOT).as_posix(),
        "image_directory": "assets/images/finland_orders_pack1_2026-09-26/",
        "counts": {
            "distinct_award_families": len({row["family"] for row in records}),
            "variant_rows": len(records),
            "complete_image_files": len(images),
            "physical_photo_views": sum(1 for row in records if row["image_kind"] == "specimen_photo"),
            "official_diagram_views": sum(1 for row in records if row["image_kind"] == "official_design"),
        },
        "images": images,
    }
    out_volume.write_text(json.dumps(normalized_volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_manifest.write_text(json.dumps(normalized_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"normalized {len(records)} records and {len(images)} images")


if __name__ == "__main__":
    main()
