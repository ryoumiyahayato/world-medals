"""Bulk-extract national award-system list pages into raw candidate queues."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import date
from pathlib import Path
import requests
from lxml import html as lxml_html

ROOT=Path(__file__).resolve().parents[1]
SCOPES={
 'saudi_arabia':('Orders, decorations, and medals of Saudi Arabia','沙特阿拉伯'),
 'jordan':('Orders, decorations, and medals of Jordan','约旦哈希姆王国'),
}
SKIP={'References','Citations','Sources','See also','External links','Recipients','Notes'}

def clean(text: str) -> str: return re.sub(r'\s+',' ',text).strip()

def main() -> None:
 p=argparse.ArgumentParser(); p.add_argument('scope',choices=SCOPES); a=p.parse_args(); page,country=SCOPES[a.scope]
 api='https://en.wikipedia.org/w/api.php'; params={'action':'parse','page':page,'prop':'text|displaytitle','format':'json','formatversion':'2'}
 response=requests.get(api,params=params,headers={'User-Agent':'world-medals-research/1.0'},timeout=60); response.raise_for_status(); payload=response.json()['parse']; html=payload['text']
 cache=ROOT/f'sources/pages/wikipedia_awards/{a.scope}.html'; cache.parent.mkdir(parents=True,exist_ok=True); cache.write_text(html,encoding='utf-8')
 tree=lxml_html.fromstring(html); rows=[]; section='Introduction'; seen=set()
 for node in tree.xpath('//h2|//h3|//h4|//tr|//li'):
  if node.tag in ('h2','h3','h4'):
   section=clean(node.text_content()).replace('[edit]','').strip(); continue
  if section in SKIP or any(section.startswith(x) for x in SKIP): continue
  if node.tag=='tr':
   cells=[clean(x.text_content()) for x in node.xpath('./th|./td')]
   if len(cells)<2 or all(not x for x in cells): continue
   text=' | '.join(cells)
  else:
   if not node.xpath('ancestor::table|ancestor::ol|ancestor::ul'): continue
   text=clean(node.text_content())
  if len(text)<4 or text in seen: continue
  if any(x in text.lower() for x in ['isbn','retrieved ','wikipedia','edit source']): continue
  seen.add(text); links=[x.get('href') for x in node.xpath('.//a[@href]') if x.get('href','').startswith('/wiki/')]
  rid=hashlib.sha1((section+'\0'+text).encode()).hexdigest()[:12]
  rows.append({'source_id':f'wikipedia-{a.scope}-{rid}','source_system':'English Wikipedia national honours list','country_zh':country,'section':section,'page_title':page,'working_name_zh':'待归并','name_original':text,'date_candidates':re.findall(r'(?<!\d)(?:1[789]\d{2}|20\d{2})(?!\d)',text),'category':'award_list_candidate','grade_material_clues':text,'object_url':'https://en.wikipedia.org/wiki/'+page.replace(' ','_'),'linked_pages':['https://en.wikipedia.org'+x for x in links],'status':'RAW_CANDIDATE','access_date':date.today().isoformat()})
 out=ROOT/f'data/raw_candidates/wikipedia_{a.scope}_award_system.jsonl'; out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 report={'source_id':f'wikipedia-{a.scope}-award-system','source_url':'https://en.wikipedia.org/wiki/'+page.replace(' ','_'),'accessed':date.today().isoformat(),'scope':'Complete current national honours list page, all award tables and lists excluding references and recipient lists.','status':'complete','raw_candidates':len(rows),'cached_page':cache.relative_to(ROOT).as_posix(),'raw_output':out.relative_to(ROOT).as_posix()}
 dest=ROOT/f'data/source_sweeps/wikipedia_{a.scope}_award_system_2026-09-28.json'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
