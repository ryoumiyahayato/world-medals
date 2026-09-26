"""Fetch the legacy catalog's source images into a review staging area."""
import hashlib
import json
import time
import urllib.request
from urllib.parse import urlparse
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / 'data/legacy_pending.json').read_text(encoding='utf-8'))
stage = ROOT / 'sources/legacy_review'
stage.mkdir(parents=True, exist_ok=True)
report = []
last_host = None
for row in rows:
    outputs = []
    for index, url in enumerate(row['image_urls']):
        suffix = url.split('?', 1)[0].rsplit('.', 1)[-1].lower()
        suffix = suffix if suffix in ('jpg', 'jpeg', 'png', 'gif', 'webp') else 'img'
        path = stage / f"{row['legacy_key']}-{index+1}.{suffix}"
        entry = {'url': url, 'path': str(path.relative_to(ROOT)).replace('\\','/')}
        if path.exists():
            raw = path.read_bytes()
        else:
            try:
                host = urlparse(url).netloc
                if host == last_host:
                    time.sleep(1.4)
                req = urllib.request.Request(url, headers={'User-Agent':'WorldMedalsCatalog/1.0 (research; source attribution retained)'})
                with urllib.request.urlopen(req, timeout=22) as response:
                    raw = response.read(25_000_001)
                    if len(raw)>25_000_000:
                        raise ValueError('image exceeds 25 MB review limit')
                with Image.open(BytesIO(raw)) as picture:
                    picture.verify()
                path.write_bytes(raw)
                last_host = host
            except Exception as exc:
                entry['error'] = f'{type(exc).__name__}: {exc}'
                outputs.append(entry)
                print(row['legacy_key'], index+1, 'FAIL', entry['error'], flush=True)
                continue
        with Image.open(BytesIO(raw)) as picture:
            entry.update(width=picture.width, height=picture.height, format=picture.format,
                         sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        outputs.append(entry)
        print(row['legacy_key'], index+1, entry['width'], entry['height'], flush=True)
    report.append({'legacy_key':row['legacy_key'], 'images':outputs})
    (stage/'download_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
