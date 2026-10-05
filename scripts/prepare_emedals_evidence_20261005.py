"""Join cached object evidence to provisional matches without asserting identification."""
from pathlib import Path
import collections, hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
SID = 'emedals_austria_imperial_20261005'
def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

raw = read_lines(ROOT / 'data/raw_candidates' / f'{SID}.jsonl')
objects = {row['object_id']: row for row in read_lines(ROOT / 'data/raw_candidates' / f'{SID}_objects.jsonl')}
crosswalk = json.loads((ROOT / 'data/staging' / SID / 'family_crosswalk.json').read_text(encoding='utf-8'))
matches = {row['object_id']: family for family, rows in crosswalk['existing_family_groups'].items() for row in rows}
drafts, image_queue = [], {}
for row in raw:
    evidence = objects[row['object_id']]
    cached = ROOT / evidence['html']
    assert hashlib.sha256(cached.read_bytes()).hexdigest() == evidence['sha256']
    description = evidence['description']
    flags = {}
    for label, pattern in {
        'copy_or_reproduction': r'\b(?:copy|copies|replica|reproduction|reproductions)\b',
        'private_or_later_manufacture': r'privately|private purchase|later manufacture|post.?war|restrike',
        'damage_or_missing_parts': r'chipped|missing|repaired|damage|broken|replacement',
        'miniature': r'\bminiature\b',
    }.items():
        fragments = [part.strip() for part in re.split(r'(?<=[.!?;])\s+', description) if re.search(pattern, part, re.I)]
        if fragments:
            flags[label] = fragments
    draft = {
        'source_id': SID, 'object_id': row['object_id'], 'object_page': evidence['object_page'],
        'accessed': evidence['accessed'], 'title': row['page_title'],
        'provisional_family_id': matches.get(row['object_id']), 'category': row['category'],
        'evidence_summary_original': description, 'cached_page': evidence['html'],
        'page_sha256': evidence['sha256'], 'review_flags': flags,
        'images': evidence['images'], 'rights': evidence['rights'],
        'status': 'object_evidence_joined_identification_and_visual_review_pending',
    }
    drafts.append(draft)
    for image in evidence['images']:
        url = image['image_url']
        item = image_queue.setdefault(url, dict(image_url=url, source_id=SID, objects=[], width=image.get('width'), height=image.get('height'), status='original_download_and_full_outline_review_pending', publication_eligible=False))
        item['objects'].append(row['object_id'])

out = ROOT / 'data/normalized_drafts' / f'{SID}_object_evidence.jsonl'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in drafts), encoding='utf-8')
queue = ROOT / 'data/queues' / f'{SID}_images.json'
queue.write_text(json.dumps(dict(source_id=SID, as_of='2026-10-05', boundary='1724 cached collection objects; image URLs are leads, not accepted views', tasks=list(image_queue.values())), ensure_ascii=False, indent=2), encoding='utf-8')
counts = dict(object_evidence=len(drafts), provisional_matches=len(matches), unique_original_image_leads=len(image_queue), flagged_objects=sum(bool(row['review_flags']) for row in drafts), accepted_new_families=0, accepted_new_views=0)
(ROOT / 'data/checkpoints' / f'{SID}_evidence.json').write_text(json.dumps(dict(as_of='2026-10-05', counts=counts, next='Review family, variant and flagged object evidence; download missing original views in bounded batches'), indent=2), encoding='utf-8')
print(json.dumps(counts))
