"""Deduplicate byte-identical source assets without merging award records."""
import filecmp, json
from collections import defaultdict
from pathlib import Path

def compact(root, out, materials):
    path=root/'mobile/build/image-provenance.json'
    mapping=json.loads(path.read_text(encoding='utf-8'))
    groups=defaultdict(list);aliases={};reused=0
    for relative,entry in sorted(mapping.items()):
        source=materials/relative
        rule=entry['processing']
        key=(source.stat().st_size,rule['status'],tuple(rule['crop']),rule['margin'])
        match=next((old for old in groups[key] if filecmp.cmp(source,materials/old,shallow=False)),None)
        if match:
            prior=mapping[match]
            for label in ('src','thumb'):
                aliases[entry[label]]=prior[label]
                entry[label]=prior[label]
            entry['processing']['detail']=prior['src'];entry['processing']['thumb']=prior['thumb']
            reused+=1
        else:groups[key].append(relative)
    catalogue=out/'catalog.js'
    raw=catalogue.read_text(encoding='utf-8')
    data=json.loads(raw[len('window.CATALOG='):-1])
    for row in data['rows']:
        for photo in row['photos']:
            for label in ('src','thumb','originalSrc'):
                if photo.get(label) in aliases:photo[label]=aliases[photo[label]]
    catalogue.write_text('window.CATALOG='+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';',encoding='utf-8')
    path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'image-provenance.json').write_bytes(path.read_bytes())
    used={entry[label] for entry in mapping.values() for label in ('src','thumb')}
    for relative in aliases:
        if relative not in used:(out/relative).unlink(missing_ok=True)
    report_path=root/'mobile/build/export-report.json'
    report=json.loads(report_path.read_text())
    report.update(reusedDuplicateAssets=reused,displayFiles=len(used),imageBytes=sum((out/item).stat().st_size for item in used))
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    from prepare_display import material_root
    root=Path(__file__).resolve().parents[2]
    compact(root,root/'mobile/build/site',material_root(root))
