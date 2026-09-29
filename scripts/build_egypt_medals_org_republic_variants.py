"""Build explicit Republic of Egypt class/type rows from the completed catalogue sweep."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets/raw/medals_org_egypt_republic"
OUT = ROOT / "assets/images/egypt_medals_org_republic"
VOLUME = ROOT / "data/volumes/egypt_medals_org_republic_variants.json"
MANIFEST = ROOT / "data/volumes/egypt_medals_org_republic_variants_manifest.json"

# suffix, family, name, original, date, variant, source page number, image suffixes
SPECS = [
    ("LABOUR-CLASS-3", "EGY-MEDALS-ORG-ORDER-LABOUR", "劳动勋章", "Order of Labour", "1966年设立", "三级；完整实物正面；低清参考", "009", [("05", "完整正面")]),
    ("MILITARY-COURAGE-CLASS-1", "EGY-GAP-MILITARY-COURAGE", "军事勇气奖章", "Military Medal of Courage", "1959年7月9日设立", "一等金质奖章；完整正反面；低清参考", "016", [("01", "完整正面"), ("02", "完整反面")]),
    ("MILITARY-COURAGE-CLASS-2", "EGY-GAP-MILITARY-COURAGE", "军事勇气奖章", "Military Medal of Courage", "1959年7月9日设立", "二等银质奖章；完整正反面；低清参考", "016", [("03", "完整正面"), ("04", "完整反面")]),
    ("MILITARY-COURAGE-CLASS-3", "EGY-GAP-MILITARY-COURAGE", "军事勇气奖章", "Military Medal of Courage", "1959年7月9日设立", "三等铜质奖章；完整正反面；低清参考", "016", [("05", "完整正面"), ("06", "完整反面")]),
    ("MERIT-MEDAL-CLASS-1", "EGY-WAWARDS-MEDAL-OF-MERIT", "功绩奖章", "Medal for Merit", "1953年设立", "一等金质奖章；完整正反面；低清参考", "018", [("01", "完整正面"), ("02", "完整反面")]),
    ("MERIT-MEDAL-CLASS-2", "EGY-WAWARDS-MEDAL-OF-MERIT", "功绩奖章", "Medal for Merit", "1953年设立", "二等银质奖章；完整正反面；低清参考", "018", [("03", "完整正面"), ("04", "完整反面")]),
    ("MERIT-MEDAL-CLASS-3", "EGY-WAWARDS-MEDAL-OF-MERIT", "功绩奖章", "Medal for Merit", "1953年设立", "三等铜质奖章；完整正反面；低清参考", "018", [("05", "完整正面"), ("06", "完整反面")]),
    ("MOBILISATION-CLASS-1", "EGY-GAP-MOBILISATION", "动员奖章", "Mobilisation Medal", "1953年设立", "一等；完整正反面；低清参考", "019", [("01", "完整正面"), ("02", "完整反面")]),
    ("MOBILISATION-CLASS-2", "EGY-GAP-MOBILISATION", "动员奖章", "Mobilisation Medal", "1953年设立", "二等；完整正反面；低清参考", "019", [("03", "完整正面"), ("04", "完整反面")]),
    ("MOBILISATION-CLASS-3", "EGY-GAP-MOBILISATION", "动员奖章", "Mobilisation Medal", "1953年设立", "三等；完整正反面；低清参考", "019", [("05", "完整正面"), ("06", "完整反面")]),
    ("MILITARY-DUTY-CLASS-1", "EGY-GAP-MILITARY-DUTY", "军事职责奖章", "Medal of Military Duty", "1953年7月9日设立", "一等金质奖章；目录所示型；完整正反面；低清参考", "020", [("01", "完整正面"), ("02", "完整反面")]),
    ("MILITARY-DUTY-CLASS-2", "EGY-GAP-MILITARY-DUTY", "军事职责奖章", "Medal of Military Duty", "1953年7月9日设立", "二等银质奖章；目录所示型；完整正反面；低清参考", "020", [("03", "完整正面"), ("04", "完整反面")]),
    ("MILITARY-DUTY-CLASS-3", "EGY-GAP-MILITARY-DUTY", "军事职责奖章", "Medal of Military Duty", "1953年7月9日设立", "三等铜质奖章；目录所示型；完整正反面；低清参考", "020", [("05", "完整正面"), ("06", "完整反面")]),
    ("DISTINGUISHED-SERVICE-TYPE-4", "EGY-MEDALS-ORG-DISTINGUISHED-SERVICE", "杰出服务奖章", "Medal of Distinguished Service", "1972年设立；1984年起四型", "四型（1984年至今）；完整正反面；低清参考", "031", [("07", "完整正面"), ("08", "完整反面")]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    manifest = []
    for suffix, family, name, original, date, variant, page_no, view_specs in SPECS:
        record_id = f"EGY-MEDALS-ORG-REP-{suffix}"
        views = []
        for number, (image_no, label) in enumerate(view_specs, 1):
            source_name = f"egypt-republic{page_no}_egypt-republic{page_no}-{image_no}.jpg"
            source = RAW / source_name
            target = OUT / f"{suffix.lower()}-{number:02d}.jpg"
            shutil.copyfile(source, target)
            with Image.open(target) as image:
                image.verify()
            with Image.open(target) as image:
                dimensions = list(image.size)
            payload = target.read_bytes()
            view_key = f"{record_id}-V{number}"
            views.append({"key": view_key, "label": label})
            manifest.append({
                "key": f"egypt-medals-org-rep-{suffix.lower()}-{number:02d}", "record_id": record_id,
                "view_key": view_key, "local_path": target.relative_to(ROOT).as_posix(),
                "source_page": f"https://medals.org.uk/egypt/egypt-republic/egypt-republic{page_no}.htm",
                "image_url": f"https://medals.org.uk/egypt/egypt-republic/images/egypt-republic{page_no}-{image_no}.jpg",
                "artist": "Medals of the World", "license": "Rights status not stated; retained for offline research catalogue",
                "dimensions": dimensions, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                "decoded": True, "visually_checked": True,
            })
        records.append({
            "id": record_id, "family": family, "country_zh": "埃及", "name": name, "original": original,
            "date": date, "variant": variant, "views": views, "source_ids": ["medals_org_egypt_republic"],
            "image_kind": "object_photo", "html_eligible": True,
        })
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "埃及共和国明确等级与时期型差集", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} Republic of Egypt class/type rows and {len(manifest)} complete local views")


if __name__ == "__main__":
    main()
