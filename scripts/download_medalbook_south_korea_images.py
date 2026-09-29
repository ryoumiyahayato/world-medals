"""Download every image exposed by the complete MedalBook South Korea sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_south_korea.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_south_korea"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_south_korea_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_south_korea_images"
download.BOUNDARY = "All original image URLs exposed by the completed MedalBook South Korea sweep"

if __name__ == "__main__":
    download.main()
