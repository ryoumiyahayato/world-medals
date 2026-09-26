"""Normalize the isolated Russia pack 3 into the catalogue build schema."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / "data/volumes/russia_bulk_pack3_2026-09-26.json").read_text(encoding="utf-8"))
manifest_source = json.loads((ROOT / "data/volumes/russia_bulk_pack3_2026-09-26_manifest.json").read_text(encoding="utf-8"))

records = []
for family in source["records"]:
    image_row = family["image_row"]
    records.append({
        "id": image_row["variant_id"], "family": family["family_id"],
        "name": family["names"][1], "original": family["names"][0],
        "date": f"{family['establishment_date']}设立",
        "variant": f"{image_row['label_zh']}；{image_row['image_type']}；{image_row['status']}",
        "views": [{"key": image_row["image_id"], "label": "完整实物正面"}],
        "source_ids": [item["url"] for item in family["evidence"]],
    })

normalized = {"as_of": source["as_of"], "volume": "苏联：来源优先批次三", "scope": source["scope"], "records": records, "notes": source["formalization_notes"]}
manifest = {
    "as_of": manifest_source["as_of"], "volume": manifest_source["volume"],
    "images": [
        {"view_key": image["image_id"], "local_path": image["local_path"].replace("assets/raw/russia_bulk_pack3_2026-09-26/", "assets/images/russia_bulk_pack3_2026-09-26/")}
        for image in manifest_source["images"] if image.get("accepted_for_body_record")
    ],
    "rights_review": manifest_source["rights_review"],
}
(ROOT / "data/volumes/russia_bulk_pack3.json").write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/volumes/russia_bulk_pack3_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
