import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8').replace(/^\uFEFF/, ''));

// One decision for every MedalBook family that the complete Ottoman catalogue
// sweep classified as a main award candidate.  Several catalogue headings are
// aliases for one stable project family; they deliberately share a family_id.
const MAPPING = {
  '1st crete campaign medal 1869': ['formal_pictured', 'OTT-CRETE-1869'],
  '1st yemen campaign medal 1846': ['formal_pictured', 'OTT-YEMEN-1847', 'Catalogue year 1846; project retains the securely documented 1847 issue label.'],
  '2nd crete campaign medal 1890': ['formal_pictured', 'OTT-CRETE-1890'],
  '2nd yemen campaign medal 1892': ['formal_pictured', 'OTT-YEMEN-1892'],
  '3rd yemen campaign medal 1905': ['formal_unpictured', 'OTT-YEMEN-1905'],
  'bosnia campaign medal 1850': ['formal_pictured', 'OTT-BOSNIA-1850'],
  'campaign medal for montenegro 1863': ['formal_pictured', 'OTT-MONTENEGRO'],
  'commemorative medal for the danube campaign': ['formal_pictured', 'OTT-GENERAL-SERVICE-1854'],
  'commemorative medal for the defense of kars 1854': ['formal_pictured', 'OTT-KARS'],
  'commemorative medal for the hejaz railway at maan 1904': ['formal_pictured', 'OTT-HEJAZ-MAAN'],
  'commemorative medal for the hejaz railway at medina 1908': ['formal_pictured', 'OTT-HEJAZ-MEDINA'],
  'commemorative medal of abide i hurriyet': ['formal_pictured', 'OTT-MESRUTIYET-MONUMENT'],
  'commemorative medal of avusturya mulakati': ['formal_pictured', 'OTT-KARL-I-VISIT-1918'],
  'commemorative medal of fenerbahce idman yurdu': ['related_unpictured', 'OTT-REL-FENERBAHCE-1917'],
  'commemorative medal of galatasaray futbol kulubu': ['related_pictured', 'OTT-REL-GALATASARAY-FOUNDING'],
  'commemorative medal of hatti humayun': ['related_unpictured', 'OTT-REL-HATTI-HUMAYUN'],
  'commemorative medal of hilal i ahmer sergisi': ['related_pictured', 'OTT-REL-RED-CRESCENT-EXHIBITION-1917'],
  'commemorative medal of hirfet sanat ticaret': ['formal_pictured', 'OTT-1862-EXHIBITION'],
  'commemorative medal of ihtifal i milli': ['related_unpictured', 'OTT-REL-IHTIFAL-MILLI'],
  'commemorative medal of kaiser wilhelm': ['formal_pictured', 'OTT-WILHELM-II-COMMEMORATIVE'],
  'commemorative medal of kaiser wilhelm the second': ['formal_pictured', 'OTT-WILHELM-II-VISIT-1917', 'Mehmed V cypher distinguishes the later visit issue.'],
  'commemorative medal of macar zuvvari hatirasi': ['related_unpictured', 'OTT-REL-HUNGARIAN-VISITORS-1908'],
  'commemorative medal of mudafa i milliye cemiyeti bicki yurdu': ['formal_pictured', 'OTT-MUDAFAA-MILLIYE'],
  'commemorative medal of sishaneli tufek': ['formal_pictured', 'OTT-RIFLE-SHOOTING'],
  'commemorative medal of traktor musabakasi': ['related_unpictured', 'OTT-REL-TRACTOR-1921'],
  'commemorative medal of ziraat ve sinaat': ['formal_pictured', 'OTT-AGRI-INDUSTRY'],
  'commemorative silistre medal 1854': ['formal_pictured', 'OTT-SILISTRA'],
  'crimea medal 1854': ['formal_pictured', 'OTT-CRIMEA'],
  'crusier hamidiye medal': ['formal_pictured', 'OTT-HAMIDIYE-CRUISER'],
  'defense of kars 1855': ['formal_pictured', 'OTT-KARS'],
  'fleet donation medal': ['formal_pictured', 'OTT-NAVAL-DONATION'],
  'general service medal 1853': ['formal_pictured', 'OTT-GENERAL-SERVICE-1853'],
  'greek campaign medal 1896': ['formal_pictured', 'OTT-GREEK-WAR'],
  'hejaz railway medal': ['formal_pictured', 'OTT-HEJAZ-RAIL'],
  'imtiyaz medal': ['formal_pictured', 'OTT-IMTIYAZ-MEDAL'],
  'lifesaving medal': ['formal_pictured', 'OTT-LIFESAVING'],
  'liyakat medal': ['formal_pictured', 'OTT-LIYAKAT'],
  'medal for kurdistan 1846': ['formal_pictured', 'OTT-KURDISTAN'],
  'medal for scutari 1831': ['formal_pictured', 'OTT-SCUTARI-1831'],
  'medal for the reconstruction of the mosque of hagia sophia': ['formal_pictured', 'OTT-HAGIA-SOPHIA-RESTORATION'],
  'medal for the russian military mission 1833': ['formal_pictured', 'OTT-HUNKAR-ISKELESI'],
  'medal of acre 1840': ['formal_pictured', 'OTT-ACRE'],
  'medal of anadolu musabinine lane': ['formal_pictured', 'OTT-ANADOLU-EPIDEMIC'],
  'medal of belediye': ['formal_pictured', 'OTT-MUNICIPAL-ASSEMBLY-1908'],
  'medal of bezm i alem valide sultanisi': ['related_unpictured', 'OTT-REL-BEZMIALEM-1916'],
  'medal of cami i nusret': ['formal_pictured', 'OTT-CAMI-NUSRET'],
  'medal of canakkale ziraat sergisi': ['formal_pictured', 'OTT-CANAKKALE-AGRICULTURE-1918'],
  'medal of cholera': ['formal_pictured', 'OTT-CHOLERA'],
  'medal of darulfunun': ['related_unpictured', 'OTT-REL-DARULFUNUN-1907'],
  'medal of ferahi': ['formal_pictured', 'OTT-FERAHI'],
  'medal of hadim ul haremeyn is serifeyn': ['formal_pictured', 'OTT-HADIM-HAREMEYN'],
  'medal of hareket i arz': ['formal_pictured', 'OTT-EARTHQUAKE-1894'],
  'medal of harir musabakasi': ['formal_pictured', 'OTT-HARIR-MUSABAKA'],
  'medal of hunkar iskelesi': ['formal_pictured', 'OTT-HUNKAR-ISKELESI'],
  'medal of iftihar': ['formal_pictured', 'OTT-IFTIHAR-MEDAL'],
  'medal of ittihad i spor': ['related_pictured', 'OTT-REL-SPORTS-ASSOCIATION'],
  'medal of kadikoy fukaraperver cemiyeti': ['related_pictured', 'OTT-REL-FLOWER-FESTIVAL'],
  'medal of kadikoy ittihad i osmani mektebi': ['related_pictured', 'OTT-REL-KADIKOY-SCHOOL'],
  'medal of masallah': ['identity_conflict', null, 'Catalogue description alone does not establish a formal award rather than a talismanic or commemorative medal.'],
  'medal of mekteb i rustiye': ['formal_pictured', 'OTT-RUSDIYE'],
  'medal of mekteb i tibbi yenin acilmasi': ['related_unpictured', 'OTT-REL-MEDICAL-SCHOOL-OPENING-1838'],
  'medal of nisan i endaht': ['formal_pictured', 'OTT-NISAN-ENDAHT'],
  'medal of sehid evladi ve malul askere iane sergisi': ['formal_pictured', 'OTT-SEHID-EVLAD-MALUL'],
  'medal of sinop 1853': ['formal_pictured', 'OTT-SINOP-1853'],
  'medal of takdir i hunder': ['formal_pictured', 'OTT-SKILL-KNOWLEDGE'],
  'medal of tanzimat i hayriye': ['related_pictured', 'OTT-REL-TANZIMAT-1850'],
  'medal of tarz i atik imtiyaz': ['formal_pictured', 'OTT-IMTIYAZ-MEDAL', 'Old-style material types remain variants of the Imtiyaz medal family.'],
  'medal of tashih i ayar i sikke': ['formal_pictured', 'OTT-TASHIH-AYAR'],
  'medal of tayyare': ['formal_pictured', 'OTT-AVIATION-1914'],
  'medal of tesisat i askeriye': ['formal_pictured', 'OTT-TESISAT-ASKERIYYE'],
  'medal of ticaret mekteb i alisi': ['related_unpictured', 'OTT-REL-TICARET-MEKTEBI-1916'],
  'medal of uclu ittifak': ['related_pictured', 'OTT-TRIPLE-ALLIANCE'],
  'medal of zabtiye cavusu': ['formal_unpictured', 'OTT-GENDARMERIE-SERGEANT'],
  'new coin medal': ['formal_pictured', 'OTT-SIKKE-CEDID'],
  'order of akka': ['formal_pictured', 'OTT-ACRE', 'Catalogue order heading is a duplicate presentation of the Acre medal family.'],
  'order of cami i nusret': ['formal_pictured', 'OTT-CAMI-NUSRET'],
  'order of donanma': ['formal_pictured', 'OTT-NAVAL-DONATION'],
  'order of education': ['formal_pictured', 'OTT-MAARIF-ORDER'],
  'order of ertugrul': ['proposed_not_made', 'NEW-ERTUGRUL-ORDER', 'MedalBook explicitly states that it was never struck.'],
  'order of kurdistan': ['formal_pictured', 'OTT-KURDISTAN'],
  'order of mecruchin i askeriye i iane cemiyeti': ['related_unpictured', 'OTT-REL-MECRUHIN-IANE-CEMIYETI', 'Source says it was not recognized as an official Ottoman order.'],
  'order of medjidjie': ['formal_pictured', 'OTT-MEDJ'],
  'order of nishan el iftihair': ['formal_pictured', 'OTT-IFTIHAR-ORDER'],
  'order of nishan imtiaz': ['formal_pictured', 'OTT-IMTIYAZ-ORDER'],
  'order of nishani shefkat': ['formal_pictured', 'OTT-SEFKAT'],
  'order of osmania': ['formal_pictured', 'OTT-OSM'],
  'order of tasvir i humayun': ['formal_pictured', 'OTT-TASVIR-HUMAYUN'],
  'order of the crescent': ['formal_pictured', 'MENA7-ORDER-OF-THE-CRESCENT'],
  'order of the house of osman': ['formal_pictured', 'OTT-HOUSE-OSMAN'],
  'plevne campaign medal 1877': ['formal_pictured', 'OTT-PLEVNA'],
  'red crescent medal': ['formal_pictured', 'OTT-RED-CRESCENT'],
  'sanayi medal': ['formal_pictured', 'OTT-SANAYI'],
  'sebastopol medal 1855': ['proposed_or_unissued', 'OTT-PROPOSED-SIVASTOPOL-1855', 'SALT records physical gold and bronze trial objects but says the medal was very likely not awarded.'],
  'silistria medal 1854': ['formal_pictured', 'OTT-SILISTRA'],
  'sultans medal for egypt 1801': ['formal_pictured', 'OTT-EGYPT-1801'],
  'turkish russian war medal 1877': ['formal_pictured', 'OTT-RUSSO-TURKISH-WAR-1877'],
  'war medal of 1915': ['formal_pictured', 'OTT-WAR'],
};

