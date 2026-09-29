const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const harvestPath = path.join(root, 'data', 'image_harvest', 'czech_slovak_fast_2026-09-28.json');
const normPath = path.join(root, 'data', 'normalized', 'czech_slovak_fast_2026-09-28.json');
const outHarvest = path.join(root, 'data', 'image_harvest', 'czech_slovak_fast_reviewed_2026-09-28.json');
const outNorm = path.join(root, 'data', 'normalized', 'czech_slovak_fast_reviewed_2026-09-28.json');
const cpPath = path.join(root, 'data', 'checkpoints', 'czech_slovak_fast_2026-09-28.json');

const harvest = JSON.parse(fs.readFileSync(harvestPath, 'utf8').replace(/^\uFEFF/, ''));
const norm = JSON.parse(fs.readFileSync(normPath, 'utf8').replace(/^\uFEFF/, ''));

// The Artis Bohemiae Amicis file is a contextual photograph containing the medal
// alongside its certificate. Retain it as a source lead, but do not promote it to
// a body-only catalogue row under the current image rules.
const excludedIds = new Set(['csk-cze_artis']);
const excludedCandidates = new Set(['CZE-ARTIS']);
const specialNotes = {
  'csk_csk_wl_collar': 'Complete collar chain is visible; pendant/star are not shown in this file. Kept only as collar-chain reference, not a generic grand-cross badge.',
  'csk_csk_mil_order_liberty': 'Complete breast-star insignia visible; row describes the pictured star form, not an unseen pendant.',
  'csk_csk_wl_victory_star': 'Complete breast-star insignia visible; row describes the pictured star form.',
  'csk_cssr_friendship': 'Complete star insignia visible; no unseen pendant inferred.',
  'csk_cssr_red_banner': 'Complete star insignia visible; no unseen pendant inferred.',
  'csk_cssr_red_star': 'Complete star insignia visible; no unseen pendant inferred.',
  'csk_cze_diplomacy_en': 'Complete medal and ribbon visible; not a ribbon-only image.',
  'csk_cze_mod_injury': 'Front/reverse pair of the complete medal design is visible; no certificate or box used.',
  'csk_cze_heroism': 'Complete medal pair shown; medal bodies and ribbons visible.',
};

for (const f of harvest.files) {
  if (excludedIds.has(f.file_id)) {
    f.visual_integrity = 'reviewed: contextual medal-plus-certificate photograph; excluded from正文 because certificate is present';
    f.chapter_eligibility = 'excluded_related_reference';
    f.notes = `${f.notes || ''}; retained only as an excluded source lead under certificate rule.`;
  } else {
    f.visual_integrity = specialNotes[f.file_id] || 'reviewed contact sheet: complete medal/order body visible; not ribbon-only, portrait, box, certificate or reverse-only';
    f.chapter_eligibility = 'body_eligible_pictured_row';
    if (f.source_image_kind.includes('derivative')) f.notes = `${f.notes || ''}; original Wikimedia route returned HTTP 429 in this environment; local file is the complete Commons max-size derivative and is not called original-resolution.`;
  }
}

const byId = new Map(norm.records.map(r => [r.candidate_id, r]));
const reviewed = [];
for (const rec of norm.records) {
  if (excludedCandidates.has(rec.candidate_id)) continue;
  if (rec.candidate_id === 'CSSR-SLOVAK-UPRISING-II-BACK') {
    const front = byId.get('CSSR-SLOVAK-UPRISING-II');
    if (front) {
      front.image_manifest_file_ids = [...new Set([...(front.image_manifest_file_ids || []), ...(rec.image_manifest_file_ids || [])])];
      front.views = [
        { key: front.image_manifest_file_ids[0], label: '正面' },
        { key: front.image_manifest_file_ids[1], label: '背面' }
      ];
      front.variant_key = '二等；正背同件';
      front.notes = `${front.notes}; 同一版型背面已配对，未另计新行。`;
    }
    continue;
  }
  rec.image_status = 'complete local image; contact-sheet visually checked';
  rec.public_row_readiness = 'ready_for_body_row_after_parent_merge';
  if (!rec.views) rec.views = [{ key: rec.image_manifest_file_ids[0], label: '正面或完整对象图' }];
  reviewed.push(rec);
}
// Ensure the merged SNP row is retained in its original order.
const mergedFront = byId.get('CSSR-SLOVAK-UPRISING-II');
if (mergedFront && !reviewed.some(r => r.candidate_id === mergedFront.candidate_id)) {
  mergedFront.image_status = 'complete local image pair; contact-sheet visually checked';
  mergedFront.public_row_readiness = 'ready_for_body_row_after_parent_merge';
  reviewed.splice(Math.max(0, norm.records.findIndex(r => r.candidate_id === mergedFront.candidate_id)), 0, mergedFront);
}

