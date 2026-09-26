"""Regression audit for previously reported catalogue failures."""
import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")

section_pattern = re.compile(r'<section[^>]*data-country="([^"]+)"[^>]*id="([^"]+)"[^>]*>(.*?)</section>', re.S)
row_pattern = re.compile(r'<tr id="([^"]+)"[^>]*>(.*?)</tr>', re.S)
image_pattern = re.compile(r'<img[^>]+src="([^"]+)"')

paths = defaultdict(list)
hashes = defaultdict(list)
ribbon_only = []
row_ids = []
section_ids = []

for country, section_id, body in section_pattern.findall(html):
    section_ids.append(section_id)
    for row_id, row_body in row_pattern.findall(body):
        row_ids.append(row_id)
        text = re.sub(r'<[^>]+>', ' ', row_body)
        if re.search(r'(^|[； ])(单独绶带|勋略|ribbon bar|ribbon only)($|[； ])', text, re.I):
            ribbon_only.append((section_id, row_id, re.sub(r'\s+', ' ', text).strip()[:180]))
        for path in image_pattern.findall(row_body):
            occurrence = (country, section_id, row_id, path)
            paths[path].append(occurrence)
            hashes[hashlib.sha256((ROOT / path).read_bytes()).hexdigest()].append(occurrence)

duplicate_paths = {key: value for key, value in paths.items() if len(value) > 1}
duplicate_hashes = {key: value for key, value in hashes.items() if len(value) > 1}
cross_country_hashes = {key: value for key, value in duplicate_hashes.items() if len({x[0] for x in value}) > 1}

assert len(row_ids) == len(set(row_ids)), "duplicate record IDs in rendered sections"
assert len(section_ids) == len(set(section_ids)), "duplicate rendered section IDs"
assert not duplicate_paths, f"one local path reused by multiple rows: {duplicate_paths}"
assert not duplicate_hashes, f"one image payload reused by multiple rows: {duplicate_hashes}"
assert not cross_country_hashes, f"same image payload appears under multiple countries: {cross_country_hashes}"
assert not ribbon_only, f"standalone ribbon/ribbon-bar rows detected: {ribbon_only}"
assert all(label not in html for label in ("第一轮整理中", "开放图源补充卷", "中东与穆斯林国家"))
assert 'placeholder="名称、原名、年代、国家；支持单字"' in html
assert 'function showCountry(country)' in html and 'function showTarget(target)' in html

print(
    "PASS regression audit:",
    len(section_ids), "country/period sections;",
    len(row_ids), "pictured rows;",
    len(paths), "unique local image paths;",
    "0 reused image payloads; 0 ribbon-only rows; concise labels and generic single-character search retained",
)
