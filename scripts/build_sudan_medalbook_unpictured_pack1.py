"""Normalize the MedalBook Sudan family/grade difference set without inventing images."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/medalbook_sudan.jsonl"
VOLUME = ROOT / "data/volumes/sudan_medalbook_unpictured_pack1.json"
MANIFEST = ROOT / "data/volumes/sudan_medalbook_unpictured_pack1_manifest.json"

NEW_FAMILIES = {
    "good accomplishment medal": ("SDN-MB-GOOD-ACCOMPLISHMENT-MEDAL", "良好成就奖章", "Good Accomplishment Medal"),
    "medal for conscientious work": ("SDN-MB-CONSCIENTIOUS-WORK-MEDAL", "尽职工作奖章", "Medal for Conscientious Work"),
    "medal for meritorious service": ("SDN-MB-MERITORIOUS-SERVICE-MEDAL", "功绩服务奖章", "Medal for Meritorious Service"),
    "medal for political merit": ("SDN-MB-POLITICAL-MERIT-MEDAL", "政治功绩奖章", "Medal for Political Merit"),
    "medal of military achievement": ("SDN-MB-MILITARY-ACHIEVEMENT-MEDAL", "军事成就奖章", "Medal of Military Achievement"),
    "police distinguished service medal": ("SDN-MB-POLICE-DISTINGUISHED-SERVICE", "警察杰出服务奖章", "Police Distinguished Service Medal"),
    "police good accomplishment medal": ("SDN-MB-POLICE-GOOD-ACCOMPLISHMENT", "警察良好成就奖章", "Police Good Accomplishment Medal"),
    "sudan defence force long service and good conduct medal": ("SDN-MB-SDF-LONG-SERVICE-GOOD-CONDUCT", "苏丹防卫军长期服务与良好品行奖章", "Sudan Defence Force Long Service and Good Conduct Medal"),
    "order of duty": ("SDN-MB-ORDER-OF-DUTY", "职责勋章", "Order of Duty"),
    "order of the palm and crocodile": ("SDN-MB-ORDER-PALM-CROCODILE", "棕榈与鳄鱼勋章", "Order of the Palm and Crocodile"),
}

EXISTING_VARIANTS = {
    "long service and good conduct medal": ("MENA7-LONG-SERVICE-AND-GOOD-CONDUCT-MEDAL-FOR-POLICE", "长期服务与良好品行奖章", {"Long Service and Good Conduct Medal, for Army", "Long Service and Good Conduct Medal, for Prison"}),
    "medal for merit": ("MENA7-MEDAL-FOR-MERIT", "功绩奖章", {"Medal for Merit, II Class"}),
    "order of merit": ("MENA7-ORDER-OF-MERIT-OF-THE-SUDANESE-REPUBLIC", "苏丹共和国功绩勋章", {"Order of Merit, I Class", "Order of Merit, II Class", "Order of Merit, III Class"}),
    "order of production": ("MENA7-ORDER-OF-PRODUCTION-SUDAN", "生产功绩勋章", {"Order of Production, I Class", "Order of Production, II Class", "Order of Production, III Class"}),
    "order of science literature and the arts": ("SDN-WAWARDS-ORDER-OF-SCIENCE-AND-THE-ARTS", "科学、文学与艺术勋章", {"Order of Science, Literature, and the Arts, in Gold", "Order of Science, Literature, and the Arts, in Silver"}),
    "order of sport": ("MENA7-ORDER-OF-SPORT-IN-SILVER", "体育勋章", {"Order of Sport, in Bronze", "Order of Sport, in Gold"}),
    "order of the republic": ("MENA7-ORDER-OF-THE-REPUBLIC", "苏丹共和国勋章", {"Order of the Republic, I Class", "Order of the Republic, I Class Breast Star", "Order of the Republic, III Class", "Order of the Republic, IV Class", "Order of the Republic, V Class"}),
    "order of the two niles": ("MENA7-ORDER-OF-THE-TWO-NILES", "两尼罗河勋章", {"Order of the Two Niles, Grand Officer", "Order of the Two Niles, Grand Officer Breast Star", "Order of the Two Niles, Officer"}),
}

ZH_VARIANTS = {
    "I Class": "一等", "II Class": "二等", "III Class": "三等", "IV Class": "四等", "V Class": "五等",
    "Breast Star": "星章", "in Bronze": "铜质版", "in Gold": "金质版", "in Silver": "银质版",
    "for Army": "陆军版", "for Prison": "监狱版", "Badge": "挂章",
}

# Keep this as the authoritative unresolved set.  Entries leave this set only
# after a reviewed, complete image has been published in another Sudan volume.
PENDING_TITLES = {
    "Good Accomplishment Medal, I Class",
    "Good Accomplishment Medal, II Class",
    "Good Accomplishment Medal, III Class",
    "Medal for Political Merit",
    "Police Good Accomplishment Medal",
    "Order of Duty, I Class",
    "Order of Duty, II Class",
    "Order of Sport, in Bronze",
    "Order of the Palm and Crocodile, Badge",
    "Order of the Palm and Crocodile, Breast Star",
    "Order of the Republic, IV Class",
    "Order of the Republic, V Class",
}


def slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")


def variant_zh(title: str) -> str:
    # Test longer Roman-numeral grades first and do not let ``I Class`` match
    # the tail of ``II/III/IV Class``.
    parts = []
    for token, zh in ZH_VARIANTS.items():
        if token.startswith(("I ", "II ", "III ", "IV ", "V ")):
            if re.search(rf"(?<![IV]){re.escape(token)}", title):
                parts.append(zh)
        elif token in title:
            parts.append(zh)
    return "；".join(parts) if parts else "目录所列正式版型"


def main() -> None:
    candidates = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = []
    for row in candidates:
        if row["page_title"] not in PENDING_TITLES:
            continue
        hint = row.get("family_hint")
        if hint in NEW_FAMILIES:
            family, name, original = NEW_FAMILIES[hint]
        elif hint in EXISTING_VARIANTS and row["page_title"] in EXISTING_VARIANTS[hint][2]:
            family, name = EXISTING_VARIANTS[hint][:2]
            original = row["page_title"].split(",", 1)[0]
        else:
            continue
        title = row["page_title"]
        records.append({
            "id": f"SDN-MB-PENDING-{slug(title)}", "family": family, "country_zh": "苏丹",
            "name": f"{name}·{variant_zh(title)}", "original": title,
            "date": "制度日期待考", "variant": f"{variant_zh(title)}；有目录文字记录，暂缺完整图片",
            "views": [], "source_ids": [row["source_id"]], "image_kind": "unpictured_record", "html_eligible": True,
        })
    if len(records) != len(PENDING_TITLES):
        raise RuntimeError(f"Expected {len(PENDING_TITLES)} normalized pending variants, got {len(records)}")
    VOLUME.write_text(json.dumps({"as_of": "2026-09-27", "volume": "苏丹 MedalBook 差集（待配图）", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"as_of": "2026-09-27", "images": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} source-backed unpictured Sudan variants across {len({r['family'] for r in records})} families")


if __name__ == "__main__":
    main()
