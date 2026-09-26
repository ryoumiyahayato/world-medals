import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const ROOT = process.cwd();
const API = 'https://commons.wikimedia.org/w/api.php';
const AS_OF = '2026-09-26';
const UA = 'world-medals-source-sweep/1.0 (research catalogue; no original-image downloads)';
const OUT = path.join(ROOT, 'data', 'raw_candidates', 'commons_ottoman.jsonl');
const STATE_PATH = path.join(ROOT, 'data', 'source_sweeps', 'commons_ottoman.json');
const CACHE = path.join(ROOT, 'sources', 'cache', 'commons_ottoman');
const CATEGORY_DELAY_MS = 700;
const IMAGE_BATCH_SIZE = 30;

// The first entry is the Commons umbrella category used by the project.  The
// remaining entries are the fixed high-level and award-specific seed roots.
// They are intentionally kept as exact current Commons category titles.
const SEEDS = [
  { key: 'commons_total', title: 'Category:Orders, decorations and medals of the Ottoman Empire' },
  { key: 'orders', title: 'Category:Orders of the Ottoman Empire' },
  { key: 'medals', title: 'Category:Medals of the Ottoman Empire' },
  { key: 'military_decorations', title: 'Category:Military decorations of the Ottoman Empire' },
  { key: 'ribbon_bars', title: 'Category:Ribbon bars of the Ottoman Empire' },
  { key: 'medjidie', title: 'Category:Order of the Medjidie' },
  { key: 'osmanieh', title: 'Category:Order of Osmanieh' },
  { key: 'glory', title: 'Category:Order of Glory (Ottoman Empire)' },
  { key: 'crescent', title: 'Category:Order of the Crescent' },
  { key: 'sefkat', title: 'Category:Şefkat Order' },
  { key: 'imtiyaz', title: 'Category:Imtiyaz Medal' },
  { key: 'liyakat', title: 'Category:Liyakat Medal' },
  { key: 'gallipoli_star', title: 'Category:Gallipoli Star' },
  { key: 'turkish_crimea', title: 'Category:Turkish Crimea Medal' },
  { key: 'syrian_campaign_1840', title: 'Category:Syrian Campaign Medal (1840)' },
];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const sha1 = (value) => crypto.createHash('sha1').update(value).digest('hex');
const sha256 = (value) => crypto.createHash('sha256').update(value).digest('hex');

function ensureDirs() {
  for (const dir of [path.dirname(OUT), path.dirname(STATE_PATH), CACHE]) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function readJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJson(file, value) {
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  fs.renameSync(tmp, file);
}

function metadataValue(meta, key) {
  const item = meta?.[key];
  if (!item) return null;
  if (typeof item === 'string') return item;
  return item.value ?? null;
}

function pageUrl(title) {
  return `https://commons.wikimedia.org/wiki/${encodeURIComponent(title.replaceAll(' ', '_'))}`;
}

function loadProcessedTitles() {
  const seen = new Set();
  if (!fs.existsSync(OUT)) return seen;
  for (const line of fs.readFileSync(OUT, 'utf8').split(/\r?\n/)) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      if (row.file_title) seen.add(row.file_title);
    } catch {
      // Preserve a possible partial final line; it will be rewritten by the
      // next successful run only if needed.
    }
  }
  return seen;
}

async function fetchJson(params, state, label) {
  const query = new URLSearchParams({ ...params, action: 'query', format: 'json', formatversion: '2' });
  const url = `${API}?${query.toString()}`;
  const cacheFile = path.join(CACHE, `${sha256(url)}.json`);
  if (fs.existsSync(cacheFile)) {
    try {
      return JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
    } catch {
      // A truncated cache entry is discarded below and fetched again.
    }
  }

  const maxAttempts = 7;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    await sleep(CATEGORY_DELAY_MS);
    try {
      const response = await fetch(url, { headers: { 'User-Agent': UA, Accept: 'application/json' } });
      const text = await response.text();
      if (!response.ok) {
        const error = new Error(`${response.status} ${response.statusText}`);
        error.code = response.status;
        error.body = text.slice(0, 500);
        throw error;
      }
      const data = JSON.parse(text);
      fs.writeFileSync(cacheFile, `${JSON.stringify(data)}\n`, 'utf8');
      state.api_requests += 1;
      return data;
    } catch (error) {
      const retryable = [429, 500, 502, 503, 504].includes(Number(error.code));
      if (!retryable || attempt === maxAttempts) {
        state.failures.push({ stage: label, url, error: String(error.message || error), attempts: attempt });
        return null;
      }
      const delay = Math.min(120000, 8000 * (2 ** (attempt - 1)) + Math.floor(Math.random() * 2000));
      console.log(`retry ${label} attempt ${attempt}/${maxAttempts} after ${delay}ms (${error.message})`);
      await sleep(delay);
    }
  }
  return null;
}

