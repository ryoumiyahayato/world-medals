import json,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];SRC=Path('C:/Users/agcrf/Desktop/勋章复原资料图/其他')
S=R/'data/staging/user_other_20261003';S.mkdir(parents=True,exist_ok=True)
D=R/'assets/processed/user_other_20261003';D.mkdir(parents=True,exist_ok=True)
items=[]
for i,p in enumerate(sorted(SRC.rglob('*')),1):
 if not p.is_file():continue
 try:
  with Image.open(p) as im:
   im.load();w,h=im.size;mode=im.mode;alpha=im.getchannel('A').getextrema() if 'A' in im.getbands() else None
  sha=hashlib.sha256(p.read_bytes()).hexdigest();dest=D/(sha[:20]+p.suffix.lower())
  if not dest.exists():shutil.copy2(p,dest)
  items.append(dict(number=len(items)+1,source_file=str(p),filename=p.name,local_path=dest.relative_to(R).as_posix(),sha256=sha,width=w,height=h,mode=mode,alpha=alpha,status='needs_visual_identification',image_kind='user_restored_or_generated_reference'))
 except Exception as e:items.append(dict(source_file=str(p),error=str(e),status='decode_failed'))
(S/'inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n','utf-8')
valid=[x for x in items if 'local_path' in x]
for k in range(0,len(valid),12):
 sheet=Image.new('RGB',(1200,1600),'#b8b9ba');draw=ImageDraw.Draw(sheet)
 for j,x in enumerate(valid[k:k+12]):
  xx=(j%3)*400;yy=(j//3)*400
  with Image.open(R/x['local_path']) as im:
   im=ImageOps.contain(im.convert('RGBA'),(380,355));sheet.paste(im,(xx+(400-im.width)//2,yy+35+(355-im.height)//2),im)
  draw.text((xx+10,yy+7),str(x['number'])+' / '+str(x['width'])+'x'+str(x['height']),fill='black')
 sheet.save(S/f'contact_{k//12+1:02d}.jpg',quality=94)
print(json.dumps(dict(files=len(items),decoded=len(valid),contact_sheets=(len(valid)+11)//12)))
