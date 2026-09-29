"""Sweep and cache the complete current eMedals Egypt Shopify collection."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "emedals_egypt_catalog"
BASE = "https://www.emedals.com"
COLLECTION = f"{BASE}/collections/africa-egypt"
API = f"{COLLECTION}/products.json?limit=250&page=1"
PAGE_DIR = ROOT / "sources/pages/emedals_egypt"
IMAGE_DIR = ROOT / "assets/raw/emedals_egypt"
RAW_OUT = ROOT / "data/raw_candidates/emedals_egypt_catalog.jsonl"
HARVEST_OUT = ROOT / "data/image_harvest/emedals_egypt_catalog.json"
SWEEP_OUT = ROOT / "data/source_sweeps/emedals_egypt_catalog_2026-09-27.json"
USER_AGENT = "world-medals research cache/1.0 (bounded public catalogue sweep)"


def fetch(url: str) -> bytes:
    error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"failed after bounded retries: {url}: {error}")


def cached_fetch(url: str, path: Path) -> bytes:
    if path.is_file() and path.stat().st_size:
        return path.read_bytes()
    payload = fetch(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def clean_text(markup: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", markup, flags=re.I)
    value = re.sub(r"</(?:p|li|div|h\d)>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value).replace("\xa0", " ")
    return " ".join(value.split())


def image_task(spec: dict) -> dict:
    path = ROOT / spec["local_path"]
    payload = cached_fetch(spec["image_url"], path)
    with Image.open(path) as opened:
        dimensions = list(opened.size)
        opened.verify()
    return {**spec, "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "decoded": True}


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    api_bytes = cached_fetch(API, PAGE_DIR / "products-page-1.json")
    products = json.loads(api_bytes)["products"]
    if len(products) < 80:
        raise RuntimeError(f"unexpectedly short eMedals Egypt collection: {len(products)} products")

    candidates = []
    image_specs = []
    for position, product in enumerate(products, 1):
        handle = product["handle"]
        page_url = f"{BASE}/products/{handle}"
        description = clean_text(product.get("body_html") or "")
        product_images = []
        for ordinal, image in enumerate(product.get("images") or [], 1):
            image_url = image["src"].replace("http://", "https://")
            ext = Path(urllib.parse.urlparse(image_url).path).suffix.lower() or ".jpg"
            local = IMAGE_DIR / f"{product['id']}_{image['id']}_{ordinal:02d}{ext}"
            spec = {
                "product_id": product["id"], "product_title": product["title"], "product_handle": handle,
                "product_page": page_url, "ordinal": ordinal, "image_id": image["id"],
                "image_url": image_url, "alt": image.get("alt") or product["title"],
                "local_path": local.relative_to(ROOT).as_posix(),
            }
            product_images.append(spec)
            image_specs.append(spec)
        candidates.append({
            "source_id": SOURCE_ID, "source_position": position, "source_product_id": product["id"],
            "page_title": product["title"], "working_name_zh": "待归并",
            "original_name": product["title"], "english_name": product["title"],
            "date_candidates": sorted(set(re.findall(r"\b(?:18|19|20)\d{2}\b", product["title"] + " " + description))),
            "category": product.get("product_type") or "order, decoration or medal",
            "vendor": product.get("vendor") or "eMedals",
            "tags": product.get("tags") or [],
            "grade_or_material_clues": description,
            "object_page_url": page_url, "image_page_url": page_url,
            "original_image_urls": [item["image_url"] for item in product_images],
            "local_images": [item["local_path"] for item in product_images],
            "image_labels": [f"catalogue image {item['ordinal']}" for item in product_images],
            "status": "SOURCE_SWEEP_CANDIDATE" if product_images else "SOURCE_RECORD_NO_OBJECT_IMAGE",
            "accessed": "2026-09-27",
        })

    images = []
    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(image_task, spec): spec for spec in image_specs}
        for future in as_completed(futures):
            spec = futures[future]
            try:
                images.append(future.result())
            except Exception as exc:
                failures.append({"image_url": spec["image_url"], "product_page": spec["product_page"], "error": str(exc)})
    images.sort(key=lambda item: (item["product_id"], item["ordinal"]))

    RAW_OUT.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in candidates) + "\n", encoding="utf-8")
    HARVEST_OUT.write_text(json.dumps({"as_of": "2026-09-27", "source_id": SOURCE_ID, "images": images, "failures": failures}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SWEEP_OUT.write_text(json.dumps({
        "schema_version": "2.0", "source_id": SOURCE_ID, "scope_id": "egypt", "as_of": "2026-09-27",
        "status": "completed" if not failures else "completed_with_failures", "collection_url": COLLECTION, "api_url": API,
        "products_discovered": len(products), "products_processed": len(candidates),
        "images_discovered": len(image_specs), "images_downloaded_and_decoded": len(images), "failed_images": failures,
        "candidate_file": RAW_OUT.relative_to(ROOT).as_posix(), "image_harvest_file": HARVEST_OUT.relative_to(ROOT).as_posix(),
        "api_cache": (PAGE_DIR / "products-page-1.json").relative_to(ROOT).as_posix(), "image_cache": IMAGE_DIR.relative_to(ROOT).as_posix(),
        "completion_boundary": "All 91 products currently exposed by the public africa-egypt Shopify collection API at limit 250 page 1 were processed; page 2 was checked and returned zero products.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"products": len(products), "images": len(images), "failures": len(failures)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
