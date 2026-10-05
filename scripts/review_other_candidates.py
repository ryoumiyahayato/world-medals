from pathlib import Path
import json
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];S=R/'data/staging/user_other_20261003'
soup=BeautifulSoup((R/'index.html').read_text('utf-8'),'html.parser');items=[];seen=set()
for sec in soup.select('section.period-section'):
 if sec.get('id') not in ['egypt','nepal','laos-kingdom','vietnam-annam','tai-federation','qing-empire','myanmar','mongolian-peoples-republic','lebanon','turkmenistan','cambodia-kingdom','cambodia-protectorate','morocco']:continue
 for tr in sec.select('tr[id]'):
  cells=tr.find_all('td',recursive=False)
  if len(cells)!=3:continue
  name=cells[0].get_text(' ',strip=True);image=cells[2].select_one('img[src]')
  if not image or not any(x in name for x in ['勋章','之星','金新月','册立','王储','双龙','金磬']):continue
  family=tr.get('data-award-family',tr.get('data-family-key'));variant=cells[1].get_text(' ',strip=True)
  key=(family,variant)
  if key in seen:continue
  seen.add(key);items.append(dict(number=len(items)+1,id=tr['id'],family=family,name=name,variant=variant,volume=sec['id'],source_ids=tr.get('data-source-ids'),image=image['src']))
(S/'existing_candidates.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf-8')
for k in range(0,len(items),20):
 sheet=Image.new('RGB',(1600,1500),'#ddd');draw=ImageDraw.Draw(sheet)
 for j,x in enumerate(items[k:k+20]):
  xx=j%4*400;yy=j//4*300
  with Image.open(R/x['image']) as im:
   im=ImageOps.contain(im.convert('RGBA'),(385,255));sheet.paste(im,(xx+(400-im.width)//2,yy+40),im)
  draw.text((xx+5,yy+5),str(x['number'])+' '+x['family'][:43],fill='black')
 sheet.save(S/f'existing_{k//20+1:02}.jpg',quality=90)
print(len(items))
