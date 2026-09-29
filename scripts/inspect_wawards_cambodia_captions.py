import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / "data/raw_candidates/wawards_cambodia.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
for row in rows:
    slug = Path(row["object_url"]).stem
    page = ROOT / "sources/pages/wawards_cambodia" / f"{row['historical_polity']}__{slug}.html"
    body = page.read_text(encoding="utf-8", errors="replace")
    captions = [html.unescape(title).strip() for href, title in re.findall(r'<a href="([^"]*/images/cambodia/[^"]+)"[^>]*title="([^"]*)"', body, re.I) if "_thumb" not in href]
    print(f"{row['historical_polity']} {slug}: {captions}")
