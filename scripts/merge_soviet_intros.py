"""Normalize isolated source summaries into the existing mobile article data."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text('utf-8-sig'))
target=R/'mobile/web/award-intros.json'
current=read('mobile/web/award-intros.json')
prior={r['award_id']:r for r in current['items']}
incoming=[]
for filename,expected in [('orders_intros.json',20),('medals_01_30_intros.json',30),('medals_31_55_intros.json',25)]:
    batch=read('data/staging/soviet_completion/'+filename)
    items=batch['items'] if isinstance(batch,dict) else batch
    assert len(items)==expected,(filename,len(items))
    if filename=='medals_01_30_intros.json':
        # Keep the institutional summary. Broad visual descriptions and research
        # caveats are not a substitute for the photographed object's caption.
        for item in items:
            if item['award_id'] not in ['USSR-MED-08','USSR-MED-10']:
                item['introduction_zh']=item['introduction_zh'][:1]
    incoming.extend(items)
assert len({r['award_id'] for r in incoming})==75
html=BeautifulSoup((R/'index.html').read_text('utf-8'),'html.parser')
rows=html.select('#soviet-union tr[id]')
for item in incoming:
    # Retain the earlier Lenin text, which also has an official-library source.
    if item['award_id']=='USSR-ORD-01':item=prior[item['award_id']]
    if item['award_id']=='USSR-ORD-03':item['introduction_zh']=item['introduction_zh'][:1]
    item['introduction_zh']=[p.replace('在困难条件下保存并击败敌军','在困难条件下保存己方实力并击败敌军') for p in item['introduction_zh']]
    item['volume_pattern']='soviet|ussr'
    names=set(item.get('match_names',[]))|{item['canonical_name_zh']}
    for row in rows:
        if row['id'].startswith(item['award_id']+'-'):
            names.add(row.select_one('td strong').get_text(' ',strip=True))
    item['match_names']=sorted(names)
    for form in item.get('variant_guidance',{}).get('period_forms',[]):
        if not form.get('period'):form['period']='时期待考'
        if 'form' not in form:
            form['form']='：'.join(x for x in [form.get('label_zh'),form.get('description_zh')] if x)
        assert form.get('form'),(item['award_id'],form)
    assert item.get('introduction_zh') and item.get('sources'),item['award_id']
    for source in item['sources']:assert source.get('url') and source.get('title'),source
    prior[item['award_id']]=item
current['items']=list(prior.values())
current['as_of']='2026-09-29'
current['status']='source-summarized; historical variants remain open to further object review'
target.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Merged 75 Soviet introductions, preserving other countries and the official-source Lenin summary.')
