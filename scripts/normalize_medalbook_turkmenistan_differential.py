"""Normalize the pictured and unpictured MedalBook differential after the complete Wawards sweep."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = [json.loads(line) for line in (ROOT / 'data/raw_candidates/medalbook_turkmenistan.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
HARVEST = json.loads((ROOT / 'data/source_sweeps/medalbook_turkmenistan_images_2026-09-28.json').read_text(encoding='utf-8'))['items']
OUT_DIR = ROOT / 'assets/images/medalbook_turkmenistan'
VOLUME = ROOT / 'data/volumes/turkmenistan_medalbook_differential.json'
MANIFEST = ROOT / 'data/volumes/turkmenistan_medalbook_differential_manifest.json'

MISSING = {
    'Commemorative Medal 15 Years of Independence Military Parade',
    'Commemorative Medal for 15 Years of Turkmenistan Independence',
    'Honour Award of Saparmurat Turkmenbashi',
    'Jubilee Medal 10 Years of Turkmenistan Independence',
    'Jubilee Medal 60 Anniversary of Victory in Great Patriotic War',
    'Makhtumkuli International Prize Award',
    'Medal for Service to the State',
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = next(item for item in HARVEST if item['record_index'] == 12 and item['image_index'] == 2)
    source_path = ROOT / source['local_path']
    with Image.open(source_path) as image:
        image.verify()
    relative = 'assets/images/medalbook_turkmenistan/hero_gold_shield_star.jpg'
    shutil.copy2(source_path, ROOT / relative)
    record_id = 'TKM-MEDALBOOK-HERO-GOLD-SHIELD'
    view_key = record_id + '-VIEW1'
    record = {
        'id': record_id,
        'family': 'TKM-AWARD-GOLDEN-CRESCENT-MEDAL',
        'country_zh': '土库曼斯坦',
        'name': '土库曼斯坦英雄（金新月奖章）',
        'original': 'Hero of Turkmenistan',
        'date': '1992年9月30日设立',
        'variant': '金质盾形星章版',
        'views': [{'key': view_key, 'label': '完整正面'}],
        'source_ids': [RAW[12]['source_id']],
        'image_kind': 'object_photo',
        'html_eligible': True,
    }
    image = {
        'key': 'tkm-medalbook-hero-gold-shield',
        'record_id': record_id,
        'view_key': view_key,
        'local_path': relative,
        'source_page': source['page_url'],
        'image_url': source['url'],
        'artist': 'MedalBook catalogue image',
        'license': 'Source terms apply; retained for offline research catalogue',
        'dimensions': [source['width'], source['height']],
        'bytes': source['bytes'],
        'sha256': source['sha256'],
        'decoded': True,
        'visually_checked': True,
    }
    unpictured = [
        {
            'source_id': item['source_id'],
            'name': item['page_title'],
            'date': '待考',
            'page_url': item['page_url'],
            'status': '完整目录有记录；当前来源无公开实物图',
        }
        for item in RAW if item['page_title'] in MISSING
    ]
    VOLUME.write_text(json.dumps({'as_of': '2026-09-28', 'volume': '土库曼斯坦 · MedalBook差集', 'records': [record]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    MANIFEST.write_text(json.dumps({
        'as_of': '2026-09-28',
        'images': [image],
        'unpictured_candidates': unpictured,
        'excluded_candidates': [
            {'kind': 'same_variant_lower_resolution_or_repeated_source_images', 'count': 6, 'reason': '其余图片与已入编版型相同或为同图低分辨率副本，未重复入编'}
        ],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rows': 1, 'families': 1, 'views': 1, 'unpictured': len(unpictured)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
