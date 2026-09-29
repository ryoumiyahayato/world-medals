"""Print Wawards Egypt object-link labels for grade-level normalization."""
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WANTED = {
    "Order of Ismail", "Order of Muhammad Ali", "Order of the Nile", "Order of Independence",
    "Order of Merit", "Order of the Republic", "Order of the Virtues", "Order of Sciences and Arts", "Order of Sport",
}

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag != "a": return
        data = dict(attrs); href = data.get("href", "")
        if href.startswith("/images/egypt/"):
            self.rows.append((href, data.get("title", "")))

for line in (ROOT / "data/raw_candidates/wawards_egypt.jsonl").read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    if row["page_title"] not in WANTED: continue
    parser = Links(); parser.feed((ROOT / row["cache_file"]).read_text(encoding="utf-8", errors="ignore"))
    print("\n" + row["page_title"] + " | " + row["page_url"])
    for href, title in parser.rows: print(href, "|", title)