const families = new Set(reviewed.map(r => r.family_id));
const revisedNorm = {
  ...norm,
  batch_id: 'czech_slovak_fast_reviewed_2026-09-28',
  records: reviewed,
  summary: {
    ...norm.summary,
    reviewed_records: reviewed.length,
    reviewed_families: families.size,
    excluded_certificate_context: excludedCandidates.size,
    manual_visual_review_status: 'complete_contact_sheet_review',
    public_files_modified: []
  }
};
const revisedHarvest = {
  ...harvest,
  batch_id: 'czech_slovak_fast_reviewed_2026-09-28',
  files: harvest.files,
  counts: {
    ...harvest.counts,
    visually_checked_files: harvest.files.length,
    body_eligible_rows: reviewed.length,
    excluded_related_reference: excludedIds.size,
    manual_review_pending: 0
  },
  review: {
    status: 'complete_contact_sheet_review',
    excluded_file_ids: [...excludedIds],
    image_policy_applied: 'reject ribbon-only, certificate, box, portrait and reverse-only; merge same-item front/back; preserve exact variant wording',
    contact_sheet: 'data/image_harvest/czech_slovak_fast_contact_sheet.jpg'
  },
  public_files_modified: []
};
fs.writeFileSync(outNorm, JSON.stringify(revisedNorm, null, 2) + '\n', 'utf8');
fs.writeFileSync(outHarvest, JSON.stringify(revisedHarvest, null, 2) + '\n', 'utf8');

const cp = JSON.parse(fs.readFileSync(cpPath, 'utf8').replace(/^\uFEFF/, ''));
cp.status = 'reviewed_ready_for_parent_merge';
cp.images = { requested_specs: harvest.counts.requested_specs, downloaded_files: harvest.counts.downloaded_files, decoded_files: harvest.counts.decoded_files, visually_checked_files: harvest.files.length, body_eligible_rows: reviewed.length, excluded_related_reference: excludedIds.size, failed_or_missing: harvest.counts.missing_or_failed, contact_sheet: 'data/image_harvest/czech_slovak_fast_contact_sheet.jpg' };
cp.normalized = { families: families.size, variants: reviewed.length, status: 'reviewed_ready_for_parent_merge', file: 'data/normalized/czech_slovak_fast_reviewed_2026-09-28.json' };
cp.quality = { no_ribbon_only_rows: true, no_certificate_context_rows: true, no_portrait_or_box_rows: true, front_back_pair_merged: true, decoded_local_files_verified: true, original_route_429_derivatives_explicitly_labeled: true };
cp.next_action = 'Parent merges reviewed normalized rows into the main offline catalogue; no public HTML modified by this task.';
cp.public_files_modified = [];
fs.writeFileSync(cpPath, JSON.stringify(cp, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ reviewed_rows: reviewed.length, families: families.size, body_eligible_files: harvest.files.length - excludedIds.size, excluded: [...excludedCandidates], normalized: 'data/normalized/czech_slovak_fast_reviewed_2026-09-28.json', image_harvest: 'data/image_harvest/czech_slovak_fast_reviewed_2026-09-28.json', checkpoint: 'data/checkpoints/czech_slovak_fast_2026-09-28.json' }, null, 2));
