"""Build one precise illustrated Soviet variant per missing family from one MedalBook directory sweep."""
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
BASE = "https://www.medalbook.com"
ROOT_PATH = "/russia/russian-soviet-federative-socialist-republic-soviet-russia-1917-1991/orders"
INDEX = BASE + ROOT_PATH
CACHE = ROOT / "sources" / "pages" / "medalbook_soviet_orders"
OUT = ROOT / "assets" / "images" / "soviet_gap_round4_2026-09-26"
VOL = ROOT / "data" / "volumes"
for p in (CACHE, OUT, VOL):
    p.mkdir(parents=True, exist_ok=True)

FAMILIES = {
    "order-of-the-october-revolution": ("USSR-ORD-02", "十月革命勋章", "Орден Октябрьской Революции", "1967-10-31设立"),
    "order-of-victory": ("USSR-ORD-03", "胜利勋章", "Орден «Победа»", "1943-11-08设立"),
    "order-of-kutuzov": ("USSR-ORD-06", "库图佐夫勋章", "Орден Кутузова", "1942-07-29设立"),
    "order-of-bogdan-khmelitsky": ("USSR-ORD-07", "波格丹·赫梅利尼茨基勋章", "Орден Богдана Хмельницкого", "1943-10-10设立"),
    "order-of-alexander-nevsky": ("USSR-ORD-08", "亚历山大·涅夫斯基勋章", "Орден Александра Невского", "1942-07-29设立"),
    "order-of-ushakov": ("USSR-ORD-09", "乌沙科夫勋章", "Орден Ушакова", "1944-03-03设立"),
    "order-of-nakhimov": ("USSR-ORD-10", "纳希莫夫勋章", "Орден Нахимова", "1944-03-03设立"),
    "order-of-the-red-star": ("USSR-ORD-11", "红星勋章", "Орден Красной Звезды", "1930-04-06设立"),
    "order-of-the-patriotic-war": ("USSR-ORD-12", "卫国战争勋章", "Орден Отечественной войны", "1942-05-20设立"),
    "order-of-the-red-banner-of-labour": ("USSR-ORD-13", "劳动红旗勋章", "Орден Трудового Красного Знамени", "1928-09-07设立"),
    "order-of-friendship-of-peoples": ("USSR-ORD-14", "各族人民友谊勋章", "Орден Дружбы народов", "1972-12-17设立"),
    "order-of-the-badge-of-honour": ("USSR-ORD-15", "荣誉勋章", "Орден «Знак Почёта»", "1935-11-25设立"),
    "order-of-glory": ("USSR-ORD-16", "光荣勋章", "Орден Славы", "1943-11-08设立"),
    "order-of-maternal-glory": ("USSR-ORD-17", "母亲光荣勋章", "Орден «Материнская слава»", "1944-07-08设立"),
    "order-mother-heroine": ("USSR-ORD-18", "英雄母亲勋章", "Орден «Мать-героиня»", "1944-07-08设立"),
    "order-of-labour-glory": ("USSR-ORD-19", "劳动光荣勋章", "Орден Трудовой Славы", "1974-01-18设立"),
    "order-for-service-to-the-motherland-in-the-armed-forces-of-the-ussr-15": ("USSR-ORD-20", "在苏联武装力量中为祖国服务勋章", "Орден «За службу Родине в Вооружённых Силах СССР»", "1974-10-28设立"),
    "order-for-personal-courage": ("USSR-ORD-21", "个人英勇勋章", "Орден «За личное мужество»", "1988-12-28设立"),
}


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.meta={}
    def handle_starttag(self, tag, attrs):
        a={k:(v or "") for k,v in attrs}
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="img":
            src=a.get("src") or a.get("data-src")
            if src: self.images.append({"url":urllib.parse.urljoin(BASE,src),"alt":html.unescape(a.get("alt", ""))})
        if tag=="meta" and a.get("content"):
            key=a.get("property") or a.get("name")
            if key: self.meta[key.lower()]=html.unescape(a["content"]).strip()


