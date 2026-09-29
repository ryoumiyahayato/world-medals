"""Sweep the complete current Medals of the World Egypt kingdom index and linked pages."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "medals_org_egypt_kingdom"
INDEX_URL = "https://medals.org.uk/egypt/egypt-kingdom/egypt-kingdom-text1.htm"
PAGE_DIR = ROOT / "sources/pages/medals_org_egypt_kingdom"
IMAGE_DIR = ROOT / "assets/raw/medals_org_egypt_kingdom"
RAW_OUT = ROOT / "data/raw_candidates/medals_org_egypt_kingdom.jsonl"
HARVEST_OUT = ROOT / "data/image_harvest/medals_org_egypt_kingdom.json"
SWEEP_OUT = ROOT / "data/source_sweeps/medals_org_egypt_kingdom_2026-09-27.json"

USER_AGENT = "world-medals research cache/1.0 (single bounded catalogue sweep)"


def fetch(url: str) -> bytes:
    error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=30) as response:
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


def text_content(markup: str) -> str:
    cleaned = re.sub(r"<(script|style)\b.*?</\1>", " ", markup, flags=re.I | re.S)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"</(?:p|h\d|li|tr)>", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    return "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())


def first_tag(markup: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", markup, flags=re.I | re.S)
    return text_content(match.group(1)) if match else ""


def attrs(fragment: str) -> dict[str, str]:
    return {
        key.lower(): html.unescape(value)
        for key, _, value in re.findall(r"([:\w-]+)\s*=\s*(['\"])(.*?)\2", fragment, flags=re.S)
    }


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    HARVEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_OUT.parent.mkdir(parents=True, exist_ok=True)

    index_path = PAGE_DIR / "egypt-kingdom-text1.htm"
    index_bytes = cached_fetch(INDEX_URL, index_path)
    index_html = index_bytes.decode("latin-1")

    discovered: list[tuple[str, str]] = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", index_html, flags=re.I | re.S):
        attributes = attrs(match.group(1))
        href = attributes.get("href", "")
        if re.fullmatch(r"egypt-kingdom\d{3}\.htm", href):
            discovered.append((href, text_content(match.group(2))))
    if len(discovered) != 24:
        raise RuntimeError(f"expected 24 linked object pages, found {len(discovered)}")

    unlinked = [
        text_content(value)
        for value in re.findall(r"<li>(?!\s*<a\b)(.*?)</li>", index_html, flags=re.I | re.S)
        if text_content(value)
    ]

    candidates: list[dict] = []
    images: list[dict] = []
    ribbons: list[dict] = []
    failures: list[dict] = []

    for position, (href, index_name) in enumerate(discovered, start=1):
        page_url = urllib.parse.urljoin(INDEX_URL, href)
        try:
            page_bytes = cached_fetch(page_url, PAGE_DIR / href)
        except RuntimeError as exc:
            failures.append({"url": page_url, "error": str(exc)})
            continue
        page_html = page_bytes.decode("latin-1")
        title = first_tag(page_html, "title")
        heading = first_tag(page_html, "h2") or index_name
        summary_lines = [
            line
            for line in text_content(page_html).splitlines()
            if line.startswith(("Ribbon:", "Instituted:", "Discontinued:", "Awarded:"))
        ]
        image_records = []
        for image_match in re.finditer(r"<img\b([^>]*)>", page_html, flags=re.I | re.S):
            attributes = attrs(image_match.group(1))
            src = attributes.get("src", "")
            alt = attributes.get("alt", "").strip()
            if not src or (not alt and src.lower().endswith(("r.gif", "r.jpg", "r.png"))):
                continue
            image_url = urllib.parse.urljoin(page_url, src)
            filename = f"{Path(href).stem}_{Path(urllib.parse.urlparse(src).path).name}"
            local = IMAGE_DIR / filename
            try:
                payload = cached_fetch(image_url, local)
                with Image.open(local) as opened:
                    dimensions = list(opened.size)
                    opened.verify()
                digest = hashlib.sha256(payload).hexdigest()
                record = {
                    "page": href,
                    "label": alt or "object image",
                    "image_url": image_url,
                    "local_path": local.relative_to(ROOT).as_posix(),
                    "dimensions": dimensions,
                    "bytes": len(payload),
                    "sha256": digest,
                    "decoded": True,
                }
                if not alt:
                    record["classification"] = "ribbon_or_unlabelled_site_graphic"
                    ribbons.append(record)
                else:
                    record["classification"] = "object_image"
                    image_records.append(record)
                    images.append(record)
            except Exception as exc:  # keep the sweep moving and report exact failures
                failures.append({"url": image_url, "page": page_url, "error": str(exc)})
        candidates.append(
            {
                "source_id": SOURCE_ID,
                "source_position": position,
                "page_title": title,
                "working_name_zh": "待归并",
                "original_name": heading.removeprefix("Kingdom of Egypt: "),
                "english_name": index_name,
                "date_candidates": re.findall(r"\b(?:18|19|20)\d{2}\b", " ".join([heading, *summary_lines])),
                "category": "order, decoration or medal",
                "grade_or_material_clues": [],
                "object_page_url": page_url,
                "image_page_url": page_url,
                "original_image_urls": [record["image_url"] for record in image_records],
                "local_images": [record["local_path"] for record in image_records],
                "image_labels": [record["label"] for record in image_records],
                "notes": " ".join(summary_lines),
                "status": "SOURCE_SWEEP_CANDIDATE" if image_records else "SOURCE_RECORD_NO_OBJECT_IMAGE",
                "accessed": "2026-09-27",
            }
        )
        time.sleep(0.15)

    RAW_OUT.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in candidates) + "\n",
        encoding="utf-8",
    )
    HARVEST_OUT.write_text(
        json.dumps(
            {
                "as_of": "2026-09-27",
                "source_id": SOURCE_ID,
                "images": images,
                "ribbon_or_unlabelled_graphics": ribbons,
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    SWEEP_OUT.write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "source_id": SOURCE_ID,
                "scope_id": "egypt",
                "as_of": "2026-09-27",
                "status": "completed" if not failures else "completed_with_failures",
                "index_url": INDEX_URL,
                "linked_object_pages_discovered": len(discovered),
                "linked_object_pages_processed": len(candidates),
                "unlinked_index_entries": unlinked,
                "object_images_downloaded": len(images),
                "ribbon_or_unlabelled_graphics_cached": len(ribbons),
                "failed_urls": failures,
                "candidate_file": RAW_OUT.relative_to(ROOT).as_posix(),
                "image_harvest_file": HARVEST_OUT.relative_to(ROOT).as_posix(),
                "page_cache": PAGE_DIR.relative_to(ROOT).as_posix(),
                "image_cache": IMAGE_DIR.relative_to(ROOT).as_posix(),
                "completion_boundary": "The current kingdom text index and every linked award page were processed. The unlinked Cholera Epidemic Medal label was recorded separately.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "pages": len(candidates),
                "images": len(images),
                "ribbons_or_unlabelled": len(ribbons),
                "unlinked": unlinked,
                "failures": len(failures),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
