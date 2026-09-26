"""Bulk-discover pictured awards for MENA and adjacent Muslim-majority states.

Writes raw candidates only. It does not modify the public catalogue.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw_candidates" / "wikidata_mena_awards_2026-09-26.jsonl"
SUMMARY = ROOT / "data" / "checkpoints" / "wikidata_mena_awards_sweep_2026-09-26.json"
UA = "world-medals-local-research/1.0 (offline catalogue)"

COUNTRIES = [
    ("Q12560", "奥斯曼帝国", "Ottoman Empire"),
    ("Q79", "埃及", "Egypt"),
    ("Q1049", "苏丹", "Sudan"),
    ("Q794", "伊朗／波斯", "Iran"),
    ("Q43", "土耳其共和国", "Turkey"),
    ("Q796", "伊拉克", "Iraq"),
    ("Q810", "约旦", "Jordan"),
    ("Q858", "叙利亚", "Syria"),
    ("Q822", "黎巴嫩", "Lebanon"),
    ("Q805", "也门", "Yemen"),
    ("Q817", "科威特", "Kuwait"),
    ("Q398", "巴林", "Bahrain"),
    ("Q842", "阿曼", "Oman"),
    ("Q878", "阿联酋", "United Arab Emirates"),
    ("Q851", "沙特阿拉伯", "Saudi Arabia"),
    ("Q889", "阿富汗", "Afghanistan"),
    ("Q843", "巴基斯坦", "Pakistan"),
    ("Q1028", "摩洛哥", "Morocco"),
    ("Q262", "阿尔及利亚", "Algeria"),
    ("Q948", "突尼斯", "Tunisia"),
    ("Q1016", "利比亚", "Libya"),
    ("Q227", "阿塞拜疆", "Azerbaijan"),
    ("Q232", "哈萨克斯坦", "Kazakhstan"),
    ("Q265", "乌兹别克斯坦", "Uzbekistan"),
]

KEEP = re.compile(
    r"\b(order|medal|cross|star|badge|decoration|honou?r|merit|hero|glory|service|valour|valor|bravery|courage|campaign|jubilee|commemorative)\b",
    re.I,
)
DROP = re.compile(r"\b(prize|award for best|film|music|literary|sports? award|festival|competition|scholarship)\b", re.I)


def get_json(url: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def sparql(country_qid: str) -> list[dict]:
    query = f'''SELECT DISTINCT ?item ?image ?inception ?enLabel ?zhLabel WHERE {{
      ?item wdt:P17 wd:{country_qid}; wdt:P18 ?image; wdt:P31/wdt:P279* wd:Q618779.
      OPTIONAL {{ ?item wdt:P571 ?inception. }}
      OPTIONAL {{ ?item rdfs:label ?enLabel. FILTER(LANG(?enLabel)="en") }}
      OPTIONAL {{ ?item rdfs:label ?zhLabel. FILTER(LANG(?zhLabel)="zh") }}
    }} ORDER BY ?item'''
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(query)
    return get_json(url)["results"]["bindings"]


def value(row: dict, key: str) -> str:
    return row.get(key, {}).get("value", "")


def main() -> None:
    rows: list[dict] = []
    failures: list[dict] = []
    source_counts: dict[str, int] = {}
    for qid, country_zh, country_en in COUNTRIES:
        try:
            found = sparql(qid)
        except Exception as exc:  # saved for exact continuation
            failures.append({"country_qid": qid, "country": country_en, "error": f"{type(exc).__name__}: {exc}"})
            continue
        admitted = 0
        for source in found:
            en = value(source, "enLabel")
            zh = value(source, "zhLabel")
            if not en or DROP.search(en) or not (KEEP.search(en) or re.search(r"勋|勳|奖章|獎章|勋章|勳章|十字|星章|英雄", zh)):
                continue
            item_url = value(source, "item")
            item_qid = item_url.rsplit("/", 1)[-1]
            image = value(source, "image")
            inception = value(source, "inception")
            rows.append({
                "source_id": f"wikidata-{item_qid}",
                "wikidata_qid": item_qid,
                "country_qid": qid,
                "country_zh": country_zh,
                "country_en": country_en,
                "title": en,
                "name_zh": zh or "待译",
                "date_candidates": [inception[:10]] if inception else [],
                "category": "正式奖励候选",
                "source_page_url": item_url,
                "image_page_url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(urllib.parse.unquote(image.rsplit("/", 1)[-1]).replace(" ", "_"), safe="_()-,.'"),
                "image_special_url": image.replace("http://", "https://"),
                "status": "SOURCE_SWEEP_CANDIDATE",
                "notes": "Wikidata P17/P18 and award-class discovery; must verify Commons file page, image completeness, and official scope before formal ingest.",
            })
            admitted += 1
        source_counts[qid] = admitted
        time.sleep(0.25)

    dedup = {row["wikidata_qid"]: row for row in rows}
    ordered = sorted(dedup.values(), key=lambda row: (next(i for i, c in enumerate(COUNTRIES) if c[0] == row["country_qid"]), row["title"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ordered), encoding="utf-8")
    summary = {
        "as_of": "2026-09-26",
        "method": "Wikidata pictured-award source sweep; no formal HTML changes",
        "planned_countries": len(COUNTRIES),
        "completed_countries": len(COUNTRIES) - len(failures),
        "failed_countries": len(failures),
        "candidate_rows": len(ordered),
        "counts_by_country_qid": source_counts,
        "failures": failures,
        "output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
