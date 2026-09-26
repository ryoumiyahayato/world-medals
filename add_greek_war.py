"""One-time, idempotent intake of the photographed Ottoman 1897 Greek War Medal."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
catpath = root / 'data/catalogue.json'
cat = json.loads(catpath.read_text(encoding='utf-8'))
if any(r['id'] == 'OTT-GREEK-WAR-SILVER-01' for r in cat['records']):
    raise SystemExit('Greek War Medal already recorded')

page = 'https://www.emedals.com/products/turkey-ottoman-empire-a-medal-for-ottoman-greek-war-of-1897-eu14917rl2'
urls = [
    'https://www.emedals.com/cdn/shop/files/c18-016215_1_1.jpg?v=1692893854&width=1445',
    'https://www.emedals.com/cdn/shop/files/c18-016217_1_1.jpg?v=1692893836&width=1445',
]
manifest_path = root / 'image_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
sources_path = root / 'data/sources.json'
sources = json.loads(sources_path.read_text(encoding='utf-8'))
views = []
for i, url in enumerate(urls, 1):
    key = f'GREEK-{i}'
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
    label = '正面' if i == 1 else '斜视背面'
    manifest.append({
        'key': key, 'path': str(archive.relative_to(root)).replace('\\', '/'),
        'source_page': page, 'image_url': url,
        'description': f'eMedals EU14917 {label}; complete medal, ribbon missing',
        'license': 'eMedals copyright; local research only', 'artist': 'eMedals',
        'sha256': digest, 'width': width, 'height': height, 'accessed': '2026-09-25',
    })
    sources['image-' + key] = {
        'page': page, 'image_url': url, 'summary': f'EU14917 {label}; complete medal, ribbon missing',
        'sha256': digest, 'dimensions': [width, height],
        'license': 'eMedals copyright; local research only', 'accessed': '2026-09-25',
    }
    views.append({'key': key, 'label': label})
sources['emedals-greek-war'] = {
    'page': page, 'object_id': 'EU14917', 'accessed': '2026-09-25',
    'summary': 'Ottoman Greek War Medal dated AH 1314 / 1897; silver, 24.5 mm. Complete medal and suspension bar photographed front and oblique reverse; ribbon absent.',
}
cat['records'].append({
    'id': 'OTT-GREEK-WAR-SILVER-01', 'family': 'OTT-GREEK-WAR',
    'name': '希腊战争奖章', 'original': 'Yunan Muharebesi Madalyası / Ottoman Greek War Medal',
    'date': '1897', 'variant': '银质；24.5毫米；章体和悬挂件完整；本件绶带缺失；正背同件',
    'views': views, 'source_ids': ['tdv-madalya', 'emedals-greek-war'] + ['image-' + x['key'] for x in views],
})
unpath = root / 'data/unpictured.json'
unpictured = json.loads(unpath.read_text(encoding='utf-8'))
unpictured = [x for x in unpictured if x['family'] != 'OTT-GREEK-WAR']
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding='utf-8')
catpath.write_text(json.dumps(cat, ensure_ascii=False, indent=2), encoding='utf-8')
unpath.write_text(json.dumps(unpictured, ensure_ascii=False, indent=2), encoding='utf-8')
print('Greek War Medal added')
