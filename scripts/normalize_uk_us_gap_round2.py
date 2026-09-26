import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOL = ROOT / "data" / "volumes" / "uk_us_gap_round2_2026-09-26.json"
MAN = ROOT / "data" / "volumes" / "uk_us_gap_round2_2026-09-26_manifest.json"


volume = json.loads(VOL.read_text(encoding="utf-8"))
manifest = json.loads(MAN.read_text(encoding="utf-8"))
by_id = {item["record_id"]: item for item in manifest["images"]}
normalized_images = []

for record in volume["records"]:
    item = by_id[record["id"]]
    key = record["id"] + "-VIEW-1"
    local_path = record["image"]
    path = ROOT / local_path
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != item["sha256"].lower():
        raise RuntimeError(f"hash mismatch: {record['id']}")
    record["country_zh"] = record.pop("country")
    record["views"] = [{"key": key, "label": record.get("image_kind") or "完整图样"}]
    normalized_images.append(
        {
            "view_key": key,
            "local_path": local_path,
            "source_page": record.get("source_page", ""),
            "direct_image_url": record.get("image_source_url", ""),
            "width": item["width"],
            "height": item["height"],
            "sha256": digest,
            "license": record.get("rights", "见来源页"),
            "creator": "见来源页",
        }
    )

manifest["images"] = normalized_images
manifest["counts"] = {
    "distinct_award_families": len({r["family"] for r in volume["records"]}),
    "variant_rows": len(volume["records"]),
    "complete_image_files": len(normalized_images),
}
VOL.write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
MAN.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(manifest["counts"])
