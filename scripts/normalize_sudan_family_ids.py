"""Merge obvious duplicate Sudan family IDs and clean inherited raw-file titles."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/volumes/mena_round7_2026-09-26.json"

UPDATES = {
    "MENA7-ARMY-DISTINGUISHED-SERVICE-MEDAL-2-DD8F8D148508": {
        "family": "MENA7-ARMY-DISTINGUISHED-SERVICE-MEDAL",
        "name": "苏丹陆军杰出服务奖章",
        "original": "Army Distinguished Service Medal",
        "variant": "另一实物版型；完整正面；低清参考",
    },
    "MENA7-SUDAN-ORDER-OF-CIVIL-ACCOMPLISHMENT-LPM-149FB2623EEA": {
        "family": "MENA7-ORDER-OF-CIVIL-ACCOMPLISHMENT",
        "name": "苏丹民事成就勋章",
        "original": "Order of Civil Accomplishment",
        "variant": "四等；文官组；完整正面；低清参考",
    },
    "MENA7-SUDAN-ORDER-OF-THE-REPUBLIC-C1E12FEA9328": {
        "family": "MENA7-ORDER-OF-THE-REPUBLIC",
        "name": "苏丹共和国勋章",
        "original": "Order of the Republic, 2nd issue",
        "variant": "第二版；图示等级待考；完整正面；低清参考",
    },
    "MENA7-QUEEN-S-SUDAN-MEDAL-6F8B2E605E2F": {
        "name": "女王苏丹奖章",
        "original": "Queen's Sudan Medal",
        "variant": "英国王室名义的苏丹服役奖章；完整正面；低清参考",
    },
    "MENA7-ORDER-OF-REGIONAL-GOVERNMENT-B99C1E3535B5": {
        "name": "苏丹地方政府勋章",
        "original": "Order of Regional Government",
        "variant": "另一实物版型；完整正面；低清参考",
    },
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    found = set()
    for record in data["records"]:
        update = UPDATES.get(record["id"])
        if update:
            record.update(update)
            found.add(record["id"])
    missing = set(UPDATES) - found
    if missing:
        raise RuntimeError(f"Missing Sudan record IDs: {sorted(missing)}")
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"normalized {len(found)} Sudan rows; merged 3 duplicate family IDs")


if __name__ == "__main__":
    main()
