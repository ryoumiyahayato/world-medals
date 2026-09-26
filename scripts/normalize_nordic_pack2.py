"""Normalize the Nordic isolated package into per-country catalogue volumes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / "data/volumes/nordic_formal_pack2_2026-09-26.json").read_text(encoding="utf-8"))

for issuer, stem, title in [
    ("瑞典王国", "sweden_orders_pack1", "瑞典王国国家勋章首包"),
    ("挪威王国", "norway_orders_pack1", "挪威王国国家勋章首包"),
]:
    selected = [row for row in source["rows"] if row["issuer"] == issuer]
    records = []
    images = []
    for row in selected:
        records.append({
            "id": row["variant_id"], "family": row["award_family_id"],
            "name": row["name_date"].split("；")[0],
            "original": row["name_date"].split("；")[1],
            "date": "；".join(row["name_date"].split("；")[2:]),
            "variant": f"{row['grade_variant']}；{row['image_kind']}",
            "views": [{"key": row["variant_id"] + "-VIEW", "label": "完整正面"}],
            "source_ids": row["source_ids"],
        })
        images.append({"view_key": row["variant_id"] + "-VIEW", "local_path": row["image"]})
    (ROOT / f"data/volumes/{stem}.json").write_text(json.dumps({"as_of": source["as_of"], "volume": title, "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / f"data/volumes/{stem}_manifest.json").write_text(json.dumps({"as_of": source["as_of"], "volume": title, "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
