"""Harvest complete award images from Polish/English article pages in bulk.

The Polish master list's first column is deliberately ribbon-bar-only and is
not used as a body image.  This script follows each distinct article page,
selects a complete object illustration/photo from its file gallery, retrieves
the original/large Wikimedia rendition, verifies local decoding, and writes a
standalone Poland volume plus image manifest.  It is intentionally limited to
state and ministerial awards; local/non-state tables remain discovery-only.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from lxml import html as lxml_html
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
UA = "world-medals-research/1.0 (bulk image harvest; contact project maintainer)"
RAW = ROOT / "data/raw_candidates/wikipedia_poland_pl_awards.jsonl"
OUT_DIR = ROOT / "assets/images/poland_wikipedia_families"
CACHE = ROOT / "sources/pages/wikipedia_awards/poland_objects"
PL_API = "https://pl.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
SKIP_WORDS = {
    "bar", "baret", "ribbon", "wstaz", "wstąż", "rozet", "miniatur",
    "legitym", "diplom", "diploma", "logo", "godlo", "godło", "herb",
    "coat", "flag", "flaga", "portrait", "portret", "person", "uniform",
    "mundur", "order of precedence", "precedence", "schemat", "diagram",
    "collage", "kolaż", "katalog", "catalogue", "box", "pudeł", "pudlo",
    "rewers", "reverse", "back", "tył", "tyl", "awers", "obraz", "painting",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def get(url: str, **kwargs) -> requests.Response:
    response = requests.get(url, headers={"User-Agent": UA}, timeout=90, **kwargs)
    response.raise_for_status()
    return response


def slug_for_url(url: str) -> str:
    title = unquote(urlparse(url).path.rsplit("/", 1)[-1])
    title = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").lower()
    return title[:90] or "award"


def file_title_from_href(href: str) -> str | None:
    if "/wiki/Plik:" in href:
        return "File:" + unquote(href.split("/wiki/Plik:", 1)[1])
    if "/wiki/File:" in href:
        return "File:" + unquote(href.split("/wiki/File:", 1)[1])
    return None


def metadata(api: str, title: str) -> dict | None:
    params = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": title, "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1600,
    }
    try:
        payload = get(api, params=params).json()
    except Exception:
        return None
    for page in payload.get("query", {}).get("pages", {}).values():
        infos = page.get("imageinfo") or []
        if infos:
            info = infos[0]
            info["file_page"] = "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
            return info
    return None


def image_candidates(page_url: str) -> tuple[str, list[str], str]:
    html = get(page_url).text
    cache = CACHE / f"{slug_for_url(page_url)}.html"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(html, encoding="utf-8")
    tree = lxml_html.fromstring(html)
    title = clean(tree.xpath("string(//h1)")) or page_url.rsplit("/", 1)[-1]
    files = []
    for a in tree.xpath("//a[contains(@class,'mw-file-description') or contains(@class,'image')]"):
        file_title = file_title_from_href(a.get("href", ""))
        if file_title and file_title not in files:
            files.append(file_title)
    # Article HTML occasionally omits the class on the first infobox image.
    if not files:
        for img in tree.xpath("//img[@resource]"):
            file_title = file_title_from_href(img.get("resource", ""))
            if file_title and file_title not in files:
                files.append(file_title)
    return title, files, html


def score_file(title: str, info: dict) -> int:
    lower = title.lower()
    score = 0
    if any(word in lower for word in SKIP_WORDS):
        score -= 1000
    if re.search(r"\.(jpg|jpeg|png)$", lower):
        score += 20
    elif lower.endswith(".svg"):
        score += 10
    width, height = int(info.get("width", 0)), int(info.get("height", 0))
    if min(width, height) >= 500:
        score += 35
    elif min(width, height) >= 300:
        score += 20
    elif min(width, height) >= 180:
        score += 5
    # A near-square object plate is more likely a complete insignia than a
    # horizontal ribbon bar.
    ratio = max(width, height) / max(1, min(width, height))
    if 0.65 <= ratio <= 1.8:
        score += 20
    if "order" in lower or "medal" in lower or "cross" in lower or "star" in lower:
        score += 10
    return score


def download_and_verify(info: dict, path: Path) -> tuple[bool, str, tuple[int, int]]:
    url = info.get("thumburl") or info.get("url")
    if not url:
        return False, "", (0, 0)
    try:
        response = get(url)
        path.write_bytes(response.content)
        with Image.open(path) as image:
            image.load()
            size = image.size
            fmt = (image.format or "").lower()
        if fmt not in {"jpeg", "png", "webp", "gif", "tiff", "bmp"}:
            path.unlink(missing_ok=True)
            return False, "", (0, 0)
        return True, hashlib.sha256(path.read_bytes()).hexdigest(), size
    except Exception:
        path.unlink(missing_ok=True)
        return False, "", (0, 0)


def chinese_name(original: str) -> str:
    # Keep the Polish official title visible and provide a stable Chinese
    # working label.  The editor can refine translations without losing the
    # source-language identity.
    known = {
        "Order Orła Białego": "白鹰勋章",
        "Order Virtuti Militari": "维尔蒂蒂·米利塔里勋章",
        "Order Odrodzenia Polski": "波兰复兴勋章",
        "Order Krzyża Wojskowego": "军事十字勋章",
        "Order Krzyża Niepodległości": "独立十字勋章",
        "Order Zasługi Rzeczypospolitej Polskiej": "波兰共和国功绩勋章",
        "Krzyż Walecznych": "英勇十字勋章",
        "Krzyż Zasługi": "功绩十字勋章",
        "Medal Virtus et Fraternitas": "Virtus et Fraternitas奖章",
        "Medal za Ofiarność i Odwagę": "牺牲与勇气奖章",
        "Medal Stulecia Odzyskanej Niepodległości": "收复独立百年纪念奖章",
        "Krzyż Wolności i Solidarności": "自由与团结十字勋章",
    }
    base = re.split(r"\s+[–-]\s+", original, maxsplit=1)[0].strip()
    if base in known:
        return known[base]
    return "波兰·" + base


def main() -> None:
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    in_scope = [row for row in rows if row.get("section_kind") in {"state_award", "ministerial_award"}]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in in_scope:
        for page in row.get("object_pages", []):
            grouped[page].append(row)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, images, failures, seen_sha = [], [], [], {}
    used_titles = set()
    for index, (page_url, page_rows) in enumerate(sorted(grouped.items()), 1):
        try:
            title, files, _ = image_candidates(page_url)
            infos = []
            for file_title in files[:18]:
                if file_title in used_titles:
                    continue
                info = metadata(PL_API, file_title) or metadata(COMMONS_API, file_title)
                if info and int(info.get("width", 0)) >= 160 and int(info.get("height", 0)) >= 160:
                    infos.append((score_file(file_title, info), file_title, info))
            infos.sort(reverse=True, key=lambda x: x[0])
            chosen = next((x for x in infos if x[0] >= 15), None)
            if not chosen:
                failures.append({"page": page_url, "title": title, "reason": "no complete non-ribbon article image"})
                continue
            score, file_title, info = chosen
            used_titles.add(file_title)
            family_slug = slug_for_url(page_url)
            family = "POL-WIKI-" + re.sub(r"[^A-Z0-9]+", "_", family_slug.upper()).strip("_")
            rid = family + "-REPRESENTATIVE"
            ext = ".png" if "png" in (info.get("mime") or "") or str(info.get("thumburl", "")).lower().endswith(".png") else ".jpg"
            local = OUT_DIR / f"{family_slug}_01{ext}"
            ok, sha, size = download_and_verify(info, local)
            if not ok:
                failures.append({"page": page_url, "title": title, "file": file_title, "reason": "download_or_decode_failed"})
                continue
            if sha in seen_sha:
                # Do not create duplicate image payloads under another family;
                # retain the candidate in the report for later variant review.
                local.unlink(missing_ok=True)
                failures.append({"page": page_url, "title": title, "file": file_title, "reason": "duplicate_image_payload", "same_as": seen_sha[sha]})
                continue
            seen_sha[sha] = rid
            row = page_rows[0]
            original = clean(re.split(r"\s+[–-]\s+", row["name_original"], maxsplit=1)[0]) or title
            date_candidates = []
            for r in page_rows:
                date_candidates.extend(r.get("date_candidates", []))
            year = sorted(set(date_candidates))[0] if date_candidates else None
            records.append({
                "id": rid,
                "family": family,
                "country_zh": "波兰",
                "name": chinese_name(original),
                "original": original,
                "date": f"{year}年设立／纪年" if year else "日期待考",
                "variant": "国家／部门奖章对象页完整章体；同一条目含多等级时本行以该图示为准，具体制造商待考",
                "views": [{"key": rid + "-VIEW1", "label": "完整图样"}],
                "source_ids": [r["source_id"] for r in page_rows[:8]],
                "source_page": page_url,
                "image_kind": "wikimedia_object_page_image",
                "html_eligible": True,
            })
            images.append({
                "key": rid.lower() + "-image-01",
                "record_id": rid,
                "view_key": rid + "-VIEW1",
                "local_path": str(local.relative_to(ROOT)).replace("\\", "/"),
                "source_page": page_url,
                "image_page": info.get("descriptionurl") or info.get("file_page"),
                "image_url": info.get("thumburl") or info.get("url"),
                "license": ((info.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "Wikimedia Commons; verify file license"),
                "dimensions": list(size),
                "bytes": local.stat().st_size,
                "sha256": sha,
                "decoded": True,
                "visually_checked": False,
                "source_file_title": file_title,
            })
            if index % 15 == 0:
                print(f"processed {index}/{len(grouped)} pages; records={len(records)} images={len(images)}")
            time.sleep(0.08)
        except Exception as exc:
            failures.append({"page": page_url, "reason": f"exception: {type(exc).__name__}: {exc}"})
    volume = {"as_of": date.today().isoformat(), "volume": "波兰", "records": records}
    manifest = {"as_of": date.today().isoformat(), "images": images, "unpictured_candidates": failures}
    (ROOT / "data/volumes/poland_wikipedia_families.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/volumes/poland_wikipedia_families_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "source_id": "wikipedia-poland-object-image-harvest",
        "accessed": date.today().isoformat(), "status": "complete",
        "candidate_object_pages": len(grouped), "processed_object_pages": len(grouped),
        "pictured_families": len(records), "decoded_images": len(images), "failures_or_unpictured": len(failures),
        "raw_candidate_source": "data/raw_candidates/wikipedia_poland_pl_awards.jsonl",
        "volume": "data/volumes/poland_wikipedia_families.json",
        "manifest": "data/volumes/poland_wikipedia_families_manifest.json",
    }
    out = ROOT / "data/source_sweeps/wikipedia_poland_object_images_2026-09-28.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
