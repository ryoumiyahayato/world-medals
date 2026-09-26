import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const asOf = '2026-09-26';
const batchId = 'SWE-SHM-ORDERS-B1-20260926';
const cacheRoot = path.join(root, 'sources/cache/sweden_shm_api');
const outputDirs = [
  'data/raw_candidates/sweden',
  'data/volumes',
  'data/checkpoints',
  'data/source_atlas',
  'data/queues',
  'sources',
  'assets/images/sweden_shm_orders_batch1',
].map(p => path.join(root, p));

const families = {
  Serafimer: {
    family: 'SWE-SERAFIMERORDEN',
    name_zh: '塞拉菲默尔勋章',
    original_name: 'Serafimerorden',
    issuer: '瑞典王国·Serafimerorden授予体系',
    reason: 'SHM对象记录将Serafimerorden作为独立具名授勋体系，并分别标记其章体与星章；等级、星章及佩戴方式均保留在此family内。',
  },
  Svards: {
    family: 'SWE-SVARDSORDEN',
    name_zh: '剑勋章',
    original_name: 'Svärdsorden',
    issuer: '瑞典王国·Svärdsorden授予体系',
    reason: 'SHM对象记录将Svärdsorden作为独立具名授勋体系；骑士、指挥官、大十字及星章是同一family的等级／版型。',
  },
  Nordstjarne: {
    family: 'SWE-NORDSTJARNEORDEN',
    name_zh: '北极星勋章',
    original_name: 'Nordstjärneorden',
    issuer: '瑞典王国·Nordstjärneorden授予体系',
    reason: 'SHM对象记录将Nordstjärneorden作为独立具名授勋体系；骑士、指挥官、大十字及星章是同一family的等级／版型。',
  },
  Vasa: {
    family: 'SWE-VASAORDEN',
    name_zh: '瓦萨勋章',
    original_name: 'Vasaorden',
    issuer: '瑞典王国·Vasaorden授予体系',
    reason: 'SHM对象记录将Vasaorden作为独立具名授勋体系；骑士、指挥官、大十字及星章是同一family的等级／版型。',
  },
  CarlXIII: {
    family: 'SWE-CARL-XIII-ORDEN',
    name_zh: '卡尔十三世勋章',
    original_name: 'Carl XIII:s orden',
    issuer: '瑞典王国·Carl XIII:s orden授予体系',
    reason: 'SHM对象记录将Carl XIII:s orden作为独立具名授勋体系；颈章、胸章与小型章均是同一family的版型。',
  },
};

const selectedIds = [
  { id: '9D13DF03-48AB-4CB5-8523-AB59E847540F', key: 'Serafimer', variant: '骑士星章；刺绣大绶／披肩佩戴式星章，约1800年', main: true },
  { id: '3AF73294-0BAD-480D-BB67-62827DA201D4', key: 'Serafimer', variant: '骑士星章；Olof Wihlborg制造，1818年', main: false },
  { id: '33B64533-18D7-4176-9412-190FB83AB7C8', key: 'Serafimer', variant: '骑士十字章；SHM标注1860年式', main: false },
  { id: '71380294-7B11-4654-967C-D595EDD80C8B', key: 'Svards', variant: '大十字骑士章（第二级）；颈章佩戴式，1810–1814年', main: true },
  { id: '07418087-2FD4-46E4-B9FC-905C5DE111FC', key: 'Svards', variant: '指挥官十字章；1856年后式', main: false },
  { id: '8D8EDE99-61B7-41D8-BE06-41FDFF61B58F', key: 'Svards', variant: '骑士一级十字章；1856年后式', main: false },
  { id: '6FF43489-DBEF-4787-8A96-5DEC45D7C312', key: 'Nordstjarne', variant: '大十字胸星；1800–1820年式', main: true },
  { id: '75AE6A5C-3797-49DA-9753-967681151248', key: 'Nordstjarne', variant: '骑士十字章；1780–1799年式', main: false },
  { id: '76AC0B68-8590-4B0D-8F1A-EC5712CFD236', key: 'Nordstjarne', variant: '大十字胸星；1952年式', main: false },
  { id: 'A913107C-F0DD-4B5D-AE38-BBA12CFFA7C5', key: 'Vasa', variant: '大十字指挥官星章；约1800年式', main: true },
  { id: 'B60025C7-3162-4CCE-B17F-EBD307653686', key: 'Vasa', variant: '骑士十字章；1772年式', main: false },
  { id: '5F18D93A-1EC5-40AB-BB40-52B09661DE35', key: 'Vasa', variant: '指挥官十字章；1911年式', main: false },
  { id: 'C6019EA9-9955-45D4-B735-2E4C4A7BF5F3', key: 'CarlXIII', variant: '骑士颈章；馆方定年1811年', main: true },
  { id: '86A610F3-D989-4BC8-87E8-17DCBCACD8A8', key: 'CarlXIII', variant: '骑士胸章；1800–1820年式', main: false },
  { id: 'FE570A1D-3A30-4265-BA1E-B2144E97942C', key: 'CarlXIII', variant: '骑士颈章；1800–1899年馆方宽定年', main: false },
];

