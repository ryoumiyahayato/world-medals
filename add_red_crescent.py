"""One-time Ottoman Red Crescent bronze medal intake with paired source views."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
catpath = root / 'data/catalogue.json'
cat = json.loads(catpath.read_text(encoding='utf-8'))
if any(r['id'] == 'OTT-RED-CRESCENT-BRONZE-01' for r in cat['records']):
    raise SystemExit('Red Crescent medal already recorded')
page = 'https://www.emedals.com/products/turkey-ottoman-empire-a-red-crescent-medal-iii-class-bronze-grade-c1918-eu20367'
statutes_page = 'https://www.kuenker.de/tuerkei/680973'
urls = [
    'https://www.emedals.com/cdn/shop/files/l22_mnc6762_249.jpg?v=1692906551&width=1946',
    'https://www.emedals.com/cdn/shop/files/l22_mnc6764_250.jpg?v=1692906562&width=1946',
]
manifest_path = root / 'image_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
sources_path = root / 'data/sources.json'
sources = json.loads(sources_path.read_text(encoding='utf-8'))
views = []
for i, url in enumerate(urls, 2):
    key = f'RED-CRESCENT-{i}'
    src = root / f'sources/legacy_review/{key}.jpg'
    with Image.open(src) as image:
        image.verify()
    with Image.open(src) as image:
        width, height = image.size
    archive = root / f'originals/ottoman_2026-09-25/{key}.jpg'
    asset = root / f'assets/images/ottoman/{key}.jpg'
    archive.parent.mkdir(parents=True, exist_ok=True)
    asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, archive)
    shutil.copy2(src, asset)
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    label = '正面' if i == 2 else '背面'
    manifest.append({
        'key': key, 'path': str(archive.relative_to(root)).replace('\\', '/'),
        'source_page': page, 'image_url': url,
        'description': f'eMedals EU20367 {label}; same specimen, full ribbon and medal',
        'license': 'eMedals copyright; local research only', 'artist': 'eMedals',
        'sha256': digest, 'width': width, 'height': height, 'accessed': '2026-09-25',
    })
    sources['image-' + key] = {
        'page': page, 'image_url': url, 'summary': f'EU20367 {label}; same specimen',
        'sha256': digest, 'dimensions': [width, height],
        'license': 'eMedals copyright; local research only', 'accessed': '2026-09-25',
    }
    views.append({'key': key, 'label': label})
sources['emedals-red-crescent'] = {
    'page': page, 'object_id': 'EU20367', 'accessed': '2026-09-25',
    'summary': 'Third class bronze Ottoman Red Crescent Medal, 28.7 x 61 mm including suspension; original ribbon and case; same specimen photographed front and back. Source estimates circa 1918 production.',
}
sources['kuenker-red-crescent-statutes'] = {
    'page': statutes_page, 'object_id': 'eLive Auction 75, lot 486', 'accessed': '2026-09-25',
    'summary': 'Künker cites statutes of 4 Zilkade AH 1330 for a three-grade gold, silver, bronze Red Crescent medal; oak leaves for war merit. Established under Sultan Mehmed V in 1912. Künker lot is a distinct bronze specimen, not the pictured eMedals object.',
}
cat['records'].append({
    'id': 'OTT-RED-CRESCENT-BRONZE-01', 'family': 'OTT-RED-CRESCENT',
    'name': '红新月会功绩奖章',
    'original': 'Hilâl-i Ahmer Madalyası / Red Crescent Medal',
    'date': '1912',
    'variant': '三级；铜质；原绶带及悬挂件；实物约1918年；正背同件',
    'views': views,
    'source_ids': ['kuenker-red-crescent-statutes', 'emedals-red-crescent'] + ['image-' + v['key'] for v in views],
})
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding='utf-8')
catpath.write_text(json.dumps(cat, ensure_ascii=False, indent=2), encoding='utf-8')
print('Red Crescent Medal added')
