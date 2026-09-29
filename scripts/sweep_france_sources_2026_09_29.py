from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
UA = "world-medals-research/1.0 (source-first catalogue audit)"
TODAY = date.today().isoformat()
DATE_RE = re.compile(r"\b(?:1[0-9]{3}|20[0-9]{2})\b")
IMAGE_EXT_RE = re.compile(r"\.(?:jpe?g|png|webp|gif)(?:$|\?)", re.I)
SKIP_IMAGE_RE = re.compile(
    r"(?:logo|favicon|avatar|emoji|cropped-|header|footer|spinner|placeholder|blank|icon)", re.I
)


def get(session: requests.Session, url: str, tries: int = 2) -> requests.Response:
    last = None
    for attempt in range(tries):
        try:
            response = session.get(url, timeout=(10, 20))
            if response.status_code in {429, 500, 502, 503, 504}:
                last = RuntimeError(f"HTTP {response.status_code}")
                time.sleep(2 + attempt * 3)
                continue
            response.raise_for_status()
            return response
        except Exception as exc:  # retained in sweep state
            last = exc
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"GET failed: {url}: {last}")


def sitemap_urls(session: requests.Session, url: str) -> tuple[bytes, list[str]]:
    payload = get(session, url).content
    root = ET.fromstring(payload)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return payload, [node.text.strip() for node in root.findall(".//s:loc", ns) if node.text]


def safe_name(index: int, url: str) -> str:
    path = urlparse(url).path.strip("/")
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", path)[-130:] or "root"
    return f"{index:04d}_{slug}.html"


def clean_text(soup: BeautifulSoup) -> str:
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def title_of(soup: BeautifulSoup) -> str:
    for selector in ("h1", "article h2", "meta[property='og:title']", "title"):
        node = soup.select_one(selector)
        if not node:
            continue
        value = node.get("content") if node.name == "meta" else node.get_text(" ", strip=True)
        if value:
            return " ".join(value.split())
    return ""


def image_refs(soup: BeautifulSoup, page_url: str, same_host: str) -> list[dict]:
    refs: dict[str, dict] = {}
    for image in soup.find_all("img"):
        candidates: list[str] = []
        for attr in ("data-src", "data-lazy-src", "src"):
            if image.get(attr):
                candidates.append(image.get(attr))
        for attr in ("srcset", "data-srcset"):
            if image.get(attr):
                candidates.extend(item.strip().split()[0] for item in image.get(attr).split(","))
        for raw in candidates:
            absolute = urljoin(page_url, raw)
            parsed = urlparse(absolute)
            if parsed.netloc != same_host or not IMAGE_EXT_RE.search(absolute):
                continue
            if SKIP_IMAGE_RE.search(parsed.path):
                continue
            refs[absolute] = {
                "url": absolute,
                "alt": " ".join((image.get("alt") or "").split()),
                "title": " ".join((image.get("title") or "").split()),
            }
    return list(refs.values())