const draft = read('data/normalized_drafts/medalbook_ottoman_families.json');
const candidates = draft.families.filter((x) => x.candidate_scope === 'main_award_candidate');
const sourceKeys = new Set(candidates.map((x) => x.normalized_key));
const mappingKeys = new Set(Object.keys(MAPPING));
const missing = [...sourceKeys].filter((x) => !mappingKeys.has(x));
const extra = [...mappingKeys].filter((x) => !sourceKeys.has(x));
if (missing.length || extra.length) throw new Error(`Crosswalk key mismatch; missing=${missing.join(', ')} extra=${extra.join(', ')}`);

const formalFiles = ['data/catalogue.json', ...fs.readdirSync(path.join(ROOT, 'data/volumes'))
  .filter((n) => n.endsWith('.json') && !n.includes('manifest') && n.startsWith('ottoman_') && !n.includes('_related'))
  .map((n) => `data/volumes/${n}`), 'data/volumes/mena_round7_2026-09-26.json'];
const relatedFiles = fs.readdirSync(path.join(ROOT, 'data/volumes'))
  .filter((n) => n.endsWith('.json') && !n.includes('manifest') && n.startsWith('ottoman_') && n.includes('_related'))
  .map((n) => `data/volumes/${n}`);
const records = (files) => files.flatMap((f) => { const d = read(f); return Array.isArray(d) ? d : (d.records || []); });
const formalFamilies = new Set(records(formalFiles).filter((r) => r.views?.length).map((r) => r.family));
const relatedFamilies = new Set(records(relatedFiles).filter((r) => r.views?.length).map((r) => r.family));
const formalUnpictured = new Set(read('data/unpictured.json').map((r) => r.family));
const relatedUnpictured = new Set(read('data/related_unpictured.json').map((r) => r.family));

