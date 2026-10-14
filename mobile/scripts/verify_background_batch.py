"""Focused verification of the explicitly reviewed background rules."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageDraw
from background_trim import load_rules,apply_rule
from prepare_display import material_root

ROOT=Path(__file__).resolve().parents[2]

def verify(only=None):
    rules=load_rules(ROOT);materials=material_root(ROOT)
    mapping=json.loads((ROOT/'mobile/build/image-provenance.json').read_text(encoding='utf-8'))
    count=0;crops=0
    for relative,rule in rules.items():
        if only and relative not in only:continue
        if rule.get('approved') is not True:continue
        with Image.open(materials/relative) as source:
            original=ImageOps.exif_transpose(source).convert('RGBA')
            processed=apply_rule(original,rule)
        assert processed.convert('RGB').tobytes()==original.convert('RGB').tobytes(),relative
        red,green,blue=original.convert('RGB').split()
        low=ImageChops.darker(ImageChops.darker(red,green),blue)
        high=ImageChops.lighter(ImageChops.lighter(red,green),blue)
        if rule.get('kind')=='crop-only':
            protected=Image.new('L',original.size,0)
            x0,y0,x1,y1=rule['crop']
            ImageDraw.Draw(protected).rectangle((x0,y0,x1-1,y1-1),fill=255)
            crops+=1
        elif rule.get('kind')=='reviewed-runs':
            protected=Image.new('L',original.size,0)
            draw=ImageDraw.Draw(protected)
            for polygon in rule.get('protectedPolygons',[]):
                draw.polygon([tuple(point) for point in polygon],fill=255)
        else:
            tonal = high.point(lambda v:255 if v>rule['maximum'] else 0) if rule.get('kind')=='edge-connected-dark' else low.point(lambda v:255 if v<rule['minimum'] else 0)
            protected=ImageChops.lighter(tonal,
                          ImageChops.subtract(high,low).point(lambda v:255 if v>rule['chroma'] else 0))
        removed=ImageChops.subtract(original.getchannel('A'),processed.getchannel('A'))
        assert ImageChops.multiply(protected,removed).getbbox() is None,relative
        entry=mapping[relative]
        assert entry['processing']['status']==('crop-reviewed' if rule.get('kind')=='crop-only' else 'background-removed-reviewed')
        assert entry['provenance'].get('image_kind')!='user_restored_reference'
        for label,limit in (('thumb',384),('src',1200)):
            with Image.open(ROOT/'mobile/build/site'/entry[label]) as image:
                image.load();assert max(image.size)<=limit
                bounds=image.getchannel('A').getbbox()
                assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<image.width and bounds[3]<image.height
        count+=1
    print(json.dumps({'reviewedBackgroundImages':count-crops,'reviewedCropImages':crops,'retainedRGB':'unchanged','protectedPixels':'retained','displayDecodeAndMargins':'passed'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--only',nargs='+',help='Check only these source-relative paths')
    verify(parser.parse_args().only)