def get(url):
    path=CACHE/(hashlib.sha256(url.encode()).hexdigest()+".html")
    if path.is_file(): return path.read_text(encoding="utf-8",errors="replace")
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 world-medals research catalogue"})
    with urllib.request.urlopen(req,timeout=45) as r: raw=r.read()
    text=raw.decode("utf-8",errors="replace"); path.write_text(text,encoding="utf-8"); time.sleep(.25); return text


def parse(text):
    p=Parser(); p.feed(text); return p


index=parse(get(INDEX))
all_links=sorted({urllib.parse.urljoin(BASE,x).split("?",1)[0] for x in index.links if ROOT_PATH+"/" in urllib.parse.urljoin(BASE,x)})
records=[]; images=[]; sources=[]; failures=[]
for family_slug,(family_id,name,original,date) in FAMILIES.items():
    marker=ROOT_PATH+"/"+family_slug+"/"
    candidates=[u for u in all_links if marker in u and re.search(r"-\d+$",urllib.parse.urlsplit(u).path)]
    if not candidates:
        failures.append({"family":family_id,"error":"no object link in directory"}); continue
    url=candidates[0]
    try:
        page=parse(get(url)); title=page.meta.get("og:title") or url.rsplit("/",1)[-1].replace("-"," ")
        attachment=[x for x in page.images if "/attachments/" in x["url"] and not re.search(r"ribbon|certificate|document",x["alt"],re.I)]
        attachment.sort(key=lambda x:(0 if re.search(r"obverse|front",x["alt"],re.I) else 1, -int("1000" in x["url"])))
        if not attachment: raise RuntimeError("no complete object image")
        selected=attachment[0]; direct=selected["url"]
        ext=Path(urllib.parse.urlparse(direct).path).suffix.lower()
        if ext not in {".jpg",".jpeg",".png",".webp"}: ext=".jpg"
        target=OUT/(family_id.lower()+ext)
        if not target.is_file():
            req=urllib.request.Request(direct,headers={"User-Agent":"Mozilla/5.0 world-medals research catalogue"})
            with urllib.request.urlopen(req,timeout=45) as r: target.write_bytes(r.read())
            time.sleep(.2)
        with Image.open(target) as im: im.verify()
        digest=hashlib.sha256(target.read_bytes()).hexdigest(); view=family_id+"-MB-VIEW"
        records.append({"id":family_id+"-MB-V01","family":family_id,"name":name,"original":original,"date":date,
            "variant":title+"；目录所示具体等级／版型；完整实物图；商业目录图片，仅限本地研究",
            "views":[{"key":view,"label":"完整实物图"}],"source_ids":[url,INDEX]})
        images.append({"view_key":view,"local_path":target.relative_to(ROOT).as_posix(),"source_page_url":url,"original_file_url":direct,"sha256":digest})
        sources.append({"family":family_id,"directory":INDEX,"object_page":url,"object_title":title,"image_alt":selected["alt"]})
    except Exception as exc: failures.append({"family":family_id,"url":url,"error":repr(exc)})

volume={"as_of":"2026-09-27","volume":"苏联：MedalBook整套勋章目录差集批次","scope":"处理同一苏联勋章目录的78个具体等级／版型入口；每个缺失family先编入一个明确对象页版型。","records":records,"notes":["单独绶带、证书和文件图已排除。","同一章种其他等级保留为后续variant，不重复计算family。"]}
manifest={"as_of":"2026-09-27","volume":volume["volume"],"images":images,"source_coverage":{"directory":INDEX,"directory_object_links":len(all_links),"selected_missing_families":len(records),"failures":failures}}
(VOL/"soviet_gap_round4_2026-09-26.json").write_text(json.dumps(volume,ensure_ascii=False,indent=2),encoding="utf-8")
(VOL/"soviet_gap_round4_2026-09-26_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
(VOL/"soviet_gap_round4_2026-09-26_sources.json").write_text(json.dumps({"sources":sources},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"directory_links":len(all_links),"records":len(records),"images":len(images),"failures":failures},ensure_ascii=False))