def download_images(
    session: requests.Session,
    refs: list[dict],
    out_dir: Path,
    pause: float,
) -> tuple[list[dict], list[dict]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    done: dict[str, dict] = {}
    errors: list[dict] = []

    def download_one(ref: dict) -> tuple[dict | None, dict | None]:
        url = ref["url"]
        try:
            response = requests.get(
                url,
                timeout=(8, 15),
                headers={"User-Agent": UA, "Accept-Language": "fr,en;q=0.8"},
            )
            response.raise_for_status()
            payload = response.content
            digest = hashlib.sha256(payload).hexdigest()
            suffix = Path(urlparse(url).path).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                suffix = ".bin"
            path = out_dir / f"{digest[:20]}{suffix}"
            if not path.exists():
                path.write_bytes(payload)
            try:
                with Image.open(path) as im:
                    im.verify()
                with Image.open(path) as im:
                    width, height = im.size
                    fmt = im.format
                status = "decoded"
            except Exception as exc:
                width = height = 0
                fmt = None
                status = f"decode_error:{exc}"
            result = {
                **ref,
                "local_path": path.relative_to(ROOT).as_posix(),
                "sha256": digest,
                "bytes": len(payload),
                "width": width,
                "height": height,
                "format": fmt,
                "status": status,
                "content_type": response.headers.get("content-type"),
            }
            time.sleep(pause)
            return result, None
        except Exception as exc:
            return None, {"url": url, "error": str(exc)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(download_one, ref) for ref in refs]
        for i, future in enumerate(as_completed(futures), 1):
            result, error = future.result()
            if result:
                done[result["url"]] = result
            if error:
                errors.append(error)
            if i % 50 == 0:
                print(f"images {i}/{len(refs)}", flush=True)
    return list(done.values()), errors


def sweep_samlhoc(session: requests.Session, pause: float, download: bool) -> dict:
    cache = ROOT / "sources/cache/france_samlhoc_full_2026-09-29"
    pages = cache / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    raw_dir = ROOT / "data/raw_candidates"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sitemap_url = "https://www.samlhoc.fr/phaleristique-sitemap.xml"
    payload, all_urls = sitemap_urls(session, sitemap_url)
    (cache / "phaleristique-sitemap.xml").write_bytes(payload)
    selected = [
        u for u in all_urls
        if any(f"/phaleristique/{tree}/" in u for tree in ("ordres-chevalerie", "decorations", "medailles"))
    ]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    failures: list[dict] = []
    all_images: dict[str, dict] = {}
    for i, url in enumerate(selected, 1):
        target = pages / safe_name(i, url)
        try:
            if target.exists():
                content = target.read_bytes()
            else:
                content = get(session, url).content
                target.write_bytes(content)
            soup = BeautifulSoup(content, "html.parser")
            path_parts = [p for p in urlparse(url).path.split("/") if p]
            tree = path_parts[1] if len(path_parts) > 1 else "unknown"
            family_slug = path_parts[2] if len(path_parts) > 2 else "unknown"
            refs = image_refs(soup, url, "www.samlhoc.fr")
            for ref in refs:
                all_images[ref["url"]] = ref
            text = clean_text(soup)
            groups[(tree, family_slug)].append({
                "page_url": url,
                "page_title": title_of(soup),
                "local_cache": target.relative_to(ROOT).as_posix(),
                "date_candidates": sorted(set(DATE_RE.findall(text)))[:80],
                "image_refs": refs,
                "text_excerpt": text[:1200],
            })
        except Exception as exc:
            failures.append({"url": url, "error": str(exc)})
        if i % 50 == 0:
            print(f"samlhoc pages {i}/{len(selected)}", flush=True)
        time.sleep(pause)

    image_manifest, image_errors = ([], [])
    if download:
        image_manifest, image_errors = download_images(
            session,
            list(all_images.values()),
            ROOT / "assets/raw/france_samlhoc_full_2026-09-29",
            pause,
        )
    image_by_url = {item["url"]: item for item in image_manifest}
    raw_path = raw_dir / "france_samlhoc_full_2026-09-29.jsonl"
    with raw_path.open("w", encoding="utf-8", newline="\n") as handle:
        for (tree, slug), page_rows in sorted(groups.items()):
            urls = sorted({ref["url"] for page in page_rows for ref in page["image_refs"]})
            record = {
                "source_id": f"FR-SAMLHOC-{tree.upper()}-{slug.upper().replace('-', '_')}",
                "source_system": "SAMLHOC / France Phaléristique",
                "accessed": TODAY,
                "category_tree": tree,
                "family_slug": slug,
                "family_guess": f"FRA-SAMLHOC-{slug.upper().replace('-', '-')}",
                "page_count": len(page_rows),
                "page_titles": [p["page_title"] for p in page_rows],
                "pages": page_rows,
                "original_image_urls": urls,
                "downloaded_images": [image_by_url[u] for u in urls if u in image_by_url],
                "status": "raw_family_candidate",
                "rights": "SAMLHOC site states all rights reserved; internal research cache only unless independent reuse permission is found.",
                "note": "Family-level raw aggregation from the complete visible sitemap branch; normalize grantor, family identity and object variants before public use.",
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    manifest_path = cache / "image_manifest.json"
    manifest_path.write_text(json.dumps({
        "source": sitemap_url,
        "accessed": TODAY,
        "images": image_manifest,
        "errors": image_errors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    state = {
        "source_id": "FR-SAMLHOC-FULL-PHALERISTIQUE",
        "source_url": "https://www.samlhoc.fr/phaleristique/",
        "sitemap_url": sitemap_url,
        "accessed": TODAY,
        "scope": ["ordres-chevalerie", "decorations", "medailles"],
        "sitemap_total_urls": len(all_urls),
        "selected_urls": len(selected),
        "completed_pages": len(selected) - len(failures),
        "failed_pages": failures,
        "raw_family_candidates": len(groups),
        "unique_image_refs": len(all_images),
        "downloaded_images": len(image_manifest),
        "decoded_images": sum(1 for x in image_manifest if x["status"] == "decoded"),
        "image_errors": image_errors,
        "raw_candidates": raw_path.relative_to(ROOT).as_posix(),
        "cache_root": cache.relative_to(ROOT).as_posix(),
        "rights": "All rights reserved; source cached for research and gap analysis only.",
    }
    state_path = ROOT / "data/source_sweeps/france_samlhoc_full_2026-09-29.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def relevant_official(url: str) -> bool:
    path = urlparse(url).path.lower()
    if "/fr/les-decorations/" in path or "/fr/le-musee/" in path:
        return True
    terms = (
        "decoration", "medaille", "ordre-national", "legion-dhonneur", "merite",
        "phaleristique", "insigne", "musee", "exposition", "publication",
    )
    return "/fr/actualites/" in path and any(term in path for term in terms)


def sweep_official(session: requests.Session, pause: float, download: bool) -> dict:
    cache = ROOT / "sources/cache/france_legiondhonneur_full_2026-09-29"
    pages = cache / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    sitemap_url = "https://www.legiondhonneur.fr/sitemap.xml"
    payload, all_urls = sitemap_urls(session, sitemap_url)
    (cache / "sitemap.xml").write_bytes(payload)
    selected = [u for u in all_urls if relevant_official(u)]
    failures: list[dict] = []
    rows: list[dict] = []
    all_images: dict[str, dict] = {}
    for i, url in enumerate(selected, 1):
        target = pages / safe_name(i, url)
        try:
            if target.exists():
                content = target.read_bytes()
            else:
                content = get(session, url).content
                target.write_bytes(content)
            soup = BeautifulSoup(content, "html.parser")
            refs = image_refs(soup, url, "www.legiondhonneur.fr")
            for ref in refs:
                all_images[ref["url"]] = ref
            text = clean_text(soup)
            rows.append({
                "source_id": f"FR-GCLH-{i:04d}",
                "page_url": url,
                "page_title": title_of(soup),
                "local_cache": target.relative_to(ROOT).as_posix(),
                "date_candidates": sorted(set(DATE_RE.findall(text)))[:100],
                "image_refs": refs,
                "text_excerpt": text[:1800],
                "status": "official_verification_page",
            })
        except Exception as exc:
            failures.append({"url": url, "error": str(exc)})
        if i % 25 == 0:
            print(f"official pages {i}/{len(selected)}", flush=True)
        time.sleep(pause)
    image_manifest, image_errors = ([], [])
    if download:
        image_manifest, image_errors = download_images(
            session,
            list(all_images.values()),
            ROOT / "assets/raw/france_legiondhonneur_full_2026-09-29",
            pause,
        )
    image_by_url = {item["url"]: item for item in image_manifest}
    raw_path = ROOT / "data/raw_candidates/france_legiondhonneur_full_2026-09-29.jsonl"
    with raw_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            row["downloaded_images"] = [
                image_by_url[ref["url"]] for ref in row["image_refs"] if ref["url"] in image_by_url
            ]
            row["source_system"] = "Grande chancellerie de la Légion d'honneur"
            row["accessed"] = TODAY
            row["rights"] = "Official-site material; no blanket open reuse licence located in this sweep."
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (cache / "image_manifest.json").write_text(json.dumps({
        "source": sitemap_url,
        "accessed": TODAY,
        "images": image_manifest,
        "errors": image_errors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    state = {
        "source_id": "FR-GCLH-OFFICIAL-FULL",
        "source_url": "https://www.legiondhonneur.fr/fr",
        "sitemap_url": sitemap_url,
        "accessed": TODAY,
        "sitemap_total_urls": len(all_urls),
        "selected_urls": len(selected),
        "completed_pages": len(rows),
        "failed_pages": failures,
        "unique_image_refs": len(all_images),
        "downloaded_images": len(image_manifest),
        "decoded_images": sum(1 for x in image_manifest if x["status"] == "decoded"),
        "image_errors": image_errors,
        "raw_candidates": raw_path.relative_to(ROOT).as_posix(),
        "cache_root": cache.relative_to(ROOT).as_posix(),
        "rights": "No blanket open reuse licence found; use pages for institutional facts and keep images internal unless object-level permission is clear.",
    }
    state_path = ROOT / "data/source_sweeps/france_legiondhonneur_full_2026-09-29.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["samlhoc", "official", "both"], default="both")
    parser.add_argument("--pause", type=float, default=0.12)
    parser.add_argument("--no-images", action="store_true")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "fr,en;q=0.8"})
    result = {}
    if args.source in {"samlhoc", "both"}:
        result["samlhoc"] = sweep_samlhoc(session, args.pause, not args.no_images)
    if args.source in {"official", "both"}:
        result["official"] = sweep_official(session, args.pause, not args.no_images)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
