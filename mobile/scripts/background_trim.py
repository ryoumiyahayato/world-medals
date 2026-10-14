"""Reviewed deterministic matte removal. No image synthesis or recolouring."""
import json,re
from PIL import Image, ImageChops, ImageDraw, ImageOps

def remove_edge_dark(frame, maximum=8, chroma=6, keep_polygons=None):
    """Remove only reviewed exterior-connected near-black pixels."""
    inverted = ImageOps.invert(frame.convert('RGB')).convert('RGBA')
    inverted.putalpha(frame.convert('RGBA').getchannel('A'))
    matte = remove_edge_light(inverted, 255-maximum, chroma, keep_polygons)
    result = frame.convert('RGBA')
    result.putalpha(matte.getchannel('A'))
    return result

def apply_rule(frame, rule):
    if rule.get('kind') == 'crop-only':
        x0,y0,x1,y1 = rule['crop']
        if not all(type(v) is int for v in (x0,y0,x1,y1)) or not 0 <= x0 < x1 <= frame.width or not 0 <= y0 < y1 <= frame.height:
            raise ValueError('Reviewed crop is outside source')
        mask=Image.new('L',frame.size,0)
        ImageDraw.Draw(mask).rectangle((x0,y0,x1-1,y1-1),fill=255)
        result=frame.convert('RGBA')
        result.putalpha(ImageChops.multiply(result.getchannel('A'),mask))
        return result
    if rule.get('kind') == 'reviewed-runs':
        rows = rule['retainedRuns']
        if len(rows) != frame.height:
            raise ValueError('Reviewed mask height does not match source')
        mask = Image.new('L', frame.size, 0)
        draw = ImageDraw.Draw(mask)
        for y, runs in enumerate(rows):
            previous = 0
            for run in runs:
                if len(run) not in (2,3):
                    raise ValueError('Invalid reviewed mask run length')
                start, end = run[:2]
                opacity = run[2] if len(run)==3 else 255
                if not isinstance(start, int) or not isinstance(end, int) or not 0 <= previous <= start < end <= frame.width:
                    raise ValueError('Invalid reviewed mask run')
                if not isinstance(opacity,int) or not 1 <= opacity <= 255:
                    raise ValueError('Invalid reviewed mask opacity')
                draw.line((start, y, end-1, y), fill=opacity)
                previous = end
        result = frame.convert('RGBA')
        result.putalpha(ImageChops.multiply(result.getchannel('A'), mask))
        if not result.getchannel('A').getbbox():
            raise ValueError('Reviewed mask is empty')
        return result
    if rule.get('kind') == 'edge-connected-dark':
        return remove_edge_dark(frame, rule['maximum'], rule['chroma'], rule.get('keepPolygons'))
    return remove_edge_light(frame, rule['minimum'], rule['chroma'], rule.get('keepPolygons'))

def load_rules(root):
    path=root/'data/display_images/background_rules.json'
    return json.loads(path.read_text(encoding='utf-8'))['images'] if path.exists() else {}

def save_rules(root, document):
    """Keep reviewed alpha coordinates compact while retaining readable rules."""
    text=json.dumps(document,ensure_ascii=False,indent=2)
    decoder=json.JSONDecoder()
    for match in reversed(list(re.finditer(r'"retainedRuns":\s*',text))):
        value,end=decoder.raw_decode(text,match.end())
        text=text[:match.end()]+json.dumps(value,separators=(',',':'))+text[end:]
    (root/'data/display_images/background_rules.json').write_text(text+'\n',encoding='utf-8')

def remove_edge_light(frame, minimum=248, chroma=8, keep_polygons=None):
    rgb=frame.convert('RGB');red,green,blue=rgb.split()
    low=ImageChops.darker(ImageChops.darker(red,green),blue)
    high=ImageChops.lighter(ImageChops.lighter(red,green),blue)
    bright=low.point(lambda value:255 if value>=minimum else 0)
    neutral=ImageChops.subtract(high,low).point(lambda value:255 if value<=chroma else 0)
    candidate=ImageChops.multiply(bright,neutral)
    # Only regions connected to the exterior are removed. Enclosed pale enamel,
    # inscriptions and hardware interiors remain unchanged.
    for x in range(frame.width):
        for y in (0,frame.height-1):
            if candidate.getpixel((x,y))==255:ImageDraw.floodfill(candidate,(x,y),128)
    for y in range(frame.height):
        for x in (0,frame.width-1):
            if candidate.getpixel((x,y))==255:ImageDraw.floodfill(candidate,(x,y),128)
    mask=candidate.point(lambda value:0 if value==128 else 255)
    # Reviewed coordinates protect pale real parts connected to the exterior.
    # A small source-background halo is preferable to clipping ribbon fabric.
    if keep_polygons:
        draw=ImageDraw.Draw(mask)
        for polygon in keep_polygons:
            draw.polygon([tuple(point) for point in polygon],fill=255)
    rgba=frame.convert('RGBA')
    rgba.putalpha(ImageChops.multiply(rgba.getchannel('A'),mask))
    if not rgba.getchannel('A').getbbox():raise ValueError('Background removal produced an empty image')
    return rgba
