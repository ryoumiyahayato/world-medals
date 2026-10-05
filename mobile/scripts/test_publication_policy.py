"""Verify restricted research facts survive export while their photos do not."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[2];out=R/'mobile/build/site'
soup=BeautifulSoup((R/'index.html').read_text(encoding='utf-8'),'html.parser')
script=(out/'catalog.js').read_text(encoding='utf-8')
catalog=json.loads(script.removeprefix('window.CATALOG=').removesuffix(';'))
rows={row['id']:row for row in catalog['rows']}
restricted=[]
for tr in soup.select('section.period-section tr[id]'):
    if tr.get('data-publication-eligible')=='false':
        assert tr['id'] in rows, 'Missing research fact record: '+tr['id']
        assert not rows[tr['id']]['photos'], 'Restricted image exported: '+tr['id']
        restricted.extend(image['src'] for image in tr.select('img[src]'))
    else:
        restricted.extend(image['src'] for image in tr.select('img[data-publication-eligible="false"]'))
provenance=json.loads((out/'image-provenance.json').read_text(encoding='utf-8'))
assert not set(restricted).intersection(provenance), 'Restricted original in package provenance'
print('Restricted research records retained without images:',sum(tr.get('data-publication-eligible')=='false' for tr in soup.select('section.period-section tr[id]')))