function saveState(state) {
  state.updated_at = new Date().toISOString();
  writeJson(STATE_PATH, state);
}

function initialState() {
  return {
    source_id: 'commons_ottoman',
    source_name: 'Wikimedia Commons Ottoman orders, medals, decorations and ribbon-bar category sweep',
    as_of: AS_OF,
    accessed: AS_OF,
    status: 'running',
    started_at: new Date().toISOString(),
    updated_at: null,
    completion_rule: 'Every currently visible subcategory and file page reachable from every fixed seed was paginated until its continuation token was exhausted; failures remain listed.',
    seed_categories: [],
    queue: [],
    visited_categories: [],
    category_log: {},
    pending_file_titles: [],
    processed_file_titles: [],
    counters: {
      categories_discovered: 0,
      categories_fetched: 0,
      category_member_requests: 0,
      category_member_entries_seen: 0,
      file_members_seen: 0,
      duplicate_file_members: 0,
      unique_files: 0,
      imageinfo_batches: 0,
      imageinfo_files_returned: 0,
      api_requests: 0,
    },
    failures: [],
  };
}

async function resolveSeeds(state) {
  if (state.seed_categories.length) return;
  const data = await fetchJson({ titles: SEEDS.map((x) => x.title).join('|'), prop: 'info' }, state, 'seed_resolution');
  const pages = data?.query?.pages ?? [];
  const byTitle = new Map(pages.map((page) => [page.title, page]));
  for (const seed of SEEDS) {
    const page = byTitle.get(seed.title);
    const resolved = page && !page.missing;
    state.seed_categories.push({
      ...seed,
      pageid: resolved ? page.pageid : null,
      resolved,
      page_url: pageUrl(seed.title),
    });
    if (resolved) {
      state.queue.push({ title: seed.title, root_seed: seed.key, path: [seed.title] });
    } else {
      state.failures.push({ stage: 'seed_resolution', category: seed.title, error: 'category page missing from current Commons API response' });
    }
  }
  state.counters.categories_discovered = state.queue.length;
  saveState(state);
}

function enqueueCategory(state, title, rootSeed, categoryPath) {
  if (!title || state.visited_categories.includes(title)) return false;
  if (state.queue.some((item) => item.title === title)) return false;
  state.queue.push({ title, root_seed: rootSeed, path: categoryPath });
  state.counters.categories_discovered += 1;
  return true;
}

