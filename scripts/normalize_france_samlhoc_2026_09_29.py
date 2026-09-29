from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw_candidates/france_samlhoc_full_2026-09-29.jsonl"
OUT = ROOT / "data/normalized/france_samlhoc_full_2026-09-29.json"
GAP_OUT = ROOT / "data/queues/france_samlhoc_gap_queue_2026-09-29.json"

# Sitemap siblings that are institutional/text/person lists or pages belonging to
# another award root. They must not inflate the public award-family count.
ALIASES = {
    "legion_honneur_scandale_decorations": "legion_honneur",
    "legion_honneur_textes_officiels_1": "legion_honneur",
    "legion_honneur_textes_officiels_2": "legion_honneur",
    "ordre_liberation_compagnons": "ordre_liberation",
    "ordre_national_merite_textes_officiels": "ordre_national_merite",
    "ordre_national_travail_titulaires": "ordre_national_travail",
    "ordre_saint_louis_titulaires": "ordre_saint_louis",
    "ordre_tahiti_nui_titulaires": "ordre_tahiti_nui",
    "decorations_vainqueurs_bastille_titulaires": "decorations_vainqueurs_bastille",
    "medaille_coloniale_mission_foureau-lamy": "medaille_coloniale",
    "medaille_coloniale_textes_officiels": "medaille_coloniale",
    "medaille_militaire_textes_officiels_1": "medaille_militaire",
    "medaille_militaire_textes_officiels_2": "medaille_militaire",
    "medaille_commemorative_francaise_coree": "medaille_commemorative_francaise",
    "medaille_commemorative_francaise_operations_moyen-orient": "medaille_commemorative_francaise",
}
EXCLUDE = {
    "unknown",
    "lettre_president_05-02-1996",
    "lettre_president_11-07-08",
    "ordres_coloniaux",
}
ISSUER_SCOPE = {
    "ordre_cambodge": "柬埔寨王国／法国保护国时期体系（待逐页核定）",
    "ordre_dragon_annam": "安南帝国／法国保护国时期体系（待逐页核定）",
    "ordre_merite_indochinois": "法属印度支那",
    "ordre_merite_madagascar_dependances": "法属马达加斯加及属地",
    "ordre_merite_cameroun": "法属喀麦隆",
    "ordre_etoile_anjouan": "昂儒昂／法国殖民体系",
    "ordre_nichan_el-anouar": "塔朱拉／法国殖民体系",
    "ordre_etoile_noire": "达荷美／法国殖民体系",
    "ordre_tahiti_nui": "法属波利尼西亚",
}
KNOWN_FAMILIES = {
    "legion_honneur": "FRA-LEGION-HONOUR",
    "ordre_national_merite": "FRA-ORDRE-NATIONAL-MERITE",
    "croix_guerre_1914-1918": "FRA-III-CROIX-DE-GUERRE-1914-1918",
    "medaille_coloniale": "FRA-III-MEDAILLE-COLONIALE",
    "medaille_militaire": "FRA-III-MEDAILLE-MILITAIRE",
    "medaille_nationale_reconnaissance_victimes_terrorisme": "FRA-MEDAILLE-VICTIMES-TERRORISME",
    "medaille_commemorative_campagne_italie_1859": "FRA-MEDAILLE-CAMPAGNE-ITALIE-1859",
    "medaille_commemorative_dardanelles": "FRA-III-DARDANELLES-COMMEMORATIVE",
    "medaille_commemorative_expedition_chine_1900-1901": "FRA-III-CHINA-COMMEMORATIVE",
    "medaille_commemorative_expedition_dahomey": "FRA-III-DAHOMEY-COMMEMORATIVE",
    "medaille_commemorative_expedition_mexique": "FRA-MEDAILLE-EXPEDITION-MEXIQUE-1863",
    "medaille_commemorative_grande_guerre": "FRA-III-GREAT-WAR-COMMEMORATIVE",
    "medaille_commemorative_guerre_1870": "FRA-III-WAR-1870-1871-COMMEMORATIVE",
    "medaille_commemorative_maroc": "FRA-III-MOROCCO-COMMEMORATIVE",
    "medaille_commemorative_orient": "FRA-III-ORIENT-COMMEMORATIVE",
    "medaille_commemorative_syrie-cilicie": "FRA-III-SYRIE-CILICIE-COMMEMORATIVE",
    "medaille_honneur_epidemies": "FRA-III-MEDAILLE-HONNEUR-EPIDEMIES",
    "medaille_honneur_mutualite": "FRA-III-MUTUALITY-HONOUR",
    "medaille_honneur_sapeurs-pompiers": "FRA-III-FIREFIGHTERS-HONOUR",
    "medaille_interalliee_victoire": "FRA-III-MEDAILLE-INTERALLIEE-VICTOIRE",
    "medailles_commemoratives_madagascar": "FRA-III-MADAGASCAR-COMMEMORATIVE",
}


