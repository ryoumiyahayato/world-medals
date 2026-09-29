"""Retry transient ODM Pakistan image failures without rescanning the completed directory."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
from pathlib import Path

from PIL import Image
import sweep_medals_org_mongolia as helper

ROOT=Path(__file__).resolve().parents[1]
SWEEP=ROOT/"data/source_sweeps/medals_org_pakistan_2026-09-28.json"
RAW=ROOT/"data/raw_candidates/medals_org_pakistan.jsonl"
payload=json.loads(SWEEP.read_text(encoding="utf-8"))
rows=[json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
remaining=[]; recovered=[]
for failed in payload.get("failed_items",[]):
    url=failed["url"]
    try:
        data=helper.fetch(url)
        record_index=next(i for i,r in enumerate(rows) if Path(urllib.parse.urlsplit(r["cache_file"]).path).name and Path(urllib.parse.urlsplit(url).path).name in (ROOT/r["cache_file"]).read_text(encoding="utf-8",errors="ignore"))
        page=(ROOT/rows[record_index]["cache_file"]).read_bytes(); parsed=helper.parse(page)
        image_urls=[]
        for src in parsed.images:
            image_url=urllib.parse.urljoin(rows[record_index]["page_url"],src)
            if any(x in image_url.lower() for x in ("flag","ribbon","logo","button")): continue
            image_urls.append(image_url)
        image_index=list(dict.fromkeys(image_urls)).index(url)+1
        suffix=Path(urllib.parse.urlsplit(url).path).suffix.lower() or ".jpg"
        path=ROOT/f"assets/raw/medals_org_pakistan/{record_index+1:03d}_{image_index:02d}{suffix}"
        path.write_bytes(data)
        with Image.open(path) as im: width,height,fmt=*im.size,im.format; im.verify()
        item={"record_index":record_index,"image_index":image_index,"title":rows[record_index]["page_title"],"page_url":rows[record_index]["page_url"],"url":url,"local_path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"width":width,"height":height,"format":fmt,"sha256":hashlib.sha256(data).hexdigest(),"status":"downloaded"}
        payload["items"].append(item); recovered.append(item)
        if url not in rows[record_index]["original_image_urls"]: rows[record_index]["original_image_urls"].append(url)
        rows[record_index]["image_page_url"]=rows[record_index]["page_url"]
    except Exception as exc:
        remaining.append({"url":url,"error":repr(exc)})
payload["items"].sort(key=lambda x:(x["record_index"],x["image_index"]))
payload["failed_items"]=remaining
payload["downloaded_images"]=len(payload["items"])
payload["pictured_object_pages"]=sum(bool(r["original_image_urls"]) for r in rows)
payload["status"]="completed" if payload["processed_object_pages"]==payload["planned_object_pages"] and not remaining else "partial"
SWEEP.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
RAW.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")
print(json.dumps({"recovered":len(recovered),"remaining":len(remaining),"status":payload["status"]},ensure_ascii=False))
