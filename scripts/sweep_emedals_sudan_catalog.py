"""Sweep eMedals collection JSON endpoints for every Sudan product.

This is a source-level inventory pass.  It caches collection responses and
product pages, but does not promote candidates into the public catalogue.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sources/pages/emedals_sudan_catalog"
OUTPUT = ROOT / "data/raw_candidates/emedals_sudan_catalog.jsonl"
SWEEP = ROOT / "data/source_sweeps/emedals_sudan_catalog_2026-09-27.json"
BASE = "https://www.emedals.com"
COLLECTIONS = ("africa", "africa-other", "middle-east-other")
HEADERS = {"User-Agent": "world-medals research catalogue/1.0"}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def get(url: str) -> tuple[bytes, str]:
    with urlopen(Request(url, headers=HEADERS), timeout=45) as response:
        raw = response.read()
    return raw, raw.decode("utf-8", errors="replace")


def page_candidates(collection: str) -> tuple[list[dict], int]:
    found: dict[str, dict] = {}
    page = 1
    while True:
        url = f"{BASE}/collections/{collection}/products.json?limit=250&page={page}"
        raw, text = get(url)
        cache_path = CACHE / f"collection_{collection}_{page:03d}.json"
        atomic_text(cache_path, text)
        payload = json.loads(text)
        products = payload.get("products", [])
        if not products:
            return list(found.values()), page
        for product in products:
            title = str(product.get("title", ""))
            # Product descriptions often mention neighbouring Sudan only as
            # geography or provenance.  Keep the sweep scoped to objects whose
            # actual catalogue title identifies them as Sudan/Sudanese.
            body = str(product.get("body_html", ""))
            explicit_sudan_title = re.search(r"\bsudan(?:ese)?\b", title, re.I) and not title.lower().startswith("egypt")
            known_sudan_pair = "Order of Civil Accomplishment" in body and "Order of Political Accomplishment" in body
            if explicit_sudan_title or known_sudan_pair:
                found[product["handle"]] = product
        page += 1
        time.sleep(0.15)


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    products: dict[str, dict] = {}
    collection_pages: dict[str, int] = {}
    membership: dict[str, set[str]] = {}

    for collection in COLLECTIONS:
        candidates, terminating_page = page_candidates(collection)
        collection_pages[collection] = terminating_page
        for product in candidates:
            handle = product["handle"]
            products[handle] = product
            membership.setdefault(handle, set()).add(collection)

    rows = []
    for handle in sorted(products):
        url = f"{BASE}/products/{handle}"
        page_path = CACHE / f"product_{handle}.html"
        if page_path.exists():
            raw = page_path.read_bytes()
            text = raw.decode("utf-8", errors="replace")
        else:
            raw, text = get(url)
            atomic_text(page_path, text)
        product = products[handle]
        images = []
        for image in product.get("images", []):
            src = image.get("src")
            if src:
                images.append(src if src.startswith("http") else "https:" + src)
        body = re.sub(r"<[^>]+>", " ", product.get("body_html") or "")
        body = re.sub(r"\s+", " ", body).strip()
        rows.append({
            "source": "eMedals",
            "source_id": f"emedals-{handle.rsplit('-', 1)[-1]}",
            "source_scope": "eMedals Sudan products across Africa, Africa-Other and Middle East-Other collections",
            "collections": sorted(membership[handle]),
            "title": product.get("title", ""),
            "handle": handle,
            "product_url": url,
            "description": body,
            "product_type": product.get("product_type", ""),
            "tags": product.get("tags", []),
            "image_original_urls": images,
            "image_count": len(images),
            "cache_path": page_path.relative_to(ROOT).as_posix(),
            "cache_sha256": hashlib.sha256(raw).hexdigest(),
            "accessed": str(date.today()),
            "status": "RAW_CANDIDATE_PENDING_NORMALIZATION",
        })
        if not page_path.exists():
            time.sleep(0.15)

    atomic_text(OUTPUT, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    atomic_text(SWEEP, json.dumps({
        "as_of": str(date.today()),
        "source_id": "emedals_sudan_catalog",
        "status": "completed_current_collection_json_sweep",
        "collections": list(COLLECTIONS),
        "terminating_empty_page_by_collection": collection_pages,
        "unique_sudan_products": len(rows),
        "product_pages_cached": len(rows),
        "products_with_images": sum(bool(row["image_count"]) for row in rows),
        "raw_candidate_path": OUTPUT.relative_to(ROOT).as_posix(),
        "notes": "Each collection JSON endpoint was paged until its first empty page; matching product pages were cached once and deduplicated by Shopify handle.",
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"swept {len(rows)} unique Sudan eMedals products from {len(COLLECTIONS)} collections")


if __name__ == "__main__":
    main()
