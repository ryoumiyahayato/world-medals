"""Upgrade Egypt Commons rows with recovered originals and remove invalid duplicates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "data/volumes/mena_round7_2026-09-26.json"
MANIFEST = ROOT / "data/volumes/mena_round7_manifest_2026-09-26.json"
ASSET_DIR = ROOT / "assets/images/egypt_commons_batch1"


FILES = {
    "MENA7-030-FRONT": ("EGY-COMMONS-003.JPG", "https://commons.wikimedia.org/wiki/File:Grand_Cordon_of_the_Order_of_the_Nile_(Egypt)_-_Memorial_JK_-_Brasilia_-_DSC00434.JPG", "https://upload.wikimedia.org/wikipedia/commons/2/2d/Grand_Cordon_of_the_Order_of_the_Nile_%28Egypt%29_-_Memorial_JK_-_Brasilia_-_DSC00434.JPG", "Daderot", "CC0 1.0"),
    "MENA7-031-FRONT": ("EGY-COMMONS-010.jpg", "https://commons.wikimedia.org/wiki/File:(2)وسام_الجمهورية_من_الدرجة_الأولى_1977.jpg", "https://upload.wikimedia.org/wikipedia/commons/9/94/%282%29%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%AC%D9%85%D9%87%D9%88%D8%B1%D9%8A%D8%A9_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89_1977.jpg", "Nagui elnakadi", "CC BY-SA 4.0"),
    "MENA7-032-FRONT": ("EGY-COMMONS-015.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_the_Virtues_Nishan_al_Kemal_Egypt.jpg", "https://upload.wikimedia.org/wikipedia/commons/d/d7/Order_of_the_Virtues_Nishan_al_Kemal_Egypt.jpg", "Alexeinikolayevichromanov", "CC BY-SA 4.0"),
    "MENA7-190-FRONT": ("EGY-COMMONS-018.jpg", "https://commons.wikimedia.org/wiki/File:وسام_الاستحقاق_من_الدرجة_الثالثة_(1960_).jpg", "https://upload.wikimedia.org/wikipedia/commons/3/33/%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%AD%D9%82%D8%A7%D9%82_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB%D8%A9_%281960_%29.jpg", "Nagui elnakadi", "CC BY-SA 4.0"),
    "MENA7-191-FRONT": ("EGY-COMMONS-017.jpg", "https://commons.wikimedia.org/wiki/File:وسام_الاستحقاق_من_الدرجة_الثالثة_1960.jpg", "https://upload.wikimedia.org/wikipedia/commons/c/ce/%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%AD%D9%82%D8%A7%D9%82_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB%D8%A9_1960.jpg", "Nagui elnakadi", "CC BY-SA 4.0"),
    "MENA7-192-FRONT": ("EGY-COMMONS-019.jpg", "https://commons.wikimedia.org/wiki/File:وسام_الاستحقاق_من_الدرجة_الرابعة_(!).jpg", "https://upload.wikimedia.org/wikipedia/commons/e/eb/%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%AD%D9%82%D8%A7%D9%82_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%B1%D8%A7%D8%A8%D8%B9%D8%A9_%28%21%29.jpg", "Nagui elnakadi", "CC BY-SA 4.0"),
    "MENA7-198-FRONT": ("EGY-COMMONS-008.jpg", "https://commons.wikimedia.org/wiki/File:Orden_Nila.jpg", "https://upload.wikimedia.org/wikipedia/commons/b/ba/Orden_Nila.jpg", "Kei", "Public domain"),
    "MENA7-199-FRONT": ("EGY-COMMONS-013.jpg", "https://commons.wikimedia.org/wiki/File:Orden_Republike_Egipat_01.jpg", "https://upload.wikimedia.org/wikipedia/commons/1/1a/Orden_Republike_Egipat_01.jpg", "Aleksandra Đuričić", "CC BY-SA 4.0"),
    "MENA7-200-FRONT": ("EGY-COMMONS-014.jpg", "https://commons.wikimedia.org/wiki/File:Orden_Republike_Egipat_02.jpg", "https://upload.wikimedia.org/wikipedia/commons/b/b8/Orden_Republike_Egipat_02.jpg", "Aleksandra Đuričić", "CC BY-SA 4.0; Wikimedia 1920px derivative retained after original endpoint rate limit"),
    "MENA7-201-FRONT": ("EGY-COMMONS-011.jpg", "https://commons.wikimedia.org/wiki/File:وسام_الجمهورية_من_الدرجة_الأولى1977.jpg", "https://upload.wikimedia.org/wikipedia/commons/6/6a/%D9%88%D8%B3%D8%A7%D9%85_%D8%A7%D9%84%D8%AC%D9%85%D9%87%D9%88%D8%B1%D9%8A%D8%A9_%D9%85%D9%86_%D8%A7%D9%84%D8%AF%D8%B1%D8%AC%D8%A9_%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%891977.jpg", "Nagui elnakadi", "CC BY-SA 4.0"),
}

REMOVE_IDS = {
    "MENA7-ORDER-OF-THE-NILE-80279C901227",  # duplicate of dedicated Carter row
    "MENA7-ORDER-OF-THE-NILE-F75C978DF6B0",  # pendant detail only
    "MENA7-ORDER-OF-THE-NILE-B407FBD232BB",  # chain-link detail only
}

RECORD_UPDATES = {
    "MENA7-ORDER-OF-THE-NILE-1DDEAEDDA709": ("尼罗河勋章", "قلادة النيل / Order of the Nile", "1953年设立；1972年法律重定", "大绶级项圈／大绶章；纪念馆陈列完整实物正面"),
    "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT-9D30F099136D": ("埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；图示实物标注1977年", "一级星章；完整实物正面"),
    "MENA7-ORDER-OF-THE-VIRTUES-6040547D07B8": ("美德勋章（尼尚·卡迈勒）", "نيشان الكمال / Order of the Virtues", "1915年设立；共和国时期继续授予", "三级章；蝴蝶结绶带；完整实物正面"),
    "MENA7-ORDER-OF-MERIT-EGYPT-E738E47775D9": ("埃及功绩勋章", "وسام الاستحقاق / Order of Merit", "1953年设立；图示实物标注1960年", "三级章；完整实物正面"),
    "MENA7-ORDER-OF-MERIT-EGYPT-1649BD2D5521": ("埃及功绩勋章", "وسام الاستحقاق / Order of Merit", "1953年设立；图示实物标注1960年", "三级章；另一实物版型；完整实物正面"),
    "MENA7-ORDER-OF-MERIT-EGYPT-C1ABF3C730AE": ("埃及功绩勋章", "وسام الاستحقاق / Order of Merit", "1953年设立；共和国时期", "四级章；完整实物正面"),
    "MENA7-ORDER-OF-THE-NILE-093AD3FBC161": ("尼罗河勋章", "قلادة النيل / Order of the Nile", "1953年设立；1972年法律重定", "项圈；完整实物正面"),
    "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT-453923B8880C": ("埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；共和国时期", "一级套装；博物馆陈列完整实物"),
    "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT-5E696AD4E373": ("埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；共和国时期", "一级套装；博物馆陈列另一视角"),
    "MENA7-ORDER-OF-THE-REPUBLIC-EGYPT-FBC2F52EE5EC": ("埃及共和国勋章", "وسام الجمهورية / Order of the Republic", "1953年设立；图示实物标注1977年", "一级挂章；完整实物正面"),
}


def image_metadata(view_key: str, filename: str, page: str, url: str, artist: str, license_name: str) -> dict:
    path = ASSET_DIR / filename
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        dimensions = list(image.size)
    payload = path.read_bytes()
    return {
        "key": f"egypt-commons-upgrade-{view_key.lower()}",
        "view_key": view_key,
        "local_path": path.relative_to(ROOT).as_posix(),
        "source_page": page,
        "image_url": url,
        "artist": artist,
        "license": license_name,
        "dimensions": dimensions,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "decoded": True,
        "visually_checked": True,
        "download_status": "cached_complete_local_image",
    }


def main() -> None:
    volume = json.loads(VOLUME.read_text(encoding="utf-8"))
    kept = []
    for record in volume["records"]:
        if record["id"] in REMOVE_IDS:
            continue
        if record["id"] in RECORD_UPDATES:
            record["name"], record["original"], record["date"], record["variant"] = RECORD_UPDATES[record["id"]]
        kept.append(record)
    volume["records"] = kept
    VOLUME.write_text(json.dumps(volume, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["images"] = [item for item in manifest["images"] if item.get("view_key") not in FILES and item.get("view_key") not in {"MENA7-195-FRONT", "MENA7-196-FRONT", "MENA7-197-FRONT"}]
    manifest["images"].extend(image_metadata(key, *values) for key, values in FILES.items())
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"updated {len(RECORD_UPDATES)} Egypt rows; removed {len(REMOVE_IDS)} duplicate/partial rows")


if __name__ == "__main__":
    main()
