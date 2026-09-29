"""Build Kuenker 299 Ottoman batch 5: late official awards, 1908-1918."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
EXTRACTED=ROOT/'tmp/pdfs/kuenker299_embedded'; ASSETS=ROOT/'assets/images/ottoman_kuenker299_batch5'
VOLUME=ROOT/'data/volumes/ottoman_kuenker299_batch5.json'; MANIFEST=ROOT/'data/volumes/ottoman_kuenker299_batch5_manifest.json'

LOTS=[
 (7329,210,4,5,'OTT-CONSTITUTION','宪政奖章','Kânûn-ı Esâsî Madalyası','1908-1909','银级；佩戴式；红白条纹绶带'),
 (7330,210,2,3,'OTT-CONSTITUTION','宪政奖章','Kânûn-ı Esâsî Madalyası','1908-1909','银级；无环无绶带'),
 (7331,211,4,5,'OTT-CONSTITUTION-CRESCENTS','双新月宪政奖章','Hilâlli Kânûn-ı Esâsî Madalyası','1909','金级；27.2×23.6毫米；无环无绶带；具体用途待考'),
 (7332,211,2,10,'OTT-BURSA-EXHIBITION','布尔萨展览奖章','Bursa Sergisi Madalyası','1909','银级；43.9毫米；非佩戴式'),
 (7333,211,9,8,'OTT-BURSA-EXHIBITION','布尔萨展览奖章','Bursa Sergisi Madalyası','1909','银级；43.8毫米；佩戴式；无环无绶带；受奖人题名'),
 (7334,211,6,7,'OTT-MUNICIPAL-ASSEMBLY-1908','市政总会首次会议纪念章','Cemiyet-i Umûmiyye-i Belediyenin İlk İctimaı Hâtıra Madalyası','1908','成员纪念章；43.8毫米；非佩戴式'),
 (7337,213,2,3,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','小型金级；28.1毫米；佩戴扣；无绶带'),
 (7338,213,4,5,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','银级；27.9毫米；胸绶带与横条；原盒'),
 (7339,214,4,5,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','银级；26.9毫米；佩戴扣；无绶带'),
 (7340,214,2,3,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','银级；27毫米；移除悬环；非佩戴式'),
 (7341,214,6,7,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','女士银级；27.9毫米；蝴蝶结与双针；原盒'),
 (7342,215,2,3,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','镍级；24.7毫米；胸绶带与横条；原盒'),
 (7343,215,6,7,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','镍级；24.7毫米；正背图案倒置版；胸绶带与横条'),
 (7346,216,4,5,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','小型青铜级；24.7毫米；仅有悬环'),
 (7347,216,2,3,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','大型青铜级；27.7毫米；非佩戴式'),
 (7348,217,2,3,'OTT-NAVAL-DONATION','奥斯曼舰队捐助功绩奖章','Donanma İane Madalyası','1912','小型青铜级；24.5毫米；非佩戴式'),
 (7349,217,4,5,'OTT-RED-CRESCENT','奥斯曼红新月奖章','Hilâl-i Ahmer Madalyası','1912-1914','第一版银级；1327-1329纪年横条；局部珐琅'),
 (7350,217,6,7,'OTT-RED-CRESCENT','奥斯曼红新月奖章','Hilâl-i Ahmer Madalyası','1912-1914','第一版银级；Kafkas横条；横条原配性待考'),
 (7351,218,2,3,'OTT-RED-CRESCENT','奥斯曼红新月奖章','Hilâl-i Ahmer Madalyası','1912-1914','第一版青铜级；1327-1329纪年横条；局部珐琅'),
 (7352,218,6,4,'OTT-RED-CRESCENT','奥斯曼红新月奖章','Hilâl-i Ahmer Madalyası','约1914以后','第二版金级加金质橡叶；无年份横条；原绶带'),
 (7355,221,3,4,'OTT-IMTIYAZ-MEDAL','大伊姆蒂亚兹忠勇奖章','Sadakat ve Şecaat Madalyası','1914年战时型；1916年授予','金级；1332纪年双剑横条；原绶带；埃尔祖鲁姆战役题名'),
 (7357,222,2,3,'OTT-IMTIYAZ-MEDAL','大伊姆蒂亚兹忠勇奖章','Sadakat ve Şecaat Madalyası','1914年战时型','银级；1332纪年双剑横条；原绶带'),
 (7358,223,2,4,'OTT-IMTIYAZ-MEDAL','大伊姆蒂亚兹忠勇奖章','Sadakat ve Şecaat Madalyası','1914年战时型','银级；无绶带；双剑与佩戴横条；恩维尔帕夏题名真实性无保证'),
 (7359,224,2,3,'OTT-IMTIYAZ-MEDAL','大伊姆蒂亚兹忠勇奖章','Sadakat ve Şecaat Madalyası','约1915','德国后制复制品；威廉二世授予件仿制；白色金属铸造；非佩戴式'),
 (7360,224,4,5,'OTT-IMTIYAZ-MEDAL','大伊姆蒂亚兹忠勇奖章','Sadakat ve Şecaat Madalyası','约1915','德国后制复制品微型章；白色金属铸造；非佩戴式'),
 (7361,224,6,7,'OTT-LIYAKAT','忠勇功绩奖章','Liyakât Madalyası','1914年战时型','金级；1332纪年双剑横条；原绶带与原盒'),
 (7363,225,2,3,'OTT-LIYAKAT','忠勇功绩奖章','Liyakât Madalyası','1914年战时型','银级；1332纪年双剑横条；原绶带'),
 (7366,226,5,6,'OTT-LIYAKAT','忠勇功绩奖章','Liyakât Madalyası','1914年战时型','奥地利旧制私人后配版；镀银贱金属；三角绶带与双剑横条'),
 (7367,228,3,2,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','奥斯曼原制；氧化铝质；红漆；横针'),
 (7369,228,6,5,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','德国B.B.&Co.制；镀银贱金属与红珐琅；Kafkas横条'),
 (7373,230,3,2,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','德国B.B.&Co.制；镀银贱金属与红珐琅；Kanal横条'),
 (7375,230,8,5,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','德国或奥地利未知厂；58.8毫米厚型；银质精细机刻珐琅'),
 (7376,231,3,2,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','柏林Alfred Werner & Söhne制；银质珐琅；镂空图格拉；七枚石饰；原盒'),
 (7377,231,6,5,'OTT-WAR','奥斯曼战争奖章','Harp Madalyası','1915','奥地利超大型版；48.4毫米；镂空图格拉；镀银贱金属珐琅；星形戳记'),
 (7379,232,3,4,'OTT-KARL-I-VISIT-1918','奥皇卡尔一世访问君士坦丁堡纪念章','Avusturya Mülâkat Madalyası','1918','银级；64.4毫米；非佩戴式；原盒'),
 (7380,232,7,8,'OTT-KARL-I-VISIT-1918','奥皇卡尔一世访问君士坦丁堡纪念章','Avusturya Mülâkat Madalyası','1918','青铜级；65毫米；非佩戴式'),
 (7381,232,5,6,'OTT-CANAKKALE-AGRICULTURE-1918','恰纳卡莱农业展览奖章','Çanakkale Zirâat Sergisi Madalyası','1918','银级；重度佩戴；无环无绶带'),
]

def extracted(page,index):
 m=sorted((EXTRACTED/f'page_{page:03d}').glob(f'{index:02d}_*'))
 if len(m)!=1: raise RuntimeError((page,index,m))
 return m[0]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 ASSETS.mkdir(parents=True,exist_ok=True); records=[]; images=[]
 for lot,page,fi,bi,family,name,original,date,variant in LOTS:
  rid=f'OK299-{lot}'; views=[]
  for side,label,index in [('FRONT','正面完整实物图',fi),('BACK','背面完整实物图',bi)]:
   src=extracted(page,index); dst=ASSETS/f'lot_{lot}_{side.lower()}{src.suffix.lower()}'; shutil.copy2(src,dst)
   with Image.open(dst) as im: width,height=im.size; im.verify()
   key=f'{rid}-{side}'; views.append({'key':key,'label':label})
   images.append({'view_key':key,'local_path':dst.relative_to(ROOT).as_posix(),'source_id':f'kuenker299-lot-{lot}','download_status':'extracted_and_decoded','source_page_url':f'https://kuenker.s3.eu-central-1.amazonaws.com/media/31/1d/22/1736866624/299_kuenker-katalog_web.pdf#page={page}','source_original_url':f'embedded image in Kuenker Auction 299 PDF, page {page}, image {index}','license':'Kuenker Auction 299 catalogue photograph; local research use only','width':width,'height':height,'sha256':digest(dst),'pdf_page':page,'lot':lot,'side':side.lower()})
  records.append({'id':rid,'family':family,'country_zh':'奥斯曼帝国','name':name,'original':original,'date':date,'variant':f'{variant}；Künker 299图录实物照 · 2017','views':views,'source_ids':[f'kuenker299-lot-{lot}'],'image_kind':'object_photo','html_eligible':True})
 VOLUME.write_text(json.dumps({'as_of':'2026-09-27','volume':'奥斯曼帝国：Künker 299专题拍卖差集第五批','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 MANIFEST.write_text(json.dumps({'as_of':'2026-09-27','source':'Künker Auction 299, The Ottoman Collection Part 2','source_pdf':'sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf','pages_processed':sorted({x[1] for x in LOTS}),'lots_ingested':[x[0] for x in LOTS],'images':images},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'wrote {len(records)} records and {len(images)} images')
if __name__=='__main__': main()
