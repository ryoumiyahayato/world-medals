"""Read-only source -> conservative alpha trim -> two WebP display sizes."""
import io, json, os
from pathlib import Path
from PIL import Image, ImageOps, ImageChops

def material_root(default):
    return Path(os.environ.get('WORLD_MEDALS_MATERIAL_ROOT', default)).resolve()

def prepare(path, out, relative, reference=False, background=None, source_bytes=None):
    image_source = io.BytesIO(source_bytes) if source_bytes is not None else path
    with Image.open(image_source) as source:
        source.load()
        frame = ImageOps.exif_transpose(source).convert('RGBA')
    size = frame.size
    applied_background = False
    if background and background.get('approved') is True and not reference:
        source_length = len(source_bytes) if source_bytes is not None else path.stat().st_size
        if list(size) != background['sourceSize'] or source_length != background['sourceBytes']:
            raise ValueError('Reviewed source changed: '+relative)
        from background_trim import apply_rule
        frame = apply_rule(frame, background)
        applied_background = True
    alpha = frame.getchannel('A')
    transparent = alpha.getextrema()[0] < 255
    bounds = alpha.getbbox() if transparent else (0, 0, *size)
    if bounds is None:
        raise ValueError('Empty image: ' + relative)
    # Every nonzero alpha pixel survives. No component removal, rotation,
    # recolouring or inferred background segmentation is performed.
    crop = (0, 0, *size) if reference else bounds
    white_margin = False
    if not transparent and not reference:
        rgb = frame.convert('RGB')
        if all(rgb.getpixel(point)==(255,255,255) for point in ((0,0),(rgb.width-1,0),(0,rgb.height-1),(rgb.width-1,rgb.height-1))):
            exact_nonwhite = ImageChops.difference(rgb, Image.new('RGB',rgb.size,'white')).getbbox()
            if exact_nonwhite:
                crop = exact_nonwhite
                white_margin = crop != (0,0,*size)
    frame = frame.crop(crop)
    margin = max(1, round(max(frame.size) * .035)) if transparent or white_margin else 0
    if margin:
        canvas = Image.new('RGBA', (frame.width+2*margin, frame.height+2*margin), (0,0,0,0) if transparent else (255,255,255,255))
        canvas.paste(frame, (margin, margin))
        frame = canvas
    result = {'sourceSize': size, 'crop': crop, 'margin': margin,
              'referenceReused': reference,
              'status': 'reference-reused' if reference else 'crop-reviewed' if applied_background and background.get('kind')=='crop-only' else 'background-removed-reviewed' if applied_background else 'alpha-trimmed' if transparent else 'opaque-margin-trimmed' if white_margin else 'opaque-background-review'}
    for label, limit, quality in [('thumb', 384, 86), ('detail', 1200, 90)]:
        image = frame.copy()
        image.thumbnail((limit, limit), Image.Resampling.LANCZOS)
        if not transparent:
            image = image.convert('RGB')
        dest = Path('images') / label / (relative + '.webp')
        target = out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, 'WEBP', quality=quality, method=4, exact=True)
        with Image.open(target) as check:
            check.load()
            if check.size != image.size:
                raise ValueError('Display dimensions changed')
        result[label] = dest.as_posix()
        result[label+'Size'] = image.size
    return result

def public_metadata(value):
    """Keep provenance while omitting workstation paths and image digests."""
    if isinstance(value, dict):
        return {k: public_metadata(v) for k, v in value.items()
                if k not in ('sha256', 'md5', 'provenance_source_file')
                and not (isinstance(v, str) and (len(v)>2 and v[1:3] in (':\\', ':/')))}
    if isinstance(value, list):
        return [public_metadata(v) for v in value]
    return value
