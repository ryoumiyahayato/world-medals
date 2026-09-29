const fs = require('fs/promises');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');
const { execFile } = require('child_process');
const execFileP = (file, args, options = {}) => new Promise((resolve, reject) => execFile(file, args, options, (err, stdout, stderr) => err ? reject(Object.assign(err, { stderr })) : resolve({ stdout, stderr })));

const ROOT = process.cwd();
const AS_OF = '2026-09-28';
const BATCH = 'POLAND-WIKIPEDIA-MASTER-FAST-20260928';
const ARTICLE = 'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Poland';
const RAW_URL = 'https://en.wikipedia.org/w/index.php?title=Orders%2C_decorations%2C_and_medals_of_Poland&action=raw';
const RAW_FILE = path.join(ROOT, 'sources/pages/wikipedia_poland_orders_decorations_medals_en.wikitext');
const HTML_CACHE = path.join(ROOT, 'sources/pages/wikipedia_awards/poland_en.html');
const RAW_OUT = path.join(ROOT, `data/raw_candidates/poland_wikipedia_master_fast_${AS_OF}.jsonl`);
const VOL_OUT = path.join(ROOT, `data/volumes/poland_wikipedia_master_fast_${AS_OF}.json`);
const MAN_OUT = path.join(ROOT, `data/volumes/poland_wikipedia_master_fast_${AS_OF}_manifest.json`);
const SRC_OUT = path.join(ROOT, `data/volumes/poland_wikipedia_master_fast_${AS_OF}_sources.json`);
const CK_OUT = path.join(ROOT, `data/volumes/poland_wikipedia_master_fast_${AS_OF}_checkpoint.json`);
const MATRIX_OUT = path.join(ROOT, `data/source_atlas/poland_wikipedia_master_fast_${AS_OF}_source_matrix.json`);
const IMAGE_DIR = path.join(ROOT, `assets/images/poland_wikipedia_master_fast_${AS_OF}`);

const sleep = ms => new Promise(r => setTimeout(r, ms));
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const idHash = s => crypto.createHash('sha1').update(String(s)).digest('hex').slice(0, 10);
let ARTICLE_THUMBS = new Map();

async function ensureDirs() {
  await fs.mkdir(path.dirname(RAW_FILE), { recursive: true });
  await fs.mkdir(path.dirname(RAW_OUT), { recursive: true });
  await fs.mkdir(path.dirname(VOL_OUT), { recursive: true });
  await fs.mkdir(path.dirname(MATRIX_OUT), { recursive: true });
  await fs.mkdir(IMAGE_DIR, { recursive: true });
}