def main() -> None:
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    excluded = []
    for row in rows:
        slug = row["family_slug"]
        if slug in EXCLUDE:
            excluded.append({
                "category_tree": row["category_tree"],
                "family_slug": slug,
                "page_titles": row["page_titles"],
                "reason": "category overview or contextual/institutional page; retained in raw candidates",
            })
            continue
        root = ALIASES.get(slug, slug)
        groups[(row["category_tree"], root)].append(row)

    families = []
    for (tree, root), members in sorted(groups.items()):
        page_rows = [page for member in members for page in member["pages"]]
        images = {img["url"]: img for member in members for img in member["downloaded_images"]}
        preferred = next((m for m in members if m["family_slug"] == root), members[0])
        titles = [title for m in members for title in m["page_titles"] if title]
        families.append({
            "family_id": f"FRA-SAMLHOC-{tree.upper().replace('-', '_')}-{root.upper().replace('-', '_')}",
            "category_tree": tree,
            "canonical_slug": root,
            "original_name_candidate": preferred["page_titles"][0] if preferred["page_titles"] else root,
            "issuer_scope": ISSUER_SCOPE.get(root, "法国国家／历史政权；具体授予主体待逐页核定"),
            "merged_raw_slugs": [m["family_slug"] for m in members],
            "page_count": len(page_rows),
            "page_title_candidates": titles,
            "local_decoded_images": len(images),
            "image_urls": sorted(images),
            "status": "normalized_family_candidate_unverified_for_publication",
            "rights": "SAMLHOC all-rights-reserved research cache; do not publish images without independent permission or an open replacement.",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "as_of": "2026-09-29",
        "source": "FR-SAMLHOC-FULL-PHALERISTIQUE",
        "method": "Collapse category overviews, institutional/text/person-list siblings and known subpages into award-family candidates. This is a family crosswalk, not final object authentication.",
        "counts": {
            "raw_groups": len(rows),
            "excluded_context_groups": len(excluded),
            "normalized_family_candidates": len(families),
            "families_with_images": sum(bool(f["local_decoded_images"]) for f in families),
            "families_without_images": sum(not f["local_decoded_images"] for f in families),
            "decoded_image_references": sum(f["local_decoded_images"] for f in families),
        },
        "excluded_context_groups": excluded,
        "families": families,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    mapped = [
        {"canonical_slug": family["canonical_slug"], "family_id": KNOWN_FAMILIES[family["canonical_slug"]]}
        for family in families if family["canonical_slug"] in KNOWN_FAMILIES
    ]
    unresolved = [
        {
            "family_id": family["family_id"],
            "canonical_slug": family["canonical_slug"],
            "original_name_candidate": family["original_name_candidate"],
            "issuer_scope": family["issuer_scope"],
            "local_decoded_images": family["local_decoded_images"],
            "status": "unresolved_difference_candidate",
        }
        for family in families if family["canonical_slug"] not in KNOWN_FAMILIES
    ]
    GAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    GAP_OUT.write_text(json.dumps({
        "as_of": "2026-09-29",
        "policy": "only_add_never_silently_drop",
        "source": "FR-SAMLHOC-FULL-PHALERISTIQUE",
        "method": "Exact source-slug crosswalk against the locally known France family ids, including the four-row official-core batch. Unresolved rows remain candidates and are not asserted as confirmed new formal awards.",
        "counts": {
            "normalized_source_families": len(families),
            "mapped_known_families": len(mapped),
            "unresolved_difference_candidates": len(unresolved),
            "unresolved_without_any_local_image": sum(not x["local_decoded_images"] for x in unresolved),
        },
        "mapped_known_families": mapped,
        "unresolved_difference_candidates": unresolved,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(json.loads(OUT.read_text(encoding="utf-8"))["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
