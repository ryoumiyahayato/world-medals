"""Recursively sweep the Wikimedia Commons Sudan award category tree once."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://commons.wikimedia.org/w/api.php"
SCOPE_ID = "sudan"
SCOPE_LABEL = "Sudan"
AS_OF = "2026-09-27"
START = "Category:Orders, decorations and medals of Sudan"
OUT = ROOT / "data/raw_candidates/commons_sudan.jsonl"
SWEEP = ROOT / "data/source_sweeps/commons_sudan_complete_2026-09-27.json"
STATE = ROOT / "sources/cache/commons_sudan_sweep_state.json"
RAW = ROOT / "assets/raw/commons_sudan"
RAW.mkdir(parents=True, exist_ok=True)
UA = "world-medals-research/1.0 (offline catalogue; respectful single-threaded sweep)"
SKIP_CATEGORY_TERMS = ("recipient", "recipients", "people awarded", "holders of")
OBJECT_TERMS = (
    "medal", "order", "decoration", "badge", "star", "collar", "sash", "cross",
    "وسام", "ميدالية", "نيشان",
)
FOLLOW_CATEGORY_TERMS = OBJECT_TERMS + (
    "award", "honour", "honor", "gallantry", "bravery", "merit", "service",
    "accomplishment", "independence", "defence force",
)


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            retry_after = exc.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 5 * (attempt + 1))
    raise RuntimeError("unreachable")


def members(category: str) -> list[dict]:
    result, cont = [], {}
    while True:
        data = api({"action": "query", "list": "categorymembers", "cmtitle": category,
                    "cmtype": "subcat|file", "cmlimit": "max", **cont})
        result.extend(data["query"]["categorymembers"])
        if "continue" not in data:
            return result
        cont = data["continue"]
        time.sleep(0.5)


def image_infos(titles: list[str]) -> dict[str, dict]:
    result = {}
    for offset in range(0, len(titles), 50):
        batch = titles[offset:offset + 50]
        data = api({"action": "query", "prop": "imageinfo", "titles": "|".join(batch),
                    "iiprop": "url|size|mime|sha1|extmetadata"})
        for page in data["query"]["pages"]:
            result[page["title"]] = (page.get("imageinfo") or [{}])[0]
        time.sleep(1.0)
    return result


def main() -> None:
    if STATE.exists():
        saved = json.loads(STATE.read_text(encoding="utf-8"))
        todo, seen = saved["todo"], set(saved["seen"])
        files = {title: set(categories) for title, categories in saved["files"].items()}
    else:
        todo, seen, files = [START], set(), {}
    while todo:
        category = todo.pop(0)
        if category in seen:
            continue
        if len(seen) >= 200:
            raise RuntimeError("Category safety limit reached before completing the tree")
        seen.add(category)
        for item in members(category):
            title = item["title"]
            lower_title = title.casefold()
            if (item["ns"] == 14 and title not in seen
                    and not any(term in lower_title for term in SKIP_CATEGORY_TERMS)
                    and any(term in lower_title for term in FOLLOW_CATEGORY_TERMS)):
                todo.append(title)
            elif item["ns"] == 6:
                files.setdefault(title, set()).add(category)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({
            "todo": todo, "seen": sorted(seen),
            "files": {title: sorted(categories) for title, categories in files.items()},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(0.5)

    rows, downloaded, failures = [], 0, []
    ordered_titles = sorted(files)
    details = image_infos(ordered_titles)
    for index, title in enumerate(ordered_titles, 1):
        info = details.get(title, {})
        url = info.get("url")
        ext = Path(urllib.parse.urlparse(url or "").path).suffix.lower()
        local = None
        description = (info.get("extmetadata", {}).get("ImageDescription") or {}).get("value", "")
        object_likelihood = (title + " " + description).casefold()
        likely_object = any(term in object_likelihood for term in OBJECT_TERMS) and "ribbon" not in object_likelihood
        if url and likely_object and ext in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
            name = hashlib.sha256(title.encode("utf-8")).hexdigest()[:16] + ext
            path = RAW / name
            if not path.exists():
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=90) as response:
                        path.write_bytes(response.read())
                except Exception as exc:
                    failures.append({"title": title, "url": url, "error": str(exc)})
                    path.unlink(missing_ok=True)
            if path.exists():
                local = path.relative_to(ROOT).as_posix()
                downloaded += 1
        meta = info.get("extmetadata") or {}
        rows.append({
            "source_id": f"commons-{SCOPE_ID}-{index:04d}", "source_system": "Wikimedia Commons",
            "scope": f"{SCOPE_LABEL} category tree", "page_title": title.removeprefix("File:"),
            "file_title": title, "categories": sorted(files[title]),
            "page_url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":()'_,.-"),
            "original_image_url": url, "local_raw_image": local,
            "width": info.get("width"), "height": info.get("height"), "mime": info.get("mime"),
            "sha1": info.get("sha1"),
            "description": (meta.get("ImageDescription") or {}).get("value"), "likely_object": likely_object,
            "license": (meta.get("LicenseShortName") or {}).get("value"),
            "artist": (meta.get("Artist") or {}).get("value"),
            "status": "RAW_CANDIDATE", "access_date": AS_OF,
        })
        time.sleep(0.5)

    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": AS_OF, "source": START, "status": "complete" if not failures else "complete_with_download_failures",
        "categories_visited": len(seen), "files_discovered": len(rows), "raster_files_cached": downloaded,
        "download_failures": failures, "categories": sorted(seen),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    STATE.unlink(missing_ok=True)
    print(f"swept {len(seen)} categories, {len(rows)} files, cached {downloaded} rasters, failures {len(failures)}")


if __name__ == "__main__":
    main()
