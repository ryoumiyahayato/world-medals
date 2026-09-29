"""Render one normalized volume's selected images for visual review."""
import argparse,json,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('volume');p.add_argument('manifest');p.add_argument('output');a=p.parse_args()
rows=json.loads((ROOT/a.volume).read_text(encoding='utf-8'))['records'];items=json.loads((ROOT/a.manifest).read_text(encoding='utf-8'))['images'];by={}
view_owner={v['key']:r['id'] for r in rows for v in r.get('views',[])}
for item in items:
 rid=item.get('record_id') or item.get('variant_id') or view_owner.get(item.get('view_key'))
 if rid:by.setdefault(rid,item)
cols,cw,ch=4,360,330;nr=(len(rows)+cols-1)//cols;canvas=Image.new('RGB',(cols*cw,max(1,nr)*ch),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default()
for n,r in enumerate(rows):
 x,y=(n%cols)*cw,(n//cols)*ch;item=by[r['id']]
 with Image.open(ROOT/item['local_path']) as src:im=src.convert('RGB');im.thumbnail((cw-20,255));canvas.paste(im,(x+(cw-im.width)//2,y+5+(250-im.height)//2))
 label=f'{n+1:02d} {r["name"]} / {r["original"]}';draw.multiline_text((x+6,y+260),'\n'.join(textwrap.wrap(label,48)[:3]),fill='black',font=font,spacing=2);draw.rectangle((x,y,x+cw-1,y+ch-1),outline='#999')
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);canvas.save(out,quality=88);print(out)
