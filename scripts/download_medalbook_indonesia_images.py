"""Download every image exposed by the completed MedalBook Indonesia sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_indonesia.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_indonesia"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_indonesia_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_indonesia_images"
download.BOUNDARY = "All original image URLs exposed by the completed Indonesia catalogue sweep"

if __name__ == "__main__": download.main()
