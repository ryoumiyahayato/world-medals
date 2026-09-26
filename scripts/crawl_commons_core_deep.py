"""Deep recursive sweep of the five core MENA award category trees."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw_candidates/commons_core_deep_2026-09-26.jsonl"
CHECKPOINT = ROOT / "data/checkpoints/commons_core_deep_2026-09-26.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-local-research/1.0 (offline catalogue)"
SEEDS = [
    ("奥斯曼帝国", "Orders, decorations and medals of the Ottoman Empire"),
    ("埃及", "Orders, decorations and medals of Egypt"),
    ("苏丹", "Orders, decorations and medals of Sudan"),
    ("伊朗／波斯", "Orders, decorations and medals of Iran"),
    ("土耳其共和国", "Orders, decorations and medals of Turkey"),
]
SKIP = ("recipients of", "people with", "portraits of", "wearing ", "award ceremonies", "documents of", "stamps of")

def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.load(response)
            time.sleep(1.25)
            return result
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(12 * (attempt + 1))
    raise RuntimeError

def members(category: str) -> list[dict]:
    result, cont = [], {}
    while True:
        data = api({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + category,
                    "cmtype": "subcat|file", "cmlimit": 500, **cont})
        result.extend(data.get("query", {}).get("categorymembers", []))
        if "continue" not in data:
            return result
        cont = data["continue"]

output, stats, failures = [], {}, []
for country, seed in SEEDS:
    queue = deque([(seed, 0, seed)])
    visited = set()
    while queue:
        category, depth, family = queue.popleft()
        if category in visited:
            continue
        visited.add(category)
        try:
            rows = members(category)
        except Exception as exc:
            failures.append({"seed": seed, "category": category, "error": f"{type(exc).__name__}: {exc}"})
            continue
        for row in rows:
            title = row["title"]
            if title.startswith("Category:") and depth < 3:
                child = title[9:]
                if not any(token in child.casefold() for token in SKIP):
                    queue.append((child, depth + 1, child))
            elif title.startswith("File:"):
                output.append({"source_id": "commons-core-deep", "country_zh": country, "seed_category": seed,
                               "category": category, "family_hint": family, "file_title": title,
                               "file_page_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":_()-,.'\""),
                               "status": "SOURCE_SWEEP_CANDIDATE"})
    stats[seed] = {"categories_visited": len(visited), "files_found": sum(r["seed_category"] == seed for r in output)}
    dedup = {(row["country_zh"], row["file_title"]): row for row in output}
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in dedup.values()), encoding="utf-8")
    print(f"deep saved {seed}: {len(visited)} categories / {stats[seed]['files_found']} files", flush=True)

dedup = {(row["country_zh"], row["file_title"]): row for row in output}
OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in sorted(dedup.values(), key=lambda x: (x["country_zh"], x["family_hint"], x["file_title"]))), encoding="utf-8")
summary = {"as_of": "2026-09-26", "planned_sources": len(SEEDS), "completed_sources": len(SEEDS) - len({f['seed'] for f in failures}),
           "partial_sources": len({f['seed'] for f in failures}), "unique_files": len(dedup), "stats": stats, "failures": failures,
           "output": str(OUT.relative_to(ROOT)).replace("\\", "/")}
CHECKPOINT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
