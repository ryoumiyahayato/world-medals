import json
import re
from pathlib import Path

p = Path(r'C:\Users\agcrf\Downloads\ottoman_catalogue_28_full_images.html')
s = p.read_text(encoding='utf-8')
print('html chars',len(s))
for m in re.finditer(r'<script([^>]*)>(.*?)</script>',s,re.S):
    print('script',m.group(1)[:100],len(m.group(2)))
m = re.search(r'<script id="catalogue-data" type="application/json">(.*?)</script>',s,re.S)
d = json.loads(m.group(1))
print('keys',list(d))
print('records',len(d['records']))
print('media',[(x['key'],x['name'],x.get('media')) for x in d['records']])
print('other',[(k,type(v).__name__,len(v) if hasattr(v,'__len__') else 0) for k,v in d.items() if k!='records'])
print('entry first',[(k,len(v),v[:35]) for k,v in list(d['entries'].items())[:4]])
print('image entries',[(k,len(v)) for k,v in d['entries'].items() if k.startswith('xl/media/')])
print('html lines',[(i+1,line[:200]) for i,line in enumerate(s.splitlines()) if i<14 or 'const ' in line or 'function render' in line][:30])
