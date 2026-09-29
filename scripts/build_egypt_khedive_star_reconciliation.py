"""Reconcile the OMSA Bronze Star candidate with the Khedive's Bronze Star family."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "assets/raw/egypt_awm_khedive_star"
IMAGE_DIR = ROOT / "assets/images/egypt_khedive_star"
VOLUME = ROOT / "data/volumes/egypt_khedive_star_reconciled.json"
MANIFEST = ROOT / "data/volumes/egypt_khedive_star_reconciled_manifest.json"
CROSSWALK = ROOT / "data/normalized/egypt_omsa_family_crosswalk_2026-09-27.json"
RAW_CANDIDATES = ROOT / "data/raw_candidates/egypt_khedive_star_reconciliation.jsonl"
SWEEP = ROOT / "data/source_sweeps/awm_khedive_star_2026-09-27.json"

FAMILY = "MENA7-KHEDIVE-S-STAR"


def image_entry(*, key: str, record_id: str, view_key: str, path: Path,
                source_page: str, image_url: str, artist: str, license_note: str) -> dict:
    with Image.open(path) as image:
        dimensions = list(image.size)
        image.verify()
    return {
        "key": key,
        "record_id": record_id,
        "view_key": view_key,
        "local_path": path.relative_to(ROOT).as_posix(),
        "source_page": source_page,
        "image_url": image_url,
        "artist": artist,
        "license": license_note,
        "dimensions": dimensions,
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "decoded": True,
        "visually_checked": True,
    }


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    awm_front = IMAGE_DIR / "khedive_star_1884_86_front.jpg"
    awm_reverse = IMAGE_DIR / "khedive_star_1884_86_reverse.jpg"
    shutil.copy2(RAW_DIR / "awm_RELAWM14684_3847716.jpg", awm_front)
    shutil.copy2(RAW_DIR / "awm_RELAWM14684_3847715.jpg", awm_reverse)

    records = [
        {
            "id": "EGY-KHEDIVE-STAR-1882-OBVERSE",
            "family": FAMILY,
            "country_zh": "埃及",
            "name": "赫迪夫青铜星章",
            "original": "Khedive's Egyptian Star 1882",
            "date": "1882年型",
            "variant": "1882年型；青铜；完整正面；低清参考",
            "views": [{"key": "EGY-KHEDIVE-STAR-1882-V1", "label": "完整正面"}],
            "source_ids": ["commons_egypt_awards", "nam_khedive_star_1882"],
            "image_kind": "object_photo",
            "html_eligible": True,
            "supersedes_id": "MENA7-KHEDIVE-S-STAR-2FD1A0CB6779",
        },
        {
            "id": "EGY-KHEDIVE-STAR-1884-86-AWM",
            "family": FAMILY,
            "country_zh": "埃及",
            "name": "赫迪夫青铜星章",
            "original": "Khedive's Bronze Star",
            "date": "1884—1886年型；约1886年制作",
            "variant": "1884—1886年型；青铜；Henry Jenkins & Sons（伯明翰）；完整正反面",
            "views": [
                {"key": "EGY-KHEDIVE-STAR-1884-86-V1", "label": "完整正面"},
                {"key": "EGY-KHEDIVE-STAR-1884-86-V2", "label": "完整反面"},
            ],
            "source_ids": ["awm_khedive_star_1884_86", "omsa_egypt_awards_appendix"],
            "image_kind": "object_photo",
            "html_eligible": True,
            "supersedes_id": "MENA7-KHEDIVE-S-STAR-BE6E7592741B",
        },
        {
            "id": "EGY-KHEDIVE-STAR-TOKAR-BAR",
            "family": FAMILY,
            "country_zh": "埃及",
            "name": "赫迪夫青铜星章",
            "original": "Khedive's Star, Tokar bar",
            "date": "1880年代；版次待考",
            "variant": "托卡尔横条型；青铜星章；完整正面；低清参考",
            "views": [{"key": "EGY-KHEDIVE-STAR-TOKAR-V1", "label": "完整正面"}],
            "source_ids": ["commons_egypt_awards"],
            "image_kind": "object_photo",
            "html_eligible": True,
            "supersedes_id": "MENA7-KHEDIVE-S-STAR-1C075D62D222",
        },
    ]

    images = [
        image_entry(
            key="egypt-khedive-star-1882-obverse",
            record_id=records[0]["id"],
            view_key="EGY-KHEDIVE-STAR-1882-V1",
            path=ROOT / "assets/images/mena_round7/core7-2fd1a0cb6779.png",
            source_page="https://commons.wikimedia.org/wiki/File:Khedives_Star_Obverse.jpg",
            image_url="https://upload.wikimedia.org/wikipedia/commons/c/c5/Khedives_Star_Obverse.jpg",
            artist="Helensq / Wikimedia Commons",
            license_note="CC BY-SA 4.0",
        ),
        image_entry(
            key="egypt-khedive-star-1884-86-awm-front",
            record_id=records[1]["id"],
            view_key="EGY-KHEDIVE-STAR-1884-86-V1",
            path=awm_front,
            source_page="https://www.awm.gov.au/collection/C134468",
            image_url="https://s3-ap-southeast-2.amazonaws.com/awm-media/collection/RELAWM14684/screen/3847716.JPG",
            artist="Australian War Memorial, RELAWM14684",
            license_note="Australian War Memorial collection image; retained for offline research catalogue",
        ),
        image_entry(
            key="egypt-khedive-star-1884-86-awm-reverse",
            record_id=records[1]["id"],
            view_key="EGY-KHEDIVE-STAR-1884-86-V2",
            path=awm_reverse,
            source_page="https://www.awm.gov.au/collection/C134468",
            image_url="https://s3-ap-southeast-2.amazonaws.com/awm-media/collection/RELAWM14684/screen/3847715.JPG",
            artist="Australian War Memorial, RELAWM14684",
            license_note="Australian War Memorial collection image; retained for offline research catalogue",
        ),
        image_entry(
            key="egypt-khedive-star-tokar-bar",
            record_id=records[2]["id"],
            view_key="EGY-KHEDIVE-STAR-TOKAR-V1",
            path=ROOT / "assets/images/mena_round7/core7-1c075d62d222.png",
            source_page="https://commons.wikimedia.org/wiki/File:Khedives_star,_Tokar_bar.jpg",
            image_url="https://upload.wikimedia.org/wikipedia/commons/b/bf/Khedives_star%2C_Tokar_bar.jpg",
            artist="Helensq / Wikimedia Commons",
            license_note="CC BY-SA 4.0",
        ),
    ]

    VOLUME.write_text(json.dumps({
        "as_of": "2026-09-27",
        "volume": "埃及赫迪夫青铜星章版型校订",
        "records": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": images}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    CROSSWALK.write_text(json.dumps({
        "as_of": "2026-09-27",
        "scope": "OMSA Egypt appendix family reconciliation",
        "mappings": [{
            "source_candidate": "EGY-OMSA-BRONZE-STAR",
            "source_name": "Bronze Star",
            "normalized_family": FAMILY,
            "normalized_name_zh": "赫迪夫青铜星章",
            "status": "MERGED_EXISTING_FAMILY",
            "reason": "OMSA's 1882, 1884 and 1886 versions are dated issues of the Khedive's Bronze Star, not a separate Egyptian award family.",
            "evidence_sources": ["omsa_egypt_awards_appendix", "awm_khedive_star_1884_86", "nam_khedive_star_1882"],
        }],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    raw_rows = [
        {
            "source_id": "awm_khedive_star_1884_86",
            "page_title": "Khedive's Star",
            "working_name_zh": "赫迪夫青铜星章",
            "original_names": ["Khedive's Star", "Khedive's Bronze Star"],
            "date_candidates": [1884, 1886],
            "category": "campaign medal",
            "grade_material_clues": "Bronze; Henry Jenkins & Sons; Birmingham; c.1886",
            "object_page_url": "https://www.awm.gov.au/collection/C134468",
            "image_page_urls": ["https://www.awm.gov.au/collection/C134468"],
            "original_image_urls": [images[1]["image_url"], images[2]["image_url"]],
            "notes": "The museum catalogue explicitly describes the 1884-6 obverse and crowned TM reverse.",
            "status": "NORMALIZED_AND_PICTURED",
        },
        {
            "source_id": "nam_khedive_star_1882",
            "page_title": "Khedive's Egyptian Star 1882-91",
            "working_name_zh": "赫迪夫青铜星章",
            "original_names": ["Khedive's Egyptian Star 1882-91"],
            "date_candidates": [1882],
            "category": "foreign award / campaign medal",
            "grade_material_clues": "Bronze; obverse inscription Egypt 1882",
            "object_page_url": "https://collection.nam.ac.uk/detail.php?acc=1996-08-172-7",
            "image_page_urls": [],
            "original_image_urls": [],
            "notes": "Institutional catalogue supports the 1882 dated issue; the formal row uses a separately licensed Commons object photograph.",
            "status": "NORMALIZED_WITH_SEPARATE_IMAGE_SOURCE",
        },
    ]
    RAW_CANDIDATES.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in raw_rows), encoding="utf-8")
    SWEEP.write_text(json.dumps({
        "as_of": "2026-09-27",
        "source_id": "awm_khedive_star_1884_86",
        "status": "completed_bounded_object",
        "boundary": "AWM object C134468 and both downloadable image pages",
        "object_pages_processed": 1,
        "image_pages_processed": 2,
        "images_downloaded_and_decoded": 2,
        "formal_rows_added": 1,
        "formal_views_added": 2,
        "result": "Exact 1884-6 obverse and reverse promoted; maker, material and c.1886 production data retained.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("built 3 corrected Khedive's Bronze Star variants and 4 complete local views")


if __name__ == "__main__":
    main()
