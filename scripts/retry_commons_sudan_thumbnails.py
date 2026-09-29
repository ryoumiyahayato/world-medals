"""Respectfully retry the selected Sudan Commons object images via thumbnails."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/image_harvest/commons_sudan_full_body_retry.json"
DEST = ROOT / "assets/raw/commons_sudan"
UA = "world-medals-research/1.0 (offline catalogue; respectful thumbnail retry)"


def save_queue(data: dict) -> None:
    QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    data = json.loads(QUEUE.read_text(encoding="utf-8"))
    pending = data["pending"]
    successes = 0
    consecutive_failures = 0
    DEST.mkdir(parents=True, exist_ok=True)
    for item in pending:
        if item.get("status") == "DOWNLOADED" and item.get("local_path"):
            path = ROOT / item["local_path"]
            if path.exists():
                continue
        suffix = Path(item["page_title"]).suffix.lower() or ".img"
        if suffix == ".gif":
            suffix = ".png"
        filename = hashlib.sha256(item["file_title"].encode("utf-8")).hexdigest()[:16] + suffix
        path = DEST / filename
        try:
            req = urllib.request.Request(item["thumbnail_retry_url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as response:
                path.write_bytes(response.read())
            with Image.open(path) as image:
                image.verify()
            item["status"] = "DOWNLOADED"
            item["local_path"] = path.relative_to(ROOT).as_posix()
            item.pop("last_error", None)
            successes += 1
            consecutive_failures = 0
        except Exception as exc:
            path.unlink(missing_ok=True)
            item["status"] = "RETRY_FAILED"
            item["last_error"] = str(exc)
            consecutive_failures += 1
            save_queue(data)
            if consecutive_failures >= 3:
                print(f"stopped after 3 consecutive failures; downloaded {successes} this run")
                return
        save_queue(data)
        # Commons explicitly rate-limits this source; keep requests well below
        # one per second and preserve every successful item before continuing.
        time.sleep(8.0)
    print(f"retry pass complete; downloaded {successes} this run; total {sum(x.get('status') == 'DOWNLOADED' for x in pending)}")


if __name__ == "__main__":
    main()
