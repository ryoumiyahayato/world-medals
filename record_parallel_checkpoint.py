"""Refresh the local progress checkpoint from the four intake volumes."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
data=root/'data'
read=lambda path:json.loads(path.read_text(encoding='utf-8'))
ott=read(data/'catalogue.json')['records']
related=read(data/'related.json')
unpictured=read(data/'unpictured.json')
slugs=('japan_meiji','prussia_kingdom','france_third_republic')
volumes={slug:read(data/'volumes'/f'{slug}.json')['records'] for slug in slugs}
pictured=[r for rows in volumes.values() for r in rows if r.get('views')]
pending=[r for rows in volumes.values() for r in rows if not r.get('views')]
prussia_manifest=read(data/'volumes/prussia_kingdom_manifest.json')
additional_pending=len(prussia_manifest.get('unpictured_candidates',[]))
all_pictured=ott+pictured
progress={
 'as_of':'2026-09-25','volume':'Global offline HTML catalogue',
 'main_families':len({r['family'] for r in all_pictured}),
 'main_variants':len(all_pictured),
 'main_local_images':sum(len(r['views']) for r in all_pictured),
 'related_variants':len(related),
 'related_local_images':sum(len(r['views']) for r in related),
 'unpictured_documented':len(unpictured)+len(pending)+additional_pending,
 'unpictured_main_families':sum(r['category']=='主编' for r in unpictured)+len(pending)+additional_pending,
 'legacy_candidates_start':28,'legacy_migration_unresolved':0,
 'legacy_without_complete_local_image':0,
 'active_volumes':{
   'ottoman':{'families':len({r['family'] for r in ott}),'variants':len(ott),'images':sum(len(r['views']) for r in ott)},
   **{slug:{'families':len({r['family'] for r in rows if r.get('views')}),
            'variants':sum(bool(r.get('views')) for r in rows),
            'images':sum(len(r['views']) for r in rows)} for slug,rows in volumes.items()},
 },
 'next_batch':'奥斯曼继续射击、霍乱、克里特、航空奖章配图；日本明治战争纪念章；普鲁士其他国家勋章；法国第三共和国民事与战役奖章。',
 'review_items':['日本旭日章、瑞宝章具体等级；宪法纪念章金银版授予条件；明治三十三年従軍記章条例全文。',
                 '法国消防员荣誉奖章馆藏说明与1937法规年限冲突；胜利奖章私藏扫描具体版型。',
                 '普鲁士Pour le Mérite和平级照片的馆藏号未注明。'],
 'limits':['浏览器自动化安全策略阻止对本地页面进行真实浏览器视觉验收；已通过静态资源及脚本交互模拟检查，视觉验收仍未测。',
           '部分原图版权仅允许本地研究，不能据此公开发布整库。'],
}
(data/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:progress[k] for k in ('main_families','main_variants','main_local_images','unpictured_documented')})
