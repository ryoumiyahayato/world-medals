"""Sweep the complete public MedalBook Turkmenistan order and medal catalogues."""
from __future__ import annotations
import urllib.parse
import sweep_medalbook_thailand as sweep

sweep.COUNTRY_PREFIX = '/middle-east/turkmenistan/'
sweep.SOURCE_SLUG = 'turkmenistan'
sweep.SOURCE_SYSTEM = 'MedalBook Turkmenistan catalogue'
sweep.COUNTRY_LABEL = 'Turkmenistan'
sweep.AS_OF = '2026-09-28'
sweep.INDEX_URLS = [
    sweep.BASE + '/middle-east/turkmenistan/orders',
    sweep.BASE + '/middle-east/turkmenistan/medals-decorations',
]
sweep.CACHE = sweep.ROOT / 'sources/pages/medalbook_turkmenistan'
sweep.OUT = sweep.ROOT / 'data/raw_candidates/medalbook_turkmenistan.jsonl'
sweep.STATE = sweep.ROOT / 'data/source_sweeps/medalbook_turkmenistan_2026-09-28.json'


def award_item_link(href: str) -> str | None:
    url = urllib.parse.urljoin(sweep.BASE, href)
    parsed = urllib.parse.urlsplit(url)
    prefixes = ('/middle-east/turkmenistan/orders/', '/middle-east/turkmenistan/medals-decorations/')
    if parsed.netloc != 'www.medalbook.com' or not parsed.path.startswith(prefixes):
        return None
    if len(parsed.path[len(sweep.COUNTRY_PREFIX):].strip('/').split('/')) < 3:
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))


sweep.item_link = award_item_link

if __name__ == '__main__':
    sweep.main()
