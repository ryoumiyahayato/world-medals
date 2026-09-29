"""Formalise the already swept MedalBook Ottoman orders/medals catalogue.

This is a source-first batch: it consumes the complete cached catalogue sweep,
keeps one complete obverse/object view per accessible award page, and writes a
separate review contact sheet before the volume is admitted by site_build.py.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_ottoman.jsonl"
OUT = ROOT / "assets/images/ottoman_medalbook_pack2"
OUT.mkdir(parents=True, exist_ok=True)
UA = "world-medals-local-research/1.0 (offline catalogue)"

NAME_MAP = {
    "1st Crete Campaign Medal": ("第一次克里特战役奖章", "OTT-CRETE-1869"),
    "2nd Yemen Campaign Medal": ("第二次也门战役奖章", "OTT-YEMEN-1892"),
    "Bosnia Campaign Medal": ("波斯尼亚战役奖章", "OTT-BOSNIA-1850"),
    "Campaign Medal for Montenegro": ("黑山战役奖章", "OTT-MONTENEGRO"),
    "Commemorative Medal for the Defense of Kars": ("卡尔斯防御纪念奖章", "OTT-KARS"),
    "Commemorative Medal of Kaiser Wilhelm": ("威廉二世访问纪念奖章", "OTT-WILHELM-II-COMMEMORATIVE"),
    "Commemorative Medal of Sashaneli Tufek": ("六膛线步枪纪念奖章", "OTT-RIFLE-SHOOTING"),
    "Crimea Medal": ("克里米亚战争奖章", "OTT-CRIMEA"),
    "Defense of Kars": ("卡尔斯防御奖章", "OTT-KARS"),
    "General Service Medal": ("一般服务奖章", "OTT-GENERAL-SERVICE-1853"),
    "Greek Campaign Medal": ("希腊战役奖章", "OTT-GREEK-WAR"),
    "Hejaz Railway": ("汉志铁路奖章", "OTT-HEJAZ-RAIL"),
    "Imtiyaz Medal": ("伊姆蒂亚兹奖章", "OTT-IMTIYAZ-MEDAL"),
    "Lifesaving Medal": ("救生奖章", "OTT-LIFESAVING"),
    "Liyakat Medal": ("利亚卡特奖章", "OTT-LIYAKAT"),
    "Medal for Scutari": ("斯库台奖章", "OTT-SCUTARI-1831"),
    "Medal for the Russian Military Mission": ("许恩卡尔伊斯凯莱西条约纪念章", "OTT-HUNKAR-ISKELESI"),
    "Medal of Acre": ("阿卡战役奖章", "OTT-ACRE"),
    "Medal of Iftihar": ("伊夫蒂哈尔奖章", "OTT-IFTIHAR-MEDAL"),
    "Plevne Campaign Medal": ("普列夫纳战役奖章", "OTT-PLEVNA"),
    "Red Crescent Medal": ("红新月奖章", "OTT-RED-CRESCENT"),
    "Sanayi Medal": ("工艺功绩奖章", "OTT-SANAYI"),
    "Silistria Medal": ("锡利斯特拉奖章", "OTT-SILISTRA"),
    "Sultan's Medal for Egypt": ("苏丹埃及战役奖章", "OTT-EGYPT-1801"),
    "War Medal of 1915": ("奥斯曼战争奖章", "OTT-WAR"),
    "Order of Medjidjie": ("麦吉迪勋章", "OTT-MEDJ"),
    "Order of Nishan El Iftihar": ("伊夫蒂哈尔勋章", "OTT-IFTIHAR-ORDER"),
    "Order of Nishani-Shefkat": ("慈善勋章", "OTT-SEFKAT"),
    "Order of Osmania": ("奥斯曼勋章", "OTT-OSM"),
    "Order of the House of Osman": ("奥斯曼王室勋章", "OTT-HOUSE-OSMAN"),
}


def identity(title: str) -> tuple[str, str] | None:
    for prefix, result in NAME_MAP.items():
        if title.startswith(prefix):
            return result
    return None


def variant(title: str) -> str:
    parts = []
    for token, label in [
        ("Civil Division", "文职组"), ("Military Division", "军职组"),
        ("I Class", "一等"), ("II Class", "二等"), ("III Class", "三等"),
        ("IV Class", "四等"), ("V Class", "五等"), ("VI Class", "六等"),
        ("Breast Star", "胸星"), ("Collar", "链章"),
        ("in Gold", "金质／金色版"), ("in Silver", "银质／银色版"),
        ("in Bronze", "铜质／铜色版"), ("in Nickel", "镍质版"),
        ("Small Medal", "小型章"), ("Foreign State", "外国外授型"),
    ]:
        # Roman grades must be matched as complete tokens: otherwise every
        # "II Class" also becomes I Class and every "IV Class" becomes I Class.
        pattern = rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])" if token.endswith(" Class") else re.escape(token)
        if re.search(pattern, title, re.I):
            parts.append(label)
    return "；".join(dict.fromkeys(parts)) if parts else "目录实物所示版型"


def date_text(row: dict, family: str) -> str:
    established = {
        "OTT-MEDJ": "1852年设立；图示版型时期待考", "OTT-OSM": "1861年设立；图示版型时期待考",
        "OTT-SEFKAT": "1878年设立；图示版型时期待考", "OTT-HOUSE-OSMAN": "1893年设立；图示版型时期待考",
    }
    if family in established:
        return established[family]
    years = row.get("date_candidates") or []
    return "／".join(str(year) for year in years) if years else "制度日期待考"


def choose_url(urls: list[str]) -> str:
    obverse = [url for url in urls if re.search(r"obv|front", url, re.I)]
    candidates = obverse or [url for url in urls if not re.search(r"rev|back", url, re.I)] or urls
    return max(candidates, key=lambda url: ("/1000/" in url, len(url)))


def fetch(url: str, path: Path) -> None:
    if path.is_file():
        with Image.open(path) as image:
            image.verify()
        return
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
            path.write_bytes(data)
            return
        except Exception as exc:
            error = exc
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"download failed: {url}: {error}")


rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
records, images, failures = [], [], []
for row in rows:
    if row.get("category") not in {"orders", "medals-decorations"} or not row.get("original_image_urls"):
        continue
    found = identity(row["page_title"])
    if not found:
        continue
    name, family = found
    digest = hashlib.sha1(row["page_url"].encode()).hexdigest()[:12].upper()
    record_id = f"OMB2-{digest}"
    view_key = record_id + "-FRONT"
    url = choose_url(row["original_image_urls"])
    extension = ".png" if ".png" in url.casefold() else ".jpg"
    path = OUT / (record_id.lower() + extension)
    try:
        fetch(url, path)
        with Image.open(path) as image:
            width, height = image.size
    except Exception as exc:
        failures.append({"page_title": row["page_title"], "error": str(exc)})
        continue
    records.append({
        "id": record_id, "family": family, "country_zh": "奥斯曼帝国", "name": name,
        "original": row["page_title"], "date": date_text(row, family),
        "variant": variant(row["page_title"]) + "；完整实物图；商业目录图像，仅限本地研究",
        "views": [{"key": view_key, "label": "完整实物图"}], "source_ids": [row["source_id"]],
        "image_kind": "object_photo", "html_eligible": True,
    })
    images.append({
        "view_key": view_key, "local_path": path.relative_to(ROOT).as_posix(), "source_id": row["source_id"],
        "download_status": "downloaded_and_decoded", "source_page_url": row["page_url"],
        "source_original_url": url, "license": "MedalBook catalogue image; local research only",
        "width": width, "height": height, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    })
    time.sleep(0.35)

(ROOT / "data/volumes/ottoman_medalbook_pack2.json").write_text(
    json.dumps({"as_of": "2026-09-26", "records": records}, ensure_ascii=False, indent=2), encoding="utf-8"
)
(ROOT / "data/volumes/ottoman_medalbook_pack2_manifest.json").write_text(
    json.dumps({"as_of": "2026-09-26", "images": images, "unpictured_candidates": [], "failures": failures}, ensure_ascii=False, indent=2), encoding="utf-8"
)

# Review atlas: every admitted image appears once with its English page title.
font = ImageFont.load_default()
cell_w, cell_h, columns = 260, 230, 4
for page_index in range(0, len(records), 20):
    batch = records[page_index:page_index + 20]
    sheet = Image.new("RGB", (cell_w * columns, cell_h * 5), "white")
    draw = ImageDraw.Draw(sheet)
    for index, record in enumerate(batch):
        image_meta = next(item for item in images if item["view_key"] == record["views"][0]["key"])
        with Image.open(ROOT / image_meta["local_path"]) as source:
            source = source.convert("RGB")
            source.thumbnail((230, 180))
            x = (index % columns) * cell_w + (cell_w - source.width) // 2
            y = (index // columns) * cell_h + 4
            sheet.paste(source, (x, y))
        label = record["original"][:38]
        draw.text(((index % columns) * cell_w + 6, (index // columns) * cell_h + 188), label, fill="black", font=font)
    sheet.save(ROOT / "sources/cache" / f"ottoman_medalbook_pack2_review_{page_index // 20 + 1}.jpg", quality=88)

print(json.dumps({"records": len(records), "families": len({r['family'] for r in records}), "images": len(images), "failures": len(failures)}, ensure_ascii=False))
