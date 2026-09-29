"""Create labelled review sheets for already extracted PDF images."""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'tmp/pdfs/kuenker299_embedded'

def main():
    pages=[int(x) for x in sys.argv[1:]]
    if not pages: raise SystemExit('Pass one or more one-based PDF page numbers')
    font=ImageFont.load_default()
    for page in pages:
        folder=BASE/f'page_{page:03d}'
        files=[p for p in sorted(folder.iterdir()) if p.name!='contact.jpg' and p.suffix.lower() in {'.jpg','.jpeg','.png'}][1:]
        thumbs=[]
        for path in files:
            with Image.open(path) as src:
                im=src.convert('RGB'); im.thumbnail((360,280))
            tile=Image.new('RGB',(400,330),'white'); tile.paste(im,((400-im.width)//2,10))
            ImageDraw.Draw(tile).text((10,300),path.name,fill='black',font=font)
            thumbs.append(tile)
        cols=4; rows=max(1,(len(thumbs)+cols-1)//cols)
        sheet=Image.new('RGB',(cols*400,rows*330),(225,225,225))
        for i,tile in enumerate(thumbs): sheet.paste(tile,((i%cols)*400,(i//cols)*330))
        sheet.save(folder/'contact.jpg',quality=90)
        print(f'page {page}: {len(thumbs)} review images')

if __name__=='__main__': main()