async function fetchCategory(state, item, processedTitles, outHandle) {
  const title = item.title;
  const log = state.category_log[title] ?? {
    title,
    root_seed: item.root_seed,
    path: item.path,
    status: 'running',
    api_requests: 0,
    members_seen: 0,
    file_members: 0,
    subcategories: 0,
    continuation_pages: 0,
    continuation_exhausted: false,
    files_seen_titles: [],
  };
  state.category_log[title] = log;
  const newFileTitles = [];
  let continuation = null;
  let hadError = false;

  do {
    const params = {
      list: 'categorymembers',
      cmtitle: title,
      cmtype: 'file|subcat',
      cmlimit: 'max',
    };
    if (continuation) params.cmcontinue = continuation;
    const data = await fetchJson(params, state, `categorymembers:${title}`);
    log.api_requests += 1;
    state.counters.category_member_requests += 1;
    if (!data) {
      hadError = true;
      log.status = 'failed';
      log.error = 'categorymembers request failed; continuation position preserved in failure log';
      break;
    }
    const members = data.query?.categorymembers ?? [];
    log.continuation_pages += 1;
    state.counters.category_member_entries_seen += members.length;
    log.members_seen += members.length;
    for (const member of members) {
      if (member.ns === 14) {
        log.subcategories += 1;
        enqueueCategory(state, member.title, item.root_seed, [...item.path, member.title]);
      } else if (member.ns === 6) {
        state.counters.file_members_seen += 1;
        if (!log.files_seen_titles.includes(member.title)) log.files_seen_titles.push(member.title);
        if (processedTitles.has(member.title) || newFileTitles.includes(member.title)) {
          state.counters.duplicate_file_members += 1;
        } else {
          newFileTitles.push(member.title);
        }
      }
    }
    continuation = data.continue?.cmcontinue ?? null;
    if (continuation) await sleep(CATEGORY_DELAY_MS);
  } while (continuation);

  if (!hadError) {
    log.continuation_exhausted = true;
    log.status = 'complete';
    state.counters.categories_fetched += 1;
    state.visited_categories.push(title);
  }

  // Fetch metadata in bounded batches.  The original image URL is recorded,
  // never fetched, so this source pass does not create duplicate image copies.
  for (let i = 0; i < newFileTitles.length; i += IMAGE_BATCH_SIZE) {
    const batch = newFileTitles.slice(i, i + IMAGE_BATCH_SIZE);
    const data = await fetchJson({
      titles: batch.join('|'),
      prop: 'imageinfo',
      iiprop: 'url|size|mime|mediatype|extmetadata|timestamp|sha1',
      iilimit: '1',
    }, state, `imageinfo:${title}:${i}`);
    state.counters.imageinfo_batches += 1;
    if (!data) {
      state.pending_file_titles.push(...batch.filter((x) => !state.pending_file_titles.includes(x)));
      continue;
    }
    const pages = data.query?.pages ?? [];
    state.counters.imageinfo_files_returned += pages.length;
    for (const page of pages) {
      const info = page.imageinfo?.[0];
      if (!page.title || processedTitles.has(page.title)) continue;
      if (!info) {
        state.failures.push({ stage: 'imageinfo', file_title: page.title, pageid: page.pageid ?? null, error: 'no imageinfo returned' });
        continue;
      }
      const meta = info.extmetadata ?? {};
      const row = {
        source_id: `commons-ottoman-${sha1(page.title).slice(0, 16)}`,
        source_system: 'Wikimedia Commons MediaWiki API',
        source_type: 'discovery_metadata_only',
        accessed: AS_OF,
        category_seed: item.root_seed,
        category_path: item.path,
        category_title: title,
        file_title: page.title,
        pageid: page.pageid ?? null,
        file_page: pageUrl(page.title),
        description_url: info.descriptionurl ?? null,
        original_url: info.url ?? null,
        file_name: info.descriptionurl ? info.descriptionurl.split('/').pop() : null,
        mime: info.mime ?? null,
        mediatype: info.mediatype ?? null,
        width: info.width ?? null,
        height: info.height ?? null,
        size_bytes: info.size ?? null,
        timestamp: info.timestamp ?? null,
        sha1: info.sha1 ?? null,
        extmetadata: {
          object_name: metadataValue(meta, 'ObjectName'),
          image_description: metadataValue(meta, 'ImageDescription'),
          date_time_original: metadataValue(meta, 'DateTimeOriginal'),
          date: metadataValue(meta, 'Date'),
          artist: metadataValue(meta, 'Artist'),
          author: metadataValue(meta, 'Author'),
          credit: metadataValue(meta, 'Credit'),
          source: metadataValue(meta, 'Source'),
          attribution: metadataValue(meta, 'Attribution'),
          license: metadataValue(meta, 'License'),
          license_short_name: metadataValue(meta, 'LicenseShortName'),
          usage_terms: metadataValue(meta, 'UsageTerms'),
          categories: metadataValue(meta, 'Categories'),
          depicts: metadataValue(meta, 'Depicts'),
        },
        status: 'RAW_CANDIDATE',
        note: 'Image URL recorded for later review; original bytes intentionally not downloaded in source sweep.',
      };
      outHandle.write(`${JSON.stringify(row)}\n`);
      processedTitles.add(page.title);
      state.processed_file_titles.push(page.title);
      state.counters.unique_files += 1;
    }
    await sleep(CATEGORY_DELAY_MS);
  }
  state.pending_file_titles = state.pending_file_titles.filter((x) => !processedTitles.has(x));
  saveState(state);
}

