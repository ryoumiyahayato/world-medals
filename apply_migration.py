"""One-time, auditable union of the 28 legacy leads with the existing gallery."""
import hashlib,json,re,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
data=ROOT/'data'
if (data/'migration_log.json').exists():
    raise SystemExit('Legacy migration is already recorded; use build_site.py for subsequent builds.')
legacy=json.loads((data/'legacy_pending.json').read_text(encoding='utf-8'))
downloads={x['legacy_key']:x for x in json.loads((ROOT/'sources/legacy_review/download_report.json').read_text(encoding='utf-8'))}
cat=json.loads((data/'catalogue.json').read_text(encoding='utf-8'))
sources=json.loads((data/'sources.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))
old_html=(ROOT/'sources/legacy_ottoman_28_unverified.html').read_text(encoding='utf-8')
old={x['key']:x for x in json.loads(re.search(r'<script id="catalogue-data" type="application/json">(.*?)</script>',old_html,re.S).group(1))['records']}
present={x['id'] for x in cat['records']}
main={
 'MEDJ-I':('OTT-MEDJ','1852','一等；大绶章挂章；无剑；约1900年；现代绶带'),
 'MEDJ-II':('OTT-MEDJ','1852','二等；文职胸星；无剑；约1880年'),
 'MEDJ-IV':('OTT-MEDJ','1852','四等；挂章；无剑；原绶带'),
 'MEDJ-V-S':('OTT-MEDJ','1852','五等；军用加剑；银质；替换绶带'),
 'OSM-III':('OTT-OSM','1861年条例／1862年设立说','三等；指挥官颈章；第二型；无剑；约1910年'),
 'EDU-ORDER':('OTT-MAARIF-ORDER','1910年5月15日','教育勋章；等级待核；低清参考'),
 'LIY-S':('OTT-LIYAKAT','1890–1891','银质；花丝悬挂；无剑；低清参考'),
 'LIY-MINI':('OTT-LIYAKAT','1890–1891','微型章；交叉剑饰；铜色金属，材质待核；约1915年'),
 'IMT-MEDAL':('OTT-IMTIYAZ-MEDAL','1883','大功绩奖章；银质；36毫米；正背同图'),
 'SANAYI':('OTT-SANAYI','1884（拍品说明）','工业奖章；银质；31毫米；替换绶带'),
 'AGRI-S':('OTT-AGRI-INDUSTRY','1892–1893','农业与工业奖章；银质；44.4毫米；非佩戴型'),
 'GRAD':('OTT-MAARIF-MEDAL','1899','教育奖章；银质；毕业奖励；正背同图'),
 'HEJAZ-G':('OTT-HEJAZ-RAIL','1900','汉米迪耶汉志铁路奖章；金质小型佩戴章；盒与正背同图'),
 'BOSNIA':('OTT-BOSNIA-1850','1850','波斯尼亚奖章；等级／材质待核；穿孔佩戴实例'),
 'YEMEN-I':('OTT-YEMEN-1847','1847','第一次也门战役奖章；银质；正背同图'),
 'YEMEN-II':('OTT-YEMEN-1892','1892–1893','新式也门战役奖章；银质；25毫米；正背同图'),
 'KARS':('OTT-KARS','1855–1856','卡尔斯保卫战奖章；银质；低清参考'),
 'NAVAL':('OTT-NAVAL-DONATION','1912／1913','海军募捐奖章；材质待核；低清参考'),
}
related={
 'RED-CRESCENT':('OTT-RED-CRESCENT','20世纪初','红新月救护奖章；铜色金属；授予机构待核'),
 'NUSRET':('OTT-NUSRET-MOSQUE','19世纪前期','努斯雷特清真寺纪念章；金质；非佩戴'),
 'MAAN':('OTT-HEJAZ-MAAN','1904','汉志铁路马安段开通纪念章；银质；非佩戴'),
 'RELIEF':('OTT-RELIEF-EXHIBITION','1897','烈士遗孤与伤残军人救济展览纪念章；镍质；非佩戴'),
 'CHELENGK-COPY':('OTT-CHELENGK','约1870年制作','宫廷赏赐羽饰复制品 / Copy；非历史原授件'),
}
merges={'CONSTITUTION':('OTT-CONSTITUTION-01','同一宪法奖章与图像版型，合并到已有实物行'),
        'WAR':('OTT-WAR-1915-01','同一1915年战争奖章家族；旧图为另一实物且绶带局部，保留已核完整馆藏图')}
unpictured={'IFT-ORDER':('OTT-IFTIHAR-ORDER','荣誉勋章，旧图下载失败；源页已核，暂入有记载未配图'),
            'IMT-ORDER':('OTT-IMTIYAZ-ORDER','伊姆提雅兹勋章，旧图下载失败；与同名圆形奖章分开') ,
            'DEPUTIES':('OTT-DEPUTIES-BADGE','议员身份徽章，归相关附编；旧图源429，暂缺本地完整图')}

assert len(set(main)|set(related)|set(merges)|set(unpictured))==len(legacy)==28
archive=ROOT/'originals/ottoman_legacy_2026-09-25';archive.mkdir(parents=True,exist_ok=True)
assets=ROOT/'assets/images/ottoman';assets.mkdir(parents=True,exist_ok=True)
related_rows=[];no_image=[];log=[]
for lead in legacy:
    key=lead['legacy_key']; original=old[key]
    page_id='legacy-page-'+key
    sources[page_id]={'page':lead['source_page'],'summary':original['variant'].replace('\n','; '),
                      'object_key':key,'accessed':'2026-09-25'}
    available=[im for im in downloads[key]['images'] if 'error' not in im]
    if key in main or key in related:
        assert available, key
        family,date,variant=(main if key in main else related)[key]
        record_id='OTT-LEG-'+key
        views=[]
        for n,im in enumerate(available):
            src=ROOT/im['path'];dest=archive/src.name;shutil.copy2(src,dest)
            asset=assets/src.name;shutil.copy2(src,asset)
            image_key='LEG-'+key+'-'+str(n+1)
            same_frame=key in {'IMT-MEDAL','AGRI-S','GRAD','MAAN','RELIEF','BOSNIA','YEMEN-I','YEMEN-II','NUSRET','HEJAZ-G','NAVAL'}
            label=('正背同图' if same_frame else ('正面' if n==0 else '背面'))
            views.append({'key':image_key,'label':label})
            meta={'key':image_key,'path':str(dest.relative_to(ROOT)).replace('\\','/'),
                  'source_page':lead['source_page'],'image_url':im['url'],
                  'description':f'{key} {label}; legacy candidate independently opened and decoded',
                  'license':'原站版权／许可待核；仅供本地研究','artist':'原站标注待核',
                  'sha256':im['sha256'],'width':im['width'],'height':im['height'],
                  'accessed':'2026-09-25'}
            manifest.append(meta)
            sources['image-'+image_key]={'page':lead['source_page'],'image_url':im['url'],
              'summary':meta['description'],'dimensions':[im['width'],im['height']],
              'sha256':im['sha256'],'accessed':'2026-09-25','license':meta['license']}
        record={'id':record_id,'family':family,'name':original['name'],
                'original':original['original'],'date':date,'variant':variant,
                'views':views,'source_ids':[page_id]+['image-'+v['key'] for v in views],
                'origin_legacy_key':key}
        if key in related: related_rows.append(record); disposition='related_gallery'
        else: cat['records'].append(record);disposition='main_gallery'
        log.append({'legacy_key':key,'disposition':disposition,'target':record_id,
                    'reason':'原对象页可访问，图片已下载并解码；分类与日期按对象页及土耳其语目录修订。',
                    'local_images':len(views)})
    elif key in merges:
        target,reason=merges[key]
        log.append({'legacy_key':key,'disposition':'merged','target':target,'reason':reason,'local_images':0})
    else:
        family,reason=unpictured[key]
        item={'legacy_key':key,'family':family,'name':original['name'],
              'original':original['original'],'date':original.get('date','待考'),
              'known_grade':original['variant'].replace('\n','；'),
              'category':'相关附编' if key=='DEPUTIES' else '主编',
              'source_ids':[page_id],'reason':reason}
        no_image.append(item)
        log.append({'legacy_key':key,'disposition':'unpictured_appendix','target':family,
                    'reason':reason,'local_images':0})

assert len({r['id'] for r in cat['records']})==len(cat['records'])
cat['records'].sort(key=lambda r:(int(re.search(r'\d{4}',r['date']).group()) if re.search(r'\d{4}',r['date']) else 9999,r['family'],r['id']))
(data/'catalogue.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding='utf-8')
(data/'related.json').write_text(json.dumps(related_rows,ensure_ascii=False,indent=2),encoding='utf-8')
(data/'unpictured.json').write_text(json.dumps(no_image,ensure_ascii=False,indent=2),encoding='utf-8')
(data/'migration_log.json').write_text(json.dumps({'as_of':'2026-09-25','baseline_verified_rows':9,
 'baseline_legacy_candidates':28,'items':log},ensure_ascii=False,indent=2),encoding='utf-8')
(data/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'image_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('main',len(cat['records']),'related',len(related_rows),'unpictured legacy',len(no_image),
      'images',len(manifest),'legacy resolved',len(log))
