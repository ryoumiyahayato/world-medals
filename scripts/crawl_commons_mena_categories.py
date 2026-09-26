"""Recursively sweep known Commons award category trees into raw candidates."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw_candidates" / "commons_mena_category_sweep_2026-09-26.jsonl"
SUMMARY = ROOT / "data" / "checkpoints" / "commons_mena_category_sweep_2026-09-26.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "world-medals-local-research/1.0 (offline catalogue)"

SEEDS = [
    ("奥斯曼帝国", "Orders, decorations and medals of the Ottoman Empire"),
    ("埃及", "Orders, decorations and medals of Egypt"),
    ("苏丹", "Orders, decorations and medals of Sudan"),
    ("伊朗／波斯", "Orders, decorations and medals of Iran"),
    ("土耳其共和国", "Orders, decorations and medals of Turkey"),
    ("伊拉克", "Orders, decorations and medals of Iraq"),
    ("约旦", "Orders, decorations and medals of Jordan"),
    ("叙利亚", "Orders, decorations and medals of Syria"),
    ("黎巴嫩", "Orders, decorations and medals of Lebanon"),
    ("也门", "Orders, decorations and medals of Yemen"),
    ("科威特", "Orders, decorations and medals of Kuwait"),
    ("巴林", "Orders, decorations and medals of Bahrain"),
    ("阿曼", "Orders, decorations and medals of Oman"),
    ("阿联酋", "Orders, decorations and medals of the United Arab Emirates"),
    ("沙特阿拉伯", "Orders, decorations and medals of Saudi Arabia"),
    ("阿富汗", "Orders, decorations and medals of Afghanistan"),
    ("巴基斯坦", "Orders, decorations and medals of Pakistan"),
    ("摩洛哥", "Orders, decorations and medals of Morocco"),
    ("阿尔及利亚", "Orders, decorations and medals of Algeria"),
    ("突尼斯", "Orders, decorations and medals of Tunisia"),
    ("利比亚", "Orders, decorations and medals of Libya"),
    ("阿塞拜疆", "Orders, decorations and medals of Azerbaijan"),
    ("哈萨克斯坦", "Orders, decorations and medals of Kazakhstan"),
    ("乌兹别克斯坦", "Orders, decorations and medals of Uzbekistan"),
]

SKIP = (
    "recipients of", "ribbon bars", "people with", "portraits of", "wearing ",
    "presentation of", "award ceremonies", "documents of", "stamps of",
)


def api(params: dict) -> dict:
    params = {"format": "json", "formatversion": 2, **params}
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
            time.sleep(1.2)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("unreachable")


def members(category: str) -> list[dict]:
    rows: list[dict] = []
    cont: dict = {}
    while True:
        data = api({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + category,
                    "cmtype": "subcat|file", "cmlimit": "500", **cont})
        rows.extend(data.get("query", {}).get("categorymembers", []))
        if "continue" not in data:
            return rows
        cont = data["continue"]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    output: list[dict] = []
    if OUT.is_file():
        output = [json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    previous = {}
    previous_failures: list[dict] = []
    if SUMMARY.is_file():
        prior = json.loads(SUMMARY.read_text(encoding="utf-8"))
        previous = prior.get("stats", {})
        previous_failures = prior.get("failures", [])
    stats: dict[str, dict] = {}
    failures: list[dict] = []
    for country_zh, seed in SEEDS:
        seed_had_failure = any(item.get("seed") == seed for item in previous_failures)
        prior_stat = previous.get(seed, {})
        if any(row.get("seed_category") == seed for row in output) and not seed_had_failure and prior_stat.get("categories_visited"):
            stats[seed] = {"categories_visited": "cached", "files_found": sum(row.get("seed_category") == seed for row in output)}
            continue
        queue = deque([(seed, 0, seed)])
        visited: set[str] = set()
        category_count = file_count = 0
        while queue:
            category, depth, family_hint = queue.popleft()
            if category in visited:
                continue
            visited.add(category)
            try:
                rows = members(category)
            except Exception as exc:
                failures.append({"seed": seed, "category": category, "error": f"{type(exc).__name__}: {exc}"})
                continue
            category_count += 1
            for row in rows:
                title = row["title"]
                if title.startswith("Category:"):
                    child = title[len("Category:"):]
                    if depth < 1 and not any(token in child.lower() for token in SKIP):
                        next_hint = child if depth == 0 or any(w in child.lower() for w in ("order", "medal", "cross", "star", "decoration", "collar")) else family_hint
                        queue.append((child, depth + 1, next_hint))
                elif title.startswith("File:"):
                    file_count += 1
                    output.append({
                        "source_id": "commons-category-tree",
                        "country_zh": country_zh,
                        "seed_category": seed,
                        "category": category,
                        "family_hint": family_hint,
                        "file_title": title,
                        "file_page_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":_()-,.'"),
                        "status": "SOURCE_SWEEP_CANDIDATE",
                    })
        stats[seed] = {"categories_visited": category_count, "files_found": file_count}
        partial = {(row["country_zh"], row["file_title"]): row for row in output}
        OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in sorted(partial.values(), key=lambda x: (x["country_zh"], x["family_hint"], x["file_title"]))), encoding="utf-8")
        print(f"saved {seed}: {category_count} categories / {file_count} files", flush=True)
    dedup = {(row["country_zh"], row["file_title"]): row for row in output}
    ordered = sorted(dedup.values(), key=lambda x: (x["country_zh"], x["family_hint"], x["file_title"]))
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ordered), encoding="utf-8")
    summary = {
        "as_of": "2026-09-26",
        "planned_seed_categories": len(SEEDS),
        "swept_seed_categories": len(SEEDS),
        "unique_file_candidates": len(ordered),
        "stats": stats,
        "failures": failures,
        "output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
