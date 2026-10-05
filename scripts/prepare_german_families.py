from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'data/staging/german_completion'
def load(n):return json.loads((D/n).read_text('utf-8'))
base=load('families_base.json');families={f['family']:f for f in base}
def sources(x):return [dict(title=s['title'],url=s['url'],summary=s.get('evidence_summary_zh',s.get('summary',''))) for s in x['sources']]
def guidance(x):return [dict(period=v['name'],form=v['period_forms']) for v in x.get('variants',[]) if isinstance(v,dict) and v.get('period_forms')]
for f in families.values():f['variant_guidance']=[g for g in f.get('variant_guidance',[]) if g.get('period') and g.get('form')]
for x in load('ordensmuseum_records.json')['items']:
 fid='GER-FED-BUNDESVERDIENSTORDEN' if x['family_id']=='GER-BUNDESVERDIENSTORDEN' else x['family_id']
 families[fid]['variant_guidance']=guidance(x)
for x in load('deutschen_federal_other_awards.json')['items']:
 families[x['family_id']]=dict(family=x['family_id'],name_zh=x['name_zh'],original=x['original'],anchor='germany-federal-republic',volume_title='德意志联邦共和国',date=x['date'],introduction_zh=x['introduction_zh'],sources=[s for s in sources(x) if '/impressum/' not in s['url']],variant_guidance=[])
same={'GER-BUNDESWEHR-EHRENZEICHEN':'GER-FED-BUNDESWEHR-EHRENZEICHEN','GER-GRUBENWEHR-EHRENZEICHEN':'GER-FED-GRUBENWEHR-EHRENZEICHEN'}
states={'BW':('baden-wuerttemberg-state','巴登-符腾堡州'),'BAV':('bavaria-state','巴伐利亚州'),'HH':('hamburg-state','汉堡自由汉萨市'),'HE':('hessen-state','黑森州'),'NRW':('north-rhine-westphalia-state','北莱茵-威斯特法伦州'),'RP':('rhineland-palatinate-state','莱茵兰-普法尔茨州'),'SH':('schleswig-holstein-state','石勒苏益格-荷尔斯泰因州')}
adjacent={'recognized_association_award','recognized_religious_order_award','federal_association_award','federal_group_award'}
extras=load('ordensmuseum_current_extra.json')
for x in extras['items']:
 fid=same.get(x['family_id'],x['family_id'])
 if fid in families:
  f=families[fid];urls={s['url'] for s in f['sources']};f['sources'] += [s for s in sources(x) if s['url'] not in urls];continue
 anchor,title=('germany-federal-republic','德意志联邦共和国')
 if x['category']=='state_rescue_award':anchor,title=states[fid.split('-')[1]]
 related=x['category'] in adjacent
 if related:anchor,title='related',x['issuer']
 f=dict(family=fid,name_zh=x['name_zh'],original=x['original'],anchor=anchor,volume_title=title,date=x['date'],introduction_zh=x['introduction_zh'],sources=sources(x),variant_guidance=guidance(x),is_related=related,category=x['category'])
 if fid=='GER-EINSATZMEDAILLE-FLUTHILFE-2002':f['name_zh']='德国2002年洪灾救援奖章'
 if fid=='GER-BW-RETTUNGSMEDAILLE':f['date']='1953年恢复授予'
 families[fid]=f
for n,x in enumerate(extras['related_candidates']):
 fid='GER-RELATED-QUALIFICATION-'+str(x['page_id']);families[fid]=dict(family=fid,name_zh=x['name_zh'],original=x['original'],anchor='related',volume_title='德国 · 体育与救生资格徽章',date='具体版型时期待考',introduction_zh=x['introduction_zh'],sources=sources(x),variant_guidance=[],is_related=True,category='qualification_badge')
families['SAX-RUE-CROWN']['introduction_zh']=families['SAX-RUE-CROWN']['introduction_zh'].replace('其章种包括','其佩戴形制包括')
(D/'families_final.json').write_text(json.dumps(list(families.values()),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Formal:',sum(not f.get('is_related') for f in families.values()),'adjacent:',sum(bool(f.get('is_related')) for f in families.values()))
