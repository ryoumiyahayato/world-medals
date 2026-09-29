"""Build a contact sheet for one cached Commons scope."""
from __future__ import annotations
import argparse, json, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('scope'); args=p.parse_args(); scope=args.scope
rows=[json.loads(x) for x in (ROOT/f'data/raw_candidates/commons_{scope}.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
items=[x for x in rows if x.get('local_raw_image')]
cols,cw,ch=3,420,340; nrows=(len(items)+cols-1)//cols
canvas=Image.new('RGB',(cols*cw,max(1,nrows)*ch),'white'); draw=ImageDraw.Draw(canvas); font=ImageFont.load_default()
for n,item in enumerate(items):
 x,y=(n%cols)*cw,(n//cols)*ch
 with Image.open(ROOT/item['local_raw_image']) as src:
  im=src.convert('RGB'); im.thumbnail((cw-20,260)); canvas.paste(im,(x+(cw-im.width)//2,y+5+(260-im.height)//2))
 title=item['source_id']+' '+item['file_title'].removeprefix('File:')
 draw.multiline_text((x+6,y+270),'\n'.join(textwrap.wrap(title,width=54)[:4]),fill='black',font=font,spacing=2); draw.rectangle((x,y,x+cw-1,y+ch-1),outline='#999')
out=ROOT/f'sources/pages/commons_{scope}/contact_sheets/cached_01.jpg'; out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out,quality=88); print(out)
