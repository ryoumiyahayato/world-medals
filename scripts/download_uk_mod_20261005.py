"""Obtain the guide's original files once; decoding is not visual acceptance."""
from pathlib import Path
import json, hashlib, time
from urllib.parse import urlparse
import requests
from PIL import Image
R=Path(__file__).resolve().parents[1]
rows=[json.loads(l) for l in (R/'data/raw_candidates/uk_mod_guide_20261005.jsonl').read_text(encoding='utf-8').splitlines()]
known={}
for manifest in (R/'data/volumes').glob('*manifest*.json'):
    obj=json.loads(manifest.read_text(encoding='utf-8'))
    if isinstance(obj,dict):
        for image in obj.get('images',obj.get('items',[])):
            url=image.get('image_url') or image.get('source_url');path=image.get('local_path')
            if url and path and (R/path).is_file():known[url]=path
images={im['image_url']:im for row in rows for im in row['images']}
dest=R/'assets/raw/uk_mod_20261005';dest.mkdir(parents=True,exist_ok=True)
report=R/'data/source_sweeps/uk_mod_guide_20261005_images.json'
records=json.loads(report.read_text(encoding='utf-8'))['images'] if report.exists() else []
done={x['image_url']:x for x in records}
session=requests.Session();session.headers['User-Agent']='World-medals public source research/1.0'
for url,im in images.items():
    if url in done:continue
    record=dict(image_url=url,caption=im['caption'],source_page='https://www.gov.uk/guidance/medals-campaigns-descriptions-and-eligibility',accessed='2026-10-05')
    try:
        if url in known:path=R/known[url]
        else:
            suffix=Path(urlparse(url).path).suffix or '.img'
            path=dest/(hashlib.sha256(url.encode()).hexdigest()[:20]+suffix)
            if not path.exists():
                response=session.get(url,timeout=25);response.raise_for_status();path.write_bytes(response.content);time.sleep(1)
        with Image.open(path) as picture:picture.load();size=picture.size
        record.update(local_path=path.relative_to(R).as_posix(),dimensions=size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),status='decoded_visual_and_identity_review_pending',publication_eligible=False)
    except Exception as error:record.update(status='download_failed',error_type=type(error).__name__)
    done[url]=record
    report.write_text(json.dumps(dict(images=list(done.values()),planned=len(images),decoded=sum(x['status'].startswith('decoded') for x in done.values())),ensure_ascii=False,indent=2),encoding='utf-8')
print('Image leads',len(images),'decoded',sum(x['status'].startswith('decoded') for x in done.values()))
