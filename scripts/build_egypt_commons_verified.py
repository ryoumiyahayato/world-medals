"""Build verified Egypt Commons variants absent from the current public volume."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/volumes/egypt_commons_verified.json"
MANIFEST = ROOT / "data/volumes/egypt_commons_verified_manifest.json"

ITEMS = [
    {
        "id": "EGY-COMMONS-NILE-FOURTH-CLASS",
        "family": "MENA7-ORDER-OF-THE-NILE",
        "name": "尼罗河勋章",
        "original": "قلادة النيل / Order of the Nile",
        "date": "1953年设立；1972年法律重定",
        "variant": "四级章；皇冠悬饰；完整实物正面；低清参考",
        "view": "EGY-COMMONS-004-FRONT",
        "file": "EGY-COMMONS-004.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Order_of_the_Nile,_4th_class.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/51/Order_of_the_Nile%2C_4th_class.jpg",
        "artist": "Hsq7278",
        "license": "CC BY-SA 4.0",
    },
    {
        "id": "EGY-COMMONS-NILE-REPUBLIC-STAR",
        "family": "MENA7-ORDER-OF-THE-NILE",
        "name": "尼罗河勋章",
        "original": "قلادة النيل / Order of the Nile",
        "date": "共和国时期",
        "variant": "共和国版星章；完整实物正面；低清参考",
        "view": "EGY-COMMONS-005-FRONT",
        "file": "EGY-COMMONS-005.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Order_of_the_Nile,_star_(Republic_of_Egypt).jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Order_of_the_Nile,_star_%28Republic_of_Egypt%29.jpg",
        "artist": "Hsq7278",
        "license": "CC BY-SA 4.0",
    },
    {
        "id": "EGY-COMMONS-REPUBLIC-FIRST-CLASS-SET-1977",
        "family": "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT",
        "name": "埃及共和国勋章",
        "original": "وسام الجمهورية / Order of the Republic",
        "date": "1953年设立；图示套装标注1977年",
        "variant": "一级套装；星章、挂章与绶带同盒完整实物图",
        "view": "EGY-COMMONS-009-FRONT",
        "file": "EGY-COMMONS-009.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:(!)وسام_الجمهورية_من_الدرجة_الأولى_1977.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/33/%28%21%29%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%AC%D9%85%D9%87%D9%88%D8%B1%D9%8A%D8%A9_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89_1977.jpg",
        "artist": "Nagui elnakadi",
        "license": "CC BY-SA 4.0",
    },
]


def main() -> None:
    records = []
    images = []
    for item in ITEMS:
        path = ROOT / "assets/images/egypt_commons_batch1" / item["file"]
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            dimensions = list(image.size)
        payload = path.read_bytes()
        records.append({
            "id": item["id"], "family": item["family"], "country_zh": "埃及",
            "name": item["name"], "original": item["original"], "date": item["date"],
            "variant": item["variant"], "views": [{"key": item["view"], "label": "完整实物正面"}],
            "source_ids": [f"egypt-commons-{item['file'][12:15]}"], "image_kind": "object_photo", "html_eligible": True,
        })
        images.append({
            "key": f"egypt-commons-{item['file'][12:15]}", "record_id": item["id"], "view_key": item["view"],
            "local_path": path.relative_to(ROOT).as_posix(), "source_page": item["page"], "image_url": item["url"],
            "artist": item["artist"], "license": item["license"], "dimensions": dimensions,
            "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "decoded": True, "visually_checked": True,
        })
    OUT.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及 Commons 核验版型", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} verified Egypt variants")


if __name__ == "__main__":
    main()
