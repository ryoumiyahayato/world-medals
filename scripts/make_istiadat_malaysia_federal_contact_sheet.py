from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math

ROOT=Path(__file__).resolve().parents[1]
rows=[json.loads(line) for line in (ROOT/'data/raw_candidates/istiadat_malaysia_federal.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
thumb_w,thumb_h,label_h,cols=300,300,72,4
font=ImageFont.load_default()
sheet=Image.new('RGB',(cols*thumb_w,math.ceil(len(rows)/cols)*(thumb_h+label_h)),'white')
draw=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
    path=ROOT/row['original_images'][0]['local_path']
    with Image.open(path) as source:
        im=source.convert('RGB'); im.thumbnail((thumb_w-16,thumb_h-16))
    x=(i%cols)*thumb_w+(thumb_w-im.width)//2; y=(i//cols)*(thumb_h+label_h)+(thumb_h-im.height)//2
    sheet.paste(im,(x,y))
    label=f"{i+1:02d} {row['page_title']}"
    draw.multiline_text(((i%cols)*thumb_w+5,(i//cols)*(thumb_h+label_h)+thumb_h+3),label,fill='black',font=font,spacing=2)
out=ROOT/'sources/pages/istiadat_malaysia_federal/contact_sheet.jpg'; sheet.save(out,quality=90)
print(out)
