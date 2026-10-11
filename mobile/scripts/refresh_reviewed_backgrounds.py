"""Refresh approved local mattes in the existing export, retaining all row IDs."""
import json
from pathlib import Path
from background_trim import load_rules
from prepare_display import prepare,material_root

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'mobile/build/site'

def refresh():
    materials=material_root(ROOT)
    mapping_path=ROOT/'mobile/build/image-provenance.json'
    mapping=json.loads(mapping_path.read_text(encoding='utf-8'))
    rules=load_rules(ROOT);captions={}
    for relative,rule in rules.items():
        if rule.get('approved') is not True:continue
        entry=mapping[relative]
        if entry['provenance'].get('image_kind')=='user_restored_reference':
            raise ValueError('Reference must remain unchanged: '+relative)
        previous=entry['src']
        processed=prepare(materials/relative,OUT,relative,False,rule)
        entry.update(src=processed['detail'],thumb=processed['thumb'],processing=processed)
        captions[previous]=(entry['src'],entry['thumb'],max(processed['sourceSize'])<768)
    path=OUT/'catalog.js';raw=path.read_text(encoding='utf-8')
    data=json.loads(raw[len('window.CATALOG='):-1])
    row_ids=[row['id'] for row in data['rows']]
    for row in data['rows']:
        for photo in row['photos']:
            if photo['src'] in captions:
                photo['src'],photo['thumb'],low=captions[photo['src']]
                if '背景已处理' not in photo['caption']:photo['caption']+=' · 背景已处理'
                if low and '低清参考' not in photo['caption']:photo['caption']+=' · 低清参考'
    assert row_ids==[row['id'] for row in data['rows']]
    path.write_text('window.CATALOG='+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';',encoding='utf-8')
    mapping_path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'image-provenance.json').write_bytes(mapping_path.read_bytes())
    report_path=ROOT/'mobile/build/export-report.json';report=json.loads(report_path.read_text())
    report.update(reviewedBackgrounds=len(captions),imageBytes=sum(p.stat().st_size for p in (OUT/'images').rglob('*.webp')))
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':refresh()
