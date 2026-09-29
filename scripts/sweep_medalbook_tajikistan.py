"""Sweep the complete public MedalBook Tajikistan order and medal catalogues."""
from __future__ import annotations
import urllib.parse
import sweep_medalbook_thailand as sweep
sweep.COUNTRY_PREFIX='/middle-east/tajikistan/';sweep.SOURCE_SLUG='tajikistan';sweep.SOURCE_SYSTEM='MedalBook Tajikistan catalogue';sweep.COUNTRY_LABEL='Tajikistan';sweep.AS_OF='2026-09-28';sweep.INDEX_URLS=[sweep.BASE+'/middle-east/tajikistan/orders',sweep.BASE+'/middle-east/tajikistan/medals-decorations'];sweep.CACHE=sweep.ROOT/'sources/pages/medalbook_tajikistan';sweep.OUT=sweep.ROOT/'data/raw_candidates/medalbook_tajikistan.jsonl';sweep.STATE=sweep.ROOT/'data/source_sweeps/medalbook_tajikistan_2026-09-28.json'
def award_item_link(href:str)->str|None:
 url=urllib.parse.urljoin(sweep.BASE,href);p=urllib.parse.urlsplit(url);prefixes=('/middle-east/tajikistan/orders/','/middle-east/tajikistan/medals-decorations/')
 if p.netloc!='www.medalbook.com' or not p.path.startswith(prefixes):return None
 if len(p.path[len(sweep.COUNTRY_PREFIX):].strip('/').split('/'))<3:return None
 return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,'',''))
sweep.item_link=award_item_link
if __name__=='__main__':sweep.main()
