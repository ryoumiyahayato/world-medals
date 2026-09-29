"""Bulk-sweep the English and Polish national award inventories for Poland.

This is a discovery pass.  It intentionally records the complete table rows
and article/file links without treating ribbon-bar illustrations as award
photographs.  Object-page image harvesting is a separate batch step.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from lxml import html as lxml_html

ROOT = Path(__file__).resolve().parents[1]
UA = "world-medals-research/1.0 (bulk source sweep; contact project maintainer)"
PL_URL = "https://pl.wikipedia.org/wiki/Polskie_odznaczenia_(lista)"
EN_URL = "https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Poland"

# Formal state inventories and the current/older national state sections are
# in scope.  Ministerial tables are retained as a separately marked discovery
# pool because they often contain official service awards; non-state club and
# commemorative tables are retained only as out-of-scope audit material.
STATE_SECTIONS = {
    "Ordery",
    "Odznaczenia państwowe – krzyże",
    "Odznaczenia państwowe – krzyże (nadawane do 1992)",
    "Odznaczenia państwowe – krzyże (nadawane do 1999)",
    "Odznaczenia państwowe – medale",
    "Odznaczenia państwowe – medale (nadawane do 1992)",
    "Odznaczenia państwowe – medale (nadawane do 1999)",
    "Odznaczenia państwowe – gwiazdy",
    "II RP (nienadawane)",
    "PRL (nienadawane)",
}
MINISTERIAL_SECTIONS = {
    "Odznaczenia resortowe (medale, odznaki – honorowe, pamiątkowe)",
}
LOCAL_SECTIONS = {
    "Odznaczenia samorządów terytorialnych (odznaki honorowe, medale)",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def get(url: str) -> requests.Response:
    response = requests.get(url, headers={"User-Agent": UA}, timeout=90)
    response.raise_for_status()
    return response


def page_links(node) -> list[str]:
    links = []
    for a in node.xpath(".//a[@href]"):
        href = a.get("href", "")
        if href.startswith("/wiki/"):
            links.append(urljoin("https://pl.wikipedia.org", href))
        elif href.startswith("https://pl.wikipedia.org/wiki/"):
            links.append(href)
    return list(dict.fromkeys(links))


def row_candidates(tree, source_url: str, source_lang: str) -> list[dict]:
    section = "Introduction"
    rows = []
    for node in tree.xpath("//h2|//h3|//h4|//table"):
        if node.tag in ("h2", "h3", "h4"):
            section = clean(node.text_content()).replace("[edit]", "").strip()
            continue
        if node.tag != "table":
            continue
        for tr in node.xpath(".//tr"):
            cells = [clean(x.text_content()) for x in tr.xpath("./th|./td")]
            if len(cells) < 2:
                continue
            # Skip the header and empty rows.  The first column on the Polish
            # page is a ribbon bar; it is a discovery clue, not a body image.
            name = cells[1]
            if not name or name.lower() in {"nazwa", "award"}:
                continue
            links = page_links(tr)
            file_pages = [x for x in links if "/wiki/Plik:" in x or "/wiki/File:" in x]
            object_pages = [x for x in links if "/wiki/Plik:" not in x and "/wiki/File:" not in x]
            section_kind = (
                "state_award" if section in STATE_SECTIONS else
                "ministerial_award" if section in MINISTERIAL_SECTIONS else
                "local_award" if section in LOCAL_SECTIONS else
                "other_discovery"
            )
            # Rows with an explicit level are variants of the same article,
            # while the normalizer later groups them by object article.
            rid = hashlib.sha1(
                (source_lang + "\0" + section + "\0" + name).encode("utf-8")
            ).hexdigest()[:14]
            years = re.findall(r"(?<!\d)(?:1[4-9]\d{2}|20\d{2})(?!\d)", name)
            rows.append({
                "source_id": f"wikipedia-poland-{source_lang}-{rid}",
                "source_system": "Wikipedia national award inventory",
                "source_language": source_lang,
                "source_page_title": "Polskie odznaczenia (lista)" if source_lang == "pl" else "Orders, decorations, and medals of Poland",
                "source_page_url": source_url,
                "section": section,
                "section_kind": section_kind,
                "country_zh": "波兰",
                "working_name_zh": "待归并",
                "name_original": name,
                "date_candidates": years,
                "category": "order_or_decoration" if section_kind in {"state_award", "ministerial_award"} else "discovery_candidate",
                "grade_material_clues": name,
                "object_pages": object_pages,
                "image_pages": file_pages,
                "image_policy": "Polish list image is a ribbon-bar clue; do not use as formal body image",
                "status": "RAW_CANDIDATE",
                "access_date": date.today().isoformat(),
            })
    return rows


def main() -> None:
    cache_dir = ROOT / "sources/pages/wikipedia_awards"
    cache_dir.mkdir(parents=True, exist_ok=True)
    pl_html = get(PL_URL).text
    en_html = get(EN_URL).text
    (cache_dir / "poland_pl.html").write_text(pl_html, encoding="utf-8")
    (cache_dir / "poland_en.html").write_text(en_html, encoding="utf-8")
    pl_rows = row_candidates(lxml_html.fromstring(pl_html), PL_URL, "pl")
    en_rows = row_candidates(lxml_html.fromstring(en_html), EN_URL, "en")

    # Keep source-specific files so a later merge can identify differences.
    raw_dir = ROOT / "data/raw_candidates"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for stem, rows in (("wikipedia_poland_pl_awards", pl_rows), ("wikipedia_poland_en_awards", en_rows)):
        with (raw_dir / f"{stem}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "source_id": "wikipedia-poland-award-inventory",
        "source_urls": [EN_URL, PL_URL],
        "accessed": date.today().isoformat(),
        "status": "complete",
        "scope": "All exposed award tables in the English master list and Polish Polskie odznaczenia (lista); state, ministerial, local and other rows are explicitly classified.",
        "polish_rows": len(pl_rows),
        "polish_state_rows": sum(x["section_kind"] == "state_award" for x in pl_rows),
        "polish_ministerial_rows": sum(x["section_kind"] == "ministerial_award" for x in pl_rows),
        "english_rows": len(en_rows),
        "cached_pages": ["sources/pages/wikipedia_awards/poland_pl.html", "sources/pages/wikipedia_awards/poland_en.html"],
        "raw_outputs": ["data/raw_candidates/wikipedia_poland_pl_awards.jsonl", "data/raw_candidates/wikipedia_poland_en_awards.jsonl"],
    }
    out = ROOT / "data/source_sweeps/wikipedia_poland_award_inventory_2026-09-28.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
