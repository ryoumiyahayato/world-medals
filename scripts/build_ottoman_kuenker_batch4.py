"""Build Kuenker 299 Ottoman batch 4 (pages 171-179, 183-184)."""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
EXTRACTED=ROOT/'tmp/pdfs/kuenker299_embedded'
ASSETS=ROOT/'assets/images/ottoman_kuenker299_batch4'
VOLUME=ROOT/'data/volumes/ottoman_kuenker299_batch4.json'
MANIFEST=ROOT/'data/volumes/ottoman_kuenker299_batch4_manifest.json'

# lot,page,front,back,family,Chinese,original,date,variant
LOTS=[
 (7215,171,3,4,'OTT-HAGIA-SOPHIA-RESTORATION','圣索菲亚大教堂修缮竣工纪念章','Ayasofya Tamir Madalyası','1849','银级；44.3毫米；非佩戴式；Fossati／Robertson签名'),
 (7217,171,7,9,'OTT-BOSNIA-1850','波斯尼亚战役奖章','Bosna Madalyası','1849','金级；金质；补配青铜悬环；无绶带'),
 (7218,172,4,5,'OTT-BOSNIA-1850','波斯尼亚战役奖章','Bosna Madalyası','1849','银级；银质；非佩戴式'),
 (7219,172,2,3,'OTT-BOSNIA-1850','波斯尼亚战役奖章','Bosna Madalyası','1849','旧制非官方青铜版；蚀刻法；旧佩戴扣；无绶带'),
 (7220,172,6,7,'OTT-IFTIHAR-MEDAL','伊夫蒂哈尔奖章','İftihâr Madalyası / Nişân-ı İftihâr Madalyası','1853-1884','第三型银级；奥斯曼式镶框；后配绶带'),
 (7221,173,2,3,'OTT-IFTIHAR-MEDAL','伊夫蒂哈尔奖章','İftihâr Madalyası / Nişân-ı İftihâr Madalyası','1853-1884','第三型银级；英式铸造绶带扣；原绶带'),
 (7222,173,5,6,'OTT-IFTIHAR-MEDAL','伊夫蒂哈尔奖章','İftihâr Madalyası / Nişân-ı İftihâr Madalyası','1853-1884','第三型银级；旧式佩戴扣；绿底红边绶带'),
 (7224,174,2,3,'OTT-IFTIHAR-MEDAL','伊夫蒂哈尔奖章','İftihâr Madalyası / Nişân-ı İftihâr Madalyası','1853-1884','第三型银级；非佩戴式'),
 (7225,174,8,9,'OTT-IFTIHAR-MEDAL','伊夫蒂哈尔奖章','İftihâr Madalyası / Nişân-ı İftihâr Madalyası','1853-1884','第三型铜质试铸；非佩戴式'),
 (7226,174,6,7,'OTT-SILISTRA','锡利斯特拉战役奖章','Silistre Madalyası','1854','银级；银质；非佩戴式'),
 (7234,177,6,7,'OTT-SILISTRA','锡利斯特拉战役奖章','Silistre Madalyası','1854','银级；银质；原绶带与双钩佩戴横条'),
 (7235,177,4,5,'OTT-SILISTRA-FLAG','锡利斯特拉军旗奖章','Sancaklı Silistre Madalyası','约1854','银质；非佩戴式；可能为第二图式，是否实际授予待考'),
 (7227,174,4,5,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第一版／英国版；CRIMEA铭文；银质；无环无绶带'),
 (7228,175,2,3,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第二版／法国版；LA CRIMEE铭文；英式佩戴扣；后配绶带'),
 (7229,176,4,5,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第三版／撒丁版；LA CRIMEA铭文；撒丁式扣；旧绶带'),
 (7230,176,2,3,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第三版／撒丁版；银质；有穿孔但无环无绶带'),
 (7231,176,8,9,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第三版／撒丁版；银质；非佩戴式'),
 (7232,176,7,6,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第三版／撒丁版；私人局部珐琅改装；原穿孔封闭'),
 (7233,177,3,2,'OTT-CRIMEA','克里米亚战争奖章','Kırım Madalyası','1855-1856','第三版／撒丁版；私人彩色珐琅改装；胸针式'),
 (7236,178,2,3,'OTT-KARS','卡尔斯战役奖章','Kars Madalyası','1855','银级；银质；非佩戴式'),
 (7237,178,6,7,'OTT-KARS','卡尔斯战役奖章','Kars Madalyası','1855','银级；英式铸造绶带扣；原绶带'),
 (7238,178,4,5,'OTT-IFTIHAR-ORDER','伊夫蒂哈尔勋章奖章','Nişân-ı İftihâr Madalyası','1858','银质低阶奖章形制；非佩戴式'),
 (7239,179,2,3,'OTT-LIFESAVING','救生奖章','Tahlisiye Madalyası','约1858-1922','银质；原绶带；佩戴横条'),
 (7240,179,4,5,'OTT-LIFESAVING','救生奖章','Tahlisiye Madalyası','约1914-1922','锌质战末版；残留镀银；无环无绶带'),
 (7241,179,6,7,'OTT-LIFESAVING','救生奖章','Tahlisiye Madalyası','约1858-1922','银质；非佩戴式'),
 (7242,179,8,9,'OTT-LIFESAVING','救生奖章','Tahlisiye Madalyası','约1858-1922','青铜质试铸；非佩戴式'),
 (7249,183,2,3,'OTT-CRETE-ATIK-GIRIT','旧式克里特战役奖章','Atîk Girit Madalyası','1868','银质；后配绶带扣；旧绿色绶带'),
 (7250,183,4,5,'OTT-CRETE-ATIK-GIRIT','旧式克里特战役奖章','Atîk Girit Madalyası','1868','银质；非佩戴式'),
 (7251,184,2,3,'OTT-RUSSO-TURKISH-WAR-1877','俄土战争奖章','Rusya Muhârebesi Madalyası','1877-1878','第二版；El Gazi图格拉；银质；绶带与佩戴横条'),
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
            src=extracted(page,index); dst=ASSETS/f'lot_{lot}_{side.lower()}{src.suffix.lower()}'
            shutil.copy2(src,dst)
            with Image.open(dst) as im: width,height=im.size; im.verify()
            key=f'{rid}-{side}'; views.append({'key':key,'label':label})
            images.append({'view_key':key,'local_path':dst.relative_to(ROOT).as_posix(),'source_id':f'kuenker299-lot-{lot}','download_status':'extracted_and_decoded','source_page_url':f'https://kuenker.s3.eu-central-1.amazonaws.com/media/31/1d/22/1736866624/299_kuenker-katalog_web.pdf#page={page}','source_original_url':f'embedded image in Kuenker Auction 299 PDF, page {page}, image {index}','license':'Kuenker Auction 299 catalogue photograph; local research use only','width':width,'height':height,'sha256':digest(dst),'pdf_page':page,'lot':lot,'side':side.lower()})
        records.append({'id':rid,'family':family,'country_zh':'奥斯曼帝国','name':name,'original':original,'date':date,'variant':f'{variant}；Künker 299图录实物照 · 2017','views':views,'source_ids':[f'kuenker299-lot-{lot}'],'image_kind':'object_photo','html_eligible':True})
    VOLUME.write_text(json.dumps({'as_of':'2026-09-27','volume':'奥斯曼帝国：Künker 299专题拍卖差集第四批','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    MANIFEST.write_text(json.dumps({'as_of':'2026-09-27','source':'Künker Auction 299, The Ottoman Collection Part 2','source_pdf':'sources/ottoman_atlas_packB_cache/kuenker-299-web.pdf','pages_processed':sorted({x[1] for x in LOTS}),'lots_ingested':[x[0] for x in LOTS],'images':images},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'wrote {len(records)} records and {len(images)} images')

if __name__=='__main__': main()
