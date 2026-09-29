const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const norm = JSON.parse(fs.readFileSync(path.join(root, 'data', 'normalized', 'czech_slovak_fast_reviewed_2026-09-28.json'), 'utf8'));
const harvest = JSON.parse(fs.readFileSync(path.join(root, 'data', 'image_harvest', 'czech_slovak_fast_reviewed_2026-09-28.json'), 'utf8'));
const outDir = path.join(root, 'data', 'volumes');
fs.mkdirSync(outDir, {recursive:true});

// Main-volume boundary: formal orders/medals only. Historical commemorative
// medals stay in the reviewed package and are explicitly listed as related
// exclusions rather than counted as national award-system rows.
const excludedMain = new Map([
  ['CSK-WL-COLLAR', 'collar-chain reference lacks the pendant/star in this file; retained as related source lead'],
  ['CSK-BACHMAC', 'historical commemorative medal; separate related category'],
  ['CSK-SOKOLOV', 'historical commemorative medal; separate related category'],
  ['CSK-SNP-COMMEMORATIVE', 'commemorative medal of an order; separate related category'],
  ['SVK1939-DEFENCE-MARCH', 'historical commemorative medal; separate related category'],
  ['CZE-ARTIS', 'certificate-context photograph; excluded by image policy']
]);
const imageById = new Map(harvest.files.map(f => [f.file_id, f]));
const records = [];
const usedImageIds = new Set();
const relatedExcluded = [];

for (const r of norm.records) {
  if (excludedMain.has(r.candidate_id)) {
    relatedExcluded.push({candidate_id:r.candidate_id, reason:excludedMain.get(r.candidate_id), image_manifest_file_ids:r.image_manifest_file_ids || []});
    continue;
  }
  const views = (r.views || (r.image_manifest_file_ids || []).map((key,i)=>({key,label:i===0?'正面':'背面'}))).filter(v => imageById.has(v.key));
  if (!views.length) continue;
  for (const v of views) usedImageIds.add(v.key);
  records.push({
    id: `${r.candidate_id}-01`, family:r.family_id, country_zh:r.country, period_scope:r.period_scope,
    name:r.name, original:r.original, date:(r.date_candidates || []).join('；'), variant:r.variant_key,
    views, source_ids:[...new Set((r.image_manifest_file_ids || []).map(x => `commons-${x.replace(/^csk-/, '')}`))],
    image_kind:'specimen_photo_or_complete_object_image', html_eligible:true,
    notes:r.notes || ''
  });
}

// A back image is retained only when paired into the same row; it cannot create
// a standalone row or inflate the family count.
const manifestImages = [];
const shaSeen = new Set();
for (const id of usedImageIds) {
  const f = imageById.get(id);
  if (!f || shaSeen.has(f.sha256)) continue;
  shaSeen.add(f.sha256);
  const isBack = /back|rev/i.test(f.candidate_ids?.[0] || '') || /back|rev/i.test(f.source_file_title || '');
  manifestImages.push({
    view_key:id, local_path:f.relative_path, source_id:id,
    download_status:f.source_image_kind.includes('derivative') ? 'downloaded_complete_commons_derivative_original_429' : 'downloaded_complete_source_file',
    source_page_url:f.source_page_url, source_original_url:f.image_url,
    retrieval_url:f.source_image_kind.includes('derivative')
      ? `https://commons.wikimedia.org/w/thumb.php?f=${encodeURIComponent(f.source_file_title)}&w=2000`
      : (f.retrieval_url || f.image_url),
    license:f.license_or_rights, width:f.width, height:f.height, bytes:f.bytes, sha256:f.sha256,
    image_kind:isBack ? 'paired_back_view_not_standalone_row' : 'complete_object_front_or_full_set',
    notes:f.notes || ''
  });
}

