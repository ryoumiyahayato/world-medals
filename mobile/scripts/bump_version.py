"""Run once per delivered update, not once per build attempt."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'version.json'
v=json.loads(p.read_text(encoding='utf-8'))
v['code']+=1
major,minor=divmod(v['code'],1000)
v['name']=f'{major}.{minor:03d}'
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'v{v["name"]} ({v["channel"]})')
