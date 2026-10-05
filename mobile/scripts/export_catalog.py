"""Adapt the existing, reviewed offline HTML; never reinterpret historical facts."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import hashlib, json, shutil, re
import display_images

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'mobile/build/site'

def stamp_web_assets():
    page = OUT / 'index.html'
    def stamp(match):
        attribute, name = match.groups()
        digest = hashlib.sha256((OUT / name).read_bytes()).hexdigest()[:12]
        return f'{attribute}="{name}?v={digest}"'
    page.write_text(re.sub(r'(src|href)="([^"?]+\.(?:js|css))(?:\?[^" ]*)?"', stamp, page.read_text(encoding='utf-8')), encoding='utf-8')

def export():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'mobile/web', OUT, dirs_exist_ok=True)
    introductions = json.loads((ROOT/'mobile/web/award-intros.json').read_text(encoding='utf-8'))
    entries = []
    for item in introductions['items']:
        entries.append(dict(names=item['match_names'], families=item.get('family_ids',[item['award_id']]), volumePattern=item.get('volume_pattern') or ('soviet|ussr' if item['award_id'].startswith('USSR-') else '^france-'),
            paragraphs=item['introduction_zh'], sources=item['sources'],
            variants=[dict(title=v['period'],text=v['form'],referenceRecord=v.get('reference_record_id')) for v in item.get('variant_guidance',{}).get('period_forms',[])]))
    (OUT/'award-intros.js').write_text('window.AWARD_INTROS='+json.dumps(entries,ensure_ascii=False).replace('</','<\\/')+';',encoding='utf-8')
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
            if tr.get('data-publication-eligible') == 'false':
                continue
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
                        has_alpha = original.mode in ('RGBA', 'LA') or 'transparency' in original.info
                        rebuild = not (OUT / dest).exists()
                        if has_alpha and not rebuild:
                            with Image.open(OUT / dest) as prior:
                                rebuild = prior.mode not in ('RGBA', 'LA')
                        if rebuild:
                            preview = ImageOps.exif_transpose(original).convert('RGBA' if has_alpha else 'RGB')
                            preview.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                            preview.save(OUT / dest, 'WEBP', quality=84)
                    images[rel] = dict(src=dest, original=rel, sha256=digest, originalSize=dimensions, provenance=image_records.get(rel,{}))
                    replacement=display_images.prepare(ROOT,OUT,rel,digest,overrides.get(rel))
                    if replacement: images[rel]['display']=replacement
                fig = im.find_parent('figure')
                record=images[rel]['provenance']
                photos.append(dict(src=images[rel].get('display',{}).get('src',images[rel]['src']), alt=im.get('alt', ''), caption=txt(fig, 'figcaption') if fig else '', source=record.get('source_page',record.get('page_url','')), rights=record.get('license',record.get('rights','')), credit=record.get('artist',record.get('institution',''))))
                if record.get('image_kind')=='user_restored_reference':photos[-1]['reference']=True
                if images[rel].get('display'):
                    photos[-1]['originalSrc']=images[rel]['src']
                    photos[-1]['processing']=images[rel]['display']['processing']
                    photos[-1]['caption']=(photos[-1]['caption']+' · '+photos[-1]['processing']).strip(' ·')
            # The UI uses short reference captions; detailed provenance stays in manifests.
            for photo in photos:
                photo['caption']=photo['caption'].replace('用户修复参考图','参考').replace('用户修复参考图（非来源摄影原图）','参考')
            # The HTML builder separates source IDs with commas, not spaces.
            refs = [sources[k.strip()] for k in tr.get('data-source-ids', '').split(',') if k.strip() in sources]
            heading_key = tr.get('data-family-key', tr['id'])
            family_key = tr.get('data-award-family') or heading_key
            family_name = family_titles[heading_key].get_text(' ', strip=True) if heading_key in family_titles else txt(cells[0], 'strong')
            # The Legion of Honour's successive regimes remain one order in the UI.
            if tr['id'].startswith('FRA-LEGION-'):
                family_key, family_name = 'france-legion-of-honour', '荣誉军团勋章'
            rows.append(dict(id=tr['id'], volume=volume, family=family_key, familyName=family_name, name=txt(cells[0], 'strong') or cells[0].get_text(' ',strip=True),
                original=txt(cells[0], '.original'), date=txt(cells[0], '.date'), variant=cells[1].get_text(' ',strip=True).replace('用户修复参考图','参考'),
                photos=photos, sources=refs, note=tr.get('title','')))
            count += 1
        for i, li in enumerate(section.select('ul.noimage > li')):
            name=li.get('data-name') or li.get_text(' ',strip=True)
            refs=[sources[k] for k in li.get('data-source-ids','').split(',') if k in sources]
            rows.append(dict(id=li.get('data-id') or f'{volume}-unpictured-{i}', volume=volume, family=li.get('data-family') or f'{volume}-unpictured-{i}', familyName=name, name=name, original=li.get('data-original',''), date=li.get('data-date',''), variant=li.get('data-variant') or '有记载未配图', photos=[], sources=refs, note=''))
            count += 1
        if count:
            volumes.append(dict(id=volume, title=title, count=count))
    assert rows and images
    policy_path=ROOT/'data/display_images/row_replacements.json'
    policy=json.loads(policy_path.read_text(encoding='utf-8')) if policy_path.exists() else {'rows':{}}
    by_id={r['id']:r for r in rows}
    replacements={}
    for source_id,entry in policy['rows'].items():
        if entry.get('approved') is not True:continue
        reference=entry['reference_record']
        if source_id not in by_id or reference not in by_id:continue
        if by_id[source_id]['family']!=by_id[reference]['family'] or not any(p.get('reference') for p in by_id[reference]['photos']):
            raise ValueError('Unmatched reference replacement: '+source_id)
        replacements[source_id]=reference
    (OUT/'reference-policy.js').write_text('window.REFERENCE_ROW_REPLACEMENTS='+json.dumps(replacements)+';',encoding='utf-8')
    app_version=json.loads((ROOT/'mobile/version.json').read_text(encoding='utf-8'))
    (OUT/'version.js').write_text('window.APP_VERSION='+json.dumps(app_version)+';',encoding='utf-8')
    data = dict(schema=1, version=hashlib.sha256(source).hexdigest()[:12], appVersion=app_version, volumes=volumes, rows=rows,
                imageCount=len(images), imagePolicy='手机端等比预览，最长边不超过1200像素；来源原图保留在研究库。')
    (OUT / 'catalog.js').write_text('window.CATALOG=' + json.dumps(data, ensure_ascii=False).replace('</','<\\/') + ';', encoding='utf-8')
    (ROOT / 'mobile/build/image-provenance.json').write_text(json.dumps(images, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copyfile(ROOT / 'mobile/build/image-provenance.json', OUT/'image-provenance.json')
    # Preserve the existing source and rights records alongside the derived app data.
    shutil.copyfile(ROOT / 'data/sources.json', OUT / 'sources.json')
    # Remove obsolete derived previews; source originals remain untouched.
    allowed_images = {item['src'] for item in images.values()}
    allowed_images.update(item['display']['src'] for item in images.values() if item.get('display'))
    image_root = (OUT / 'images').resolve()
    for preview in image_root.rglob('*'):
        if preview.is_file() and preview.relative_to(OUT).as_posix() not in allowed_images:
            if not preview.resolve().is_relative_to(image_root):
                raise ValueError('Preview outside export directory')
            preview.unlink()
    report = dict(rows=len(rows), volumes=len(volumes), uniqueImages=len(images), catalogueVersion=data['version'], imageBytes=sum(p.stat().st_size for p in (OUT/'images').glob('*.webp')))
    (ROOT / 'mobile/build/export-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    stamp_web_assets()
    print(json.dumps(report))

if __name__ == '__main__':
    export()
