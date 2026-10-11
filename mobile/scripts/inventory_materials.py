"""Match material paths and existing IDs; unresolved names never create awards."""
import json, filecmp
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from prepare_display import material_root

ROOT=Path(__file__).resolve().parents[2]

def inventory():
    materials=material_root(ROOT)
    data=json.loads((ROOT/'data/release-input.json').read_text(encoding='utf-8'))
    mapping=defaultdict(list)
    missing_rows=[]
    for row,cells in data['rows'].items():
        images=BeautifulSoup(cells[2],'html.parser').select('img[src]')
        if not images:missing_rows.append(row)
        for im in images:mapping[im['src']].append(row)
    chinese=materials/'我搜索到的东西'
    metadata=chinese/'metadata.json'
    chinese_mapping={}
    candidates=[]
    if metadata.exists():
        for record in json.loads(metadata.read_text(encoding='utf-8')):
            ids=[record['id']] if record.get('id') in data['rows'] else []
            for relative in record.get('images',[]):
                key='我搜索到的东西/'+relative.replace('\\','/')
                chinese_mapping[key]=ids
            if not ids:candidates.append({'candidateId':record.get('id'),'name':record.get('name_zh'),'status':'identity-review-required'})
    files=sorted({p for base in ('assets/images','assets/raw','assets/processed','originals','我搜索到的东西')
                  for p in (materials/base).rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff')})
    def inspect(path):
        relative=path.relative_to(materials).as_posix()
        result={'file':relative,'rows':mapping.get(relative,chinese_mapping.get(relative,[])),'bytes':path.stat().st_size}
        try:
            with Image.open(path) as im:
                im.load();result['size']=im.size
            result['status']='mapped' if result['rows'] else 'identity-review-required'
        except (OSError,ValueError,Image.DecompressionBombError) as error:result['status']='decode-failed';result['error']=str(error)
        return result
    with ThreadPoolExecutor(max_workers=8) as pool:items=list(pool.map(inspect,files))
    # Byte comparison within identical file sizes; no hashes or fingerprints.
    groups=defaultdict(list);duplicates=[]
    for item in items:
        representatives=groups[item['bytes']]
        match=next((old for old in representatives if filecmp.cmp(materials/item['file'],materials/old,shallow=False)),None)
        if match:duplicates.append({'file':item['file'],'sameBytesAs':match})
        else:representatives.append(item['file'])
    result={'files':items,'exactByteDuplicates':duplicates,'unmatchedMetadata':candidates,'rowsWithoutPhotos':missing_rows,
            'missingReferencedFiles':[key for key in mapping if not (materials/key).is_file()],
            'policy':'Existing row IDs and explicit paths only. Resolution alone does not approve a replacement. No new awards or versions merged.'}
    path=ROOT/'mobile/build/material-inventory.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'localImages':len(items),'mappedFiles':sum(bool(i['rows']) for i in items),'duplicates':len(duplicates),
                      'unresolvedFiles':sum(i['status']=='identity-review-required' for i in items),'decodeFailed':sum(i['status']=='decode-failed' for i in items),
                      'unmatchedMetadata':len(candidates),'rowsWithoutPhotos':len(missing_rows),'missingReferencedFiles':len(result['missingReferencedFiles'])}))

if __name__=='__main__':inventory()
