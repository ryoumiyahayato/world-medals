"""Download every image exposed by the completed MedalBook Republic of China sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_republic_of_china.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_republic_of_china"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_republic_of_china_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_republic_of_china_images"
download.BOUNDARY = "All original image URLs exposed by the completed MedalBook Republic of China sweep"

if __name__ == "__main__":
    download.main()
