"""Render the 31 selected Jordan family images for one-pass visual review."""
from pathlib import Path
import json, textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
vol=json.loads((ROOT/'data/volumes/jordan_wawards_families.json').read_text(encoding='utf-8'))['records']
man=json.loads((ROOT/'data/volumes/jordan_wawards_families_manifest.json').read_text(encoding='utf-8'))['images']; by={x['record_id']:x for x in man}
cols,cw,ch=4,360,330; rows=(len(vol)+cols-1)//cols; canvas=Image.new('RGB',(cols*cw,rows*ch),'white'); draw=ImageDraw.Draw(canvas); font=ImageFont.load_default()
for n,r in enumerate(vol):
 x,y=(n%cols)*cw,(n//cols)*ch; item=by[r['id']]
 with Image.open(ROOT/item['local_path']) as src: im=src.convert('RGB'); im.thumbnail((cw-20,260)); canvas.paste(im,(x+(cw-im.width)//2,y+5+(255-im.height)//2))
 label=f'{n+1:02d} {r["name"]} / {r["original"]}'; draw.multiline_text((x+6,y+264),'\n'.join(textwrap.wrap(label,48)[:3]),fill='black',font=font,spacing=2); draw.rectangle((x,y,x+cw-1,y+ch-1),outline='#999')
out=ROOT/'sources/pages/wawards_jordan/contact_sheet_selected.jpg'; out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out,quality=88); print(out)
