"""Cross-check the finite TDV Ottoman list against the local family index.

This is an identity audit, not an image-finding heuristic.  Every TDV row is
explicitly assigned to a local family, a related/unpictured queue, a conflict,
or an out-of-scope/proposed bucket so that fuzzy matching cannot silently turn
different medals into one family.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_records(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("records", [])


MAPPED = {
    "tdv:nisan:hilal": ["MENA7-ORDER-OF-THE-CRESCENT"],
    "tdv:nisan:iftihar-old": ["OTT-IFTIHAR-ORDER"],
    "tdv:nisan:imtiyaz": ["OTT-IMTIYAZ-ORDER"],
    "tdv:nisan:mecidi": ["OTT-MEDJ"],
    "tdv:nisan:osmani": ["OTT-OSM"],
    "tdv:nisan:sefkat": ["OTT-SEFKAT"],
    "tdv:nisan:ali-imtiyaz": ["OTT-IMTIYAZ-ORDER"],
    "tdv:nisan:hanedan": ["OTT-HOUSE-OSMAN"],
    "tdv:nisan:maarif": ["OTT-MAARIF-ORDER"],
    "tdv:nisan:mebusan": ["OTT-MECLIS-MEBUSAN"],
    "tdv:madalya:ferahî": ["OTT-FERAHI"],
    "tdv:madalya:sikke-i-cedîd": ["OTT-SIKKE-CEDID"],
    "tdv:madalya:vak-a-i-mısriyye": ["OTT-EGYPT-1801"],
    "tdv:madalya:hilâl-i-osmânî": ["OTT-OTTOMAN-CRESCENT-1808"],
    "tdv:madalya:İşkodra---câmi-i-nusretiye": ["OTT-SCUTARI-1831", "OTT-CAMI-NUSRET"],
    "tdv:madalya:hâdimü-l-haremeyni-ş-şerîfeyn": ["OTT-HADIM-HAREMEYN"],
    "tdv:madalya:hünkâr-İskelesi": ["OTT-HUNKAR-ISKELESI"],
    "tdv:madalya:atik-İftihar": ["OTT-IFTIHAR-MEDAL"],
    "tdv:madalya:İftihar--abdülmecid-period": ["OTT-IFTIHAR-MEDAL"],
    "tdv:madalya:beriyyetü-ş-şâm-ve-kal-a-i-akkâ": ["OTT-ACRE"],
    "tdv:madalya:tashîh-i-ayâr-ı-sikke": ["OTT-TASHIH-AYAR"],
    "tdv:madalya:kürdistan": ["OTT-KURDISTAN"],
    "tdv:madalya:yemen-muharebesi": ["OTT-YEMEN-1847"],
    "tdv:madalya:ayasofya-tamir": ["OTT-HAGIA-SOPHIA-RESTORATION"],
    "tdv:madalya:bosna": ["OTT-BOSNIA-1850"],
    "tdv:madalya:İftihar--1853-54-issue": ["OTT-IFTIHAR-MEDAL"],
    "tdv:madalya:tanzîmât-ı-hayriyye": ["OTT-REL-TANZIMAT-1850"],
    "tdv:madalya:sinop": ["OTT-SINOP-1853"],
    "tdv:madalya:bahr-i-siyâh-ve-tuna": ["OTT-TRIPLE-ALLIANCE"],
    "tdv:madalya:İttifâk-ı-düvel-i-selâse": ["OTT-TRIPLE-ALLIANCE"],
    "tdv:madalya:kars": ["OTT-KARS"],
    "tdv:madalya:nişân-ı-İftihâr-madalyası": ["OTT-IFTIHAR-MEDAL"],
    "tdv:madalya:tahlîs-i-can": ["OTT-LIFESAVING"],
    "tdv:madalya:tahsîn-i-hüner-ve-mârifet": ["OTT-SKILL-KNOWLEDGE"],
    "tdv:madalya:karadağ": ["OTT-MONTENEGRO"],
    "tdv:madalya:sergi-i-umûmî-i-osmânî": ["OTT-1862-EXHIBITION"],
    "tdv:madalya:şeşhâneli-tüfek": ["OTT-RIFLE-SHOOTING"],
    "tdv:madalya:endaht-nişanı-madalyası": ["OTT-NISAN-ENDAHT"],
    "tdv:madalya:kolera": ["OTT-CHOLERA"],
    "tdv:madalya:atik-girit": ["OTT-CRETE-ATIK-GIRIT"],
    "tdv:madalya:plevne": ["OTT-PLEVNA"],
    "tdv:madalya:tarz-ı-atîk-İmtiyaz": ["OTT-IMTIYAZ-MEDAL"],
    "tdv:madalya:tarz-ı-cedîd-büyük-İmtiyaz": ["OTT-IMTIYAZ-MEDAL"],
    "tdv:madalya:İftihar--1885-issue": ["OTT-IFTIHAR-MEDAL"],
    "tdv:madalya:küçük-İmtiyaz": ["OTT-IMTIYAZ-MEDAL"],
    "tdv:madalya:alman-mülâkat--abdülhamid-period": ["OTT-WILHELM-II-COMMEMORATIVE"],
    "tdv:madalya:tarz-ı-cedîd-girit": ["OTT-CRETE-1890"],
    "tdv:madalya:liyakat": ["OTT-LIYAKAT"],
    "tdv:madalya:tarz-ı-cedîd-yemen": ["OTT-YEMEN-1892"],
    "tdv:madalya:ziraat-ve-sınaat": ["OTT-AGRI-INDUSTRY"],
    "tdv:madalya:hareket-i-arz": ["OTT-EARTHQUAKE-1894"],
    "tdv:madalya:anadolu-müsâbînîne-iâne": ["OTT-ANADOLU-EPIDEMIC"],
    "tdv:madalya:te-sîsât-ı-askeriyye-iâne": ["OTT-TESISAT-ASKERIYYE"],
    "tdv:madalya:yunan-muharebesi": ["OTT-GREEK-WAR"],
    "tdv:madalya:evlâd-ı-şühedâ-iâne-sergisi": ["OTT-SEHID-EVLAD-MALUL"],
    "tdv:madalya:maarif-madalyası": ["OTT-MAARIF-MEDAL"],
    "tdv:madalya:hamidiye-hicaz-railway": ["OTT-HEJAZ-RAIL"],
    "tdv:madalya:hamidiye-hicaz-railway-maan-opening": ["OTT-HEJAZ-MAAN"],
    "tdv:madalya:harîr-müsabakası": ["OTT-HARIR-MUSABAKA"],
    "tdv:madalya:cem-iyyet-i-umûmiyye-i-belediyye": ["OTT-MUNICIPAL-ASSEMBLY-1908"],
    "tdv:madalya:kānûn-ı-esâsî": ["OTT-CONSTITUTION"],
    "tdv:madalya:hamidiye-hicaz-railway-medine-aynüzzerka": ["OTT-HEJAZ-MEDINA"],
    "tdv:madalya:galatasaray-football-club": ["OTT-REL-GALATASARAY-FOUNDING"],
    "tdv:madalya:kadıköy-İttihâd-ı-osmânî-school": ["OTT-REL-KADIKOY-SCHOOL"],
    "tdv:madalya:bursa-exhibition": ["OTT-BURSA-EXHIBITION"],
    "tdv:madalya:hâtıra-i-âbide-i-meşrûtiyet": ["OTT-MESRUTIYET-MONUMENT"],
    "tdv:madalya:donanma": ["OTT-NAVAL-DONATION"],
    "tdv:madalya:hamidiye-cruiser": ["OTT-HAMIDIYE-CRUISER"],
    "tdv:madalya:tayyare": ["OTT-AVIATION-1914"],
    "tdv:madalya:müdâfaa-i-milliye-biçki-yurdu": ["OTT-MUDAFAA-MILLIYE"],
    "tdv:madalya:harp-madalyası": ["OTT-WAR"],
    "tdv:madalya:kahire-air-trip": ["OTT-AVIATION-1914"],
    "tdv:madalya:kadıköy-fukaraperver-cemiyeti": ["OTT-REL-FLOWER-FESTIVAL"],
    "tdv:madalya:alman-mülâkat--mehmed-reşad-period": ["OTT-WILHELM-II-VISIT-1917"],
    "tdv:madalya:avusturya-mülâkat": ["OTT-KARL-I-VISIT-1918"],
    "tdv:madalya:çanakkale-ziraat-sergisi": ["OTT-CANAKKALE-AGRICULTURE-1918"],
}

SPECIAL = {
    "tdv:nisan:ertugrul": "proposed_not_made",
    "tdv:nisan:meziyet": "proposed_not_made",
    "tdv:nisan:z_i_liyakat": "proposed_not_made",
    "tdv:nisan:aggregate-plate": "reference_plate",
    "tdv:madalya:İstiklâl-madalyası": "successor_state",
    "tdv:madalya:zaptiye-çavuşları": "formal_unpictured",
    "tdv:madalya:bosna-muharebesi": "identity_conflict",
    "tdv:madalya:dârülfünun": "related_unpictured",
    "tdv:madalya:macar-züvvâr": "related_unpictured",
    "tdv:madalya:galatasaray-terbiye-i-bedeniyye": "related_unpictured",
    "tdv:madalya:bezmiâlem-vâlide-sultânîsi": "related_unpictured",
    "tdv:madalya:ticaret-mekteb-i-âlîsi": "related_unpictured",
    "tdv:madalya:fenerbahçe-İdman-yurdu": "related_unpictured",
    "tdv:madalya:çiçek-meşheri": "related_unpictured",
    "tdv:madalya:traktör-müsabakası": "related_unpictured",
}


def main():
    tdv = [json.loads(line) for line in (ROOT / "data/raw_candidates/tdv_ottoman.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    main_records = load_records(ROOT / "data/catalogue.json")
    related_records = load_records(ROOT / "data/related.json")
    for path in (ROOT / "data/volumes").glob("*.json"):
        if path.name.endswith("manifest.json"):
            continue
        records = load_records(path)
        if path.name.startswith("ottoman_") or path.name == "mena_round7_2026-09-26.json":
            main_records.extend(r for r in records if r.get("country_zh", "奥斯曼帝国") == "奥斯曼帝国")
        if path.name in {"ottoman_kuenker299_related.json", "ottoman_cng_triple_alliance_related.json", "ottoman_cgb_related.json"}:
            related_records.extend(records)
    present = {r.get("family") for r in main_records + related_records}
    output = []
    for row in tdv:
        source_id = row["source_id"]
        if source_id in MAPPED:
            families = MAPPED[source_id]
            missing = [family for family in families if family not in present]
            status = "covered" if not missing else "mapping_target_missing"
        elif source_id in SPECIAL:
            families = []
            missing = []
            status = SPECIAL[source_id]
        else:
            raise SystemExit(f"Unclassified TDV row: {source_id} {row['original_name']}")
        output.append({
            "source_id": source_id,
            "original_name": row["original_name"],
            "date_candidates": row.get("date_candidates", []),
            "status": status,
            "local_families": families,
            "missing_mapping_targets": missing,
        })
    counts = Counter(row["status"] for row in output)
    result = {
        "as_of": "2026-09-27",
        "scope": "TDV finite Ottoman NİŞAN/MADALYA chronology crosswalk",
        "tdv_rows": len(output),
        "status_counts": dict(sorted(counts.items())),
        "notes": [
            "covered means identity-mapped, not proof that every grade, maker, or material variant is complete",
            "the three proposed orders are retained as proposed/not made and are not counted as issued award families",
            "school, club, exhibition, visit, and association pieces remain in the related-material queue unless evidence establishes a formal state award",
            "the 1877 Bosnia item remains isolated because the TDV attribution conflicts with other catalogues",
        ],
        "rows": output,
    }
    target = ROOT / "data/normalized/ottoman_tdv_family_crosswalk_2026-09-27.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"target": str(target.relative_to(ROOT)), "tdv_rows": len(output), "status_counts": result["status_counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
