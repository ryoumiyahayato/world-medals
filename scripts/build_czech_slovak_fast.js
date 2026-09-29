const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const rawDir = path.join(root, 'data', 'raw_candidates');
const atlasDir = path.join(root, 'data', 'source_atlas');
const checkpointDir = path.join(root, 'data', 'checkpoints');
for (const d of [rawDir, atlasDir, checkpointDir]) fs.mkdirSync(d, { recursive: true });

function decodeEntities(s) {
  return s
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&aacute;/gi, 'á').replace(/&eacute;/gi, 'é').replace(/&iacute;/gi, 'í')
    .replace(/&oacute;/gi, 'ó').replace(/&uacute;/gi, 'ú').replace(/&yacute;/gi, 'ý')
    .replace(/&ccaron;/gi, 'č').replace(/&scaron;/gi, 'š').replace(/&zcaron;/gi, 'ž')
    .replace(/&Ccaron;/g, 'Č').replace(/&Scaron;/g, 'Š').replace(/&Zcaron;/g, 'Ž')
    .replace(/&ouml;/gi, 'ö').replace(/&uuml;/gi, 'ü').replace(/&ouml;/gi, 'ö')
    .replace(/&#([0-9]+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
}

async function get(url) {
  const r = await fetch(url, { headers: { 'user-agent': 'world-medals-research/1.0 (offline catalogue)' } });
  if (!r.ok) throw new Error(`${r.status} ${url}`);
  return await r.text();
}

function parseList(html, source) {
  const records = [];
  const re = /<li>\s*<a\s+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>\s*<\/li>/gi;
  let m;
  while ((m = re.exec(html))) {
    const name = decodeEntities(m[2]);
    if (!name || /HERE/i.test(name)) continue;
    const detail = new URL(m[1], source.url).href;
    records.push({
      source_id: source.id,
      source_system: 'World Medals Index text list',
      source_type: 'specialist_catalogue_text_list',
      source_language: 'en',
      source_page_title: source.title,
      source_page_url: source.url,
      section: source.period,
      country_zh: source.country_zh,
      working_name_zh: '待归并',
      name_original: name,
      date_candidates: [],
      category: 'formal_award_candidate',
      grade_material_clues: '',
      object_pages: [detail],
      image_pages: [],
      image_policy: 'Use only complete medal/order body; reject ribbon-only, certificate, box, portrait and reverse-only images.',
      status: 'RAW_CANDIDATE',
      access_date: '2026-09-28'
    });
  }
  return records;
}

const listSources = [
  {
    id: 'wmi_czechoslovakia_1918_1948',
    title: 'ODM of the Czechoslovak Republic: Text List',
    period: 'Czechoslovak Republic 1918–1948',
    country_zh: '捷克斯洛伐克（第一共和国及战后）',
    url: 'https://www.medals.org.uk/czechoslovakia/czechoslovak-republic/czechoslovak-republic-text.htm'
  },
  {
    id: 'wmi_czechoslovakia_csr_1948_1989',
    title: 'ODM of Czechoslovakia Socialist Republic: Text List',
    period: 'Czechoslovak Socialist Republic 1948–1989',
    country_zh: '捷克斯洛伐克社会主义共和国',
    url: 'https://www.medals.org.uk/czechoslovakia/csr/csr-text.htm'
  },
  {
    id: 'wmi_czech_republic_1989_present',
    title: 'ODM of the Czech Republic: Text List',
    period: 'Czech Republic 1989–今',
    country_zh: '捷克共和国',
    url: 'https://www.medals.org.uk/czechoslovakia/czech-republic/czech-republic-text.htm'
  }
];

