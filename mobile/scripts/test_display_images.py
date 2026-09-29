import sys,hashlib
from pathlib import Path
from PIL import Image
import display_images
root=Path(__file__).resolve().parents[1]/'build/display-tests';root.mkdir(parents=True,exist_ok=True)
p=root/'assets/processed';p.mkdir(parents=True,exist_ok=True);out=root/'site'
im=Image.new('RGBA',(12,12),(0,0,0,0));im.putpixel((6,6),(200,160,30,255));im.save(p/'test.png')
entry={'file':'assets/processed/test.png','original_sha256':'expected','processing':'background-removed','approved':True,'reviewed_by':'test','reviewed_at':'2026-09-29'}
r=display_images.prepare(root,out,'source.png','expected',entry)
assert (out/r['src']).exists()
with Image.open(out/r['src']) as check:assert check.convert('RGBA').getchannel('A').getextrema()==(0,255)
assert display_images.prepare(root,out,'source.png','expected',dict(entry,approved=False)) is None
for changed in [dict(entry,original_sha256='wrong'),dict(entry,file='../outside.png'),dict(entry,reviewed_by=''),dict(entry,processing='unknown')]:
 try:display_images.prepare(root,out,'source.png','expected',changed)
 except ValueError:pass
 else:raise AssertionError(changed)
print('Display image interface: transparent output, disabled mapping, source mismatch, path boundary, review and label checks passed')
