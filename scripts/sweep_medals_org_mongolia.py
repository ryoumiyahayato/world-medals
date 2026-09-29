"""Recursively sweep the complete ODM / medals.org.uk Mongolia directory."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.medals.org.uk"
SOURCE_SLUG = "mongolia"
SOURCE_LABEL = "Mongolia"
INDEX = BASE + "/mongolia/mongolia-text.htm"
CACHE = ROOT / "sources/pages/medals_org_mongolia"
RAW_DIR = ROOT / "assets/raw/medals_org_mongolia"
CANDIDATES = ROOT / "data/raw_candidates/medals_org_mongolia.jsonl"
SWEEP = ROOT / "data/source_sweeps/medals_org_mongolia_2026-09-28.json"
PAGE_PATTERN = None
RECURSIVE = False


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.text=[]; self.title=""; self.in_title=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img" and a.get("src"): self.images.append(a["src"])
        if tag == "title": self.in_title=True
    def handle_endtag(self, tag):
        if tag == "title": self.in_title=False
    def handle_data(self, data):
        value=re.sub(r"\s+", " ", html.unescape(data)).strip()
        if value: self.text.append(value)
        if self.in_title and value: self.title += value


def fetch(url: str) -> bytes:
    req=urllib.request.Request(url, headers={"User-Agent":"world-medals research catalogue/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response: return response.read()


def parse(raw: bytes) -> Parser:
    p=Parser(); p.feed(raw.decode("utf-8", errors="replace")); return p


def main():
    CACHE.mkdir(parents=True, exist_ok=True); RAW_DIR.mkdir(parents=True, exist_ok=True)
    index_raw=fetch(INDEX); (CACHE/Path(urllib.parse.urlsplit(INDEX).path).name).write_bytes(index_raw); ip=parse(index_raw)
    page_pattern = PAGE_PATTERN or rf"/{re.escape(SOURCE_SLUG)}/{re.escape(SOURCE_SLUG)}\d+\.htm$"
    pages=sorted({urllib.parse.urljoin(INDEX,h) for h in ip.links if re.search(page_pattern, urllib.parse.urljoin(INDEX,h))})
    prefetched={}
    if RECURSIVE:
        queue=list(pages); discovered=set(pages)
        for url in queue:
            try:
                raw=fetch(url); cache=CACHE/Path(urllib.parse.urlsplit(url).path).name; cache.write_bytes(raw); p=parse(raw)
                prefetched[url]=(raw,p)
                for href in p.links:
                    child=urllib.parse.urljoin(url,href)
                    if re.search(page_pattern,child) and child not in discovered:
                        discovered.add(child); queue.append(child)
            except Exception:
                # The processing pass below records failures consistently.
                pass
            time.sleep(.12)
        pages=sorted(discovered)
    rows=[]; images=[]; failures=[]
    for n,url in enumerate(pages,1):
        try:
            if url in prefetched:
                raw,p=prefetched[url]
            else:
                raw=fetch(url); p=parse(raw)
            cache=CACHE/Path(urllib.parse.urlsplit(url).path).name; cache.write_bytes(raw)
            body=" ".join(p.text); title=re.sub(rf"^ODM of {re.escape(SOURCE_LABEL)}:\s*", "", p.title).strip() or p.text[0]
            instituted=(re.search(r"Instituted:\s*([^.]*(?:\.)?)", body, re.I) or [None,"Unknown"])[1].strip()
            image_urls=[]
            for src in p.images:
                image_url=urllib.parse.urljoin(url,src)
                if any(x in image_url.lower() for x in ("flag", "ribbon", "logo", "button")): continue
                image_urls.append(image_url)
            downloaded=[]
            for j,image_url in enumerate(dict.fromkeys(image_urls),1):
                try:
                    data=fetch(image_url); suffix=Path(urllib.parse.urlsplit(image_url).path).suffix.lower() or ".jpg"
                    path=RAW_DIR/f"{n:03d}_{j:02d}{suffix}"; path.write_bytes(data)
                    with Image.open(path) as im: width,height,fmt=*im.size,im.format; im.verify()
                    item={"record_index":n-1,"image_index":j,"title":title,"page_url":url,"url":image_url,"local_path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"width":width,"height":height,"format":fmt,"sha256":hashlib.sha256(data).hexdigest(),"status":"downloaded"}
                    images.append(item); downloaded.append(image_url)
                except Exception as exc: failures.append({"url":image_url,"error":repr(exc)})
            years=sorted({int(x) for x in re.findall(r"(?<!\d)(18\d{2}|19\d{2}|20\d{2})(?!\d)", body)})
            rows.append({"source_id":f"medals-org-{SOURCE_SLUG}-"+hashlib.sha1(url.encode()).hexdigest()[:16],"source_system":f"ODM / medals.org.uk {SOURCE_LABEL} directory","page_title":title,"working_name_zh":"待译","original_name":title,"english_name":title,"aliases":[],"date_candidates":years,"instituted_text":instituted,"category":"orders-decorations-medals","family_hint":re.sub(r"[^a-z0-9]+"," ",title.lower()).strip(),"grade_material_clues":body[:1500],"page_url":url,"image_page_url":url if downloaded else None,"original_image_urls":downloaded,"notes":body[:2500],"status":"RAW_CANDIDATE","cache_file":cache.relative_to(ROOT).as_posix()})
        except Exception as exc: failures.append({"url":url,"error":repr(exc)})
        time.sleep(.12)
    CANDIDATES.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")
    payload={"as_of":"2026-09-28","source_id":f"medals_org_{SOURCE_SLUG.replace('-', '_')}","status":"completed" if len(rows)==len(pages) and not failures else "partial","planned_object_pages":len(pages),"processed_object_pages":len(rows),"pictured_object_pages":sum(bool(r["original_image_urls"]) for r in rows),"downloaded_images":len(images),"failed_items":failures,"items":images,"candidate_file":CANDIDATES.relative_to(ROOT).as_posix(),"page_cache":CACHE.relative_to(ROOT).as_posix(),"image_cache":RAW_DIR.relative_to(ROOT).as_posix(),"completion_rule":f"Every award page linked by the complete {SOURCE_LABEL} text directory was fetched and every non-ribbon object image was downloaded."}
    SWEEP.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("status","planned_object_pages","processed_object_pages","pictured_object_pages","downloaded_images")},ensure_ascii=False))


if __name__ == "__main__": main()