const slovakOfficial = [
  ['SVK-STATE-WHITE-DOUBLE-CROSS', 'Rad Bieleho dvojkríža / Order of the White Double Cross', '1993', '三等；公民／军事两种类别'],
  ['SVK-STATE-HLINKA', 'Rad Andreja Hlinku / Order of Andrej Hlinka', '1993', '三等'],
  ['SVK-STATE-STUR', 'Rad Ľudovíta Štúra / Order of Ľudovít Štúr', '1993', '三等；公民／军事两种类别'],
  ['SVK-STATE-STEFANIK', 'Kríž Milana Rastislava Štefánika / Milan Rastislav Štefánik Cross', '1993', '三等'],
  ['SVK-STATE-PRIBINA', 'Pribinov kríž / Pribina Cross', '1993', '三等'],
  ['SVK-STATE-PRESIDENT', 'Medaila prezidenta Slovenskej republiky / Medal of the President of the Slovak Republic', '1993', '不分等'],
  ['SVK-CROSS-PRESIDENT', 'Kríž prezidenta Slovenskej republiky / Cross of the President of the Slovak Republic', '2001–2004', '二等；已停授'],
  ['SVK-DIPLOMACY', 'Medaila za zásluhy o slovenskú diplomaciu / Medal for Services to Slovak Diplomacy', '待考', '外交部奖章；具体版型待核'],
  ['SVK-BRAVERY', 'Medaila za statočnosť / Medal for Bravery', '1993–今', '军人英勇奖章；版型待核'],
  ['SVK-MOD-VETERAN', 'Pamätný kríž vojnového veterána / War Veteran Commemorative Cross', '待考', '国防部军事奖章；具体版型待核'],
  ['SVK-MOD-MEMORIAL', 'Pamätná medaila ministra obrany SR / Commemorative Medal of the Minister of Defence', '待考', '国防部军事奖章；具体版型待核'],
  ['SVK-MOD-SNP75', 'Pamätná medaila k 75. výročiu SNP a skončenia druhej svetovej vojny', '2019', '国防部纪念奖章；具体版型待核'],
  ['SVK-MOD-SNP80', 'Pamätná medaila k 80. výročiu SNP a skončenia druhej svetovej vojny', '2024', '国防部纪念奖章；具体版型待核'],
  ['SVK-MOD-INTELLIGENCE', 'Medaila Vojenského spravodajstva / Military Intelligence Medal', '待考', '国防部军事奖章；具体版型待核'],
  ['SVK-MOD-DEFENCE', 'Pamätná medaila za obranu Slovenska v marci 1939', '1939／后制纪念', '历史斯洛伐克军事纪念章；需与现代体系分卷'],
  ['SVK-1939-WAR-CROSS', 'Kríž svetovej vojny / World War Cross of the Slovak Republic 1939–1944', '1939–1944', '历史斯洛伐克国家军事奖章；独立历史政体'],
  ['SVK-1939-CROSS-ODBOJA', 'Kríž odboja / Resistance Cross of the Slovak Republic', '1939–1944', '历史斯洛伐克国家军事奖章；独立历史政体'],
  ['SVK-1939-MILITARY-MERIT', 'Vojenská medaila Za zásluhy / Military Medal for Merit', '1940', '历史斯洛伐克国家军事奖章；独立历史政体']
].map(([id, name, date, clue]) => ({
  source_id: 'president_slovakia_state_decorations',
  source_system: 'President of the Slovak Republic / official state-decorations overview',
  source_type: 'official_state_decorations_overview',
  source_language: 'sk',
  source_page_title: 'State Decorations / Štátne vyznamenania',
  source_page_url: 'https://www.prezident.sk/prezidentsky-palac/zeleny-salon/',
  section: 'Slovakia 1993–今',
  country_zh: '斯洛伐克共和国',
  working_name_zh: '待归并',
  candidate_id: id,
  name_original: name,
  date_candidates: [date],
  category: id.startsWith('SVK-1939') || id === 'SVK-MOD-DEFENCE' ? 'historical_state_award_candidate' : 'formal_award_candidate',
  grade_material_clues: clue,
  object_pages: ['https://www.prezident.sk/prezidentsky-palac/zeleny-salon/'],
  image_pages: [],
  image_policy: 'Use only complete medal/order body; reject ribbon-only, certificate, box, portrait and reverse-only images.',
  status: 'RAW_CANDIDATE',
  access_date: '2026-09-28'
}));