function familyFromText(text) {
  if (/serafimer/i.test(text)) return 'Serafimer';
  if (/(torn\s*[-–]?\s*och|portugal)/i.test(text) && /svärdsorden|svardsorden/i.test(text)) return null;
  if (/svärdsorden|svardsorden/i.test(text)) return 'Svards';
  if (/nordstjärneorden|nordstjarneorden/i.test(text)) return 'Nordstjarne';
  if (/vasaorden/i.test(text)) return 'Vasa';
  if (/(carl|karl)\s*xiii(?::s)?\s*(orden)?/i.test(text)) return 'CarlXIII';
  return null;
}

function classify(item, queryNames) {
  const title = item.title || '';
  const label = item.accessibilityLabel || '';
  const objectName = item.fields?.objectNames?.value || '';
  const combined = `${title} ${label} ${objectName}`;
  const objectLower = objectName.toLowerCase();
  const badgeTerm = /ordenstecken|ordenskors|kraschan|bröstkors|halskors|riddarkors|kommendörskors|riddartecken|storkorskraschan|bröstdekoration/i.test(combined);
  const clothingTerm = /\b(rock|byxa|hatt|stövel|gehäng|dräkt|jacka|handske|skärp|kåpa|livrock|sko|spira|stav|mantel|klänning|mössa|slida|uniform|etui|knapp|sköld)\b|ordensdräkt|häroldsdräkt/i.test(objectLower);
  const ribbonOnly = /ordensband|axelband|halsband|band(?:\s|$)/i.test(objectLower) && !/kraschan|kors|ordenstecken|riddartecken/i.test(objectLower);
  if (clothingTerm) return { classification: 'clothing_or_equipment', familyKey: null, note: 'Object-name field identifies clothing, accoutrement, equipment, case, or heraldic article; excluded from medal body variants.' };
  if (ribbonOnly) return { classification: 'standalone_ribbon', familyKey: null, note: 'Object-name field identifies a ribbon/band without a separately named decoration body; excluded from body variants.' };
  if (badgeTerm) {
    const familyKey = familyFromText(combined);
    if (familyKey) return { classification: 'named_order_insignia_candidate', familyKey, note: 'Award body/star vocabulary and a specific Swedish order name occur in SHM metadata; the shared query term alone was not used to assign the family.' };
    return { classification: 'other_order_or_insignia_candidate', familyKey: null, note: 'Badge-like vocabulary appears, but metadata does not establish one of the five in-scope Swedish order families.' };
  }
  return { classification: 'other_or_unresolved', familyKey: null, note: 'Broad API hit; object metadata does not identify an in-scope badge body. Retained for later review.' };
}

async function ensureDirs() {
  await Promise.all(outputDirs.map(p => fs.mkdir(p, { recursive: true })));
}

