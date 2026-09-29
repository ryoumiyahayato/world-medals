from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDFS = [
    ("kingdom", ROOT / "sources/books/cambodia/wawards_kingdom_cambodia.pdf"),
    ("peoples_republic", ROOT / "sources/books/cambodia/wawards_peoples_republic_kampuchea.pdf"),
]
PAGE_DIR = ROOT / "sources/pages/wawards_cambodia"
RAW_DIR = ROOT / "assets/raw/wawards_cambodia"
RAW_OUT = ROOT / "data/raw_candidates/wawards_cambodia.jsonl"
SWEEP_OUT = ROOT / "data/source_sweeps/wawards_cambodia_2026-09-28.json"
BASE = "https://wawards.org"
COUNTRY_SLUG = "cambodia"
URL_SCOPE = "/en/cambodia/"
IMAGE_SCOPE = "/images/cambodia/"
CATALOG_ID_PATTERN = r"(?:KHM|KAM)\d{3}"
SOURCE_URLS = [
    "https://wawards.org/images/cambodia/1/cambodia.pdf",
    "https://wawards.org/images/cambodia/2/kampuchea.pdf",
]


def curl(url: str, output: Path) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.run([
        "curl.exe", "-L", "--fail", "--retry", "2", "--retry-delay", "2",
        "--connect-timeout", "20", "--max-time", "90", "-A", "Mozilla/5.0",
        "-o", str(output), url,
    ], cwd=ROOT, capture_output=True, text=True)
    return process.returncode == 0 and output.exists() and output.stat().st_size > 0


def annotation_urls(pdf: Path) -> list[str]:
    urls: list[str] = []
    for page in PdfReader(pdf).pages:
        annotations = page.get("/Annots")
        annotations = annotations.get_object() if hasattr(annotations, "get_object") else (annotations or [])
        for annotation in annotations:
            obj = annotation.get_object()
            action = obj.get("/A")
            action = action.get_object() if hasattr(action, "get_object") else action
            uri = action.get("/URI") if action else None
            if uri and URL_SCOPE in str(uri) and str(uri) not in urls:
                urls.append(str(uri))
    return urls


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_OUT.parent.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[str, str]] = []
    pdf_pages = 0
    for polity, pdf in PDFS:
        pdf_pages += len(PdfReader(pdf).pages)
        tasks.extend((polity, url) for url in annotation_urls(pdf))

    records, failures = [], []
    image_count = 0
    for index, (polity, url) in enumerate(tasks, 1):
        slug = Path(urlparse(url).path).stem
        page_path = PAGE_DIR / f"{polity}__{slug}.html"
        if not page_path.exists() and not curl(url, page_path):
            failures.append({"url": url, "stage": "page"})
            continue
        body = page_path.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"<title>(.*?)</title>", body, flags=re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else slug.replace("-", " ").title()
        id_match = re.search(rf"\b{CATALOG_ID_PATTERN}\b", body)
        catalog_id = id_match.group(0) if id_match else f"KHM-URL-{index:03d}"
        image_urls: list[str] = []
        for href in re.findall(r'href=["\']([^"\']+)["\']', body, flags=re.I):
            if re.search(re.escape(IMAGE_SCOPE) + r".+\.(?:jpe?g|png)$", href, flags=re.I):
                absolute = urljoin(BASE, href)
                if absolute not in image_urls:
                    image_urls.append(absolute)
        local_images = []
        for view_no, image_url in enumerate(image_urls, 1):
            suffix = Path(urlparse(image_url).path).suffix.lower() or ".jpg"
            destination = RAW_DIR / f"{polity}__{slug}_{view_no:02d}{suffix}"
            if not destination.exists() and not curl(image_url, destination):
                failures.append({"url": image_url, "stage": "image", "object_url": url})
                continue
            try:
                with Image.open(destination) as image:
                    image.verify()
                with Image.open(destination) as image:
                    width, height = image.size
            except Exception as error:
                failures.append({"url": image_url, "stage": "decode", "error": str(error)})
                destination.unlink(missing_ok=True)
                continue
            local_images.append({
                "view_no": view_no,
                "image_url": image_url,
                "local_path": destination.relative_to(ROOT).as_posix(),
                "width": width,
                "height": height,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            })
            image_count += 1
        records.append({
            "source_id": f"wawards-{COUNTRY_SLUG}-{polity}-{catalog_id}-{slug}",
            "catalog_id": catalog_id,
            "historical_polity": polity,
            "page_title": title,
            "working_name_zh": "待归并",
            "name_original": title,
            "name_en": title,
            "alternate_names": [],
            "date_candidates": [],
            "category": "order_or_medal",
            "grade_material_clues": "待核",
            "object_url": url,
            "image_page_url": url,
            "original_images": local_images,
            "notes": "World Awards reference catalogue object page.",
            "status": "harvested" if local_images else "UNPICTURED",
        })
        print(f"[{index}/{len(tasks)}] {polity} {slug}: {len(local_images)} images", flush=True)
        if index != len(tasks):
            time.sleep(0.2)

    with RAW_OUT.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
    report = {
        "source_id": f"wawards-{COUNTRY_SLUG}-catalogues",
        "source_urls": SOURCE_URLS,
        "accessed": date.today().isoformat(),
        "scope": "Both complete reference catalogue PDFs, all linked object pages, and all public full-size images.",
        "status": "complete" if not failures and len(records) == len(tasks) else "partial",
        "pdf_pages": pdf_pages,
        "planned_object_pages": len(tasks),
        "processed_object_pages": len(records),
        "downloaded_images": image_count,
        "failures": failures,
        "raw_output": RAW_OUT.relative_to(ROOT).as_posix(),
    }
    SWEEP_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
