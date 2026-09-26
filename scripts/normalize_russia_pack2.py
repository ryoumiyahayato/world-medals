"""Normalize the isolated Russia pack 2 into the catalogue build schema."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / "data/volumes/russia_bulk_pack2_2026-09-26.json").read_text(encoding="utf-8"))
manifest_source = json.loads((ROOT / "data/volumes/russia_bulk_pack2_2026-09-26_manifest.json").read_text(encoding="utf-8"))

family_by_id = {item["family_id"]: item for item in source["families"]}
records = []
for variant in source["variants"]:
    family = family_by_id[variant["family_id"]]
    image_id = variant["image_ids"][0]
    records.append({
        "id": variant["variant_id"],
        "family": variant["family_id"],
        "name": family["names"][1],
        "original": family["names"][0],
        "date": f"{family['establishment_date']}设立",
        "variant": f"{variant['label_zh']}；{variant['image_type']}；{variant['variant_status']}",
        "views": [{"key": image_id, "label": "完整实物正面"}],
        "source_ids": family["evidence"],
    })

normalized = {
    "as_of": source["as_of"],
    "volume": "苏联：来源优先批次二",
    "scope": source["scope"],
    "records": records,
    "notes": source["formalization_notes"],
}
manifest = {
    "as_of": manifest_source["as_of"],
    "volume": manifest_source["volume"],
    "images": [
        {
            "view_key": image["image_id"],
            "local_path": image["local_path"].replace(
                "assets/raw/russia_normalization_pack2/",
                "assets/images/russia_normalization_pack2/",
            ),
        }
        for image in manifest_source["images"]
    ],
    "rights_review": manifest_source["rights_review"],
}

(ROOT / "data/volumes/russia_bulk_pack2.json").write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "data/volumes/russia_bulk_pack2_manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
