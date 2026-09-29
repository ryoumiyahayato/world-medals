"""Sweep the complete public MedalBook Bhutan orders/medals catalogue."""
from __future__ import annotations
import urllib.parse
import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX="/asia/bhutan/"; sweep.SOURCE_SLUG="bhutan"; sweep.SOURCE_SYSTEM="MedalBook Bhutan catalogue"; sweep.COUNTRY_LABEL="Bhutan"; sweep.AS_OF="2026-09-28"
sweep.INDEX_URLS=[sweep.BASE+"/asia/bhutan-1"]
sweep.CACHE=sweep.ROOT/"sources/pages/medalbook_bhutan"; sweep.OUT=sweep.ROOT/"data/raw_candidates/medalbook_bhutan.jsonl"; sweep.STATE=sweep.ROOT/"data/source_sweeps/medalbook_bhutan_2026-09-28.json"
def award_item_link(href:str)->str|None:
    url=urllib.parse.urljoin(sweep.BASE,href); p=urllib.parse.urlsplit(url); prefixes=("/asia/bhutan/orders/","/asia/bhutan/medals-decorations/")
    if p.netloc!="www.medalbook.com" or not p.path.startswith(prefixes): return None
    if len(p.path[len(sweep.COUNTRY_PREFIX):].strip("/").split("/"))<3: return None
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,"",""))
sweep.item_link=award_item_link
if __name__=="__main__": sweep.main()
