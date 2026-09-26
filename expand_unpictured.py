"""Record distinct Ottoman awards named in the TDV medal survey for image follow-up."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
path=ROOT/'data/unpictured.json'
items=json.loads(path.read_text(encoding='utf-8'))
known={x['family'] for x in items}
# Dates are the survey's Gregorian equivalents of Ottoman years; not exact institution days.
new=[
 ('OTT-KURDISTAN-1847','库尔德斯坦战役奖章','Kürdistan Madalyası','1847','金质／银质；镶饰版另见原目录','主编'),
 ('OTT-SINOP-1853','锡诺普战役奖章','Sinop Madalyası','1853–1854','铜质','主编'),
 ('OTT-BLACK-SEA-DANUBE','黑海与多瑙河奖章','Bahr-i Siyâh ve Tuna Madalyası','1854–1855','铅质；授予性质待核','主编'),
 ('OTT-TRIPLE-ALLIANCE','三国联盟纪念章','İttifâk-ı Düvel-i Selâse Madalyası','1854–1855','铜质／铅质；纪念章','相关附编'),
 ('OTT-LIFESAVING','救生奖章','Tahlîs-i Can Madalyası','1859–1860','银质／铜质','主编'),
 ('OTT-SKILL-KNOWLEDGE','技艺与学识奖章','Tahsîn-i Hüner ve Mârifet Madalyası','1859–1860','金质／银质／铜质','主编'),
 ('OTT-GENDARMERIE-SERGEANT','宪兵军士奖章','Zaptiye Çavuşları Madalyası','1860–1861','银质','主编'),
 ('OTT-1862-EXHIBITION','奥斯曼综合展览奖章','Sergi-i Umûmî-i Osmânî Madalyası','1862','金质／银质／铜质；展览奖励性质待核','相关附编'),
 ('OTT-RIFLE-SHOOTING','六膛线步枪射击奖章','Şeşhâneli Tüfek Madalyası','1862','金质／银质','主编'),
 ('OTT-ENDAHT','射击勋章奖章','Endaht Nişanı Madalyası','1863','银质','主编'),
 ('OTT-CHOLERA','霍乱救护奖章','Kolera Madalyası','1865','银质；授奖对象待核','主编'),
 ('OTT-CRETE-OLD','旧式克里特战役奖章','Atik Girit Madalyası','1868','银质','主编'),
 ('OTT-BOSNIA-1877','波斯尼亚战役奖章','Bosna Muharebesi Madalyası','1877','银质；与1850年波斯尼亚奖章分开','主编'),
 ('OTT-PLEVNA','普列夫纳战役奖章','Plevne Madalyası','1877','银质','主编'),
 ('OTT-IFTIHAR-MEDAL-1885','荣誉奖章','İftihar Madalyası','1885','金质／银质；与荣誉勋章分开','主编'),
 ('OTT-CRETE-NEW','新式克里特战役奖章','Tarz-ı Cedîd Girit Madalyası','1890–1891','金质／银质','主编'),
 ('OTT-EARTHQUAKE','地震救助奖章','Hareket-i Arz Madalyası','1894–1895','金质／银质／铜质','主编'),
 ('OTT-ANATOLIA-AID','安纳托利亚援助奖章','Anadolu Müsâbînîne İâne Madalyası','1895–1896','银质','主编'),
 ('OTT-MILITARY-DONATION','军事设施捐助奖章','Te’sîsât-ı Askeriyye İâne Madalyası','1896–1897','金质／银质／铝质','主编'),
 ('OTT-GREEK-WAR','希腊战争奖章','Yunan Muharebesi Madalyası','1896–1897','银质','主编'),
 ('OTT-SILK-COMPETITION','蚕丝竞赛奖章','Harîr Müsabakası Madalyası','1904','金质／银质／铜质；竞赛奖励','相关附编'),
 ('OTT-AVIATION-1914','航空奖章','Tayyare Madalyası','1914','金质／银质／铜质','主编'),
 ('OTT-NATIONAL-DEFENCE-SEWING','国防缝纫救济奖章','Müdâfaa-i Milliye Biçki Yurdu Madalyası','1914','金质／银质','主编'),
]
for family,name,original,date,grade,category in new:
    if family not in known:
        items.append({'family':family,'name':name,'original':original,'date':date,
                      'known_grade':grade,'category':category,'source_ids':['tdv-madalya'],
                      'reason':'TDV İslâm Ansiklopedisi 奖章综述有文字记载；尚未取得可核对版型的完整实物图。'})
path.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print('unpictured',len(items),'new',len(new))
