"""Focused verification of the explicitly reviewed background rules."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
from background_trim import load_rules,remove_edge_light
from prepare_display import material_root

ROOT=Path(__file__).resolve().parents[2]

def verify():
    rules=load_rules(ROOT);materials=material_root(ROOT)
    mapping=json.loads((ROOT/'mobile/build/image-provenance.json').read_text(encoding='utf-8'))
    count=0
    for relative,rule in rules.items():
        if rule.get('approved') is not True:continue
        with Image.open(materials/relative) as source:
            original=ImageOps.exif_transpose(source).convert('RGBA')
            processed=remove_edge_light(original,rule['minimum'],rule['chroma'])
        assert processed.convert('RGB').tobytes()==original.convert('RGB').tobytes(),relative
        red,green,blue=original.convert('RGB').split()
        low=ImageChops.darker(ImageChops.darker(red,green),blue)
        high=ImageChops.lighter(ImageChops.lighter(red,green),blue)
        protected=ImageChops.lighter(low.point(lambda v:255 if v<rule['minimum'] else 0),
                      ImageChops.subtract(high,low).point(lambda v:255 if v>rule['chroma'] else 0))
        removed=ImageChops.subtract(original.getchannel('A'),processed.getchannel('A'))
        assert ImageChops.multiply(protected,removed).getbbox() is None,relative
        entry=mapping[relative]
        assert entry['processing']['status']=='background-removed-reviewed'
        assert entry['provenance'].get('image_kind')!='user_restored_reference'
        for label,limit in (('thumb',384),('src',1200)):
            with Image.open(ROOT/'mobile/build/site'/entry[label]) as image:
                image.load();assert max(image.size)<=limit
                bounds=image.getchannel('A').getbbox()
                assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<image.width and bounds[3]<image.height
        count+=1
    print(json.dumps({'reviewedBackgroundImages':count,'retainedRGB':'unchanged','protectedPixels':'retained','displayDecodeAndMargins':'passed'}))

if __name__=='__main__':verify()
