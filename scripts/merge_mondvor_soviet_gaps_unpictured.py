"""Merge verified Mondvor family gaps into the unpictured appendix.

The source pages are fully cached and title-crosswalked, but Mondvor's reuse
notice requires permission for its object photographs.  Consequently these
families are registered as text-supported/unpictured rather than embedded in
the public three-column catalogue.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/mondvor_soviet_crosswalk_2026-09-29.jsonl"
UNPICTURED = ROOT / "data/unpictured.json"
NORMALIZED = ROOT / "data/normalized/mondvor_soviet_unpictured_gap_merge_2026-09-29.json"


MAPPING = {
    "За отличную службу по охране общ. порядка": (
        "USSR-MED-PUBLIC-ORDER-SERVICE",
        "维护公共秩序优异服务奖章",
        "1950-11-01",
        "正式奖章；1960年修订章体说明；具体版型待考",
    ),
    'Медаль "Золотая Звезда"': (
        "USSR-HERO-GOLD-STAR",
        "苏联英雄金星奖章",
        "1939-08-01",
        "苏联英雄称号佩章；金星奖章；具体版型待考",
    ),
    'Золотая медаль "Серп и Молот"': (
        "USSR-SOCIALIST-LABOUR-HAMMER-SICKLE",
        "社会主义劳动英雄锤子与镰刀金质奖章",
        "1940-05-22",
        "社会主义劳动英雄称号佩章；金质奖章；具体版型待考",
    ),
    "«Народный архитектор СССР»": (
        "USSR-TITLE-PEOPLES-ARCHITECT",
        "苏联人民建筑师荣誉称号佩章",
        "1967-08-12",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Народный учитель СССР»": (
        "USSR-TITLE-PEOPLES-TEACHER",
        "苏联人民教师荣誉称号佩章",
        "1977-12-30",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный штурман-испытатель СССР»": (
        "USSR-TITLE-HONOURED-TEST-NAVIGATOR",
        "苏联功勋试飞领航员荣誉称号佩章",
        "1958-08-14",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный пилот СССР»": (
        "USSR-TITLE-HONOURED-PILOT",
        "苏联功勋飞行员荣誉称号佩章",
        "1965-09-30",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный работник сельского хозяйства СССР»": (
        "USSR-TITLE-HONOURED-AGRICULTURAL-WORKER",
        "苏联功勋农业工作者荣誉称号佩章",
        "1982-05-31",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный парашютист-испытатель СССР»": (
        "USSR-TITLE-HONOURED-TEST-PARACHUTIST",
        "苏联功勋试验跳伞员荣誉称号佩章",
        "1984-07-13",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный мелиоратор СССР»": (
        "USSR-TITLE-HONOURED-LAND-RECLAMATION-WORKER",
        "苏联功勋土地改良工作者荣誉称号佩章",
        "1984-10-26",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный конструктор СССР»": (
        "USSR-TITLE-HONOURED-DESIGNER",
        "苏联功勋设计师荣誉称号佩章",
        "1985-06-14",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный технолог СССР»": (
        "USSR-TITLE-HONOURED-TECHNOLOGIST",
        "苏联功勋工艺师荣誉称号佩章",
        "1985-06-14",
        "荣誉称号佩章；具体版型待考",
    ),
    "«Заслуженный машиностроитель СССР»": (
        "USSR-TITLE-HONOURED-MACHINE-BUILDER",
        "苏联功勋机械制造者荣誉称号佩章",
        "1985-08-16",
        "荣誉称号佩章；具体版型待考",
    ),
}


def main() -> None:
    raw_rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_title = {row["page_title"]: row for row in raw_rows if row.get("page_title") in MAPPING}
    missing = sorted(set(MAPPING) - set(by_title))
    if missing:
        raise SystemExit(f"Missing expected Mondvor rows: {missing}")

    existing = json.loads(UNPICTURED.read_text(encoding="utf-8"))
    existing_families = {row["family"] for row in existing}
    normalized = []
    additions = []
    reason = (
        "Mondvor目录与对象页确认该正式奖章或荣誉称号佩章；对象页及证据摘录已缓存。"
        "该站复用说明要求事先取得许可，因此仅登记文字记录和待配图状态，不嵌入其图片。"
    )
    for title, (family, name, date, grade) in MAPPING.items():
        source = by_title[title]
        item = {
            "family": family,
            "name": name,
            "original": title,
            "date": date,
            "known_grade": grade,
            "category": "主编",
            "source_ids": ["mondvor_soviet_awards"],
            "reason": reason,
        }
        if family not in existing_families:
            additions.append(item)
        normalized.append(
            {
                **item,
                "object_page_url": source.get("object_page_url"),
                "directory_page_url": source.get("directory_page_url"),
                "decree_date_original": (source.get("source_evidence") or {}).get("decree_date_original"),
                "evidence_excerpt": (source.get("source_evidence") or {}).get("excerpt"),
                "gap_status": source.get("gap_status"),
                "image_rights_status": "permission_required_not_embedded",
            }
        )

    if additions:
        existing.extend(additions)
        UNPICTURED.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    NORMALIZED.write_text(
        json.dumps(
            {
                "as_of": "2026-09-29",
                "source_id": "mondvor_soviet_awards",
                "verified_family_gaps": len(normalized),
                "newly_appended": len(additions),
                "records": normalized,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"verified={len(normalized)} appended={len(additions)} total_unpictured={len(existing)}")


if __name__ == "__main__":
    main()
