"""Fetch selected Commons object pages and original files, preserving provenance."""
from pathlib import Path
import hashlib,json,time
import requests
from bs4 import BeautifulSoup
from PIL import Image
R=Path(__file__).resolve().parents[1]
C=R/'sources/cache/soviet_completion';I=R/'assets/images/soviet_completion'
C.mkdir(parents=True,exist_ok=True);I.mkdir(parents=True,exist_ok=True)
files={
 'public-order':'Soviet_Medal_For_Distinction_in_the_Protection_of_Public_Order.jpg',
 'hammer-sickle':'Lyubov_Smirnova,_Hammer_and_Sickle_medal_(2021-08-25)_01.jpg',
 'gold-star':'Golden_Star_medal_473_f.jpg',
 'lenin-type2':'OrderLenin_II.jpg',
}
s=requests.Session();s.headers['User-Agent']='WorldMedalsResearch/1.0 (local historical catalogue)'
out=[]
for key,name in files.items():
 row={'key':key,'source_page':'https://commons.wikimedia.org/wiki/File:'+name,'accessed':'2026-09-29'}
 try:
  cache=C/(key+'.html')
  if not cache.exists():
   res=s.get(row['source_page'],timeout=25);res.raise_for_status();cache.write_bytes(res.content);time.sleep(1)
  soup=BeautifulSoup(cache.read_bytes(),'html.parser');link=soup.select_one('.fullImageLink a')
  if not link:raise ValueError('No original image link in source page')
  row['image_url']=link['href'];row['source_text']=soup.get_text(' ',strip=True)
  target=I/(key+'.jpg')
  if not target.exists():
   res=s.get(link['href'],timeout=30);res.raise_for_status();target.write_bytes(res.content);time.sleep(1)
  with Image.open(target) as im:im.load();row['width'],row['height']=im.size
  row.update(local_path=target.relative_to(R).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),status='decoded_pending_visual_review')
 except Exception as e:row.update(status='failed',error=str(e))
 out.append(row);(C/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8');print(key,row['status'],flush=True)
