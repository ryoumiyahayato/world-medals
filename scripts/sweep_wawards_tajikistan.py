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
PDF = ROOT / "sources/books/tajikistan/wawards_tajikistan.pdf"
PAGE_DIR = ROOT / "sources/pages/wawards_tajikistan"
RAW_DIR = ROOT / "assets/raw/wawards_tajikistan"
RAW_OUT = ROOT / "data/raw_candidates/wawards_tajikistan.jsonl"
SWEEP_OUT = ROOT / "data/source_sweeps/wawards_tajikistan_2026-09-28.json"
BASE = "https://wawards.org"

CATALOG_IDS = {
    "hero-of-tajikistan-gold-star": "TJK001",
    "order-star-of-the-president-of-tajikistan": "TJK002",
    "order-of-the-golden-crown": "TJK003",
    "order-of-ismoili-somoni": "TJK004",
    "order-of-friendship": "TJK005",
    "order-of-spitamen": "TJK006",
    "order-of-glory": "TJK007",
    "medal-of-valor": "TJK008",
    "medal-for-meritorious-service": "TJK009",
    "medal-of-mercy": "TJK010",
    "valorous-border-guard-of-tajikistan": "TJK011",
    "medal-for-outstanding-service-in-the-armed-forces": "TJK012",
    "5-years-of-the-armed-forces-medal": "TJK013",
    "10-years-of-the-armed-forces-medal": "TJK014",
    "15-years-of-the-armed-forces-medal": "TJK015",
    "20-years-of-the-armed-forces-medal": "TJK016",
    "25-years-of-the-armed-forces-medal": "TJK017",
    "75-years-of-the-police-medal": "TJK018",
    "80-years-of-the-police-medal": "TJK019",
    "20-years-of-the-internal-troops-medal": "TJK020",
    "50-years-of-the-investigative-bodies-medal": "TJK021",
    "10-years-of-the-drug-control-agency-medal": "TJK022",
    "5-years-of-the-presidential-guard-medal": "TJK023",
    "20-years-of-the-emergency-situations-committee": "TJK024",
    "85-years-of-the-prosecutor-s-office-medal": "TJK025",
    "ministry-of-internal-affairs-medal-for-cooperation": "TJK026",
    "90th-anniversary-of-justice-of-tajikistan-medal": "TJK027",
    "medal-of-the-15th-anniversary-of-the-directorate-for-combating-illicit-drug-trafficking": "TJK028",
    "medal-of-the-10th-anniversary-of-the-national-guard": "TJK029",
    "medal-of-the-85th-anniversary-of-the-police": "TJK030",
    "30-years-of-the-armed-forces-medal": "TJK031",
    "jubilee-medal-20th-anniversary-of-the-border-troops": "TJK032",
    "jubilee-medal-25th-anniversary-of-the-border-troops": "TJK033",
    "jubilee-medal-30th-anniversary-of-the-border-troops": "TJK034",
    "jubilee-medal-of-the-academy-of-the-ministry-of-internal-affairs": "TJK035",
}


def curl(url: str, output: Path) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "curl.exe", "-L", "--fail", "--retry", "2", "--retry-delay", "2",
            "--connect-timeout", "20", "--max-time", "90", "-A", "Mozilla/5.0",
            "-o", str(output), url,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and output.exists() and output.stat().st_size > 0


def clean_title(html: str, fallback: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else fallback


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
            if uri and "/en/tajikistan/" in uri and uri not in urls:
                urls.append(uri)

    records: list[dict] = []
    failures: list[dict] = []
    image_count = 0
    for index, url in enumerate(urls, 1):
        slug = Path(urlparse(url).path).stem
        page_path = PAGE_DIR / f"{slug}.html"
        if not page_path.exists() and not curl(url, page_path):
            failures.append({"url": url, "stage": "page"})
            continue
        html = page_path.read_text(encoding="utf-8", errors="replace")
        title = clean_title(html, slug.replace("-", " ").title())
        image_hrefs = []
        for href in re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I):
            if re.search(r"/images/tajikistan/.+\.(?:jpe?g|png)$", href, flags=re.I):
                absolute = urljoin(BASE, href)
                if absolute not in image_hrefs:
                    image_hrefs.append(absolute)

        local_images = []
        for view_no, image_url in enumerate(image_hrefs, 1):
            suffix = Path(urlparse(image_url).path).suffix.lower() or ".jpg"
            image_path = RAW_DIR / f"{slug}_{view_no:02d}{suffix}"
            if not image_path.exists() and not curl(image_url, image_path):
                failures.append({"url": image_url, "stage": "image", "object_url": url})
                continue
            try:
                with Image.open(image_path) as image:
                    image.verify()
                with Image.open(image_path) as image:
                    width, height = image.size
            except Exception as exc:
                failures.append({"url": image_url, "stage": "decode", "error": str(exc)})
                image_path.unlink(missing_ok=True)
                continue
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            local_images.append({
                "view_no": view_no,
                "image_url": image_url,
                "local_path": image_path.relative_to(ROOT).as_posix(),
                "width": width,
                "height": height,
                "sha256": digest,
            })
            image_count += 1

        records.append({
            "source_id": f"wawards-tajikistan-{CATALOG_IDS.get(slug, slug)}",
            "catalog_id": CATALOG_IDS.get(slug, "UNKNOWN"),
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
            "notes": "World Awards 2025 reference catalogue object page; classification follows the object page and PDF section.",
            "status": "harvested" if local_images else "UNPICTURED",
        })
        if index != len(urls):
            time.sleep(0.25)

    with RAW_OUT.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    report = {
        "source_id": "wawards-tajikistan-2025",
        "source_url": "https://wawards.org/images/tajikistan/tajikistan.pdf",
        "accessed": date.today().isoformat(),
        "scope": "Complete 2025 reference catalogue PDF, all linked Tajikistan object pages, and every public full-size image linked from those pages.",
        "status": "complete" if not failures and len(records) == 35 else "partial",
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
