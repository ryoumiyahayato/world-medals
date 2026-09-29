"""Sweep the complete public MedalBook Kazakhstan awards catalogue."""
from __future__ import annotations
import urllib.parse
import sweep_medalbook_thailand as sweep
sweep.COUNTRY_PREFIX="/asia/kazakhstan/";sweep.SOURCE_SLUG="kazakhstan";sweep.SOURCE_SYSTEM="MedalBook Kazakhstan catalogue";sweep.COUNTRY_LABEL="Kazakhstan";sweep.AS_OF="2026-09-28";sweep.INDEX_URLS=[sweep.BASE+"/asia/kazakhstan-1"];sweep.CACHE=sweep.ROOT/"sources/pages/medalbook_kazakhstan";sweep.OUT=sweep.ROOT/"data/raw_candidates/medalbook_kazakhstan.jsonl";sweep.STATE=sweep.ROOT/"data/source_sweeps/medalbook_kazakhstan_2026-09-28.json"
def award_item_link(href:str)->str|None:
 url=urllib.parse.urljoin(sweep.BASE,href);p=urllib.parse.urlsplit(url);prefixes=("/asia/kazakhstan/orders/","/asia/kazakhstan/medals-decorations/")
 if p.netloc!="www.medalbook.com" or not p.path.startswith(prefixes):return None
 if len(p.path[len(sweep.COUNTRY_PREFIX):].strip("/").split("/"))<3:return None
 return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,"",""))
sweep.item_link=award_item_link
if __name__=="__main__":sweep.main()
