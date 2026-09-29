"""Build the Ottoman General Service / Danube Medal record from NAM images."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "raw" / "ottoman_nam_danube"
ASSETS = ROOT / "assets" / "images" / "ottoman_nam_danube"
VOLUME = ROOT / "data" / "volumes" / "ottoman_nam_danube.json"
MANIFEST = ROOT / "data" / "volumes" / "ottoman_nam_danube_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    source_page = "https://collection.nam.ac.uk/detail.php?acc=1963-11-31-6"
    source_images = {
        "FRONT": (RAW / "77182.jpg", "danube_general_service_front.jpg", "正面完整实物照"),
        "BACK": (RAW / "77183.jpg", "danube_general_service_back.jpg", "背面完整实物照"),
    }
    views, images = [], []
    for side, (source, filename, label) in source_images.items():
        destination = ASSETS / filename
        shutil.copy2(source, destination)
        with Image.open(destination) as decoded:
            width, height = decoded.size
            decoded.verify()
        key = f"OTT-NAM-DANUBE-1854-{side}"
        views.append({"key": key, "label": label})
        images.append({
            "view_key": key,
            "local_path": destination.relative_to(ROOT).as_posix(),
            "source_id": "nam-1963-11-31-6",
            "download_status": "downloaded_original_and_decoded",
            "source_page_url": source_page,
            "source_original_url": f"https://collection.nam.ac.uk/images/960/77000-77999/{source.stem}.jpg",
            "institution": "National Army Museum, London",
            "accession_number": "NAM.1963-11-31-6",
            "license": "National Army Museum: Out of Copyright",
            "width": width,
            "height": height,
            "sha256": sha256(destination),
            "side": side.lower(),
            "visual_check": "完整绶带、悬挂结构及章体均在画面内；正背面属于同一馆藏实物",
        })
    record = {
        "id": "OTT-NAM-DANUBE-1854",
        "family": "OTT-GENERAL-SERVICE-1854",
        "country_zh": "奥斯曼帝国",
        "name": "土耳其通用服役奖章（多瑙河奖章）",
        "original": "Turkish General Service Medal / Danube Medal / Nişan-ı İftihar Madalyası",
        "date": "1853年设立；1854年型",
        "variant": "金色金属馆藏实物（材质待核）；阿卜杜勒-迈吉德一世型；完整正背面；国家陆军博物馆藏 NAM.1963-11-31-6",
        "views": views,
        "source_ids": ["nam-1963-11-31-6", "numista-337218", "tdv-madalya"],
        "image_kind": "object_photo",
        "html_eligible": True,
    }
    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "奥斯曼帝国：通用服役／多瑙河奖章馆藏实物",
        "records": [record],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source": "National Army Museum online collection, accession NAM.1963-11-31-6",
        "source_page": source_page,
        "images": images,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote 1 record and 2 complete museum object photographs")


if __name__ == "__main__":
    main()