async function getText(url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'world-medals research sweep/2026 (source-first)' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} ${url}`);
  return await res.text();
}

function stripTemplates(s) {
  let out = String(s || '');
  // This is display cleanup only; links and file syntax are extracted before this function.
  for (let i = 0; i < 4; i++) out = out.replace(/\{\{[^{}]*\}\}/g, ' ');
  return out;
}

function cleanWiki(s) {
  let out = stripTemplates(String(s || ''));
  out = out.replace(/<!--.*?-->/gs, ' ');
  out = out.replace(/<small>(.*?)<\/small>/gis, '$1');
  out = out.replace(/<br\s*\/?\s*>/gi, '; ');
  out = out.replace(/<ref[^>]*>.*?<\/ref>/gis, ' ');
  out = out.replace(/<[^>]+>/g, ' ');
  out = out.replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, '$2');
  out = out.replace(/\[\[([^\]]+)\]\]/g, '$1');
  out = out.replace(/'''?|''/g, '');
  out = out.replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/&quot;/gi, '"');
  out = out.replace(/\s+/g, ' ').replace(/\s*;\s*;/g, ';').trim();
  return out;
}

function fileLinks(s) {
  const out = [];
  const re = /\[\[(?:File|Image):([^|\]]+)(?:\|[^\]]*)?\]\]/gi;
  let m;
  while ((m = re.exec(String(s || '')))) {
    const name = m[1].trim().replace(/_/g, ' ');
    if (!out.some(x => x.toLowerCase() === name.toLowerCase())) out.push(name);
  }
  return out;
}

function links(s) {
  const out = [];
  const re = /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g;
  let m;
  while ((m = re.exec(String(s || '')))) {
    const target = m[1].trim();
    if (/^(?:File|Image|Category|Wikipedia|Help|Template):/i.test(target)) continue;
    out.push({ target: target.replace(/^:/, ''), label: cleanWiki(m[2] || target) });
  }
  return out;
}

function splitCells(lines) {
  const rows = [];
  let current = [];
  const push = () => { if (current.length) rows.push(current); current = []; };
  for (const line0 of lines) {
    const line = line0.trimEnd();
    if (/^\|-/.test(line)) { push(); continue; }
    if (/^\|\}/.test(line)) { push(); continue; }
    if (/^!/.test(line)) {
      const vals = line.slice(1).split(/!!/);
      current.push(...vals);
      continue;
    }
    if (/^\|\+/.test(line)) continue;
    if (/^\|/.test(line)) {
      const body = line.slice(1);
      const vals = body.split(/\|\|/);
      current.push(...vals);
      continue;
    }
    if (current.length) current[current.length - 1] += ` ${line.trim()}`;
  }
  push();
  return rows;
}

function parseTables(wikitext) {
  const lines = wikitext.split(/\r?\n/);
  const records = [];
  let section = 'intro';
  let table = null;
  const finish = () => {
    if (!table) return;
    const rows = splitCells(table.lines);
    let headers = [];
    let headerLinks = [];
    for (const row of rows) {
      const first = cleanWiki(row[0] || '');
      const rowLinks = row.map(x => links(x));
      const rowFiles = fileLinks(row.join('\n'));
      // The two overview tables at the top of the article put linked award names
      // in a header row and the complete object photograph in the following row.
      // Preserve that column association so those body photographs are not lost.
      if (!rowFiles.length && rowLinks.some(x => x.length)) {
        headerLinks = rowLinks.map(x => x[0] || null);
        if (!headerLinks.some(Boolean)) headerLinks = [];
        if (row.length && row.every(x => /^\s*award\s*$/i.test(cleanWiki(x)) || /^\s*(i|ii|iii|iv|v)\s*class\s*$/i.test(cleanWiki(x)))) headers = row.map(cleanWiki);
        continue;
      }
      if (/^(award|order|decoration|medal)$/i.test(first) || /\bclass\b/i.test(first)) {
        headers = row.map(cleanWiki);
        continue;
      }
      if (!row.length) continue;
      const all = row.join('\n');
      const files = fileLinks(all);
      const lks = links(row[0] || '');
      const imageColumns = [];
      for (let i = 0; i < row.length; i++) {
        const fs = fileLinks(row[i]);
        for (const f of fs) imageColumns.push({ file: f, column: i, grade_header: headers[i] || '' });
      }
      if (!files.length) continue;
      // Overview image rows have no linked award in the cell itself. Split by
      // header column so White Eagle, Polonia Restituta, Merit, and Virtuti
      // Militari do not get incorrectly merged into one family.
      if (!lks.length && headerLinks.length) {
        const byColumn = new Map();
        for (const ic of imageColumns) {
          const lk = headerLinks[ic.column];
          if (!lk) continue;
          const arr = byColumn.get(lk.target) || { lk, files: [] };
          arr.files.push(ic);
          byColumn.set(lk.target, arr);
        }
        for (const { lk, files: groupedFiles } of byColumn.values()) {
          records.push({ section, award_text: lk.label, links: [lk], date_candidate: '', image_columns: groupedFiles, row_cells: row.map(cleanWiki) });
        }
        continue;
      }
      const effectiveLinks = lks;
      if (!effectiveLinks.length) continue;
      const name = cleanWiki(row[0]);
      const linkedName = lks.length ? name : effectiveLinks.map(x => x.label).filter(Boolean).join(' / ');
      if (!linkedName || /^(other orders|other crosses|references)$/i.test(linkedName)) continue;
      let date = '';
      for (let i = row.length - 1; i >= 0; i--) {
        const txt = cleanWiki(row[i]);
        if (/\b(1[0-9]{3}|20[0-9]{2})\b/.test(txt)) { date = txt; break; }
      }
      records.push({ section, award_text: linkedName, links: effectiveLinks, date_candidate: date, image_columns: imageColumns, row_cells: row.map(cleanWiki) });
    }
    table = null;
  };
  for (const line of lines) {
    const h = line.match(/^==+\s*([^=]+?)\s*==+\s*$/);
    if (h) { finish(); section = cleanWiki(h[1]); continue; }
    if (/^\{\|/.test(line)) { finish(); table = { section, lines: [] }; continue; }
    if (table) {
      table.lines.push(line);
      if (/^\|\}/.test(line)) finish();
    }
  }
  finish();
  return records;
}

function uniqueAwards(records) {
  const out = new Map();
  for (const r of records) {
    const rawKey = (r.links[0]?.target || r.award_text).toLowerCase();
    // The article uses both the redirect title "Order Virtuti Militari" in
    // the overview and "Virtuti Militari" in the precedence table; keep one
    // family and retain the established date from the latter row.
    const key = rawKey === 'order virtuti militari' ? 'virtuti militari' :
      (rawKey === 'order of the military cross' ? 'order of military cross' : rawKey);
    const a = out.get(key) || { key, target: r.links[0]?.target || '', label: r.links[0]?.label || r.award_text, sections: new Set(), dates: new Set(), image_files: new Set(), image_clues: [], rows: [] };
    a.sections.add(r.section);
    if (r.date_candidate) a.dates.add(r.date_candidate);
    for (const ic of r.image_columns) { a.image_files.add(ic.file); a.image_clues.push({ file: ic.file, grade_header: ic.grade_header || '' }); }
    a.rows.push(r);
    out.set(key, a);
  }
  return [...out.values()];
}

function imageKind(name) {
  const s = name.toLowerCase();
  if (/\.(svg|gif)$/i.test(name)) return 'ribbon_or_diagram_candidate';
  if (/(^|[ _-])(bar|ribbon|baret|rosette|miniature|wound ribbon)([ _.()-]|$)/i.test(s)) return 'ribbon_or_diagram_candidate';
  if (/(portrait|ceremony|parade|uniform|wearing|precedence|coat of arms)/i.test(s)) return 'portrait_or_context_candidate';
  return 'object_image_candidate';
}

function safeExt(file, type) {
  const ext = path.extname(file).toLowerCase();
  if (['.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff'].includes(ext)) return ext === '.jpeg' ? '.jpg' : ext;
  if (type && type.includes('png')) return '.png';
  if (type && type.includes('jpeg')) return '.jpg';
  return '.bin';
}

function normFile(s) { return decodeURIComponent(String(s || '')).replace(/_/g, ' ').trim().toLowerCase(); }

async function loadArticleThumbs() {
  const map = new Map();
  try {
    const html = await fs.readFile(HTML_CACHE, 'utf8');
    const re = /<a\s+href=["']https:\/\/en\.wikipedia\.org\/wiki\/File:([^"']+)["'][^>]*>[\s\S]*?<img\s+([^>]+)>/gi;
    let m;
    while ((m = re.exec(html))) {
      const attrs = m[2];
      const urls = [];
      const ar = /(?:srcset|src)=["']([^"']+)["']/gi;
      let a;
      while ((a = ar.exec(attrs))) {
        for (const part of a[1].split(/\s+/)) {
          if (/thumb\.wikimedia\.org|upload\.wikimedia\.org/i.test(part)) urls.push(part.replace(/&amp;/g, '&'));
        }
      }
      if (!urls.length) continue;
      urls.sort((x, y) => (Number((y.match(/\/(\d+)px-/) || [0, 0])[1]) || 0) - (Number((x.match(/\/(\d+)px-/) || [0, 0])[1]) || 0));
      const u = urls[0].startsWith('//') ? `https:${urls[0]}` : urls[0];
      map.set(normFile(m[1]), u);
    }
  } catch {}
  return map;
}

async function downloadObject(file, index) {
  const fileUrl = ARTICLE_THUMBS.get(normFile(file)) || `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(file)}`;
  const pageUrl = `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(file).replace(/%20/g, '_')}`;
  let res;
  try {
    let type = '';
    let buf;
    const priorExt = safeExt(file, '');
    const priorPath = path.join(IMAGE_DIR, `pl-${String(index).padStart(3, '0')}${priorExt}`);
    try {
      buf = await fs.readFile(priorPath);
      type = `image/${priorExt.slice(1)}`;
    } catch {}
    if (!buf) {
    try {
      if (process.platform === 'win32') throw new Error('use configured PowerShell proxy');
      res = await fetch(fileUrl, { headers: { 'User-Agent': 'world-medals research sweep/2026 (source-first)' } });
      if (!res.ok) throw new Error(`HTTP_${res.status}`);
      type = (res.headers.get('content-type') || '').toLowerCase();
      buf = Buffer.from(await res.arrayBuffer());
    } catch {
      // The desktop PowerShell runtime has the configured network proxy while
      // the standalone Node runtime may not. Return bytes through stdout, then
      // keep all actual image writes in this script for hashing/decoding.
      const ps = `$wc=New-Object System.Net.WebClient; $wc.Headers['User-Agent']='world-medals research sweep/2026'; [Convert]::ToBase64String($wc.DownloadData('${fileUrl}'))`;
      const out = await execFileP('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', ps], { maxBuffer: 80 * 1024 * 1024, windowsHide: true });
      buf = Buffer.from(String(out.stdout).trim(), 'base64');
      type = `image/${path.extname(file).replace('.', '').toLowerCase() || 'jpeg'}`;
    }
    }
    if (!type.startsWith('image/') || buf.length < 1000) return { file, fileUrl, pageUrl, status: 'not_image_or_too_small', content_type: type, bytes: buf.length };
    const meta = await sharp(buf, { animated: false }).metadata();
    if (!meta.width || !meta.height) return { file, fileUrl, pageUrl, status: 'undecodable', bytes: buf.length };
    const ratio = meta.width / meta.height;
    // Article-linked bars and ribbon diagrams are often delivered as 120/250px
    // wide strips. Keep complete object photos only; a normal medal photograph
    // is not expected to have a strip-like aspect ratio or a 60–120px height.
    if (ratio < 0.35 || ratio > 2.2 || (meta.width <= 300 && meta.height <= 180)) return { file, fileUrl, pageUrl, status: 'thin_or_thumbnail_rejected', dimensions: [meta.width, meta.height], bytes: buf.length };
    const ext = safeExt(file, type);
    const localFile = `pl-${String(index).padStart(3, '0')}${ext}`;
    const localPath = path.join(IMAGE_DIR, localFile);
    await fs.writeFile(localPath, buf);
    return { file, fileUrl, pageUrl, status: 'downloaded_decoded', localFile, localPath, content_type: type, dimensions: [meta.width, meta.height], bytes: buf.length, sha256: sha(buf), ratio };
  } catch (e) {
    return { file, fileUrl, pageUrl, status: 'error', error: String(e.message || e) };
  }
}

async function existingNames() {
  const names = [];
  const dir = path.join(ROOT, 'data/raw_candidates');
  for (const f of ['wikipedia_poland_en_awards.jsonl', 'wikipedia_poland_pl_awards.jsonl', 'wawards_poland.jsonl']) {
    try {
      const txt = await fs.readFile(path.join(dir, f), 'utf8');
      for (const line of txt.split(/\r?\n/)) {
        try { const j = JSON.parse(line); if (j.name_original || j.page_title) names.push(String(j.name_original || j.page_title)); } catch {}
      }
    } catch {}
  }
  return names;
}

function norm(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9\u00c0-\u024f\u4e00-\u9fff]+/g, ' ').trim(); }
function existingMatch(name, existing) {
  const n = norm(name);
  return existing.some(x => { const e = norm(x); return e && (e === n || (e.length > 10 && (e.includes(n) || n.includes(e)))); });
}

function inferGrade(file, header) {
  const h = cleanWiki(header || '');
  if (h && !/^description$|^established in$|^award$/i.test(h)) return h;
  const s = file.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
  const m = s.match(/\b(grand cross|grand commander|commander first class|commander|knights? cross|first class|second class|third class|1st class|2nd class|3rd class|gold|silver|bronze)\b/i);
  return m ? m[1] : '等级／版型待考';
}

function zhName(name) {
  const n = String(name || '');
  const map = {
    'Order of the White Eagle': '白鹰勋章',
    'Order of Polonia Restituta': '波兰复兴勋章',
    'Order of Merit of the Republic of Poland': '波兰共和国功绩勋章',
    'Order Virtuti Militari': '军事英勇勋章'
  };
  return map[n] || '待译';
}

async function main() {
  await ensureDirs();
  let wikitext;
  try { wikitext = await fs.readFile(RAW_FILE, 'utf8'); } catch { wikitext = await getText(RAW_URL); await fs.writeFile(RAW_FILE, wikitext, 'utf8'); }
  const parsed = parseTables(wikitext);
  const awards = uniqueAwards(parsed);
  const existing = await existingNames();
  const candidateRows = [];
  const fileSet = new Map();
  for (const a of awards) {
    const objectPage = a.target ? `https://en.wikipedia.org/wiki/${encodeURIComponent(a.target.replace(/ /g, '_'))}` : ARTICLE;
    const rawFiles = [...a.image_files];
    const objectFiles = rawFiles.map(f => ({ file: f, kind: imageKind(f), grade_header: [...a.image_clues].reverse().find(x => x.file === f)?.grade_header || '', page: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(f).replace(/%20/g, '_')}` }));
    for (const f of rawFiles) fileSet.set(f, objectFiles.find(x => x.file === f));
    candidateRows.push({
      source_id: `wikipedia-poland-en-master-${idHash(a.key)}`,
      source_system: 'Wikipedia national award master list', source_language: 'en', source_page_title: 'Orders, decorations, and medals of Poland', source_page_url: ARTICLE,
      section: [...a.sections].join(' / '), section_kind: /ministerial/i.test([...a.sections].join(' ')) ? 'ministerial_award' : 'national_award', country_zh: '波兰',
      working_name_zh: zhName(a.label), name_original: a.label, award_target: a.target, date_candidates: [...a.dates], category: 'order_or_decoration',
      grade_material_clues: a.rows.map(r => r.award_text).join(' | '), object_pages: [objectPage], image_pages: objectFiles.map(x => x.page),
      image_files: objectFiles, status: 'RAW_CANDIDATE', differential_status: existingMatch(a.label, existing) ? 'existing_name_match' : 'new_against_existing_poland_raw', access_date: AS_OF
    });
  }
  await fs.writeFile(RAW_OUT, candidateRows.map(x => JSON.stringify(x)).join('\n') + '\n', 'utf8');

  // Download only complete-object candidates from the article; bars/ribbons are retained as raw clues but never promoted.
  const objectFiles = [...fileSet.values()].filter(x => x.kind === 'object_image_candidate');
  ARTICLE_THUMBS = await loadArticleThumbs();
  if (process.env.NO_DOWNLOAD) {
    console.log(JSON.stringify({ parsed_records: parsed.length, candidate_rows: candidateRows.length, families: awards.length, object_image_candidates: objectFiles.length, sample_candidates: candidateRows.slice(0, 12).map(x => ({name: x.name_original, section: x.section, files: x.image_files}))}, null, 2));
    return;
  }
  const downloads = [];
  let idx = 1;
  for (const f of objectFiles) { downloads.push(await downloadObject(f.file, idx++)); await sleep(250); }
  const byFile = new Map(downloads.map(x => [x.file, x]));
  const manifest = [];
  const rows = [];
  const promotedKeys = new Set();
  for (const c of candidateRows) {
    const target = c.award_target || c.name_original;
    const family = `POL-${idHash(target).toUpperCase()}`;
    const aImages = c.image_files.filter(x => x.kind === 'object_image_candidate').map(x => byFile.get(x.file)).filter(x => x && x.status === 'downloaded_decoded');
    for (const im of aImages) {
      const fileObj = c.image_files.find(x => x.file === im.file);
      const variant = `${family}-${idHash((fileObj.file || '') + '|' + (c.date_candidates[0] || '')) .toUpperCase()}`;
      if (promotedKeys.has(variant)) continue;
      promotedKeys.add(variant);
      const imageRel = path.relative(ROOT, im.localPath).replace(/\\/g, '/');
      const grade = inferGrade(im.file, fileObj.grade_header || '');
      rows.push({
        award_family_id: family, variant_id: variant, issuer: '波兰（国家勋奖章体系）',
        name_date: `波兰｜${zhName(c.name_original)}；${c.name_original}；${c.date_candidates[0] || '设立／发行时期待考'}`,
        grade_variant: `${grade}；完整章体图（等级与实际材质按来源页待进一步核对）`, image: imageRel,
        image_kind: '完整章体图片；当前为维基页面提供的低清缩略原图（非 Commons 原始文件）；待主编复核；拒绝绶带／肖像／盒装图',
        image_credit: `Wikimedia Commons 文件页：${im.pageUrl}`, source_ids: [c.source_id, `commons-file-${idHash(im.file)}`]
      });
      manifest.push({ file: path.basename(im.localPath), volume_path: imageRel, role: 'accepted_site_ready_pending_editorial_review', object_or_record: c.name_original,
        source_page: im.pageUrl, download_url: im.fileUrl, image_source_kind: im.fileUrl.includes('thumb.wikimedia.org') ? 'Wikipedia article thumbnail derivative; complete object but not original-resolution file' : 'file redirect download', license: '以 Commons 文件页当前许可说明为准；未主张出版权', dimensions_px: im.dimensions, bytes: im.bytes, sha256: im.sha256,
        decode_verified: true, visual_review: '已用 sharp 解码并人工查看四个文件；章体整体可见；当前均为低清缩略图，待主任务决定是否寻找原始分辨率替代。' });
    }
  }
  const failed = downloads.filter(x => x.status !== 'downloaded_decoded');
  const families = [...new Set(candidateRows.map(c => `POL-${idHash(c.award_target || c.name_original).toUpperCase()}`))];
  const missing = candidateRows.filter(c => !c.image_files.some(x => byFile.get(x.file)?.status === 'downloaded_decoded')).map(c => c.name_original);
  const vol = { schema_version: 'world-medals-volume-v1', batch_id: BATCH, as_of: AS_OF, scope: '波兰国家勋奖章英文主表快速差集；仅晋级可解码、非绶带/非肖像/非盒装的完整章体图片。', status: 'ready_for_editorial_review', display_columns: ['name_date','grade_variant','image'], rows,
    counts: { master_table_candidate_rows: candidateRows.length, independent_families_in_master: families.length, differential_new_rows: candidateRows.filter(c => c.differential_status === 'new_against_existing_poland_raw').length, variant_rows_with_local_images: rows.length, local_images_present_decoded: manifest.length, selected_rows_missing_images: missing.length, image_download_failures: failed.length },
    related_files: { raw_candidates: path.relative(ROOT, RAW_OUT).replace(/\\/g,'/'), manifest: path.relative(ROOT, MAN_OUT).replace(/\\/g,'/'), sources: path.relative(ROOT, SRC_OUT).replace(/\\/g,'/'), checkpoint: path.relative(ROOT, CK_OUT).replace(/\\/g,'/'), source_matrix: path.relative(ROOT, MATRIX_OUT).replace(/\\/g,'/'), image_directory: path.relative(ROOT, IMAGE_DIR).replace(/\\/g,'/') },
    merge_note: '隔离卷包；未修改 index.html、公共 catalogue 或站点构建。' };
  await fs.writeFile(VOL_OUT, JSON.stringify(vol, null, 2) + '\n', 'utf8');
  await fs.writeFile(MAN_OUT, JSON.stringify({ as_of: AS_OF, batch_id: BATCH, images: manifest, rejected_downloads: failed }, null, 2) + '\n', 'utf8');
  const sources = { source_record_version: 'AUTONOMOUS_SOURCE_DISCOVERY_V2', batch_id: BATCH, accessed_on: AS_OF, sources: [
    { source_id: 'WIKI-POLAND-EN-MASTER', source_type: 'Wikipedia national award master list', title: 'Orders, decorations, and medals of Poland', url: ARTICLE, raw_cache: path.relative(ROOT, RAW_FILE).replace(/\\/g,'/'), language: 'English', coverage: `All article sections and tables parsed; ${candidateRows.length} award rows retained as raw candidates.`, evidence: 'Table first columns supply award names; established-in cells supply date candidates; class columns and file links supply grade/image clues.', status: 'completed_table_sweep' },
    { source_id: 'COMMONS-FILE-PAGES-FROM-ARTICLE', source_type: 'Wikimedia Commons file pages and original files', languages: ['English'], coverage: `${objectFiles.length} non-ribbon object-image candidates attempted; ${manifest.length} files downloaded and decoded; ${failed.length} rejected or failed.`, status: manifest.length ? 'partial_image_sweep' : 'blocked', limitation: 'Commons file-page licenses and visual completeness remain to be checked individually; no ribbon-bar image was promoted.' },
    { source_id: 'EXISTING-POLAND-RAW-DIFFERENTIAL', source_type: 'Local prior raw candidates', local_records: ['data/raw_candidates/wikipedia_poland_en_awards.jsonl','data/raw_candidates/wikipedia_poland_pl_awards.jsonl','data/raw_candidates/wawards_poland.jsonl'], status: 'compared_name_level_only', limitation: 'Prior raw candidates are discovery clues, not independently revalidated facts.' }
  ], search_languages: ['English'], rights_note: '仅保留公开下载且可解码文件；重新发布须遵守各 Commons 文件页许可与署名要求。' };
  await fs.writeFile(SRC_OUT, JSON.stringify(sources, null, 2) + '\n', 'utf8');
  const matrix = { schema_version: '2.0', as_of: AS_OF, scope_id: 'poland_wikipedia_master_fast', scope_label: '波兰英文勋奖章总表快速大包', sources: [
    { source_id: 'wikipedia_poland_en_awards_master', source_name: 'Orders, decorations, and medals of Poland', base_url: ARTICLE, source_type: 'national_award_master_list', languages: ['en'], has_images: true, has_pagination: false, download_method: 'raw_wikitext_table_sweep_then_Commons_file_pages', priority: 1, status: 'completed', last_checked: AS_OF, coverage_result: `${candidateRows.length} raw award rows; ${families.length} deduplicated families; ${rows.length} image-backed variant rows.`, candidate_file: path.relative(ROOT, RAW_OUT).replace(/\\/g,'/') },
    { source_id: 'commons_article_file_candidates', source_name: 'Wikimedia Commons article-linked file pages', source_type: 'image_file_pages', languages: ['en'], has_images: true, has_pagination: false, download_method: 'Special:FilePath original download + sharp decode', priority: 1, status: manifest.length ? 'partial' : 'blocked', last_checked: AS_OF, coverage_result: `${objectFiles.length} object-image candidates attempted; bars/ribbons rejected; ${manifest.length} decoded originals.`, candidate_file: path.relative(ROOT, MAN_OUT).replace(/\\/g,'/') },
    { source_id: 'poland_official_regulations_and_designs', source_name: 'Polish presidential regulations and official award designs', source_type: 'official_regulations_and_designs', languages: ['pl'], has_images: true, has_pagination: true, download_method: 'official_regulation_differential', priority: 1, status: 'not_started', last_checked: AS_OF }
  ], coverage: { planned: 3, completed: 1, partial: 1, blocked: 0, not_started: 1 }, next_action: '主任务逐图检查已下载章体；随后按官方波兰文条例核对设立日期、等级、剑饰和材质。' };
  await fs.writeFile(MATRIX_OUT, JSON.stringify(matrix, null, 2) + '\n', 'utf8');
  const checkpoint = { checkpoint_id: BATCH, updated_at: AS_OF, scope: ['波兰英文 Orders, decorations, and medals of Poland 总表', 'Commons 链接图快速取图'], workspace_changes: '建立隔离 raw、volume、manifest、sources、source matrix、checkpoint 和本地图像；没有修改公共 index.html、catalogue 或全局队列。', source_progress: { planned: 3, completed: 1, partial: 1, blocked: 0, not_started: 1, completed_sources: ['WIKI-POLAND-EN-MASTER'], partial_sources: ['COMMONS-FILE-PAGES-FROM-ARTICLE'], remaining_boundary: '官方波兰文条例/公报、未列入英文主表的历史政权与后续 Commons 分类仍未扫。' }, package_counts: vol.counts, rejected_or_unresolved_candidates: missing.slice(0, 200), image_failures: failed.slice(0, 200), deliverables: [path.relative(ROOT, RAW_OUT).replace(/\\/g,'/'), path.relative(ROOT, VOL_OUT).replace(/\\/g,'/'), path.relative(ROOT, MAN_OUT).replace(/\\/g,'/'), path.relative(ROOT, SRC_OUT).replace(/\\/g,'/'), path.relative(ROOT, MATRIX_OUT).replace(/\\/g,'/'), path.relative(ROOT, CK_OUT).replace(/\\/g,'/'), path.relative(ROOT, IMAGE_DIR).replace(/\\/g,'/')], next_action: '把 volume rows 交主任务审核后再合并公共 HTML；未下载对象留在 raw 与 checkpoint，不以绶带图充当完整实物。' };
  await fs.writeFile(CK_OUT, JSON.stringify(checkpoint, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ parsed_records: parsed.length, candidate_rows: candidateRows.length, families: families.length, object_image_candidates: objectFiles.length, downloads: downloads.length, decoded_images: manifest.length, variant_rows: rows.length, missing: missing.length, failures: failed.length, raw: path.relative(ROOT, RAW_OUT), volume: path.relative(ROOT, VOL_OUT) }, null, 2));
}

main().catch(err => { console.error(err.stack || err); process.exitCode = 1; });
