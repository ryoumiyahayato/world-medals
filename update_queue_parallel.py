"""Idempotent global navigation updates for the first parallel volumes."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
path=root/'data/global_queue.json'
data=json.loads(path.read_text(encoding='utf-8'))
for continent in data['continents']:
    if continent['name']=='欧洲':
        for region in continent['regions']:
            if region['name']=='西欧':
                for system in region['systems']:
                    if system['name']=='法国':
                        period={'name':'第三共和国（1870–1940）','periods':[]}
                        if period not in system['periods']:system['periods'].append(period)
            if region['name']=='中欧':
                system={'name':'普鲁士王国（1701–1918）','periods':[]}
                if system not in region['systems']:
                    at=next((i for i,x in enumerate(region['systems']) if x['name']=='德国／德意志地区'),len(region['systems']))
                    region['systems'].insert(at+1,system)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('global queue updated')
