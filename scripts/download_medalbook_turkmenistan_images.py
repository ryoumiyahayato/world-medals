"""Download every image exposed by the completed MedalBook Turkmenistan sweep."""
import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / 'data/raw_candidates/medalbook_turkmenistan.jsonl'
download.OUT_DIR = download.ROOT / 'assets/raw/medalbook_turkmenistan'
download.MANIFEST = download.ROOT / 'data/source_sweeps/medalbook_turkmenistan_images_2026-09-28.json'
download.SOURCE_ID = 'medalbook_turkmenistan_images'
download.BOUNDARY = 'All original image URLs exposed by the completed Turkmenistan order and medal sweeps'

if __name__ == '__main__':
    download.main()
