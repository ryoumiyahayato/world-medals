"""Sweep the complete public MedalBook Sri Lanka awards catalogue."""
from __future__ import annotations
import urllib.parse
import sweep_medalbook_thailand as sweep
sweep.COUNTRY_PREFIX="/asia/sri-lanka/";sweep.SOURCE_SLUG="sri_lanka";sweep.SOURCE_SYSTEM="MedalBook Sri Lanka catalogue";sweep.COUNTRY_LABEL="Sri Lanka";sweep.AS_OF="2026-09-28";sweep.INDEX_URLS=[sweep.BASE+"/asia/sri-lanka-1"];sweep.CACHE=sweep.ROOT/"sources/pages/medalbook_sri_lanka";sweep.OUT=sweep.ROOT/"data/raw_candidates/medalbook_sri_lanka.jsonl";sweep.STATE=sweep.ROOT/"data/source_sweeps/medalbook_sri_lanka_2026-09-28.json"
def award_item_link(href:str)->str|None:
 url=urllib.parse.urljoin(sweep.BASE,href);p=urllib.parse.urlsplit(url);prefixes=("/asia/sri-lanka/orders/","/asia/sri-lanka/medals-decorations/")
 if p.netloc!="www.medalbook.com" or not p.path.startswith(prefixes):return None
 if len(p.path[len(sweep.COUNTRY_PREFIX):].strip("/").split("/"))<3:return None
 return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,"",""))
sweep.item_link=award_item_link
if __name__=="__main__":sweep.main()
