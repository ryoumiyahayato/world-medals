"""Adapt the existing, reviewed offline HTML; never reinterpret historical facts."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import hashlib, json, shutil
import display_images

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'mobile/build/site'

def export():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'mobile/web', OUT, dirs_exist_ok=True)
    (OUT / 'images').mkdir(exist_ok=True)
    source = (ROOT / 'index.html').read_bytes()
    soup = BeautifulSoup(source.decode('utf-8'), 'html.parser')
    sources = json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8'))
    image_records = {}
    def collect_images(value, inherited=None):
        if isinstance(value,list):
            for item in value: collect_images(item,inherited)
        elif isinstance(value,dict):
            rights = dict(inherited or {})
            for k in ('license','rights','copyright','institution','artist','credit'):
                if isinstance(value.get(k),str): rights[k]=value[k]
            for k in ('local_path','path','file','local_file','original_path'):
                if isinstance(value.get(k),str):
                    p=value[k].replace('\\','/')
                    if p.startswith('assets/') or p.startswith('originals/'):
                        image_records[p]=dict(rights,**value)
            for item in value.values():
                if isinstance(item,(dict,list)): collect_images(item,rights)
    for manifest in [ROOT/'image_manifest.json', *sorted((ROOT/'data/volumes').glob('*manifest*.json'))]:
        collect_images(json.loads(manifest.read_text(encoding='utf-8-sig')))
    overrides=display_images.load(ROOT)
    rows, volumes, images = [], [], {}
    family_titles = {b.get('data-family-toggle'): txt for b in soup.select('button[data-family-toggle]') if (txt := b.select_one('.family-name')) is not None}
    def txt(node, selector):
        x = node.select_one(selector)
        return x.get_text(' ', strip=True) if x else ''
    for section in soup.select('section.period-section'):
        title = txt(section, 'h2')
        volume = section.get('id')
        count = 0
        for tr in section.select('tr[id]'):
            cells = tr.find_all('td', recursive=False)
            if len(cells) != 3:
                continue
            photos = []
            for im in cells[2].select('img[src]'):
                rel = im['src']
                path = (ROOT / rel).resolve()
                if not path.is_relative_to(ROOT) or not path.is_file():
                    raise ValueError(f'Missing or invalid image: {rel}')
                if rel not in images:
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    dest = 'images/' + digest[:24] + '.webp'
                    with Image.open(path) as original:
                        original.load()
                        dimensions = original.size
                        if not (OUT / dest).exists():
                            preview = ImageOps.exif_transpose(original).convert('RGB')
                            preview.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                            preview.save(OUT / dest, 'WEBP', quality=84)
                    images[rel] = dict(src=dest, original=rel, sha256=digest, originalSize=dimensions, provenance=image_records.get(rel,{}))
                    replacement=display_images.prepare(ROOT,OUT,rel,digest,overrides.get(rel))
                    if replacement: images[rel]['display']=replacement
                fig = im.find_parent('figure')
                record=images[rel]['provenance']
                photos.append(dict(src=images[rel].get('display',{}).get('src',images[rel]['src']), alt=im.get('alt', ''), caption=txt(fig, 'figcaption') if fig else '', source=record.get('source_page',record.get('page_url','')), rights=record.get('license',record.get('rights','')), credit=record.get('artist',record.get('institution',''))))
                if images[rel].get('display'):
                    photos[-1]['originalSrc']=images[rel]['src']
                    photos[-1]['processing']=images[rel]['display']['processing']
                    photos[-1]['caption']=(photos[-1]['caption']+' · '+photos[-1]['processing']).strip(' ·')
            refs = [sources[k] for k in tr.get('data-source-ids', '').split() if k in sources]
            family_key = tr.get('data-family-key', tr['id'])
            family_name = family_titles[family_key].get_text(' ', strip=True) if family_key in family_titles else txt(cells[0], 'strong')
            # The Legion of Honour's successive regimes remain one order in the UI.
            if tr['id'].startswith('FRA-LEGION-'):
                family_key, family_name = 'france-legion-of-honour', '荣誉军团勋章'
            rows.append(dict(id=tr['id'], volume=volume, family=family_key, familyName=family_name, name=txt(cells[0], 'strong') or cells[0].get_text(' ',strip=True),
                original=txt(cells[0], '.original'), date=txt(cells[0], '.date'), variant=cells[1].get_text(' ',strip=True),
                photos=photos, sources=refs, note=tr.get('title','')))
            count += 1
        for i, li in enumerate(section.select('ul.noimage > li')):
            rows.append(dict(id=f'{volume}-unpictured-{i}', volume=volume, name=li.get_text(' ',strip=True), original='', date='', variant='有记载未配图', photos=[], sources=[], note=''))
            count += 1
        if count:
            volumes.append(dict(id=volume, title=title, count=count))
    assert rows and images
    app_version=json.loads((ROOT/'mobile/version.json').read_text(encoding='utf-8'))
    (OUT/'version.js').write_text('window.APP_VERSION='+json.dumps(app_version)+';',encoding='utf-8')
    data = dict(schema=1, version=hashlib.sha256(source).hexdigest()[:12], appVersion=app_version, volumes=volumes, rows=rows,
                imageCount=len(images), imagePolicy='手机端等比预览，最长边不超过1200像素；来源原图保留在研究库。')
    (OUT / 'catalog.js').write_text('window.CATALOG=' + json.dumps(data, ensure_ascii=False).replace('</','<\\/') + ';', encoding='utf-8')
    (ROOT / 'mobile/build/image-provenance.json').write_text(json.dumps(images, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copyfile(ROOT / 'mobile/build/image-provenance.json', OUT/'image-provenance.json')
    # Preserve the existing source and rights records alongside the derived app data.
    shutil.copyfile(ROOT / 'data/sources.json', OUT / 'sources.json')
    report = dict(rows=len(rows), volumes=len(volumes), uniqueImages=len(images), catalogueVersion=data['version'], imageBytes=sum(p.stat().st_size for p in (OUT/'images').glob('*.webp')))
    (ROOT / 'mobile/build/export-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__':
    export()
