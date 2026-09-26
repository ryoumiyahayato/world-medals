import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "data" / "volumes" / "germany_1933_1945_gap_round1_2026-09-26_manifest.json"

manifest = json.loads(MAN.read_text(encoding="utf-8"))
images = []
for entry in manifest.get("entries", []):
    for key in entry.get("view_keys", []):
        images.append(
            {
                "view_key": key,
                "local_path": entry["local_path"],
                "source_page": entry.get("source_page", ""),
                "direct_image_url": entry.get("original_url", ""),
                "width": entry.get("width"),
                "height": entry.get("height"),
                "sha256": entry.get("sha256", ""),
                "license": entry.get("license", "见来源页"),
                "creator": entry.get("creator", "见来源页"),
            }
        )
manifest["images"] = images
MAN.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"image_mappings": len(images), "files": len({i['local_path'] for i in images})})
