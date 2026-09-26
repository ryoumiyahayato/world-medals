"""Write a human-review list of likely award-object files from the MENA sweep."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / "data/raw_candidates/commons_mena_enriched_2026-09-26.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
exclude = re.compile(
    r"(ribbon|citation|certificate|ceremony|wearing|portrait|passport|stamps?|coin|flag|uniform|"
    r"mustafa|ataturk|bundesarchiv|award ceremony|vəsiqəsi|vəsiqə|recipient|ambassador|general\s)", re.I
)
tag = re.compile(r"<[^>]+>")
selected = [row for row in rows if row.get("original_url") and not exclude.search(row["file_title"])]
groups = collections.defaultdict(list)
for row in selected:
    groups[row["country_zh"]].append(row)
output = []
for country, items in sorted(groups.items()):
    output.append(f"## {country} ({len(items)})")
    for row in items:
        description = tag.sub(" ", row.get("image_description") or "").replace("\n", " ")[:180]
        output.append(f"- {row['family_hint']} | {row['file_title'][5:]} | {description}")
    output.append("")
(ROOT / "data/checkpoints/commons_mena_filtered_titles_2026-09-26.md").write_text("\n".join(output), encoding="utf-8")
print(json.dumps({"input": len(rows), "likely_object_files": len(selected), "countries": {k: len(v) for k, v in groups.items()}}, ensure_ascii=False, indent=2))
