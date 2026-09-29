"""Extract the complete official Malaysian state honours precedence directory."""

from __future__ import annotations

import html
import json
import re
import urllib.request
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
URL='https://www.istiadat.gov.my/darjah-kebesaran-negeri/'
CACHE=ROOT/'sources/pages/istiadat_malaysia_states'
OUT=ROOT/'data/raw_candidates/istiadat_malaysia_states.jsonl'
STATE=ROOT/'data/source_sweeps/istiadat_malaysia_states_2026-09-28.json'
STATES={'TERENGGANU':'登嘉楼苏丹国','PERLIS':'玻璃市苏丹国','SELANGOR':'雪兰莪苏丹国','NEGERI SEMBILAN':'森美兰州','JOHOR':'柔佛苏丹国','KELANTAN':'吉兰丹苏丹国','PERAK':'霹雳苏丹国','KEDAH':'吉打苏丹国','PAHANG':'彭亨苏丹国','PULAU PINANG':'槟城州','SABAH':'沙巴州','SARAWAK':'砂拉越州','MELAKA':'马六甲州','WILAYAH PERSEKUTUAN':'联邦直辖区'}


def clean(value:str)->str:
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',value))).strip().replace('�C','—')


def main()->None:
    CACHE.mkdir(parents=True,exist_ok=True); page=CACHE/'state_honours.html'
    if page.is_file() and page.stat().st_size>100000: raw=page.read_bytes()
    else:
        request=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 world-medals-research'})
        with urllib.request.urlopen(request,timeout=90) as response: raw=response.read()
        page.write_bytes(raw)
    source=raw.decode('utf-8',errors='replace')
    markers=[m for m in re.finditer(r'<div >\s*([A-Z][A-Z ]{2,})\s*</div>',source) if m.group(1) in STATES]
    rows=[]; scope_counts={}
    for i,marker in enumerate(markers):
        state=marker.group(1); end=markers[i+1].start() if i+1<len(markers) else source.find('DASAR PRIVASI',marker.end())
        section=source[marker.end():end]
        pairs=re.findall(r'<td[^>]*data-id="([^"]+)"[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>',section,re.S)
        scope_counts[state]=len(pairs)
        for rank,(data_id,name_raw,abbr_raw) in enumerate(pairs,1):
            name,abbr=clean(name_raw),clean(abbr_raw)
            rows.append({'source_id':f"istiadat-malaysia-state-{state.lower().replace(' ','-')}-{rank:02d}",'page_title':name,'working_name_zh':'待归并','name_original':name,'name_en':None,'date_candidates':[],'category':'state_honour','grade_material_clues':f'Official precedence rank {rank}; abbreviation {abbr}','awarding_subject':STATES[state],'source_scope':state,'precedence_rank':rank,'abbreviation':abbr,'data_id':data_id,'object_url':URL+f"#{state.lower().replace(' ','-')}",'image_page_url':None,'original_images':[],'notes':'Official Malaysian state honours precedence directory; image differential pending state official sources.','status':'harvested_unpictured'})
    OUT.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows),encoding='utf-8')
    STATE.write_text(json.dumps({'as_of':'2026-09-28','source_id':'istiadat_malaysia_states','source_name':'Bahagian Istiadat — state honours precedence directory','seed_url':URL,'status':'completed','directory_pages':1,'state_or_territory_sections':len(markers),'candidate_rows':len(rows),'scope_counts':scope_counts,'downloaded_images':0,'candidate_file':OUT.relative_to(ROOT).as_posix(),'page_cache':CACHE.relative_to(ROOT).as_posix()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sections':len(markers),'candidates':len(rows),'by_scope':scope_counts},ensure_ascii=False))


if __name__=='__main__': main()
