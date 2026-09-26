"""Select named, likely-complete award images for visual review; no HTML is changed here."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw_candidates/commons_mena_enriched_2026-09-26.jsonl"
OUTPUT = ROOT / "data/normalized_drafts/mena_bulk_round7_candidates.json"

QUOTAS = {
    "奥斯曼帝国": 35, "埃及": 12, "苏丹": 48, "伊朗／波斯": 35, "土耳其共和国": 18,
    "伊拉克": 5, "约旦": 2, "叙利亚": 9, "也门": 1, "科威特": 4, "巴林": 1,
    "阿曼": 8, "沙特阿拉伯": 6, "阿富汗": 7, "巴基斯坦": 12, "摩洛哥": 10,
    "阿尔及利亚": 5, "突尼斯": 4, "阿塞拜疆": 70, "哈萨克斯坦": 55, "乌兹别克斯坦": 55,
}

NEGATIVE = re.compile(
    r"(ribbon|ruban|rib\. ?bar|bar\.svg|lenta|citation|certificate|ceremony|wearing|portrait|passport|"
    r"recipient|ambassador|general\s|president\s|mustafa|ataturk|bundesarchiv|document|vəsiq|"
    r"museum.+awards|assortment|coat of arms|insigne turciae|military series|world.s decorations series|"
    r"cigarettes|postage|stamp|miuz\d+|blank\)|exhibition|battle of|soldier|warrior|governor|"
    r"front and rear photo|awarded by|copy\.jpg|list of the military medals|pdf$)", re.I
)
BACK = re.compile(r"(back|reverse|rev\.|orqa|keerzijde|rückseite|реверс|تыльная|other side)", re.I)
OBJECT = re.compile(
    r"(order|medal|decoration|badge|star|cross|collar|cordon|insignia|nişan|nisan|madaly|orden|ordeni|"
    r"медал|орден|нагруд|nishon|ko.krak|döş|mükafat|fəxri|award|құрмет|жұлдыз|belgi)", re.I
)
GENERIC_FAMILIES = {
    "Orders, decorations and medals of Iran", "Orders, decorations and medals of Turkey",
    "Orders, decorations and medals of Iraq", "Orders, decorations and medals of Syria",
    "Orders, decorations and medals of Sudan", "Orders, decorations and medals of Azerbaijan",
    "Orders, decorations and medals of Kazakhstan", "Orders, decorations and medals of Uzbekistan",
    "Medals of Azerbaijan", "Medals of Kazakhstan", "Medals of Uzbekistan", "Medals of Turkey",
    "Orders of Iran", "Orders of Turkey", "Orders of Kazakhstan", "Orders of Uzbekistan",
    "Badges of Kazakhstan", "Badges of honorary titles of Azerbaijan",
    "Badges of honorary titles of Uzbekistan", "Badges of honorary titles of the Kazakh Soviet Socialist Republic",
}

def plain(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("\n", " ")

def canonical(row: dict) -> str:
    title = row["file_title"][5:]
    stem = re.sub(r"\.[^.]+$", "", title)
    stem = re.sub(r"[-_+ ]*removebg[-_ ]preview", "", stem, flags=re.I)
    stem = re.sub(r"\s*\((?:obverse|reverse|front|back|cropped)\)", "", stem, flags=re.I)
    stem = re.sub(r"\s+(?:obverse|reverse|front|back|rev)$", "", stem, flags=re.I)
    stem = re.sub(r"\b(?:old|other side)\b", "", stem, flags=re.I)
    stem = re.sub(r"Medal, (?:campaign|decoration|order) \(AM ([\d.]+)(?:-\d+)?\)", r"AM-\1", stem, flags=re.I)
    stem = re.sub(r"\s+", " ", stem).strip(" -_+().")
    return unicodedata.normalize("NFKC", stem).casefold()

def score(row: dict) -> int:
    title = row["file_title"][5:]
    desc = plain(row.get("image_description") or "")
    points = 0
    if OBJECT.search(title): points += 5
    if OBJECT.search(desc): points += 3
    if row["family_hint"] not in GENERIC_FAMILIES: points += 3
    if any(x in title.casefold() for x in ("class", "grade", "degree", "1st", "2nd", "3rd", "gold", "silver", "bronze")): points += 2
    if row.get("width", 0) >= 1000 and row.get("height", 0) >= 1000: points += 2
    if row.get("license_short_name") in ("Public domain", "CC0"): points += 1
    if row.get("mime") == "image/svg+xml": points += 1
    if "removebg" in title.casefold(): points -= 1
    return points

rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
by_country = defaultdict(list)
for row in rows:
    title = row["file_title"][5:]
    haystack = title + " " + plain(row.get("image_description") or "")
    if not row.get("original_url") or NEGATIVE.search(haystack) or BACK.search(title):
        continue
    if not OBJECT.search(haystack) and row["family_hint"] in GENERIC_FAMILIES:
        continue
    if len(re.sub(r"\W", "", title)) < 5:
        continue
    row = dict(row)
    row["canonical_candidate"] = canonical(row)
    row["selection_score"] = score(row)
    by_country[row["country_zh"]].append(row)

selected = []
for country, quota in QUOTAS.items():
    seen_sha = set()
    seen_names = set()
    candidates = sorted(by_country[country], key=lambda r: (-r["selection_score"], -int(r.get("width") or 0) * int(r.get("height") or 0), r["file_title"]))
    for row in candidates:
        key = row["canonical_candidate"]
        if row.get("sha1") in seen_sha or key in seen_names:
            continue
        seen_sha.add(row.get("sha1")); seen_names.add(key)
        row["candidate_id"] = "mena7-" + hashlib.sha1((country + "|" + row["file_title"]).encode()).hexdigest()[:12]
        selected.append(row)
        if sum(x["country_zh"] == country for x in selected) >= quota:
            break

selected.sort(key=lambda r: ({"苏丹": 0, "阿塞拜疆": 1, "哈萨克斯坦": 2, "乌兹别克斯坦": 3,
                             "伊拉克": 4, "叙利亚": 5, "阿曼": 6, "沙特阿拉伯": 7,
                             "阿富汗": 8, "巴基斯坦": 9, "摩洛哥": 10, "阿尔及利亚": 11,
                             "奥斯曼帝国": 12, "埃及": 13, "伊朗／波斯": 14, "土耳其共和国": 15}.get(r["country_zh"], 20),
                             -r["selection_score"], r["file_title"]))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps({"as_of": "2026-09-26", "records": selected}, ensure_ascii=False, indent=2), encoding="utf-8")
review = []
for country in QUOTAS:
    items = [row for row in selected if row["country_zh"] == country]
    review.append(f"## {country} ({len(items)})")
    review.extend(f"- {row['candidate_id']} | {row['family_hint']} | {row['file_title'][5:]}" for row in items)
    review.append("")
(ROOT / "data/checkpoints/mena_bulk_round7_selected_titles.md").write_text("\n".join(review), encoding="utf-8")
print(json.dumps({"selected": len(selected), "by_country": {c: sum(r["country_zh"] == c for r in selected) for c in QUOTAS}}, ensure_ascii=False, indent=2))