const result = candidates.map((candidate) => {
  const [status, family_id, note = ''] = MAPPING[candidate.normalized_key];
  if (status === 'formal_pictured' && !formalFamilies.has(family_id)) throw new Error(`Missing formal pictured family ${family_id}`);
  if (status === 'formal_unpictured' && !formalUnpictured.has(family_id)) throw new Error(`Missing formal unpictured family ${family_id}`);
  if (status === 'related_pictured' && !relatedFamilies.has(family_id) && !formalFamilies.has(family_id)) throw new Error(`Missing related pictured family ${family_id}`);
  if (status === 'related_unpictured' && !relatedUnpictured.has(family_id)) throw new Error(`Missing related unpictured family ${family_id}`);
  return {
    normalized_key: candidate.normalized_key,
    working_name: candidate.working_name,
    source_variant_count: candidate.variant_count,
    status,
    family_id,
    note,
    source_pages: candidate.source_page_urls,
  };
});
const status_counts = Object.fromEntries([...new Set(result.map((x) => x.status))].sort().map((s) => [s, result.filter((x) => x.status === s).length]));
const distinctMappedFamilies = new Set(result.filter((x) => x.family_id && !x.status.startsWith('proposed')).map((x) => x.family_id));
const output = {
  as_of: '2026-09-27',
  source: 'MedalBook Ottoman Empire complete catalogue sweep',
  scope: 'All 97 main_award_candidate catalogue families; this is a source crosswalk, not a claim that one catalogue exhausts all Ottoman awards.',
  validation: {
    source_candidates: candidates.length,
    crosswalk_entries: result.length,
    missing_keys: missing,
    extra_keys: extra,
    status_counts,
    distinct_mapped_project_families: distinctMappedFamilies.size,
  },
  entries: result,
};
const outPath = path.join(ROOT, 'data/normalized/ottoman_medalbook_family_crosswalk_2026-09-27.json');
fs.writeFileSync(outPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify(output.validation, null, 2));