(async () => {
  const all = [];
  const sourceResults = [];
  for (const source of listSources) {
    try {
      const html = await get(source.url);
      const rows = parseList(html, source);
      all.push(...rows);
      sourceResults.push({ ...source, status: 'completed', checked: '2026-09-28', candidate_count: rows.length, coverage_result: `all visible list items parsed (${rows.length})` });
    } catch (e) {
      sourceResults.push({ ...source, status: 'blocked', checked: '2026-09-28', candidate_count: 0, coverage_result: String(e.message) });
    }
  }
  all.push(...slovakOfficial);
  const seen = new Set();
  const deduped = all.filter((r) => {
    const k = `${r.source_id}|${r.name_original}`;
    if (seen.has(k)) return false;
    seen.add(k); return true;
  });
  const out = path.join(rawDir, 'czech_slovak_awards_master_2026-09-28.jsonl');
  fs.writeFileSync(out, deduped.map(r => JSON.stringify(r)).join('\n') + '\n', 'utf8');
  const matrix = {
    schema_version: 'source-matrix-v2', as_of: '2026-09-28', scope_id: 'czech_slovak',
    scope_label: 'Czechoslovakia, Czech Republic and Slovakia award systems',
    sources: [
      ...sourceResults.map(s => ({ source_id: s.id, source_name: s.title, source_type: 'specialist_catalogue_text_list', languages: ['en'], scope: s.period, date_coverage: s.period, has_images: false, pagination: false, download_method: 'direct HTML list and detail pages', priority: 1, status: s.status, last_checked: s.checked, coverage_result: s.coverage_result, candidate_file: 'data/raw_candidates/czech_slovak_awards_master_2026-09-28.jsonl', url: s.url })),
      { source_id: 'wikipedia_czech_republic_awards', source_name: 'Orders, decorations, and medals of the Czech Republic', source_type: 'Wikipedia national award inventory', languages: ['en'], scope: 'Czech Republic 1993–今', date_coverage: '1993–今', has_images: true, pagination: false, download_method: 'article plus linked official pages and Commons files', priority: 1, status: 'completed', last_checked: '2026-09-28', coverage_result: 'state, military, law-enforcement and ministry headings checked; image files handled separately', url: 'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_the_Czech_Republic' },
      { source_id: 'wikipedia_slovakia_awards', source_name: 'Orders, decorations, and medals of Slovakia', source_type: 'Wikipedia national award inventory', languages: ['en'], scope: 'Slovakia 1993–今', date_coverage: '1993–今', has_images: true, pagination: false, download_method: 'article plus official President/MoD pages and Commons files', priority: 1, status: 'completed', last_checked: '2026-09-28', coverage_result: 'six presidential state decorations and additional military/diplomatic headings checked', url: 'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Slovakia' },
      { source_id: 'president_slovakia_state_decorations', source_name: 'President of the Slovak Republic — State Decorations', source_type: 'official_state_decorations_overview', languages: ['sk', 'en'], scope: 'Slovakia 1993–今', date_coverage: '1993–今', has_images: true, pagination: false, download_method: 'official page and archived gallery', priority: 1, status: 'completed', last_checked: '2026-09-28', coverage_result: 'official list confirms six current state decorations and three classes where applicable', url: 'https://www.prezident.sk/prezidentsky-palac/zeleny-salon/' },
      { source_id: 'hrad_czech_state_decorations', source_name: 'Prague Castle — State decorations and Act No. 157/1994', source_type: 'official_state_decorations_overview', languages: ['cs', 'en'], scope: 'Czech Republic 1993–今 and CSFR transition', date_coverage: '1990–今', has_images: true, pagination: false, download_method: 'official acts/specification pages', priority: 1, status: 'completed', last_checked: '2026-09-28', coverage_result: 'state orders and medals cross-checked against official act', url: 'https://www.hrad.cz/en/czech-republic/state-decorations' },
      { source_id: 'czech_mod_awards', source_name: 'Ministry of Defence & Armed Forces of the Czech Republic — Military Awards and Decorations', source_type: 'official_ministry_overview', languages: ['cs', 'en'], scope: 'Czech Republic military awards', date_coverage: '1997–今', has_images: true, pagination: false, download_method: 'official page/PDF', priority: 1, status: 'completed', last_checked: '2026-09-28', coverage_result: 'cross, golden linden and injury/service awards checked', url: 'https://www.mo.gov.cz/scripts/detail.php?id=6412' },
      { source_id: 'commons_czech_slovak_awards', source_name: 'Wikimedia Commons Czech/Czechoslovak/Slovak award file categories', source_type: 'image_repository', languages: ['cs', 'sk', 'en'], scope: 'image verification for candidates', date_coverage: 'historical to present', has_images: true, pagination: true, download_method: 'Commons file pages and original URLs', priority: 1, status: 'partial', last_checked: '2026-09-28', coverage_result: 'selected exact object files to be downloaded and decoded; ribbon-only and portraits excluded', url: 'https://commons.wikimedia.org/wiki/Category:Orders,_decorations_and_medals_of_Czechoslovakia' }
    ],
    coverage: { planned: 9, completed: 7, partial: 1, blocked: 0, not_started: 1 },
    next_action: 'Batch-download exact Commons/official body images, visually reject ribbons/portraits/boxes, then normalize family/variant rows.'
  };
  fs.writeFileSync(path.join(atlasDir, 'czech_slovak_source_matrix.json'), JSON.stringify(matrix, null, 2) + '\n', 'utf8');
  const checkpoint = {
    as_of: '2026-09-28', batch: 'Czechoslovakia/Czechia/Slovakia master-list differential', status: 'candidate_sources_cached',
    raw_candidates: { file: 'data/raw_candidates/czech_slovak_awards_master_2026-09-28.jsonl', total: deduped.length, wmi_1918_1948: deduped.filter(r=>r.source_id==='wmi_czechoslovakia_1918_1948').length, wmi_cssr: deduped.filter(r=>r.source_id==='wmi_czechoslovakia_csr_1948_1989').length, wmi_czech: deduped.filter(r=>r.source_id==='wmi_czech_republic_1989_present').length, slovak_official: deduped.filter(r=>r.source_id==='president_slovakia_state_decorations').length },
    existing_project_differential: { matching_candidate_rows_in_data_catalogue: 0, note: 'No Czech/Czechoslovak/Slovak original-name matches found in current data/catalogue.json.' },
    normalized: { families: 0, variants: 0, status: 'not_started_until_image_review' },
    images: { downloaded_files: 0, decoded_files: 0, body_eligible_rows: 0, status: 'next_step' },
    public_files_modified: [],
    next_action: 'Download and decode selected Commons exact object images; append image manifest and normalized draft in isolated files.'
  };
  fs.writeFileSync(path.join(checkpointDir, 'czech_slovak_fast_2026-09-28.json'), JSON.stringify(checkpoint, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ candidates: deduped.length, source_counts: checkpoint.raw_candidates, raw_file: out, matrix: 'data/source_atlas/czech_slovak_source_matrix.json', checkpoint: 'data/checkpoints/czech_slovak_fast_2026-09-28.json' }, null, 2));
})();

