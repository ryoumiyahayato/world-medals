"""Group a completed MedalBook sweep into provisional award-family drafts."""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_candidates" / "medalbook_ottoman.jsonl"
OUT = ROOT / "data" / "normalized_drafts" / "medalbook_ottoman_families.json"

KNOWN_EXISTING = {
    "1st yemen campaign medal 1846": "OTT-YEMEN-1847",
    "2nd yemen campaign medal 1892": "OTT-YEMEN-1892",
    "bosnia campaign medal 1850": "OTT-BOSNIA-1850",
    "campaign medal for montenegro 1863": "OTT-MONTENEGRO",
    "commemorative medal for the defense of kars 1854": "OTT-KARS",
    "commemorative medal for the hejaz railway at maan 1904": "OTT-HEJAZ-RAIL",
    "commemorative medal of ziraat ve sinaat": "OTT-AGRI-INDUSTRY",
    "crimea medal 1854": "OTT-CRIMEA",
    "defense of kars 1855": "OTT-KARS",
    "fleet donation medal": "OTT-NAVAL-DONATION",
    "greek campaign medal 1896": "OTT-GREEK-WAR",
    "hejaz railway medal": "OTT-HEJAZ-RAIL",
    "imtiyaz medal": "OTT-IMTIYAZ-MEDAL",
    "lifesaving medal": "OTT-LIFESAVING",
    "liyakat medal": "OTT-LIYAKAT",
    "medal of acre 1840": "OTT-ACRE",
    "medal of hareket i arz": "OTT-EARTHQUAKE",
    "order of education": "OTT-MAARIF-ORDER",
    "order of medjidjie": "OTT-MEDJ",
    "order of nishan el iftihair": "OTT-IFTIHAR-ORDER",
    "order of nishan imtiaz": "OTT-IMTIYAZ-ORDER",
    "order of nishani shefkat": "OTT-SEFKAT",
    "order of osmania": "OTT-OSM",
    "plevne campaign medal 1877": "OTT-PLEVNA",
    "red crescent medal": "OTT-RED-CRESCENT",
    "sanayi medal": "OTT-SANAYI",
    "war medal of 1915": "OTT-WAR",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = value.replace("medjidjie", "medjidie").replace("osmania", "osmanieh")
    value = value.replace("nishani", "nishan").replace("shefkat", "sefkat")
    value = re.sub(r"\b(order|medal|decoration|of|the|for|ottoman|turkey|turkish)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def main() -> None:
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    existing_records = json.loads((ROOT / "data" / "catalogue.json").read_text(encoding="utf-8"))["records"]
    existing: dict[str, set[str]] = defaultdict(set)
    for row in existing_records:
        existing[row["family"]].update({row["name"], row["original"]})

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["family_hint"]].append(row)

    families = []
    for hint, variants in sorted(grouped.items()):
        hint_norm = norm(hint)
        scored = []
        for family_id, names in existing.items():
            score = max(SequenceMatcher(None, hint_norm, norm(name)).ratio() for name in names)
            if score >= 0.46:
                scored.append({"family_id": family_id, "score": round(score, 3), "labels": sorted(names)})
        scored.sort(key=lambda item: item["score"], reverse=True)
        source_titles = sorted({row["page_title"] for row in variants})
        page_urls = sorted({row["page_url"] for row in variants})
        image_urls = sorted({url for row in variants for url in row.get("original_image_urls", [])})
        categories = sorted({row["category"] for row in variants})
        related_only = all(category in {"badges-insignia", "insignia-4", "badges-3"} for category in categories)
        confirmed = KNOWN_EXISTING.get(hint)
        families.append({
            "normalized_key": hint,
            "working_name": source_titles[0] if source_titles else hint,
            "source_categories": categories,
            "candidate_scope": "related_badge_or_insignia" if related_only else "main_award_candidate",
            "variant_count": len(variants),
            "variant_titles": source_titles,
            "source_page_urls": page_urls,
            "original_image_urls": image_urls,
            "existing_match_candidates": scored[:3],
            "existing_family_id": confirmed,
            "normalization_status": "matched_existing_family" if confirmed else ("possible_existing_match" if scored else "new_family_candidate"),
            "review_note": "Automated grouping by MedalBook family path; existing matches are suggestions, not confirmed merges.",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source_id": "medalbook_ottoman",
        "raw_candidate_count": len(rows),
        "provisional_family_count": len(families),
        "main_award_family_candidates": sum(f["candidate_scope"] == "main_award_candidate" for f in families),
        "related_badge_or_insignia_candidates": sum(f["candidate_scope"] != "main_award_candidate" for f in families),
        "possible_existing_matches": sum(f["normalization_status"] == "possible_existing_match" for f in families),
        "matched_existing_families": sum(f["normalization_status"] == "matched_existing_family" for f in families),
        "new_family_candidates": sum(f["normalization_status"] == "new_family_candidate" for f in families),
        "unresolved_family_candidates": sum(f["normalization_status"] != "matched_existing_family" for f in families),
        "families": families,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "families": len(families)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
