"""Download every image exposed by the complete MedalBook Imperial China sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_imperial_china.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_imperial_china"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_imperial_china_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_imperial_china_images"
download.BOUNDARY = "All original image URLs exposed by the completed MedalBook Imperial China sweep"

if __name__ == "__main__":
    download.main()
