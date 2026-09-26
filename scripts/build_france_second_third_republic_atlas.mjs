import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const root = process.cwd();
const asOf = "2026-09-26";
const atlasPath = path.join(root, "data/source_atlas/france_second_third_republic_source_matrix.json");
const rawPath = path.join(root, "data/raw_candidates/france_second_third_republic_official_commemoratives.jsonl");
const sweepPath = path.join(root, "data/source_sweeps/france_second_third_republic_official_commemoratives.json");
const cacheDir = path.join(root, "sources/cache/france_second_third_republic");
const pdfPath = path.join(cacheDir, "les_medaille_commemoratives_francaises.pdf");
const renderDir = path.join(cacheDir, "pdf_render");

for (const p of [path.dirname(atlasPath), path.dirname(rawPath), path.dirname(sweepPath), cacheDir]) {
  fs.mkdirSync(p, { recursive: true });
}

function sha256(file) {
  if (!fs.existsSync(file)) return null;
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}
function writeJson(file, value) {
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  fs.renameSync(tmp, file);
}
function localJson(file) {
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

const existingFamilies = new Set();
for (const file of [
  "data/volumes/france_second_empire_pack1_2026-09-26.json",
  "data/volumes/france_third_republic.json",
  "data/volumes/france_third_republic_pack1.json",
]) {
  const obj = localJson(path.join(root, file));
  for (const record of obj?.records ?? []) if (record.family) existingFamilies.add(record.family);
}

const urls = {
  chancery: "https://www.legiondhonneur.fr/fr/la-france-frise",
  pdf: "https://www.legiondhonneur.fr/sites/default/files/les_mcdailles_commcmoratives_.pdf",
  legion: "https://www.samlhoc.fr/phaleristique/ordres-chevalerie/legion_honneur/",
  medals: "https://www.samlhoc.fr/phaleristique/medailles/",
  tonkin: "https://www.samlhoc.fr/phaleristique/medailles/medaille_commemorative_expedition_tonkin/",
  madagascar: "https://www.samlhoc.fr/phaleristique/medailles/medailles_commemoratives_madagascar/",
  morocco: "https://www.samlhoc.fr/phaleristique/medailles/medaille_commemorative_maroc/",
  legifrance: "https://www.legifrance.gouv.fr/",
  monnaie: "https://collectionspatrimoniales.monnaiedeparis.fr/fr/",
  parisMusees: "https://www.parismuseescollections.paris.fr/en/",
  chemins: "https://www.cheminsdememoire.gouv.fr/fr/les-medailles-commemoratives-francaises",
  gallica: "https://gallica.bnf.fr/",
};

const sources = [
  { id: "FR-OFFICIAL-CHANCERY-TIMELINE", title: "La France | La grande chancellerie", kind: "official_institutional_timeline", url: urls.chancery, access: "web_search_verified", status: "high_value_discovery", coverage: "National orders, Médaille militaire, Second Empire campaign medals, Third Republic colonial commemoratives", score: 15 },
  { id: "FR-OFFICIAL-COMMEMORATIVE-PDF", title: "Les médailles commémoratives", kind: "official_museum_catalogue_pdf", url: urls.pdf, access: "cached_download_and_rendered", status: "selected_swept", coverage: "All pages: Second Empire campaign medals and Third Republic 1870, Tonkin, Madagascar, Dahomey, China, Morocco and WWI groups", score: 19, cache_path: "sources/cache/france_second_third_republic/les_medaille_commemoratives_francaises.pdf" },
  { id: "FR-SAMLHOC-LEGION-HONOUR", title: "Ordre national de la Légion d’honneur", kind: "specialist_order_history_and_models", url: urls.legion, access: "web_search_verified", status: "candidate_followup", coverage: "Restoration through Second Empire and Third Republic model changes, grades and insignia", score: 17 },
  { id: "FR-SAMLHOC-MEDALS-CATALOGUE", title: "SAMLHOC médailles index", kind: "specialist_directory", url: urls.medals, access: "web_search_verified", status: "candidate_followup", coverage: "Broad French medal taxonomy, campaign, ministry, rescue and civil awards", score: 17 },
  { id: "FR-SAMLHOC-TONKIN", title: "Médaille commémorative de l’expédition du Tonkin", kind: "specialist_decree_and_type_page", url: urls.tonkin, access: "web_search_verified", status: "candidate_followup", coverage: "1885 Tonkin medal, law, ribbon and battle bars", score: 16 },
  { id: "FR-SAMLHOC-MADAGASCAR", title: "Médailles commémoratives de Madagascar", kind: "specialist_decree_and_type_page", url: urls.madagascar, access: "web_search_verified", status: "existing_family_variant_followup", coverage: "1886 and 1896 variants, laws and bars", score: 16 },
  { id: "FR-SAMLHOC-MOROCCO", title: "Médaille commémorative du Maroc", kind: "specialist_decree_and_type_page", url: urls.morocco, access: "web_search_verified", status: "existing_family_variant_followup", coverage: "1909 Moroccan operations, bars and law transcription", score: 16 },
  { id: "FR-LEGIFRANCE", title: "Légifrance", kind: "official_legal_database", url: urls.legifrance, access: "web_search_verified", status: "candidate_followup", coverage: "Primary legal texts and amendments for 1852–1940 awards", score: 18 },
  { id: "FR-MONNAIE-DE-PARIS", title: "Collections patrimoniales de la Monnaie de Paris", kind: "official_mint_collection", url: urls.monnaie, access: "web_search_verified", status: "candidate_followup", coverage: "Mint objects, designers, materials and accession references", score: 17 },
  { id: "FR-PARIS-MUSEES", title: "Paris Musées Collections", kind: "public_museum_collection", url: urls.parisMusees, access: "web_search_verified", status: "candidate_followup", coverage: "Open-license and accessioned French award objects, especially Third Republic", score: 17 },
  { id: "FR-CHEMINS-DE-MEMOIRE", title: "Les médailles commémoratives françaises", kind: "official_defense_history", url: urls.chemins, access: "web_search_verified", status: "candidate_followup", coverage: "Official historical overview and campaign-medal chronology", score: 15 },
  { id: "FR-GALLICA", title: "Gallica / Bibliothèque nationale de France", kind: "national_library_scanned_catalogues", url: urls.gallica, access: "discovery_entry_point", status: "candidate_followup", coverage: "Historical legislation, catalogues and illustrated works for physical types", score: 15 },
];

const taxonomy = [
  { id: "second_empire_campaign", label: "Second Empire campaign and expedition medals", period: "1852–1870", candidates: ["Médaille de Sainte-Hélène", "Médaille d’Italie", "Médaille de Chine", "Médaille du Mexique"], coverage: "official PDF swept; local difference applied" },
  { id: "third_republic_1870", label: "Third Republic 1870–1871 commemoration", period: "1870–1940", candidates: ["Médaille commémorative de la guerre de 1870–1871"], coverage: "official PDF swept; no local family record" },
  { id: "third_republic_colonial", label: "Third Republic colonial and overseas campaigns", period: "1885–1909", candidates: ["Tonkin", "Madagascar 1886", "Madagascar 1896", "Dahomey", "Chine 1901", "Maroc 1909"], coverage: "official PDF swept; existing families marked for variant follow-up" },
  { id: "third_republic_first_world_war", label: "Third Republic First World War and postwar commemoratives", period: "1914–1926", candidates: ["Interallied Victory", "Grande Guerre 1914–1918", "Syrie-Cilicie", "Dardanelles", "Orient"], coverage: "official PDF swept at group/section level; individual object sources pending" },
  { id: "continued_national_orders", label: "Orders and distinctions continued across regimes", period: "1852–1940", candidates: ["Légion d’honneur", "Médaille militaire", "Palmes académiques"], coverage: "matrix sources found; object-level sweep pending" },
  { id: "civil_ministry_rescue", label: "Ministry, rescue, medical, fire and civil awards", period: "1852–1940", candidates: ["Courage et Dévouement", "Sauvetage", "Épidémies", "Sapeurs-pompiers", "Mutualité"], coverage: "existing candidate files and specialist directory; selected PDF not comprehensive" },
];

function candidate(data) {
  const existing = Boolean(data.family && existingFamilies.has(data.family));
  return {
    ...data,
    existing_family_in_local_records: existing,
    status: existing && data.status === "difference_candidate" ? "existing_family_variant_or_coverage_gap" : data.status,
    difference_note: existing
      ? "Existing family retained; add a period-specific variant or coverage evidence, not a duplicate family."
      : data.family
        ? "No matching family in the two local France volume records; candidate remains a difference item."
        : "Boundary item retained for audit but excluded from French-family counts.",
  };
}

const candidates = [
  candidate({ key: "FRA-SE-SAINTE-HELENE-1857", family: "FRA-MEDAILLE-SAINTE-HELENE", original_names: ["Médaille de Sainte-Hélène", "Saint Helena Medal"], granting_body: "French Second Empire / Napoléon III", period: "12 August 1857 decree; veterans of Revolutionary and Napoleonic campaigns", taxonomy: "second_empire_campaign", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "not acquired in this sweep", next_step: "Locate complete open full-face specimen and decree-backed object page." }, evidence: "Official PDF identifies the 12 August 1857 decree, purpose and medal type on page 1." }),
  candidate({ key: "FRA-SE-ITALY-1859", family: "FRA-MEDAILLE-CAMPAGNE-ITALIE-1859", original_names: ["Médaille d’Italie", "Médaille commémorative de la campagne d’Italie"], granting_body: "French Second Empire / Napoléon III", period: "11 August 1859 imperial decree; Italian campaign", taxonomy: "second_empire_campaign", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "existing presentation specimen", next_step: "Add standard silver issue and Cent-Gardes crown variant as separate variants." }, evidence: "Official PDF gives 11 August 1859 decree and describes two principal models and Cent-Gardes variant on page 1." }),
  candidate({ key: "FRA-SE-CHINA-1861", family: "FRA-MEDAILLE-EXPEDITION-CHINE-1861", original_names: ["Médaille de Chine", "Médaille commémorative de l’expédition de Chine"], granting_body: "French Second Empire / Napoléon III", period: "23 January 1861 imperial decree; expedition of 1860", taxonomy: "second_empire_campaign", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 2, total: 15 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "existing local candidate incomplete/cropped", next_step: "Find complete single-specimen front and record ribbon inscription." }, evidence: "Official PDF identifies 23 January 1861 decree and the Pekin ribbon inscription on pages 1–2." }),
  candidate({ key: "FRA-SE-MEXICO-1863", family: "FRA-MEDAILLE-EXPEDITION-MEXIQUE-1863", original_names: ["Médaille du Mexique", "Médaille de l’expédition du Mexique"], granting_body: "French Second Empire / Napoléon III", period: "29 August 1863 imperial decree; personnel present in Mexico 1862–1867", taxonomy: "second_empire_campaign", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 2, total: 15 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "existing low-resolution foundation object", next_step: "Seek complete open specimen with ribbon and object provenance." }, evidence: "Official PDF identifies 29 August 1863 decree and 1862–1867 eligibility on page 2." }),
  candidate({ key: "FRA-III-WAR-1870-1871", family: "FRA-III-WAR-1870-1871", original_names: ["Médaille commémorative de la guerre de 1870–1871"], granting_body: "French Third Republic", period: "9 November 1911 law commemorating 1870–1871 combatants", taxonomy: "third_republic_1870", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "candidate listed locally but not packaged", next_step: "Prioritize complete open front/back object." }, evidence: "Official PDF states the 9 November 1911 law and describes ribbon, silver/bronze and volunteer clasp on page 2." }),
  candidate({ key: "FRA-III-TONKIN-1885", family: "FRA-III-TONKIN-COMMEMORATIVE", original_names: ["Médaille du Tonkin", "Médaille commémorative de l’expédition du Tonkin"], granting_body: "French Third Republic", period: "6 September 1885 law; attribution extended by 27 July 1887 law", taxonomy: "third_republic_colonial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-TONKIN"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "official PDF and specialist page", image: "not acquired in this sweep", next_step: "Sweep SAMLHOC and open museum objects for a complete specimen." }, evidence: "Official PDF states 6 September 1885 law, extension to 1 October 1895 and battle bars on page 2." }),
  candidate({ key: "FRA-III-MADAGASCAR-1886-1896", family: "FRA-III-MADAGASCAR-COMMEMORATIVE", original_names: ["Médaille de Madagascar 1886", "Médaille de Madagascar 1896"], granting_body: "French Third Republic", period: "31 July 1886 and 15 January 1896 laws; two expedition variants", taxonomy: "third_republic_colonial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MADAGASCAR"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "official PDF and specialist page", image: "two existing variants", next_step: "Use source page for legal and bar details; no duplicate family." }, evidence: "Official PDF states two expeditions, 31 July 1886 and 15 January 1896 laws, and 1895 bar on page 2." }),
  candidate({ key: "FRA-III-DAHOMEY-1892", family: "FRA-III-DAHOMEY-COMMEMORATIVE", original_names: ["Médaille du Dahomey"], granting_body: "French Third Republic", period: "24 November 1892 law; expedition against Behanzin", taxonomy: "third_republic_colonial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 4, access: 3, object_followup: 3, total: 15 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "not acquired", next_step: "Find complete specimen and verify Dupuis type." }, evidence: "Official PDF identifies the 24 November 1892 law and ribbon colors on page 2." }),
  candidate({ key: "FRA-III-CHINA-1901", family: "FRA-III-CHINA-1901-COMMEMORATIVE", original_names: ["Médaille de Chine 1901", "Médaille de l’expédition de Chine 1900–1901"], granting_body: "French Third Republic", period: "15 April 1902 law; relief expedition for besieged legations", taxonomy: "third_republic_colonial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "explicit in selected official PDF", image: "not acquired", next_step: "Locate complete object with 1900–Chine–1901 bar." }, evidence: "Official PDF identifies 15 April 1902 law, medal design and bar text on page 2." }),
  candidate({ key: "FRA-III-MOROCCO-1909", family: "FRA-III-MOROCCO-COMMEMORATIVE", original_names: ["Médaille du Maroc", "Médaille commémorative des opérations effectuées au Maroc"], granting_body: "French Third Republic", period: "22 July 1909 law; operations 1907–1912", taxonomy: "third_republic_colonial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MOROCCO"], score: { authority: 5, coverage: 5, access: 3, object_followup: 3, total: 16 }, status: "difference_candidate", coverage: { directory: "official PDF and specialist page", image: "existing complete front/back", next_step: "Retain as existing family and add only sourced variants/bars." }, evidence: "Official PDF identifies 22 July 1909 law and Casablanca, Oudja, Haut-Guir and Maroc bars on page 2." }),
  candidate({ key: "FRA-III-GREAT-WAR-COMMEMORATIVES-1914-1926", family: "FRA-III-GREAT-WAR-COMMEMORATIVES", original_names: ["Médaille interalliée de la Victoire", "Médaille commémorative de la Grande Guerre 1914–1918", "Médaille de Syrie-Cilicie", "Médaille des Dardanelles", "Médaille d’Orient"], granting_body: "French Third Republic / interallied and national legal systems", period: "1919–1926 laws and conference decisions", taxonomy: "third_republic_first_world_war", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF", "FR-SAMLHOC-MEDALS-CATALOGUE", "FR-LEGIFRANCE"], score: { authority: 5, coverage: 4, access: 3, object_followup: 3, total: 15 }, status: "difference_candidate", coverage: { directory: "official PDF section-level sweep", image: "individual objects not swept", next_step: "Split into stable families only after each law and object is verified." }, evidence: "Official PDF lists Victory, Grande Guerre, Syrie-Cilicie, Dardanelles and Orient with dates on page 2." }),
  candidate({ key: "FRA-CONTEXT-CRIMEA-FOREIGN-1856", family: null, original_names: ["Médaille de Crimée britannique", "Médaille de la Baltique britannique", "Médaille turque de Crimée"], granting_body: "United Kingdom and Ottoman Empire; French authorization to wear", period: "1856; foreign awards associated with Second Empire French service", taxonomy: "boundary_foreign_awards", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF"], score: { authority: 5, coverage: 3, access: 3, object_followup: 1, total: 12 }, status: "boundary_excluded_foreign_grantor", coverage: { directory: "context explicitly discussed", image: "not sought in France sweep", next_step: "Foreign-awards appendix only if that scope is opened." }, evidence: "Official PDF explains French authorization to wear British and Turkish Crimean/Baltic medals; they are not French-granted." }),
  candidate({ key: "FRA-CONTEXT-MEXICAN-MERIT-1864", family: null, original_names: ["Médaille du Mérite mexicain"], granting_body: "Emperor Maximilian of Mexico", period: "1864–1865; foreign award during French expedition context", taxonomy: "boundary_foreign_awards", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF"], score: { authority: 5, coverage: 2, access: 3, object_followup: 1, total: 11 }, status: "boundary_excluded_foreign_grantor", coverage: { directory: "context only", image: "not sought", next_step: "Separate Mexican imperial award queue." }, evidence: "Official PDF notes Maximilian decrees of 14 October 1864 and 10 March 1865; granting body is not France." }),
  candidate({ key: "FRA-CONTEXT-SOUDAN-NONOFFICIAL", family: null, original_names: ["Médaille du Soudan"], granting_body: "Unclear/private or non-official", period: "Third Republic campaign context", taxonomy: "boundary_nonofficial", source_ids: ["FR-OFFICIAL-COMMEMORATIVE-PDF"], score: { authority: 5, coverage: 2, access: 3, object_followup: 1, total: 11 }, status: "boundary_excluded_nonofficial", coverage: { directory: "explicitly noted as lacking official character", image: "not sought", next_step: "Historical/commemorative appendix only if policy permits." }, evidence: "Official PDF states the Sudan medal existed but had no official character." }),
];

const renderedPages = fs.existsSync(renderDir)
  ? fs.readdirSync(renderDir).filter((n) => /^page-\d+\.png$/.test(n)).sort().map((name) => {
      const file = path.join(renderDir, name);
      return { path: `sources/cache/france_second_third_republic/pdf_render/${name}`, bytes: fs.statSync(file).size, sha256: sha256(file) };
    })
  : [];
const rawRows = candidates.map((c, index) => {
  const scope = c.taxonomy.startsWith("second_empire") ? "france_second_empire" : c.taxonomy.startsWith("third_republic") ? "france_third_republic" : "boundary_context";
  const page = scope === "france_second_empire" ? 1 : scope === "france_third_republic" ? 2 : 1;
  return {
    source_id: `fr-official-commemoratives-${String(index + 1).padStart(3, "0")}`,
    source_system: "Musée de la Légion d’honneur / Grande Chancellerie de la Légion d’honneur",
    source_type: "official_catalogue_pdf_discovery",
    accessed: asOf,
    source_page: urls.pdf,
    local_source_file: "sources/cache/france_second_third_republic/les_medaille_commemoratives_francaises.pdf",
    pdf_page: page,
    source_section: scope === "france_second_empire" ? "Le Second Empire" : scope === "france_third_republic" ? "La IIIe République" : "Context / boundary note",
    candidate_key: c.key,
    family: c.family,
    original_names: c.original_names,
    period_scope: scope,
    granting_body: c.granting_body,
    period: c.period,
    evidence_summary: c.evidence,
    local_difference_status: c.status,
    existing_family_in_local_records: c.existing_family_in_local_records,
    score: c.score,
    status: "RAW_CANDIDATE",
    image_downloaded: false,
    note: "Directory/source sweep only; no image bytes downloaded. Boundary entries are retained for audit but are not French-family admissions.",
  };
});
fs.writeFileSync(rawPath, `${rawRows.map((r) => JSON.stringify(r)).join("\n")}\n`, "utf8");

const counts = {
  total_candidates: candidates.length,
  second_empire_candidates: candidates.filter((c) => c.taxonomy === "second_empire_campaign").length,
  third_republic_candidates: candidates.filter((c) => c.taxonomy.startsWith("third_republic")).length,
  existing_family_candidates: candidates.filter((c) => c.existing_family_in_local_records).length,
  new_difference_candidates: candidates.filter((c) => !c.existing_family_in_local_records && c.family).length,
  boundary_exclusions: candidates.filter((c) => c.taxonomy.startsWith("boundary")).length,
  source_swept_rows: rawRows.length,
};
const pdfExists = fs.existsSync(pdfPath);
const sweep = {
  source_id: "france_second_third_republic_official_commemoratives",
  source_name: "Les médailles commémoratives — official Musée de la Légion d’honneur / Grande Chancellerie PDF",
  as_of: asOf,
  accessed: asOf,
  status: "complete_page_segment_with_boundary_context",
  source_complete: true,
  sweep_method: "Downloaded the official PDF once, verified PDF metadata, extracted text with pdfplumber, rendered both pages with Poppler at 120 dpi, and visually inspected both rendered pages. Recorded all named Second Empire and Third Republic medal entries plus explicit foreign/non-official boundary notes.",
  page_count: 2,
  pages_reviewed: [1, 2],
  sections_reviewed: ["Le Second Empire", "La IIIe République"],
  continuation_tokens_exhausted: true,
  unresolved_page_segments: [],
  candidate_rows: rawRows.length,
  coverage: counts,
  pdf: { url: urls.pdf, local_path: "sources/cache/france_second_third_republic/les_medaille_commemoratives_francaises.pdf", bytes: pdfExists ? fs.statSync(pdfPath).size : null, sha256: sha256(pdfPath), render_dir: "sources/cache/france_second_third_republic/pdf_render", rendered_pages: renderedPages, extraction_method: "pdfplumber read-only extraction" },
  raw_candidate_file: "data/raw_candidates/france_second_third_republic_official_commemoratives.jsonl",
  metadata_cache_directory: "sources/cache/france_second_third_republic",
  image_bytes_downloaded: false,
  failures: [],
  next: ["Sweep SAMLHOC Tonkin page for decree and object/image candidates.", "Sweep Légifrance for primary legal texts for uncovered 1870, Dahomey, China 1901 and WWI families.", "Use Paris Musées and Monnaie de Paris for open/licensed complete object views."],
};
writeJson(sweepPath, sweep);

const atlas = {
  source_atlas_id: "france_second_third_republic_source_matrix",
  as_of: asOf,
  scope: { granting_system: "France, central state and national institutions", periods: ["Second Empire 1852–1870", "Third Republic 1870–1940"], include: ["new awards created during each period", "earlier awards still awarded during each period", "formal model changes and period bars"], exclude: ["foreign awards merely authorized for wear", "non-official/private commemoratives", "ordinary coins, badges and exhibition souvenirs"] },
  difference_method: "Existing family IDs were read only from the three local France volume records (the dated Second Empire pack, the consolidated Third Republic volume, and the Third Republic pack1 record file). Candidate rows are classified as existing-family variant/coverage gaps, new difference candidates, or explicit boundary exclusions.",
  existing_family_ids: [...existingFamilies].sort(),
  taxonomy,
  sources,
  candidates,
  selected_sweep: { source_id: "FR-OFFICIAL-COMMEMORATIVE-PDF", reason: "Highest combined authority and period coverage among accessible sources; one two-page official catalogue covers both target periods and gives named awards, decree dates, type details and page illustrations.", sweep_state: "data/source_sweeps/france_second_third_republic_official_commemoratives.json", raw_candidates: "data/raw_candidates/france_second_third_republic_official_commemoratives.jsonl", candidate_rows: rawRows.length, pages_reviewed: 2 },
  counts,
  checkpoints: { matrix_created: true, selected_source_downloaded: pdfExists, selected_source_rendered_and_viewed: renderedPages.length === 2, raw_candidates_written: fs.existsSync(rawPath), next_position: "SAMLHOC Tonkin, then legal/object sources for missing 1870, Dahomey, China 1901 and WWI entries." },
};
writeJson(atlasPath, atlas);
console.log(JSON.stringify({ atlas: atlasPath, sweep: sweepPath, raw_candidates: rawPath, candidates: candidates.length, existing: counts.existing_family_candidates, new_difference: counts.new_difference_candidates, boundary: counts.boundary_exclusions, pdf_sha256: sha256(pdfPath) }));