const families = new Set(records.map(r=>r.family));
const volume = {
  as_of:'2026-09-28', volume_id:'czech_slovak_fast_2026-09-28',
  scope:'Czechoslovakia (historical), Czech Republic and Slovakia formal award systems; first pictured differential pack',
  source_boundary:'WMI complete visible text lists plus official Prague Castle/Czech MoD and Slovak President/MoD headings; Commons exact file pages for selected object images',
  records,
  related_excluded:relatedExcluded,
  sources:[
    {source_id:'wmi_czechoslovakia_1918_1948',url:'https://www.medals.org.uk/czechoslovakia/czechoslovak-republic/czechoslovak-republic-text.htm',role:'Czechoslovak Republic 1918–48 master list'},
    {source_id:'wmi_czechoslovakia_csr_1948_1989',url:'https://www.medals.org.uk/czechoslovakia/csr/csr-text.htm',role:'CSSR 1948–89 master list'},
    {source_id:'wmi_czech_republic_1989_present',url:'https://www.medals.org.uk/czechoslovakia/czech-republic/czech-republic-text.htm',role:'Czech Republic master list'},
    {source_id:'hrad_czech_state_decorations',url:'https://www.hrad.cz/en/czech-republic/state-decorations',role:'Czech official state-decoration verification'},
    {source_id:'czech_mod_awards',url:'https://www.mo.gov.cz/scripts/detail.php?id=6412',role:'Czech Ministry of Defence military-award verification'},
    {source_id:'president_slovakia_state_decorations',url:'https://www.prezident.sk/prezidentsky-palac/zeleny-salon/',role:'Slovak official state-decoration list'},
    {source_id:'wikipedia_czech_republic_awards',url:'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_the_Czech_Republic',role:'Czech discovery cross-check'},
    {source_id:'wikipedia_slovakia_awards',url:'https://en.wikipedia.org/wiki/Orders,_decorations,_and_medals_of_Slovakia',role:'Slovak discovery cross-check'},
    {source_id:'commons_czech_slovak_awards',url:'https://commons.wikimedia.org/wiki/Category:Orders,_decorations_and_medals_of_Czechoslovakia',role:'exact image file pages; licenses/attribution retained per manifest'}
  ],
  counts:{pictured_rows:records.length, families:families.size, manifest_images:manifestImages.length, paired_back_views:manifestImages.filter(x=>x.image_kind.includes('paired_back')).length, related_excluded:relatedExcluded.length, duplicate_sha256_removed:harvest.files.length - manifestImages.length},
  public_files_modified:[]
};
const manifest = {
  as_of:'2026-09-28', volume_id:volume.volume_id, images:manifestImages,
  excluded_related:relatedExcluded,
  counts:{images:manifestImages.length, complete_front_or_full_set:manifestImages.filter(x=>!x.image_kind.includes('paired_back')).length, paired_back_views:manifestImages.filter(x=>x.image_kind.includes('paired_back')).length, sha256_unique:shaSeen.size},
  source_policy:'No ribbon-only, portrait, certificate, box, search preview, reverse-only standalone row or duplicate payload. Back images appear only as paired views in the same row.',
  public_files_modified:[]
};
const volumePath = path.join(outDir,'czech_slovak_fast_2026-09-28.json');
const manifestPath = path.join(outDir,'czech_slovak_fast_2026-09-28_manifest.json');
fs.writeFileSync(volumePath,JSON.stringify(volume,null,2)+'\n','utf8');
fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n','utf8');
const cpPath = path.join(root,'data','checkpoints','czech_slovak_fast_2026-09-28.json');
const cp = JSON.parse(fs.readFileSync(cpPath,'utf8').replace(/^\uFEFF/,''));
cp.status='standard_volume_ready_for_parent_merge';
cp.standard_volume={file:'data/volumes/czech_slovak_fast_2026-09-28.json',manifest:'data/volumes/czech_slovak_fast_2026-09-28_manifest.json',pictured_rows:records.length,families:families.size,manifest_images:manifestImages.length,related_excluded:relatedExcluded.length,duplicate_sha256_removed:harvest.files.length-manifestImages.length};
cp.next_action='Parent merges standard volume; reviewed candidates and related exclusions remain available for later separate appendices.';
cp.public_files_modified=[];
fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n','utf8');
console.log(JSON.stringify({pictured_rows:records.length,families:families.size,manifest_images:manifestImages.length,related_excluded:relatedExcluded.length,volume:'data/volumes/czech_slovak_fast_2026-09-28.json',manifest:'data/volumes/czech_slovak_fast_2026-09-28_manifest.json'},null,2));
