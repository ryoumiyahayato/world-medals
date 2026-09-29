"""Download every image exposed by the complete MedalBook Manchukuo sweep."""

import download_medalbook_thailand_images as download

download.INPUT = download.ROOT / "data/raw_candidates/medalbook_manchukuo.jsonl"
download.OUT_DIR = download.ROOT / "assets/raw/medalbook_manchukuo"
download.MANIFEST = download.ROOT / "data/source_sweeps/medalbook_manchukuo_images_2026-09-28.json"
download.SOURCE_ID = "medalbook_manchukuo_images"
download.BOUNDARY = "All original image URLs exposed by the completed 44-page MedalBook Manchukuo sweep"

if __name__ == "__main__":
    download.main()