async function processPending(state, processedTitles, outHandle) {
  if (!state.pending_file_titles.length) return;
  const pending = [...state.pending_file_titles];
  state.pending_file_titles = [];
  for (let i = 0; i < pending.length; i += IMAGE_BATCH_SIZE) {
    const batch = pending.slice(i, i + IMAGE_BATCH_SIZE).filter((x) => !processedTitles.has(x));
    if (!batch.length) continue;
    const data = await fetchJson({
      titles: batch.join('|'),
      prop: 'imageinfo',
      iiprop: 'url|size|mime|mediatype|extmetadata|timestamp|sha1',
      iilimit: '1',
    }, state, `imageinfo:pending:${i}`);
    state.counters.imageinfo_batches += 1;
    if (!data) {
      state.pending_file_titles.push(...batch);
      continue;
    }
    for (const page of data.query?.pages ?? []) {
      const info = page.imageinfo?.[0];
      if (!page.title || processedTitles.has(page.title)) continue;
      if (!info) {
        state.failures.push({ stage: 'imageinfo_pending', file_title: page.title, pageid: page.pageid ?? null, error: 'no imageinfo returned' });
        continue;
      }
      const meta = info.extmetadata ?? {};
      const row = {
        source_id: `commons-ottoman-${sha1(page.title).slice(0, 16)}`,
        source_system: 'Wikimedia Commons MediaWiki API',
        source_type: 'discovery_metadata_only',
        accessed: AS_OF,
        category_seed: 'pending_retry',
        category_path: [],
        category_title: null,
        file_title: page.title,
        pageid: page.pageid ?? null,
        file_page: pageUrl(page.title),
        description_url: info.descriptionurl ?? null,
        original_url: info.url ?? null,
        file_name: info.descriptionurl ? info.descriptionurl.split('/').pop() : null,
        mime: info.mime ?? null,
        mediatype: info.mediatype ?? null,
        width: info.width ?? null,
        height: info.height ?? null,
        size_bytes: info.size ?? null,
        timestamp: info.timestamp ?? null,
        sha1: info.sha1 ?? null,
        extmetadata: {
          object_name: metadataValue(meta, 'ObjectName'),
          image_description: metadataValue(meta, 'ImageDescription'),
          date_time_original: metadataValue(meta, 'DateTimeOriginal'),
          date: metadataValue(meta, 'Date'),
          artist: metadataValue(meta, 'Artist'),
          author: metadataValue(meta, 'Author'),
          credit: metadataValue(meta, 'Credit'),
          source: metadataValue(meta, 'Source'),
          attribution: metadataValue(meta, 'Attribution'),
          license: metadataValue(meta, 'License'),
          license_short_name: metadataValue(meta, 'LicenseShortName'),
          usage_terms: metadataValue(meta, 'UsageTerms'),
          categories: metadataValue(meta, 'Categories'),
          depicts: metadataValue(meta, 'Depicts'),
        },
        status: 'RAW_CANDIDATE',
        note: 'Image URL recorded for later review; original bytes intentionally not downloaded in source sweep.',
      };
      outHandle.write(`${JSON.stringify(row)}\n`);
      processedTitles.add(page.title);
      state.processed_file_titles.push(page.title);
      state.counters.unique_files += 1;
      state.counters.imageinfo_files_returned += 1;
    }
    await sleep(CATEGORY_DELAY_MS);
  }
  saveState(state);
}

function finalize(state) {
  const queueRemaining = state.queue.length;
  const complete = queueRemaining === 0 && state.pending_file_titles.length === 0;
  state.status = complete ? (state.failures.length ? 'complete_with_failures' : 'complete') : 'partial';
  state.completed_at = complete ? new Date().toISOString() : null;
  state.queue_remaining = queueRemaining;
  state.pending_file_titles_remaining = state.pending_file_titles.length;
  state.continuation_tokens_exhausted = complete && Object.values(state.category_log).every((x) => x.continuation_exhausted === true);
  state.raw_candidate_file = path.relative(ROOT, OUT).replaceAll('\\', '/');
  state.metadata_cache_directory = path.relative(ROOT, CACHE).replaceAll('\\', '/');
  state.failed_pages = state.failures;
  saveState(state);
}

async function main() {
  ensureDirs();
  const state = fs.existsSync(STATE_PATH) ? readJson(STATE_PATH, initialState()) : initialState();
  const processedTitles = loadProcessedTitles();
  for (const title of processedTitles) if (!state.processed_file_titles.includes(title)) state.processed_file_titles.push(title);
  state.counters.unique_files = processedTitles.size;
  if (!state.seed_categories.length) await resolveSeeds(state);
  const handle = fs.createWriteStream(OUT, { flags: 'a', encoding: 'utf8' });
  await new Promise((resolve, reject) => handle.once('open', resolve).once('error', reject));
  try {
    await processPending(state, processedTitles, handle);
    while (state.queue.length) {
      const item = state.queue.shift();
      if (state.visited_categories.includes(item.title)) continue;
      await fetchCategory(state, item, processedTitles, handle);
      if (state.counters.categories_fetched % 10 === 0 || state.counters.unique_files % 100 === 0) {
        console.log(JSON.stringify({ categories: state.counters.categories_fetched, queue: state.queue.length, files: state.counters.unique_files, failures: state.failures.length }));
      }
      saveState(state);
    }
  } finally {
    await new Promise((resolve) => handle.end(resolve));
  }
  finalize(state);
  console.log(JSON.stringify({ status: state.status, categories: state.counters.categories_fetched, files: state.counters.unique_files, failures: state.failures.length, queue_remaining: state.queue.length, pending: state.pending_file_titles.length }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

