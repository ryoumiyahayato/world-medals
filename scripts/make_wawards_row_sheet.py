"""Make an enlarged sheet for one Wawards object row (all its source views)."""
import json, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
scope, row_no, output = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rows=[json.loads(x) for x in (ROOT/f'data/raw_candidates/wawards_{scope}.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
row=rows[row_no-1]; items=row.get('original_images',[]); cols=min(4,max(1,len(items))); cw,ch=420,440
canvas=Image.new('RGB',(cols*cw, ((len(items)+cols-1)//cols)*ch),'white'); draw=ImageDraw.Draw(canvas); font=ImageFont.load_default()
for i,item in enumerate(items,1):
    x,y=(i-1)%cols*cw,(i-1)//cols*ch
    with Image.open(ROOT/item['local_path']) as src: im=src.convert('RGB')
    im.thumbnail((cw-20,380)); canvas.paste(im,(x+(cw-im.width)//2,y+5+(380-im.height)//2))
    draw.multiline_text((x+8,y+390),f'{i}: {Path(item["local_path"]).name}',fill='black',font=font)
    draw.rectangle((x,y,x+cw-1,y+ch-1),outline='#999')
out=ROOT/output; out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out,quality=90); print(out)
