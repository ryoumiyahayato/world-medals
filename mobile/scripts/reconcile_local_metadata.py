"""Associate supplied names with existing families; never infer variant identity."""
import json,re,unicodedata
from collections import Counter
from pathlib import Path
from prepare_display import material_root

ROOT=Path(__file__).resolve().parents[2]

def normalized(name):
    name=re.sub(r'[（(].*?[)）]','',name)
    return re.sub(r'[\W_]','',unicodedata.normalize('NFKC',name)).casefold()

def reconcile():
    local=material_root(ROOT)/'我搜索到的东西/metadata.json'
    if not local.exists():
        print(json.dumps({'metadataAssociations':'skipped','reason':'External materials have no optional Chinese metadata'}))
        return
    metadata={item['id']:item for item in json.loads(local.read_text(encoding='utf-8'))}
    raw=(ROOT/'mobile/build/site/catalog.js').read_text(encoding='utf-8')
    catalogue=json.loads(raw[len('window.CATALOG='):-1])
    titles={volume['id']:volume['title'] for volume in catalogue['volumes']}
    pending_path=ROOT/'mobile/build/pending-review.json'
    resolution_path=ROOT/'data/display_images/material_resolutions.json'
    resolutions=json.loads(resolution_path.read_text(encoding='utf-8'))['candidates'] if resolution_path.exists() else {}
    pending=json.loads(pending_path.read_text(encoding='utf-8')) if pending_path.exists() else {
        'unmatchedMetadata':json.loads((ROOT/'mobile/build/material-inventory.json').read_text(encoding='utf-8'))['unmatchedMetadata']}
    matches=[]
    for candidate in pending['unmatchedMetadata']:
        if candidate['candidateId'] not in metadata:
            continue
        supplied=metadata[candidate['candidateId']]
        reviewed=resolutions.get(candidate['candidateId'])
        if reviewed:
            candidate.update(reviewed)
            if reviewed.get('family'):
                candidate['existingFamily']=reviewed['family']
                candidate['candidateRows']=reviewed.get('catalogueRows') or [r['id'] for r in catalogue['rows'] if r['family']==reviewed['family']]
                matches.append(dict(candidateId=candidate['candidateId'],family=reviewed['family'],
                    rows=candidate['candidateRows'],source=reviewed['sourcePage'],status=reviewed['status']))
            else:
                candidate.pop('existingFamily',None);candidate.pop('candidateRows',None)
            continue
        rows=[row for row in catalogue['rows'] if normalized(row['name'])==normalized(supplied['name_zh'])
              and supplied['country'] in titles.get(row['volume'],'')]
        families=sorted({row['family'] for row in rows})
        if len(families)==1:
            candidate['status']='existing-family-variant-review-required'
            candidate['existingFamily']=families[0]
            candidate['candidateRows']=[row['id'] for row in rows]
            matches.append(dict(candidateId=candidate['candidateId'],family=families[0],
                                rows=candidate['candidateRows'],source='supplied name and existing country-scoped catalogue names',
                                status='Family name association only; grade, period and object identity remain unconfirmed'))
    pending['metadataFamilyMatches']=matches
    pending_path.write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'mobile/build/material-associations.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'metadataCandidates':len(pending['unmatchedMetadata']),'existingFamilyAssociations':len(matches),
                      'candidatesWithoutFamilyAssociation':len(pending['unmatchedMetadata'])-len(matches),
                      'reviewedStatusCounts':dict(Counter(resolutions[c['candidateId']]['status'] for c in pending['unmatchedMetadata'] if c['candidateId'] in resolutions)),
                      'newAwardsCreated':0}))

if __name__=='__main__':reconcile()
