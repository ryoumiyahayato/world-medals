import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const out = path.join(root, 'data', 'raw_candidates', 'commons_ottoman.jsonl');
const statePath = path.join(root, 'data', 'source_sweeps', 'commons_ottoman.json');
const cacheDir = path.join(root, 'sources', 'cache', 'commons_ottoman');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const excludedRx = /\bRecipients\b|\bKnights?\b|\bPeople\b|\bportrait(?:s)?\b|\bcoat(?:s)? of arms\b|\bheraldry\b|\bfamily crests?\b|\bpersonalities\b/i;
const value = (metadata, key) => {
  const entry = metadata?.[key];
  return entry && typeof entry === 'object' ? (entry.value ?? null) : (entry ?? null);
};
const sha1 = (text) => crypto.createHash('sha1').update(text).digest('hex');
const pageUrl = (title) => `https://commons.wikimedia.org/wiki/${encodeURIComponent(title.replaceAll(' ', '_'))}`;

const pathMap = new Map();
for (const prop of Object.values(state.category_log ?? {})) {
  for (const title of prop.files_seen_titles ?? []) {
    if (!pathMap.has(title)) pathMap.set(title, { root_seed: prop.root_seed, path: prop.path ?? [], category_title: prop.title });
  }
}

const infos = new Map();
for (const file of fs.readdirSync(cacheDir)) {
  if (!file.endsWith('.json')) continue;
  try {
    const data = JSON.parse(fs.readFileSync(path.join(cacheDir, file), 'utf8'));
    for (const page of data?.query?.pages ?? []) {
      const info = page.imageinfo?.[0];
      if (info && page.title) infos.set(page.title, { page, info });
    }
  } catch {
    // Ignore a cache entry that was incomplete; its title remains in the
    // checkpoint's missing metadata list.
  }
}

const rows = [];
const missing = [];
const removedScope = [];
for (const title of state.processed_file_titles ?? []) {
  const location = pathMap.get(title);
  if (!location) { missing.push({ file_title: title, reason: 'no category path in checkpoint' }); continue; }
  const parts = location.path ?? [];
  const ancestorExcluded = parts.slice(0, -1).some((part) => excludedRx.test(String(part).replace(/^Category:/, '')));
  if (ancestorExcluded) { removedScope.push(title); continue; }
  const source = infos.get(title);
  if (!source) { missing.push({ file_title: title, reason: 'no cached imageinfo response' }); continue; }
  const { page, info } = source;
  const meta = info.extmetadata ?? {};
  rows.push({
    source_id: `commons-ottoman-${sha1(title).slice(0, 16)}`,
    source_system: 'Wikimedia Commons MediaWiki API',
    source_type: 'discovery_metadata_only',
    accessed: state.as_of ?? '2026-09-26',
    category_seed: location.root_seed,
    category_path: parts,
    category_title: location.category_title,
    file_title: title,
    pageid: page.pageid ?? null,
    file_page: pageUrl(title),
    description_url: info.descriptionurl ?? null,
    original_url: info.url ?? null,
    file_name: info.descriptionurl ? String(info.descriptionurl).split('/').pop() : null,
    mime: info.mime ?? null,
    mediatype: info.mediatype ?? null,
    width: info.width ?? null,
    height: info.height ?? null,
    size_bytes: info.size ?? null,
    timestamp: info.timestamp ?? null,
    sha1: info.sha1 ?? null,
    extmetadata: {
      object_name: value(meta, 'ObjectName'),
      image_description: value(meta, 'ImageDescription'),
      date_time_original: value(meta, 'DateTimeOriginal'),
      date: value(meta, 'Date'),
      artist: value(meta, 'Artist'),
      author: value(meta, 'Author'),
      credit: value(meta, 'Credit'),
      source: value(meta, 'Source'),
      attribution: value(meta, 'Attribution'),
      license: value(meta, 'License'),
      license_short_name: value(meta, 'LicenseShortName'),
      usage_terms: value(meta, 'UsageTerms'),
      categories: value(meta, 'Categories'),
      depicts: value(meta, 'Depicts'),
    },
    status: 'RAW_CANDIDATE',
    note: 'Image URL recorded for later review; original bytes intentionally not downloaded in source sweep.',
  });
}

const tmp = `${out}.rebuild.tmp`;
fs.writeFileSync(tmp, `${rows.map((row) => JSON.stringify(row)).join('\n')}\n`, 'utf8');
fs.renameSync(tmp, out);
state.processed_file_titles = rows.map((row) => row.file_title);
state.counters.unique_files = rows.length;
state.rebuild = {
  rebuilt_at: new Date().toISOString(),
  source: 'cached Wikimedia Commons imageinfo responses plus category checkpoint',
  rows_rebuilt: rows.length,
  removed_scope_excluded_rows: removedScope.length,
  missing_rows: missing,
};
state.scope_excluded_cleanup = {
  rule: 'Rows whose category path has a Recipients/Knights/People/portrait or generic heraldry ancestor were removed from raw candidates.',
  removed_file_titles: removedScope,
};
fs.writeFileSync(statePath, `${JSON.stringify(state, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ rows: rows.length, removed_scope: removedScope.length, missing: missing.length, info_cache_titles: infos.size }));