async function readApiSweep() {
  const queryDirs = await fs.readdir(cacheRoot, { withFileTypes: true });
  const seen = new Map();
  const perQuery = {};
  const cachePages = [];
  for (const dirent of queryDirs.filter(d => d.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    const query = dirent.name;
    const dir = path.join(cacheRoot, query);
    const pageNames = (await fs.readdir(dir)).filter(n => /^offset_\d+\.json$/.test(n)).sort();
    let queryHits = 0;
    let totalResults = null;
    perQuery[query] = { pages: pageNames.length, hits: 0, declared_total: null };
    for (const pageName of pageNames) {
      const fullPath = path.join(dir, pageName);
      const bytes = await fs.readFile(fullPath);
      const page = JSON.parse(bytes.toString('utf8'));
      totalResults ??= page.totalResults ?? null;
      const offset = Number(pageName.match(/\d+/)[0]);
      const digest = crypto.createHash('sha256').update(bytes).digest('hex');
      cachePages.push({ path: path.relative(root, fullPath).replaceAll(path.sep, '/'), offset, bytes: bytes.length, sha256: digest, returned_items: (page.items || []).length, total_results: page.totalResults ?? null });
      for (const item of page.items || []) {
        queryHits += 1;
        const old = seen.get(item.id);
        if (old) {
          old.queryNames.add(query);
          old.locations.push({ query, offset, cache: path.relative(root, fullPath).replaceAll(path.sep, '/') });
        } else {
          seen.set(item.id, { item, queryNames: new Set([query]), locations: [{ query, offset, cache: path.relative(root, fullPath).replaceAll(path.sep, '/') }] });
        }
      }
    }
    perQuery[query].hits = queryHits;
    perQuery[query].declared_total = totalResults;
    if (totalResults !== null && queryHits !== totalResults) throw new Error(`Incomplete pagination for ${query}: ${queryHits} != ${totalResults}`);
  }
  return { seen, perQuery, cachePages };
}

function compactRecord(entry) {
  const item = entry.item;
  const queryNames = [...entry.queryNames].sort();
  const triage = classify(item, queryNames);
  return {
    source_id: 'shm-lrk-public-api',
    source_type: 'museum_api_raw_candidate',
    accessed: asOf,
    query_hits: queryNames,
    page_locations: entry.locations,
    family_candidate: triage.familyKey ? families[triage.familyKey].family : null,
    triage_class: triage.classification,
    triage_note: triage.note,
    object_id: item.id,
    object_page_url: item.url,
    api_title: item.title,
    original_object_name: item.fields?.objectNames?.value || null,
    object_number: item.fields?.objectNumber?.value || null,
    object_dating_candidate: item.fields?.productionDates?.value || null,
    institution: item.fields?.managingInstitution?.value || item.image?.publisher || null,
    image_url_original_endpoint: item.image?.url || null,
    image_url_large_endpoint: item.image?.sizes?.large?.url || null,
    image_width_reported: item.image?.width || null,
    image_height_reported: item.image?.height || null,
    image_credit: item.image?.credits || [],
    image_credit_line: item.image?.displayCredits || null,
    image_license_code: item.image?.license?.code || null,
    image_license_name: item.image?.license?.name || null,
    raw_api_item: item,
    status: 'RAW_CANDIDATE',
  };
}

async function findExistingMatches() {
  const targets = new Set(Object.values(families).map(x => x.original_name.toLowerCase()));
  const files = [path.join(root, 'data/catalogue.json')];
  for (const f of await fs.readdir(path.join(root, 'data/volumes'))) if (f.endsWith('.json') && !f.includes('sweden_shm_orders_batch1')) files.push(path.join(root, 'data/volumes', f));
  const results = [];
  for (const file of files) {
    try {
      const data = JSON.parse(await fs.readFile(file, 'utf8'));
      const text = JSON.stringify(data).toLowerCase();
      for (const term of targets) if (text.includes(term.toLowerCase())) results.push({ file: path.relative(root, file).replaceAll(path.sep, '/'), term });
    } catch {}
  }
  return { files_checked: files.map(f => path.relative(root, f).replaceAll(path.sep, '/')), name_hits: results };
}

async function writeJson(file, data) {
  await fs.writeFile(path.join(root, file), `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

async function main() {
  await ensureDirs();
  const { seen, perQuery, cachePages } = await readApiSweep();
  const entries = [...seen.values()];
  const rawRows = entries.map(compactRecord);
  const triageCounts = {};
  const familyCounts = {};
  const licenseCounts = {};
  for (const row of rawRows) {
    triageCounts[row.triage_class] = (triageCounts[row.triage_class] || 0) + 1;
    if (row.family_candidate) familyCounts[row.family_candidate] = (familyCounts[row.family_candidate] || 0) + 1;
    const license = row.image_license_code || 'missing';
    licenseCounts[license] = (licenseCounts[license] || 0) + 1;
  }

  const selected = selectedIds.map(selection => {
    const row = rawRows.find(x => x.object_id === selection.id);
    if (!row) throw new Error(`Selected object missing from complete cache: ${selection.id}`);
    if (row.family_candidate !== families[selection.key].family) throw new Error(`Family mismatch on ${selection.id}: ${row.family_candidate}`);
    if (!['CC BY 4.0', 'PDM'].includes(row.image_license_code)) throw new Error(`Unusable rights for selected object ${selection.id}: ${row.image_license_code}`);
    return {
      candidate_id: `${families[selection.key].family}-LRK-${row.object_number.replace(/[^A-Za-z0-9]+/g, '-')}`,
      award_family: families[selection.key].family,
      country_zh: '瑞典王国',
      issuer: families[selection.key].issuer,
      name: families[selection.key].name_zh,
      original: families[selection.key].original_name,
      object_dating: row.object_dating_candidate,
      variant_candidate: selection.variant,
      object_page_url: row.object_page_url,
      object_id: row.object_id,
      object_number: row.object_number,
      api_title: row.api_title,
      original_object_name: row.original_object_name,
      original_image_url: row.image_url_original_endpoint,
      large_image_url: row.image_url_large_endpoint,
      credit: row.image_credit,
      credit_line: row.image_credit_line,
      license: row.image_license_code,
      license_scope: row.raw_api_item.image?.license?.scope || null,
      first_pass_priority: Boolean(selection.main),
      image_status: 'blocked_remote_download_not_attempted_for_this_item',
      local_image: null,
      html_eligible: false,
      evidence_note: 'SHM search API metadata retained; image license and official media URL are recorded. Original bytes were not retrieved or decoded in this environment, so this is not a merge-ready illustrated record.',
    };
  });

  const pagesPerQuery = Object.fromEntries(Object.entries(perQuery).map(([k, v]) => [k, { ...v, query_url: `https://samlingar.shm.se/api/v1/search?type=object&query=${encodeURIComponent(k === 'Carl_XIII_orden' ? 'Carl XIII:s orden' : k === 'Svardsorden' ? 'Svärdsorden' : k === 'Nordstjarneorden' ? 'Nordstjärneorden' : k)}&hasImage=1&institution=Livrustkammaren&limit=50` }]));
  const sourceMatrix = {
    schema_version: '2.0', as_of: asOf, scope_id: 'sweden_shm_orders',
    scope_label: '瑞典王国五个具名骑士团；SHM Livrustkammaren API完整分页扫描批次1',
    languages: ['sv', 'en'], taxonomy: ['museum_api', 'museum_object_record', 'official_statutes', 'image_media'],
    existing_coverage: {
      volumes_checked: await findExistingMatches(),
      existing_formal_records_in_this_batch_scope: 0,
      difference_result: 'SHM五个 order 名称在现有catalogue/volume文本中未检出正式对应行；本任务仅写隔离候选文件，未更改目录或公共入口。',
    },
    source_counts: { planned: 8, completed: 5, partial: 1, blocked: 1, not_started: 1 },
    sources: [
      ...Object.entries(pagesPerQuery).map(([query, meta]) => ({
        source_id: `se_shm_api_${query.toLowerCase()}`,
        source_name: `Statens historiska museer / Livrustkammaren — ${query} public search API`,
        base_url: meta.query_url,
        source_type: 'museum_object_api_paged_search', languages: ['sv'], regions_or_polities: ['Sweden / Kingdom of Sweden'],
        date_coverage: 'Collection object-production dating; not automatically an award establishment date.',
        content_coverage: `${meta.pages} cached 50-item pages; ${meta.hits} search hits; API-declared total ${meta.declared_total}. This query is complete for its current API result set, not exhaustive for all Swedish awards.`,
        has_images: true, image_quality_notes: 'Search API reports image dimensions as 0/null. Individual original-image resolution and completeness require downloading and visual inspection.',
        has_pagination: true, download_method: 'Public API pagination by offset; original JSON pages retained under sources/cache/sweden_shm_api/.',
        priority: 1, status: 'completed', last_checked: asOf,
        local_cache: `sources/cache/sweden_shm_api/${query}/offset_*.json`, raw_candidates: 'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl',
        license_note: 'API returns per-image rights fields (CC BY 4.0, PDM or BUS). BUS is excluded from this candidate batch; only exact image/item rights can be used.',
      })),
      {
        source_id: 'se_shm_object_pages_selected', source_name: 'SHM public object pages — selected direct detail checks',
        base_url: 'https://samlingar.shm.se/object/', source_type: 'museum_object_detail_page', languages: ['sv'],
        regions_or_polities: ['Sweden / Kingdom of Sweden'], date_coverage: 'Individual object dating, former ownership, object description, literature and image credit/license.',
        content_coverage: 'Directly opened and read selected object pages for 432_LRK (Svärdsorden) and 1855_LRK (Carl XIII:s orden); 2 detailed page records checked. Selected API metadata retained for all 15 image candidates; remaining detail pages were not independently cached.',
        has_images: true, image_quality_notes: 'Object pages can show multiple images, credits, and distinct per-image licenses. Do not assume all views share one license.',
        has_pagination: false, download_method: 'Official SHM object-page retrieval via web reading; page excerpts/evidence notes are in the source file.',
        priority: 1, status: 'partial', last_checked: asOf,
        local_cache: 'sources/sweden_shm_orders_batch1_sources_2026-09-26.json',
        coverage_result: 'Verified badge identities, object dates, dimensions/description where visible, and CC BY 4.0 credit lines for the two opened pages; other records remain API-metadata candidates.',
      },
      {
        source_id: 'se_shm_original_media_batch1', source_name: 'SHM original image media endpoints — selected badge/star candidates',
        base_url: 'https://media.samlingar.shm.se/item/', source_type: 'museum_original_media', languages: ['sv'],
        regions_or_polities: ['Sweden / Kingdom of Sweden'], date_coverage: 'Not applicable.',
        content_coverage: 'SHM public search service displays a notice that image files cannot currently be downloaded due to technical issues. A representative original large-image endpoint also timed out; no Swedish image bytes were saved. Fifteen individually licensed candidate URLs are preserved in the image manifest. Stop retries until the access condition changes.',
        has_images: true, image_quality_notes: 'No downloaded image was decoded or visually checked; image count for this batch is zero.',
        has_pagination: false, download_method: 'Direct `large` endpoint; connection timeout; no screenshot or preview substituted.',
        priority: 1, status: 'blocked', last_checked: asOf,
        local_cache: 'assets/images/sweden_shm_orders_batch1/images_manifest.json', coverage_result: 'No local image bytes; no image is HTML eligible.',
        service_status_notice: { url: 'https://samlingar.shm.se/sok', accessed: asOf, text_sv: 'Just nu har vi tekniska bekymmer som gör att det inte går att ladda ner bildfiler.', text_en: 'We are currently experiencing technical issues that prevent image files from being downloaded.' },
        rights_note: 'Selected candidates are CC BY 4.0 or PDM according to the API; retain author/institution and per-image license if download later succeeds.',
      },
      {
        source_id: 'se_sweden_official_order_statutes', source_name: 'Swedish official order statutes and Royal Order portal',
        base_url: null, source_type: 'official_regulation', languages: ['sv'], regions_or_polities: ['Kingdom of Sweden'],
        date_coverage: 'Founding dates, legal grades, award criteria and historic reform dates.', content_coverage: 'Not started in this museum-API package.',
        has_images: false, image_quality_notes: 'No visual source expected.', has_pagination: false, download_method: 'Not started.', priority: 1, status: 'not_started', last_checked: asOf,
        coverage_result: 'Required before assigning founding dates or making a full legal grade taxonomy.',
      },
    ],
    query_summary: pagesPerQuery,
    triage_summary: { unique_objects: rawRows.length, total_search_hits: Object.values(perQuery).reduce((n, x) => n + x.hits, 0), query_hit_duplicates: Object.values(perQuery).reduce((n, x) => n + x.hits, 0) - rawRows.length, unique_ids_in_multiple_queries: entries.filter(x => x.queryNames.size > 1).length, class_counts: triageCounts, family_candidate_counts: familyCounts, license_counts: licenseCounts },
    next_action: 'Wait for a working official SHM media endpoint or use an alternate licensed source. Download, decode and visually check the five first-priority whole badge/star files before marking any variant merge-ready; then independently sweep official order statutes.',
  };

  const sourceFile = {
    as_of: asOf, batch_id: batchId, source: 'Statens historiska museer (SHM), Livrustkammaren',
    api_base: 'https://samlingar.shm.se/api/v1/search',
    api_query_protocol: 'type=object&query={order-name}&hasImage=1&institution=Livrustkammaren&offset={0,50,...}',
    pagination: pagesPerQuery, cache_pages: cachePages,
    object_pages_read: [
      {
        object_id: '71380294-7B11-4654-967C-D595EDD80C8B', object_number: '432_LRK',
        url: 'https://samlingar.shm.se/object/71380294-7B11-4654-967C-D595EDD80C8B?type=object&query=Sv%C3%A4rdsorden&hasImage=1&institution=Livrustkammaren&offset=50&n=63',
        accessed: asOf, evidence: 'SHM page names a gold, white-enamel cross “Ordenstecken för riddare med stora korset av Svärdsorden”; dates the object 1810–1814; records weight 23 g, width 55 mm, height 80 mm, object no. 432_LRK. The historical inventory text says the star and neck badge belonged to a great-cross knight, second class. The page lists per-image CC BY 4.0 credits and additional separately licensed views.',
        image_credit_first_view: 'Lernestål, Erik; Livrustkammaren/SHM', image_license_first_view: 'CC BY 4.0',
      },
      {
        object_id: 'C6019EA9-9955-45D4-B735-2E4C4A7BF5F3', object_number: '1855_LRK',
        url: 'https://samlingar.shm.se/object/C6019EA9-9955-45D4-B735-2E4C4A7BF5F3?type=object&query=Carl%20XIII%3As%20orden&hasImage=1&institution=Livrustkammaren&n=33',
        accessed: asOf, evidence: 'SHM page identifies a Carl XIII:s orden knight neck cross, dates it 1811, describes the cross and crown attachment, and gives width 49 mm, height 65 mm, weight 225 g, object no. 1855_LRK. It lists a CC BY 4.0 first image credited to Per Åke Persson and two further views with their own credits/licenses.',
        image_credit_first_view: 'Persson, Per Åke; Livrustkammaren/SHM', image_license_first_view: 'CC BY 4.0',
      },
    ],
    media_access_note: 'SHM public search service notice says image files currently cannot be downloaded because of technical problems (https://samlingar.shm.se/sok); direct media retrieval also timed out. No bytes, dimensions, checksum or completeness claim recorded. Do not publish as an embedded image until obtained and decoded.',
  };

  const existingHits = sourceMatrix.existing_coverage.volumes_checked.name_hits;
  sourceMatrix.existing_coverage.existing_formal_records_in_this_batch_scope = existingHits.length ? 'needs_manual_review' : 0;
  sourceMatrix.existing_coverage.difference_result = existingHits.length ? 'Name-text hits exist in existing files and need a row-level diff before merge.' : sourceMatrix.existing_coverage.difference_result;

  const candidates = {
    as_of: asOf, batch_id: batchId,
    scope: '瑞典王国五个SHM馆藏骑士团的来源优先候选整理；排除服饰、仪仗器具及单独绶带；不把同一勋章的星章/等级拆成family。',
    status: 'candidate_intake_only_images_blocked', html_eligible_records: 0,
    family_count: Object.keys(families).length, selected_variant_candidate_count: selected.length,
    ready_for_merge_count: 0, raw_candidate_file: 'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl',
    source_matrix_file: 'data/source_atlas/sweden_source_matrix.json',
    families: Object.entries(families).map(([key, f]) => ({ family: f.family, name_zh: f.name_zh, original_names: [f.original_name], issuer: f.issuer, status: 'family_candidate_from_distinct_SHM_order_name', independent_family_reason: f.reason, candidate_object_count: familyCounts[f.family] || 0, candidate_variants: selected.filter(x => x.award_family === f.family) })),
    normalization_rule: '国家/时期/授予机构 → award_family → variant。仅五个独立具名瑞典骑士团分别作family；星章、颈章、肩绶佩章、等级、年式/制造商、绶带和微型章等留在各自family之下。',
    selected_variant_candidates: selected,
    counts: {
      raw_unique_objects: rawRows.length,
      unique_source_query_hits: Object.values(perQuery).reduce((n, x) => n + x.hits, 0),
      duplicate_query_appearances: Object.values(perQuery).reduce((n, x) => n + x.hits, 0) - rawRows.length,
      candidate_award_families: Object.keys(families).length,
      award_family_insignia_candidates_in_raw_pool: Object.values(familyCounts).reduce((n, x) => n + x, 0),
      candidate_variant_rows_selected: selected.length,
      variant_rows_ready_for_merge: 0,
      decoded_local_images: 0,
      specimen_photos: 0,
      unresolved_or_unreviewed_raw_objects: rawRows.filter(x => ['other_or_unresolved', 'other_order_or_insignia_candidate'].includes(x.triage_class)).length,
      clothing_equipment_exclusions: triageCounts.clothing_or_equipment || 0,
      standalone_ribbon_exclusions: triageCounts.standalone_ribbon || 0,
      image_rights_counts: licenseCounts,
    },
    note: '此文件是可追溯的隔离候选包，不是已配图的正式分卷。SHM媒体主机本次超时，未把在线缩略图、页面截屏或外链当作图片。',
  };

  const imageManifest = {
    as_of: asOf, batch_id: batchId,
    status: 'all_selected_images_pending_original_download',
    counts: { selected_urls: selected.length, local_files: 0, decoded_files: 0, visually_checked_files: 0 },
    network_block: { host: 'media.samlingar.shm.se', method: 'official SHM `large` endpoint', result: 'timeout; no retry loop', attempted_representative_media: selected.find(x => x.first_pass_priority)?.large_image_url },
    images: selected.map(x => ({
      object_id: x.object_id, object_number: x.object_number, family: x.award_family,
      source_page_url: x.object_page_url, source_original_url: x.original_image_url,
      source_large_image_url: x.large_image_url, author_or_credit: x.credit, credit_line: x.credit_line,
      license: x.license, license_scope: x.license_scope, reported_width: null, reported_height: null,
      local_path: null, sha256: null, decodable: false, visual_completeness_checked: false,
      status: 'pending_original_media_download', priority: x.first_pass_priority ? 1 : 2,
    })),
    rights_note: 'API license field applies to the selected media item only; object pages can contain other views with distinct credits and licenses. Keep BUS rows excluded. CC BY 4.0 requires attribution to the named creator and SHM; PDM should retain any known credit.',
  };

  const checkpoint = {
    batch_id: batchId, as_of: asOf, status: 'saved_candidate_package_media_blocked',
    scope: 'Sweden / five SHM Livrustkammaren order-family queries',
    source_coverage: { planned: 8, completed: 5, partial: 1, blocked: 1, not_started: 1 },
    counts: candidates.counts,
    completed: [
      'Paged all five SHM API result sets to their declared total counts and retained the 25 exact JSON response pages.',
      'Deduplicated 1,144 query appearances to 951 unique object IDs, retaining query and page-offset provenance.',
      'Triaged names into five in-scope badge/star families, other badge-like objects, gear/clothing, standalone ribbons, and unresolved records.',
      'Selected 15 clearly named CC BY 4.0/PDM image candidates (three per family); no BUS item selected.',
      'Read SHM detail pages for a Svärdsorden great-cross neck badge and a Carl XIII:s orden neck cross; page text confirms object descriptions, dates, dimensions, museum IDs, and per-image rights.',
    ],
    blocked_or_not_done: [
      'SHM public search page announces temporary technical issues preventing image-file downloads; the media.samlingar.shm.se large-image endpoint timed out. No original image bytes were obtained, decoded, checksumed, or visually inspected.',
      'The browser-save fallback was stopped by the Windows computer-use guard because it could not determine the current Chrome URL with sufficient confidence; no browser image save occurred.',
      'All 15 selected visual rows remain non-merge-ready; zero decoded local images and zero specimen photos.',
      'Official statutory sweep for order foundation dates and grade rules not started.',
      `${rawRows.length - selected.length} objects remain outside the selected 15; those are preserved in raw candidates and require later row-level screening; ${candidates.counts.unresolved_or_unreviewed_raw_objects} currently fall into unresolved/other by heuristic triage.`,
    ],
    diff: sourceMatrix.existing_coverage,
    next_start: { scope: 'Sweden SHM original images', action: 'Resume only when the official media endpoint is reachable or use an alternate licensed museum/Commons source; verify complete object, decode and save rights before any variant becomes merge-ready.', do_not_repeat: ['Repeated direct requests to media.samlingar.shm.se while timeout persists'] },
    files: [
      'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl',
      'data/volumes/sweden_shm_orders_batch1_2026-09-26_candidates.json',
      'data/volumes/sweden_shm_orders_batch1_2026-09-26_manifest.json',
      'data/source_atlas/sweden_source_matrix.json',
      'sources/sweden_shm_orders_batch1_sources_2026-09-26.json',
      'assets/images/sweden_shm_orders_batch1/images_manifest.json',
    ],
    shared_files_not_modified: ['index.html', 'site_build.py', 'data/catalogue.json', 'data/progress.json', 'public navigation/styles'],
  };

  const rawPath = path.join(root, 'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl');
  await fs.writeFile(rawPath, `${rawRows.map(x => JSON.stringify(x)).join('\n')}\n`, 'utf8');
  await writeJson('data/volumes/sweden_shm_orders_batch1_2026-09-26_candidates.json', candidates);
  await writeJson('data/volumes/sweden_shm_orders_batch1_2026-09-26_manifest.json', {
    as_of: asOf, volume: 'Sweden — SHM order candidates batch 1', batch_id: batchId,
    status: 'candidate_only_no_local_images_not_ready_for_public_merge',
    candidates_file: 'data/volumes/sweden_shm_orders_batch1_2026-09-26_candidates.json',
    sources_file: 'sources/sweden_shm_orders_batch1_sources_2026-09-26.json',
    source_matrix_file: 'data/source_atlas/sweden_source_matrix.json',
    raw_candidates_file: 'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl',
    checkpoint_file: 'data/checkpoints/sweden_shm_orders_batch1_2026-09-26.json',
    image_manifest: 'assets/images/sweden_shm_orders_batch1/images_manifest.json',
    counts: {
      planned_sources: 8, completed_sources: 5, partial_sources: 1, blocked_sources: 1, not_started_sources: 1,
      raw_candidates: rawRows.length, independent_award_families_candidate: Object.keys(families).length,
      candidate_variant_rows: selected.length, records_ready_for_merge: 0, local_images_decoded: 0,
      official_diagrams: 0, specimen_photos: 0,
      exclusions_clothing_equipment: triageCounts.clothing_or_equipment || 0,
      exclusions_ribbon_only: triageCounts.standalone_ribbon || 0,
      unreviewed_or_unresolved_objects: candidates.counts.unresolved_or_unreviewed_raw_objects,
    },
    family_ids: Object.values(families).map(x => x.family),
    image_note: 'No file is counted as a local image until original bytes are acquired, decoded, and checked for complete insignia.',
    merge_note: 'Candidate metadata only; do not append these candidate rows to public index until image or a permitted no-image appendix workflow is explicitly handled by parent.',
  });
  await writeJson('data/source_atlas/sweden_source_matrix.json', sourceMatrix);
  await writeJson('sources/sweden_shm_orders_batch1_sources_2026-09-26.json', sourceFile);
  await writeJson('assets/images/sweden_shm_orders_batch1/images_manifest.json', imageManifest);
  await writeJson('data/checkpoints/sweden_shm_orders_batch1_2026-09-26.json', checkpoint);
  await writeJson('data/queues/sweden_shm_orders_batch1_continuation_2026-09-26.json', {
    batch_id: batchId, as_of: asOf,
    discovery_queue: [{ task: 'official statutes and establishment dates', status: 'not_started', priority: 1 }],
    image_queue: selected.map(x => ({ object_id: x.object_id, family: x.award_family, object_page_url: x.object_page_url, original_url: x.large_image_url, license: x.license, status: 'blocked_on_media_host', priority: x.first_pass_priority ? 1 : 2 })),
    remaining_raw_sweep: { unique_objects: rawRows.length - selected.length, status: 'retained_for_later_screening', raw_jsonl: 'data/raw_candidates/sweden/shm_orders_api_2026-09-26.jsonl' },
  });
  console.log(JSON.stringify({ unique: rawRows.length, queries: perQuery, triage: triageCounts, familyCounts, licenseCounts, selected: selected.length, decodedImages: 0 }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });
