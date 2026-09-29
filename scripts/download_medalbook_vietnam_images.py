"""Download every image exposed by the completed MedalBook Vietnam sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_vietnam.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_vietnam"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_vietnam_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_vietnam_images"
download.BOUNDARY = "All original image URLs exposed by the completed MedalBook Vietnam sweep"

if __name__ == "__main__":
    download.main()
