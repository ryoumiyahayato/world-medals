"""Select a second visual-review batch from the deep core MENA crawl."""
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw_candidates/commons_core_deep_enriched_2026-09-26.jsonl"
PRIOR = ROOT / "data/normalized_drafts/mena_bulk_round7_candidates.json"
OUTPUT = ROOT / "data/normalized_drafts/mena_core_deep_round7_candidates.json"
QUOTAS = {"奥斯曼帝国": 55, "埃及": 45, "苏丹": 50, "伊朗／波斯": 55, "土耳其共和国": 25}

NEG = re.compile(r"(ribbon|bar\.svg|portrait|wearing|recipient|firman|certificate|ceremony|passport|stamp|"
                 r"gaddafi|prigozhin|wagner|chris coons|zhang gaoli|concord management|poster|caricature|"
                 r"award(s)? of [A-Z][a-z]+ [A-Z]|museum.+awards|general\s|president\s|mustafa|ataturk|"
                 r"negative\.tif|miniature orders|gold chain|orders and decorations of|world.s decorations|"
                 r"military series|cigarette|coat of arms|document|battle of|soldier|warrior)", re.I)
BACK = re.compile(r"(back|reverse|rev\.|orqa|keerzijde|rückseite|реверс|other side)", re.I)
OBJ = re.compile(r"(order|medal|decoration|badge|star|cross|collar|insignia|nişan|madaly|orden|медал|орден|khedive|lion|sun)", re.I)
BAD_CATEGORY = re.compile(r"(ribbon|portrait|recipient|gaddafi|wagner|prigozhin|coons|zhang|concord|caricature|poster)", re.I)

def clean(value): return re.sub(r"<[^>]+>", " ", value or "").replace("\n", " ")
def canon(title):
    stem = re.sub(r"\.[^.]+$", "", title[5:])
    stem = re.sub(r"[-_+ ]*removebg[-_ ]preview", "", stem, flags=re.I)
    stem = re.sub(r"\s*\((obverse|reverse|front|back|cropped)\)", "", stem, flags=re.I)
    stem = re.sub(r"\s+(obverse|reverse|front|back|rev)$", "", stem, flags=re.I)
    stem = re.sub(r"\s+", " ", stem).strip(" -_+().")
    return unicodedata.normalize("NFKC", stem).casefold()

prior_titles = {r["file_title"] for r in json.loads(PRIOR.read_text(encoding="utf-8"))["records"]}
rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
grouped = defaultdict(list)
for row in rows:
    if not row.get("original_url") or row["file_title"] in prior_titles:
        continue
    title, category = row["file_title"], row["family_hint"]
    hay = title + " " + clean(row.get("image_description"))
    if NEG.search(hay) or BACK.search(title) or BAD_CATEGORY.search(category):
        continue
    specific = any(word in category.casefold() for word in ("order", "medal", "decoration", "star", "cross", "collar"))
    if not OBJ.search(hay) and not specific:
        continue
    score = (5 if OBJ.search(title) else 0) + (4 if specific else 0) + (2 if (row.get("width") or 0) >= 1000 else 0)
    if category == "Order of the Lion and the Sun": score += 8
    item = dict(row); item["canonical_candidate"] = canon(title); item["selection_score"] = score
    grouped[row["country_zh"]].append(item)

selected = []
for country, quota in QUOTAS.items():
    seen = set()
    pool = sorted(grouped[country], key=lambda r: (-r["selection_score"], r["family_hint"], r["file_title"]))
    for row in pool:
        key = row["canonical_candidate"]
        if key in seen: continue
        seen.add(key)
        row["candidate_id"] = "core7-" + hashlib.sha1((country + "|" + row["file_title"]).encode()).hexdigest()[:12]
        selected.append(row)
        if sum(r["country_zh"] == country for r in selected) >= quota: break
selected.sort(key=lambda r: (0 if r["family_hint"] == "Order of the Lion and the Sun" else 1,
                             {"伊朗／波斯": 0, "苏丹": 1, "埃及": 2, "奥斯曼帝国": 3, "土耳其共和国": 4}.get(r["country_zh"], 9),
                             -r["selection_score"], r["file_title"]))
OUTPUT.write_text(json.dumps({"as_of": "2026-09-26", "records": selected}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"selected": len(selected), "by_country": {c: sum(r["country_zh"] == c for r in selected) for c in QUOTAS},
                  "lion_sun": sum(r["family_hint"] == "Order of the Lion and the Sun" for r in selected)}, ensure_ascii=False, indent=2))
