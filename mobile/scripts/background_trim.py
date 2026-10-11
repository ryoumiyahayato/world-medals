"""Reviewed deterministic matte removal. No image synthesis or recolouring."""
import json
from PIL import Image, ImageChops, ImageDraw

def load_rules(root):
    path=root/'data/display_images/background_rules.json'
    return json.loads(path.read_text(encoding='utf-8'))['images'] if path.exists() else {}

def remove_edge_light(frame, minimum=248, chroma=8):
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
    rgba=frame.convert('RGBA')
    rgba.putalpha(ImageChops.multiply(rgba.getchannel('A'),mask))
    if not rgba.getchannel('A').getbbox():raise ValueError('Background removal produced an empty image')
    return rgba
