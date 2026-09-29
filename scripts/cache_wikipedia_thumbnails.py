"""Cache every unique Wikimedia thumbnail exposed by a saved Wikipedia HTML page."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--width", type=int, default=500)
    parser.add_argument("--delay", type=float, default=0.7)
    args = parser.parse_args()
    source = ROOT / args.input
    target = ROOT / args.output
    target.mkdir(parents=True, exist_ok=True)
    body = source.read_text(encoding="utf-8", errors="replace")
    urls = []
    for raw in re.findall(r'src=["\'](//(?:thumb|upload)\.wikimedia\.org/[^"\']+)["\']', body, re.I):
        url = "https:" + html.unescape(raw)
        if "thumb.wikimedia.org" in url:
            url = re.sub(r"/\d+px-", f"/{args.width}px-", url)
        if url not in urls:
            urls.append(url)
    records = []
    for index, url in enumerate(urls, 1):
        raw_name = unquote(Path(urlparse(url).path).name)
        suffix = Path(raw_name).suffix.lower() or ".jpg"
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            suffix = ".png"
        destination = target / f"{index:03d}_{hashlib.sha1(url.encode()).hexdigest()[:10]}{suffix}"
        status = "cached"
        error = None
        if not destination.exists():
            process = subprocess.run([
                "curl.exe", "-L", "--fail", "--connect-timeout", "8", "--max-time", "15",
                "--retry", "0", "-A", "world-medals research cache/2026",
                "-o", str(destination), url,
            ], cwd=ROOT, capture_output=True, text=True)
            if process.returncode:
                destination.unlink(missing_ok=True)
                status = "failed"
                error = process.stderr[-500:]
        width = height = None
        if destination.exists():
            try:
                with Image.open(destination) as image:
                    width, height = image.size
                    image.verify()
            except Exception as exc:
                destination.unlink(missing_ok=True)
                status = "decode_failed"
                error = str(exc)
        records.append({
            "index": index, "source_url": url, "local_path": destination.relative_to(ROOT).as_posix() if destination.exists() else None,
            "width": width, "height": height, "status": status, "error": error,
        })
        if index % 20 == 0:
            (target / "cache_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(args.delay)
    (target / "cache_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"found": len(urls), "cached": sum(1 for item in records if item["status"] == "cached"), "failed": sum(1 for item in records if item["status"] != "cached")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
