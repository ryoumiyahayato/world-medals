import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=root/'data'
load=lambda name:json.loads((data/name).read_text(encoding='utf-8'))
sources=load('sources.json')
sources['tdv-nisan']['summary']='1852-08-29 Mecidi Nişanı regulations; Osmaniye Nişanı regulations 1861-12-12; Şefkat Nişanı 1878; Iftihar order regulations recorded in 1833; Imtiyaz order granted by 1841 and had no grades.'
sources['tdv-madalya']['summary']='Ottoman medals grouped by sultan and date; includes 1847 Yemen and Kurdistan, 1850 Bosnia, 1865 cholera, 1877 Plevne/Bosnia battle, 1899 Maarif, 1900 Hejaz Railway, 1914 Tayyare and other cataloged medals.'
sources['ttk-rulers']={'page':'https://ttk.gov.tr/osmanli-padisahlari/',
 'summary':'Turkish Historical Society list of Ottoman sultans and their reign years; used for ruler navigation.',
 'accessed':'2026-09-25'}
sources['maarif-order']={'page':'https://turkmaarifansiklopedisi.org.tr/maarif-nisani',
 'summary':'Maarif Nişanı received formal status on 1910-05-15, in three grades; distinct from abolished Maarif Madalyası.',
 'accessed':'2026-09-25'}
(data/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
cat=load('catalogue.json')['records'];related=load('related.json');un=load('unpictured.json')
for row in cat:
    if row['family']=='OTT-MAARIF-ORDER' and 'maarif-order' not in row['source_ids']:
        row['source_ids'].insert(0,'maarif-order')
(data/'catalogue.json').write_text(json.dumps({'as_of':'2026-09-25','records':cat},ensure_ascii=False,indent=2),encoding='utf-8')
photos=sum(len(x['views']) for x in cat+related)
progress={'as_of':'2026-09-25','volume':'Ottoman Empire','main_families':len({x['family'] for x in cat}),
 'main_variants':len(cat),'main_local_images':sum(len(x['views']) for x in cat),
 'related_variants':len(related),'related_local_images':sum(len(x['views']) for x in related),
 'unpictured_documented':len(un),'unpictured_main_families':sum(x['category']=='主编' for x in un),
 'legacy_candidates_start':28,'legacy_migration_unresolved':0,
 'legacy_without_complete_local_image':0,
 'next_batch':'优先为TDV登记的射击、霍乱、克里特、波斯尼亚战役及航空奖章寻完整原站实物图；继续核实同名勋章与奖章。',
 'limits':['当前环境的浏览器安全策略阻止直接打开此本地项目；已完成静态离线资源与脚本交互模拟验收，尚未完成浏览器视觉验收。',
           '部分旧馆藏和拍卖图片低于1200像素，按低清参考标注。']}
(data/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
print(progress)
