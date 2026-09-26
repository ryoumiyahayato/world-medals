from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_sudan.jsonl"
OUT = ROOT / "data/image_harvest/sudan_medalbook_image_batch1.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

# Selected after visual review of four contact sheets. Each file shows the whole
# award face (including ribbon/suspension where present), not a detail or side view.
selected = {
    "04fee20a45d91a39b94e1b0f.jpg",
    "a9efdd8e3a9fa325ed68c71c.jpg",
    "d204ce5ccd828d7d46d55b21.jpg",
    "e08c4c512f1e8912f0086b6f.jpg",
    "e26bf7b344b005099360c952.jpg",
    "11d2c8add3f596e0e3160b3a.jpg",
    "3bfda11f1f77a634f811190d.jpg",
    "b0f15dba8dfe53cd8b81b818.jpg",
    "84270e311dcc40fe2744efbe.jpg",
    "da59227af1fc174cb813c2be.jpg",
    "d5c166c6ccd10e12f60b2779.jpg",
    "f32fdb43402c5a88891eff0a.jpg",
    "ec2c501722f02db96af4c277.jpg",
    "09651063fe595a8643035c38.jpg",
    "c4eee3b12e62665ba9be71ef.jpg",
    "ced57da5e1b00a338348a0b5.jpg",
    "9c5cf30cf2bce42926ea3d00.jpg",
}

rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
records = []
for row in rows:
    url_by_local = dict(zip(row.get("local_raw_images") or [], row.get("original_image_urls") or []))
    for relative in row.get("local_raw_images") or []:
        path = ROOT / relative
        if path.name not in selected:
            continue
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format
        records.append(
            {
                "scope_id": "sudan",
                "family_hint": row.get("family_hint"),
                "variant_title": row.get("page_title"),
                "source_page": row.get("page_url"),
                "original_image_url": url_by_local.get(relative),
                "local_file": relative,
                "width": width,
                "height": height,
                "format": image_format,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "visual_review": "complete frontal award view",
                "object_completeness": "accepted",
                "identity_binding": "matches the MedalBook object page title; institutional corroboration still required",
                "rights_status": "commercial catalogue image; internal research use only pending rights decision",
                "html_status": "not_approved_for_html",
            }
        )

payload = {
    "schema_version": "2.0",
    "as_of": "2026-09-26",
    "batch_id": "sudan_medalbook_image_batch1",
    "source": "MedalBook Sudan catalogue",
    "raw_images_reviewed": sum(len(row.get("local_raw_images") or []) for row in rows),
    "complete_frontal_images_selected": len(records),
    "distinct_variant_titles": len({record["variant_title"] for record in records}),
    "catalogue_ready_publication_images": 0,
    "reason_not_promoted": "Image completeness passed, but commercial-source rights and institutional identity corroboration remain pending.",
    "records": records,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: payload[k] for k in ("raw_images_reviewed", "complete_frontal_images_selected", "distinct_variant_titles", "catalogue_ready_publication_images")}, ensure_ascii=False))
