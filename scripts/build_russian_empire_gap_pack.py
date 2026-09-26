from __future__ import annotations

import hashlib
import json
import mimetypes
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images" / "russian_empire_gap_2026-09-26"
VOL = ROOT / "data" / "volumes"
UA = "world-medals-research/1.0 (offline illustrated catalogue)"


ITEMS = [
    {
        "skip": True,
        "family": "RUS-IMP-ORD-02",
        "name": "圣亚历山大·涅夫斯基勋章",
        "original": "Орден Святого Александра Невского",
        "date": "1725年设立",
        "variants": [
            ("V01", "File:Alexander Nevskiy (2021 exhibition) 01 by shakko.jpg", "佩章；2021年展览实物照片"),
        ],
    },
    {
        "family": "RUS-IMP-ORD-03",
        "name": "圣安娜勋章",
        "original": "Орден Святой Анны",
        "date": "1735年设立；1797年列入俄罗斯帝国勋章体系",
        "variants": [
            ("V01", "File:Order of Saint Anna 1st class badge star (Russian Empire 1908-1910) - Tallinn Museum of Orders.jpg", "一级佩章与胸星；1908–1910年式；塔林勋章博物馆实物照片"),
            ("V02", "File:Order of Saint Anna 2nd class badge (Russian Empire 1797-1801) - Tallinn Museum of Orders.jpg", "二级佩章；1797–1801年式；塔林勋章博物馆实物照片"),
            ("V03", "File:Order of St. Anna, 2nd class with swords - National Museum of Finland - DSC04031.JPG", "二级加剑佩章；芬兰国家博物馆实物照片"),
        ],
    },
    {
        "family": "RUS-IMP-ORD-07",
        "name": "圣斯坦尼斯瓦夫勋章",
        "original": "Орден Святого Станислава",
        "date": "1765年设立；1831年列入俄罗斯帝国勋章体系",
        "variants": [
            ("V01", "File:Order of Saint Stanislaus, 1st class - National Museum of Finland - DSC04038.JPG", "一级佩章；芬兰国家博物馆实物照片"),
            ("V02", "File:Order of Saint Stanislaus, 2nd class with swords, 1879, Senator Hjalmar Palin - National Museum of Finland - DSC04032.JPG", "二级加剑佩章；1879年受授实物；芬兰国家博物馆照片"),
        ],
    },
    {
        "family": "RUS-IMP-ORD-08",
        "name": "圣弗拉基米尔勋章",
        "original": "Орден Святого Владимира",
        "date": "1782年设立",
        "variants": [
            ("V01", "File:Order of St. Vladimir, 2nd class, Russia, 1885, General Georg Edvard Ramsay - National Museum of Finland - DSC04036.JPG", "二级佩章；1885年受授实物；芬兰国家博物馆照片"),
            ("V02", "File:Order of St. Vladimir, 4th class, Russia, 1839, Herman Rosenberg - National Museum of Finland - DSC04034.JPG", "四级佩章；1839年受授实物；芬兰国家博物馆照片"),
        ],
    },
]


def api_image(title: str) -> dict:
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1600",
        "format": "json",
        "formatversion": "2",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    payload = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = json.load(response)
            break
        except Exception:
            if attempt == 4:
                raise
            time.sleep(4 * (attempt + 1))
    page = payload["query"]["pages"][0]
    if "missing" in page or not page.get("imageinfo"):
        raise RuntimeError(f"Commons file missing: {title}")
    return page["imageinfo"][0]


def download(url: str, path: Path) -> bytes:
    if path.exists() and path.stat().st_size >= 10_000:
        return path.read_bytes()
    data = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as response:
                data = response.read()
            break
        except Exception:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    path.write_bytes(data)
    return data


def clean_meta(meta: dict, key: str) -> str:
    value = meta.get(key, {})
    return str(value.get("value") or "").strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    VOL.mkdir(parents=True, exist_ok=True)
    records = []
    images = []
    sources = []
    idx = 0
    for item in ITEMS:
        if item.get("skip"):
            idx += len(item["variants"])
            continue
        for variant_id, title, variant in item["variants"]:
            idx += 1
            info = api_image(title)
            ext = Path(urllib.parse.urlparse(info["url"]).path).suffix.lower()
            if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                ext = mimetypes.guess_extension(info.get("mime", "")) or ".bin"
            local_name = f"rus-imp-gap-{idx:02d}{ext}"
            local_path = OUT / local_name
            image_url = info.get("thumburl") or info["url"]
            data = download(image_url, local_path)
            if len(data) < 10_000:
                raise RuntimeError(f"Downloaded file unexpectedly small: {title} ({len(data)} bytes)")
            key = f"RUS-IMP-GAP-{idx:02d}-VIEW"
            page_url = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":()'_,.-")
            meta = info.get("extmetadata", {})
            records.append(
                {
                    "id": f'{item["family"]}-{variant_id}',
                    "family": item["family"],
                    "name": item["name"],
                    "original": item["original"],
                    "date": item["date"],
                    "variant": variant,
                    "views": [{"key": key, "label": "完整图样" if "历史图样" in variant else "完整实物图"}],
                    "source_ids": [
                        "commons-orders-of-the-russian-empire-gap-sweep",
                        page_url,
                    ],
                }
            )
            image = {
                "view_key": key,
                "local_path": str(local_path.relative_to(ROOT)).replace("\\", "/"),
                "source_page": page_url,
                "direct_image_url": image_url,
                "width": info.get("width"),
                "height": info.get("height"),
                "sha256": hashlib.sha256(data).hexdigest(),
                "license": clean_meta(meta, "LicenseShortName") or "见来源页",
                "creator": clean_meta(meta, "Artist") or clean_meta(meta, "Credit") or "见来源页",
            }
            images.append(image)
            sources.append(
                {
                    "source_id": f"commons-rus-imp-gap-{idx:02d}",
                    "source_page": page_url,
                    "title": title.removeprefix("File:"),
                    "accessed": "2026-09-26",
                    "summary": variant,
                }
            )
            time.sleep(2)

    volume = {
        "as_of": "2026-09-26",
        "volume": "俄罗斯帝国：既有候选查漏包",
        "scope": "从已缓存的帝俄勋章分类候选中补录缺失章种，并按图片所示等级或形制分为版型行。",
        "records": records,
        "notes": [
            "本包不使用绶带图、勋略图、邮票、人物肖像或搜索预览。",
            "同一勋章的佩章、胸星与不同等级保留在同一family下，不重复计为独立章种。",
        ],
    }
    manifest = {
        "as_of": "2026-09-26",
        "volume": volume["volume"],
        "records_file": "data/volumes/russian_empire_gap_2026-09-26.json",
        "image_directory": "assets/images/russian_empire_gap_2026-09-26/",
        "counts": {
            "distinct_award_families": len({r["family"] for r in records}),
            "variant_rows": len(records),
            "complete_image_files": len(images),
        },
        "images": images,
    }
    (VOL / "russian_empire_gap_2026-09-26.json").write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (VOL / "russian_empire_gap_2026-09-26_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (VOL / "russian_empire_gap_2026-09-26_sources.json").write_text(json.dumps({"sources": sources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
