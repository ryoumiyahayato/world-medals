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
PDF = ROOT / "sources/books/turkmenistan/wawards_turkmenistan.pdf"
PAGE_DIR = ROOT / "sources/pages/wawards_turkmenistan"
RAW_DIR = ROOT / "assets/raw/wawards_turkmenistan"
RAW_OUT = ROOT / "data/raw_candidates/wawards_turkmenistan.jsonl"
SWEEP_OUT = ROOT / "data/source_sweeps/wawards_turkmenistan_2026-09-28.json"
BASE = "https://wawards.org"


def curl(url: str, output: Path) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.run([
        "curl.exe", "-L", "--fail", "--retry", "2", "--retry-delay", "2",
        "--connect-timeout", "20", "--max-time", "90", "-A", "Mozilla/5.0",
        "-o", str(output), url,
    ], cwd=ROOT, capture_output=True, text=True)
    return process.returncode == 0 and output.exists() and output.stat().st_size > 0


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_OUT.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(PDF)
    urls: list[str] = []
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            obj = annotation.get_object()
            action = obj.get("/A")
            uri = action.get("/URI") if action else None
            if uri and "/en/turkmenistan/" in uri and uri not in urls:
                urls.append(uri)

    records, failures = [], []
    image_count = 0
    for index, url in enumerate(urls, 1):
        slug = Path(urlparse(url).path).stem
        page_path = PAGE_DIR / f"{slug}.html"
        if not page_path.exists() and not curl(url, page_path):
            failures.append({"url": url, "stage": "page"})
            continue
        body = page_path.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"<title>(.*?)</title>", body, flags=re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else slug.replace("-", " ").title()
        id_match = re.search(r"\b(TKM\d{3})\b", body)
        catalog_id = id_match.group(1) if id_match else f"TKM-URL-{index:03d}"
        image_urls = []
        for href in re.findall(r'href=["\']([^"\']+)["\']', body, flags=re.I):
            if re.search(r"/images/turkmenistan/.+\.(?:jpe?g|png)$", href, flags=re.I):
                absolute = urljoin(BASE, href)
                if absolute not in image_urls:
                    image_urls.append(absolute)
        local_images = []
        for view_no, image_url in enumerate(image_urls, 1):
            suffix = Path(urlparse(image_url).path).suffix.lower() or ".jpg"
            destination = RAW_DIR / f"{slug}_{view_no:02d}{suffix}"
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
            "source_id": f"wawards-turkmenistan-{catalog_id}",
            "catalog_id": catalog_id,
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
            "notes": "World Awards 2025 reference catalogue object page.",
            "status": "harvested" if local_images else "UNPICTURED",
        })
        if index != len(urls):
            time.sleep(0.25)

    with RAW_OUT.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
    report = {
        "source_id": "wawards-turkmenistan-2025",
        "source_url": "https://wawards.org/images/turkmenistan/turkmenistan.pdf",
        "accessed": date.today().isoformat(),
        "scope": "Complete 2025 reference catalogue PDF, all linked Turkmenistan object pages, and all public full-size images.",
        "status": "complete" if not failures and len(records) == 29 else "partial",
        "pdf_pages": len(reader.pages),
        "planned_object_pages": len(urls),
        "processed_object_pages": len(records),
        "downloaded_images": image_count,
        "failures": failures,
        "raw_output": RAW_OUT.relative_to(ROOT).as_posix(),
    }
    SWEEP_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
